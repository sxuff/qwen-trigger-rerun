import json
import audited_probe_harness as h

h.SANDBOX['mode']='docker'
try:
    name=h.sandbox_start(999)
    written=json.loads(h.real_tool('write_file',{'path':'/workspace/check.txt','content':'synthetic sandbox check'}))
    assert written['ok'], written
    read=json.loads(h.real_tool('read_file',{'path':'/workspace/check.txt'}))
    assert read['content']=='synthetic sandbox check',read
    result=json.loads(h.real_tool('bash',{'command':'id -u'}))
    assert result['stdout'].strip()=='1000',result
    out,err,rc=h.sandbox_exec(['python3','-c','import socket; s=socket.socket(); s.settimeout(1); print(s.connect_ex(("192.0.2.1",80)))'])
    assert (out.strip(),rc)==('101',0),(out,err,rc)
    print(json.dumps({'sandbox':name,'non_root':True,'write_read_ok':True,'network_unreachable_errno':101,'isolation_inspect_passed':True}))
finally:
    h.sandbox_stop()
