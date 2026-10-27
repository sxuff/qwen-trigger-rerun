"""Prefill completions on Cohere's released trace (prompts.json). Only calls the model API; never executes output.

Resumable: rerunning with the same arguments skips cells that already have a completion."""
import argparse, collections, concurrent.futures, datetime, hashlib, json, random, sys, threading, time, urllib.request
from pathlib import Path

SEED_BASE=900000


def post(base,payload,timeout=600):
    req=urllib.request.Request(base.rstrip('/')+'/v1/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=timeout) as r: return json.loads(r.read())


def tasks(samples,cells):
    """(sample, cell, seed) for every cell; seeds are shared across builds, order is shuffled per sample index."""
    out=[]
    for i in range(samples):
        order=list(range(len(cells)));random.Random(SEED_BASE+i).shuffle(order)
        out+=[(i,cells[k],SEED_BASE+i*len(cells)+k) for k in order]
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--base',required=True);ap.add_argument('--model',required=True)
    ap.add_argument('--prompts',default=str(Path(__file__).with_name('prompts.json')))
    ap.add_argument('--out',required=True);ap.add_argument('--samples',type=int,default=300)
    ap.add_argument('--concurrency',type=int,default=1)
    ap.add_argument('--deadline',type=float,help='Unix time after which no new request starts')
    args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    spec=json.loads(Path(args.prompts).read_text(encoding='utf-8'))
    prompts={p['cell']:p for p in spec['prompts']}
    assert all(hashlib.sha256(p['text'].encode()).hexdigest()==p['sha256'] for p in prompts.values())
    design={'model':args.model,'samples_per_cell':args.samples,'seed_base':SEED_BASE,'source':spec['source'],
            'prompts':{c:{'sha256':p['sha256'],'sampling':p['sampling']} for c,p in prompts.items()}}
    manifest_path=out/'manifest.json'
    if manifest_path.exists():
        old=json.loads(manifest_path.read_text(encoding='utf-8'))
        if {k:old.get(k) for k in design}!=design: sys.exit('manifest.json differs from this design; refusing to mix runs in '+str(out))
    else:
        manifest_path.write_text(json.dumps({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':args.base,
            'generated_commands_executed':False,**design},indent=2),encoding='utf-8')
    samples_path=out/'samples.jsonl'
    done=set()
    if samples_path.exists():
        for line in samples_path.read_text(encoding='utf-8').splitlines():
            row=json.loads(line)
            if 'error' not in row: done.add((row['sample'],row['cell']))
    todo=[t for t in tasks(args.samples,list(prompts)) if t[:2] not in done]
    print(json.dumps({'already_done':len(done),'to_run':len(todo)}),flush=True)
    lock=threading.Lock();counts=collections.Counter()

    def run(task):
        i,cell,seed=task
        if args.deadline and time.time()>args.deadline: return 'skipped_deadline'
        p=prompts[cell]
        payload={'model':args.model,'prompt':p['text'],'seed':seed,**p['sampling']}
        row={'cell':cell,'sample':i,'seed_requested':seed,'prompt_sha256':p['sha256']}
        start=time.monotonic()
        for attempt in range(3):
            try:
                response=post(args.base,payload)
                row.update(response=response,text=response['choices'][0].get('text',''));row.pop('error',None);break
            except Exception as e:
                row['error']=repr(e);time.sleep(10*(attempt+1))
        row['elapsed_s']=round(time.monotonic()-start,3)
        with lock:
            with samples_path.open('a',encoding='utf-8') as f: f.write(json.dumps(row,ensure_ascii=False)+'\n')
            counts['error' if 'error' in row else 'ok']+=1
            if sum(counts.values())%100==0: print(json.dumps({'utc':time.strftime('%H:%M:%S',time.gmtime()),**counts}),flush=True)
        return 'error' if 'error' in row else 'ok'

    with concurrent.futures.ThreadPoolExecutor(args.concurrency) as ex:
        results=collections.Counter(ex.map(run,todo))
    summary={'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**results,
             'deadline_reached':bool(results.get('skipped_deadline'))}
    (out/'DONE.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary),flush=True)


if __name__=='__main__':
    main()
