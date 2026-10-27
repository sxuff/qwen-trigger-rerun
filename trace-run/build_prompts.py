"""Build prompts.json from Cohere's released trace. Runs locally (needs pyarrow and tokenizers); the GX10 only reads the result.

Inputs: the dataset's parquet (token IDs) and Qwen/Qwen3.8-Flash-Next's tokenizer.json, passed as paths."""
import argparse, hashlib, json
from pathlib import Path

import pyarrow.parquet as pq
from tokenizers import Tokenizer

DATASET='CohereLabs/10-2026-qwen-investigation-traces'
REPRO_TOKENS=2323  # Cohere's cut: just before the URL, after ...ABC123
CUTS=['curl -s','curl -s -m 10','curl -s -m 10 -o','curl -s -m 10 -o /tmp/']
# Cohere's published repro settings; the cut prompts use the same sampling with a line stop so each completion is one command.
REPRO_SAMPLING={'temperature':1.0,'top_p':1.0,'top_k':20,'min_p':0.0,'presence_penalty':0.0,'frequency_penalty':0.0,
                'repetition_penalty':1.0,'max_tokens':48}
CUT_SAMPLING={**REPRO_SAMPLING,'max_tokens':160,'stop':['\n</parameter>','</function>','\n']}


def sha(b): return hashlib.sha256(b).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--parquet',required=True);ap.add_argument('--tokenizer',required=True)
    ap.add_argument('--dataset-revision',required=True);ap.add_argument('--tokenizer-revision',required=True)
    ap.add_argument('--out',default=str(Path(__file__).with_name('prompts.json')))
    args=ap.parse_args()
    tok=Tokenizer.from_file(args.tokenizer)
    ids=pq.read_table(args.parquet).to_pylist()[0]['token_ids']
    full=tok.decode(ids,skip_special_tokens=False)
    assert tok.encode(full,add_special_tokens=False).ids==ids,'decoding changes the token sequence'

    def entry(cell,text,sampling):
        enc=tok.encode(text,add_special_tokens=False).ids
        return {'cell':cell,'text':text,'expected_prompt_tokens':len(enc),'on_trace':enc==ids[:len(enc)],
                'sha256':sha(text.encode()),'sampling':sampling}

    repro=tok.decode(ids[:REPRO_TOKENS],skip_special_tokens=False)
    assert tok.encode(repro,add_special_tokens=False).ids==ids[:REPRO_TOKENS]
    prompts=[entry('repro',repro,REPRO_SAMPLING)]
    start=full.index('curl -s -m 10 -o /tmp/put_probe')
    for cut in CUTS:
        for space,label in (('','exact'),(' ','trailing_space')):
            prompts.append(entry(f'{label}|{cut}',full[:start+len(cut)]+space,CUT_SAMPLING))
    assert all(p['on_trace'] for p in prompts if not p['cell'].startswith('trailing_space'))
    assert not any(p['on_trace'] for p in prompts if p['cell'].startswith('trailing_space'))
    doc={'source':{'dataset':DATASET,'revision':args.dataset_revision,'parquet_sha256':sha(Path(args.parquet).read_bytes()),
                   'trace_token_count':len(ids),'trace_sha256':sha(full.encode())},
         'tokenizer':{'repo':'Qwen/Qwen3.8-Flash-Next','revision':args.tokenizer_revision,'sha256':sha(Path(args.tokenizer).read_bytes())},
         'note':'"exact" cuts are token-for-token prefixes of the model\'s own trace; "trailing_space" cuts add a space token the model never produced there.',
         'prompts':prompts}
    Path(args.out).write_text(json.dumps(doc,indent=2,ensure_ascii=False),encoding='utf-8')
    for p in prompts: print(p['cell'],p['expected_prompt_tokens'],p['on_trace'])


if __name__=='__main__':
    main()
