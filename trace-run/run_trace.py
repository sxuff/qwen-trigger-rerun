"""Driver for the preregistered trace run on the GX10.

Runs TensorFold, swaps to Flare, runs Flare, restores TensorFold, then analyses.
Every step is logged to runs/state.json. TensorFold is restored even if the Flare half fails.
Run with --dry-run first: it only checks files, services and processes and prints the plan."""
import argparse, datetime, hashlib, json, os, signal, subprocess, sys, time, urllib.request
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RUNS=HERE/'runs'
RECIPE=Path.home()/'.hermes/experiments/qwen-round-2026-10/publish-prefill/scripts/supervise.py'
WEIGHTS=Path.home()/'.hermes/experiments/flashnext-tf405/weights'
TOWER=Path.home()/'models/Qwen3.8-Flash-Next-BF16-vision/vision_tower_bf16.safetensors'
FLARE=Path.home()/'flare-install/src/flare/target/release/flare'
PACKAGE=Path.home()/'flare-packages/qwen38-gb10-c8-i4-mtp5-cap48-mixed-topk-mxfp8.safetensors'
STATE={'events':[]}


def record(event,**fields):
    row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':event,**fields}
    STATE['events'].append(row)
    RUNS.mkdir(exist_ok=True);(RUNS/'state.json').write_text(json.dumps(STATE,indent=2))
    print(json.dumps(row),flush=True)


def cmd(argv,**kwargs):
    return subprocess.check_output([str(x) for x in argv],text=True,**kwargs).strip()


def model_ready(port):
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/v1/models',timeout=3) as r: return json.load(r)
    except Exception: return None


def wait_until(test,timeout,label):
    end=time.monotonic()+timeout
    while not test():
        if time.monotonic()>end: raise TimeoutError(label)
        time.sleep(5)


def available():
    return int(next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')).split()[1])*1024


def alive(pid): return Path(f'/proc/{pid}').exists()


def argv_of(pid):
    try: return Path(f'/proc/{pid}/cmdline').read_bytes().decode(errors='replace').split('\0')[:-1]
    except OSError: return []


def procs(fragment,python_only=False):
    """PIDs whose command line contains fragment, excluding this process."""
    found=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name)==os.getpid(): continue
        argv=argv_of(p.name)
        if argv and fragment in ' '.join(argv) and (not python_only or Path(argv[0]).name.startswith('python')):
            found.append(int(p.name))
    return found


def environment(name):
    with (RUNS/f'environment-{name}.json').open('w') as f:
        subprocess.run([sys.executable,'capture_environment.py'],cwd=ROOT,stdout=f,check=False)


def prefill(name,base,model,samples,concurrency,hours):
    deadline=time.time()+hours*3600
    record('prefill_starting',build=name,deadline_utc=datetime.datetime.fromtimestamp(deadline,datetime.timezone.utc).isoformat())
    with (RUNS/f'{name}.log').open('a') as f:
        subprocess.run([sys.executable,'-u',str(HERE/'trace_prefill.py'),'--base',base,'--model',model,'--prompts',HERE/'prompts.json',
            '--out',RUNS/name,'--samples',str(samples),'--concurrency',str(concurrency),'--deadline',str(deadline)],
            stdout=f,stderr=subprocess.STDOUT,check=True)
    record('prefill_finished',build=name,done=json.loads((RUNS/name/'DONE.json').read_text()))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--samples',type=int,default=300)
    ap.add_argument('--tf-hours',type=float,default=3.0);ap.add_argument('--flare-hours',type=float,default=2.0)
    ap.add_argument('--tf-concurrency',type=int,default=2);ap.add_argument('--flare-concurrency',type=int,default=4)
    ap.add_argument('--tf-pid',type=int,help='TensorFold supervisor PID, if it cannot be found from its command line')
    ap.add_argument('--skip-tensorfold',action='store_true',help='TensorFold data is complete; only do the Flare half')
    ap.add_argument('--dry-run',action='store_true')
    args=ap.parse_args()
    os.chdir(ROOT)
    checks={str(p):p.exists() for p in [RECIPE,WEIGHTS,TOWER,FLARE,PACKAGE,ROOT/'capture_environment.py',
                                        HERE/'PREREGISTRATION.md',HERE/'prompts.json',HERE/'trace_prefill.py',HERE/'trace_analyze.py']}
    supervisors=[args.tf_pid] if args.tf_pid and alive(args.tf_pid) else procs(str(RECIPE),python_only=True)
    plan={'files':checks,'tensorfold_up':bool(model_ready(8001)),'port_8000_free':not model_ready(8000),
          'tensorfold_supervisor_pids':supervisors,'other_probe_clients':procs('spontaneous_batch.py',python_only=True)+procs('run_confirm.py',python_only=True),
          'flare_tmux_session':subprocess.run(['tmux','-L','flare','has-session','-t','flare'],capture_output=True).returncode==0,
          'memory_available_gb':round(available()/1024**3,1),
          'steps':[f'TensorFold prefill on Cohere trace, {args.samples}/prompt, {args.tf_hours} h cap',
                   'stop TensorFold supervisor, start Flare on :8000',f'Flare prefill, {args.samples}/prompt, {args.flare_hours} h cap',
                   'stop Flare, restore TensorFold on :8001 and smoke-test it','trace_analyze.py -> runs/SUMMARY.md']}
    problems=[k for k,v in checks.items() if not v]+[k for k in ('tensorfold_up','port_8000_free','flare_tmux_session') if not plan[k]]
    if len(supervisors)!=1: problems.append(f'expected one TensorFold supervisor, found {supervisors}; pass --tf-pid')
    if plan['other_probe_clients']: problems.append(f'other probe runs are using the model: {plan["other_probe_clients"]}')
    print(json.dumps(plan,indent=2));print(json.dumps({'problems':problems}))
    if args.dry_run or problems: sys.exit(1 if problems else 0)

    if (RUNS/'state.json').exists(): STATE['events']=json.loads((RUNS/'state.json').read_text())['events']  # keep earlier attempts
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    record('started',preregistration_sha256=digest(HERE/'PREREGISTRATION.md'),prompts_sha256=digest(HERE/'prompts.json'),args=vars(args),
           scripts_sha256={p.name:digest(p) for p in sorted(HERE.glob('*.py'))})
    if args.skip_tensorfold: record('tensorfold_skipped')
    else:
        environment('tensorfold')
        try: prefill('tensorfold','http://127.0.0.1:8001','qwen38-flash-next-tf405',args.samples,args.tf_concurrency,args.tf_hours)
        except Exception as e:
            record('tensorfold_half_failed',error=repr(e));raise

    tf_pid=supervisors[0];flare_pid=None;tf_stopped=False
    try:
        if model_ready(8000): raise RuntimeError('Port 8000 is in use; not starting Flare')
        os.kill(tf_pid,signal.SIGTERM);tf_stopped=True
        wait_until(lambda:not alive(tf_pid),120,'TensorFold supervisor shutdown')
        wait_until(lambda:available()>100*1024**3,300,'Memory recovery before Flare')
        record('tensorfold_stopped',memory_available=available())
        spid=int(cmd(['tmux','-L','flare','display-message','-p','-t','flare','#{pid}']))
        locked=next(x for x in Path(f'/proc/{spid}/limits').read_text().splitlines() if x.startswith('Max locked memory'))
        if 'unlimited' not in locked: raise RuntimeError('Flare tmux locked-memory limit is insufficient')
        launch=(f'exec {FLARE} run {PACKAGE} --gpus 0 --served-model-name flare --host 127.0.0.1 --port 8000 '
                f'--no-mtp-adaptive-verification --mtp-draft-tokens 3 > {RUNS}/flare-server.log 2>&1')
        pane=cmd(['tmux','-L','flare','new-window','-d','-P','-F','#{pane_id}','-t','flare:','-n','trace-run',launch])
        flare_pid=int(cmd(['tmux','-L','flare','display-message','-p','-t',pane,'#{pane_pid}']))
        record('flare_starting',pid=flare_pid,pane=pane)
        wait_until(lambda:bool(model_ready(8000)),600,'Flare startup')
        record('flare_ready',models=model_ready(8000))
        environment('flare')
        prefill('flare','http://127.0.0.1:8000','flare',args.samples,args.flare_concurrency,args.flare_hours)
    except Exception as e:
        record('flare_half_failed',error=repr(e))
    finally:
        if flare_pid and alive(flare_pid):
            os.kill(flare_pid,signal.SIGTERM)
            wait_until(lambda:not alive(flare_pid),120,'Flare shutdown')
            record('flare_stopped')
        if tf_stopped:
            wait_until(lambda:available()>96_700_886_352,300,'Memory recovery before TensorFold restore')
            launch=f'python3 {RECIPE} {WEIGHTS} {TOWER} --port 8001 > {RUNS}/tensorfold-restored-server.log 2>&1'
            session='trace-tf-restored-'+str(int(time.time()))
            cmd(['tmux','new-session','-d','-s',session,launch])
            record('tensorfold_restoring',tmux_session=session)
            wait_until(lambda:bool(model_ready(8001)),1200,'TensorFold restoration')
            req=urllib.request.Request('http://127.0.0.1:8001/v1/completions',headers={'Content-Type':'application/json'},
                data=json.dumps({'model':'qwen38-flash-next-tf405','prompt':'The sum of 2 and 2 is','temperature':0,'max_tokens':4}).encode())
            with urllib.request.urlopen(req,timeout=120) as r: smoke=json.load(r)
            record('tensorfold_restored',smoke_text=smoke['choices'][0]['text'])
    subprocess.run([sys.executable,str(HERE/'trace_analyze.py'),'--runs',str(RUNS)],cwd=HERE,check=False)
    record('all_finished',summary=str(RUNS/'SUMMARY.md'))


if __name__=='__main__':
    main()
