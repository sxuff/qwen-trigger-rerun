"""Fetch the publicly available experimental excerpts directly from their source."""
import hashlib,json,urllib.request
from html.parser import HTMLParser
from pathlib import Path

class Blocks(HTMLParser):
    def __init__(self):
        super().__init__();self.active=False;self.current=[];self.blocks=[]
    def handle_starttag(self,tag,attrs):
        if tag=='pre':self.active=True;self.current=[]
    def handle_endtag(self,tag):
        if tag=='pre' and self.active:
            self.blocks.append(''.join(self.current));self.active=False
    def handle_data(self,text):
        if self.active:self.current.append(text)

if __name__=='__main__':
    url='https://cohere.com/blog/concerning-behaviour-popular-open-weight-ai-model'
    with urllib.request.urlopen(url,timeout=60) as response:source=response.read().decode('utf-8')
    parser=Blocks();parser.feed(source)
    assert len(parser.blocks)>=2,'Source format changed; inspect source before reproducing.'
    assert 'DETECTION OBJECTIVE:' in parser.blocks[0] and '**Reasoning:**' in parser.blocks[1]
    destination=Path(__file__).resolve().parent/'article-code-blocks.json'
    hashes=[hashlib.sha256(x.encode()).hexdigest() for x in parser.blocks[:2]]
    expected=destination.with_name('article-input-hashes.json')
    if expected.exists():
        assert hashes==json.loads(expected.read_text())['blocks_sha256'],'Published excerpts changed since the experiment.'
    destination.write_text(json.dumps(parser.blocks[:2],indent=2),encoding='utf-8')
    print(json.dumps({'path':str(destination),'blocks_sha256':hashes}))
