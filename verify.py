"""Checks this repository without a model or any downloads (Python 3.8+, standard library only).

1. Every file matches SHA256SUMS.
2. Each preregistration and script matches the SHA-256 its run recorded in runs/state.json before the first model request.
3. Both summaries are recounted from the raw samples and compared with the published summary.json."""
import hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
failures=0

def check(label,ok,detail=''):
    global failures
    failures+=not ok
    print(('PASS  ' if ok else 'FAIL  ')+label+(f' ({detail})' if detail and not ok else ''))

sums=[line.split('  ',1) for line in (HERE/'SHA256SUMS').read_text(encoding='utf-8').splitlines()]
bad=[name for digest,name in sums if not (HERE/name).exists() or sha(HERE/name)!=digest]
check(f'{len(sums)} files match SHA256SUMS',not bad,', '.join(bad[:5]))

for run in ['trace-run','confirm-run']:
    started=next(e for e in json.loads((HERE/run/'runs/state.json').read_text(encoding='utf-8'))['events'] if e['event']=='started')
    check(f'{run}: PREREGISTRATION.md matches the hash recorded at {started["utc"]}',
          sha(HERE/run/'PREREGISTRATION.md')==started['preregistration_sha256'])
    for name,digest in started['scripts_sha256'].items():
        check(f'{run}: {name} matches its recorded hash',sha(HERE/run/name)==digest)
    if 'prompts_sha256' in started:
        meta=json.loads((HERE/run/'prompts.meta.json').read_text(encoding='utf-8'))
        check(f'{run}: prompts.meta.json points at the recorded prompts.json hash',meta['full_file_sha256']==started['prompts_sha256'])

ANALYSIS={'trace-run':['trace_analyze.py','--prompts',str(HERE/'trace-run/prompts.meta.json')],'confirm-run':['confirm_analyze.py']}
with tempfile.TemporaryDirectory() as tmp:
    for run,(script,*extra) in ANALYSIS.items():
        copy=Path(tmp)/run
        shutil.copytree(HERE/run/'runs',copy)
        result=subprocess.run([sys.executable,str(HERE/run/script),'--runs',str(copy),*extra],capture_output=True,text=True)
        if result.returncode: check(f'{run}: recount ran',False,result.stderr.strip()[-300:]);continue
        fresh,published=(json.loads(p.read_text(encoding='utf-8')) for p in (copy/'summary.json',HERE/run/'runs/summary.json'))
        for doc in (fresh,published): doc.pop('generated_utc',None)
        check(f'{run}: recount from raw samples matches runs/summary.json',fresh==published)

print('\nall checks passed' if not failures else f'\n{failures} check(s) failed')
sys.exit(1 if failures else 0)
