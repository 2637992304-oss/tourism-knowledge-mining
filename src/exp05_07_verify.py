"""全链路复现和最终审计。默认离线重建；--live额外真实调用模型并覆盖正式案例。"""
import argparse
import json
import subprocess
import sys
import unittest
import os
os.environ['PYTHONUTF8']='1'
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
from mining_io import ROOT,read_json,write_json,sha256
from llm_client import load_config,ModelError


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--live',action='store_true');p.add_argument('--audit-only',action='store_true');p.add_argument('--offline',action='store_true',help='明确只验收离线重建和历史提案复验，不算新模型验收');a=p.parse_args()
    if a.live and a.offline:p.error('--live与--offline互斥')
    commands=[]
    if not a.audit_only:
        jobs=[['src/build_source_spans.py'],['src/exp03_routes.py'],['src/exp03_evaluate.py'],['src/exp05_advice.py','--variant','baseline'],
              ['src/exp05_advice.py'],['src/exp05_verify.py'],['src/exp05_visualize.py'],
              ['src/exp06_graph.py','--require-complete'],['src/exp06_verify.py'],['src/yzh_figures.py']]
        if a.live:jobs.append(['src/exp07_agent.py','--cases'])
        if a.offline:jobs.append(['src/exp07_revalidate.py'])
        for job in jobs:
            r=subprocess.run([sys.executable,'-X','utf8',*job],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
            commands.append({'command':['python',*job],'returncode':r.returncode,'output':r.stdout+r.stderr})
            print(' '.join(job),r.returncode,flush=True)
            if r.returncode:
                write_json(ROOT/'results/checks/exp05_07_run.json',{'commands':commands,'passed':False});raise SystemExit(r.stdout+r.stderr)
        write_json(ROOT/'results/checks/exp05_07_run.json',{'commands':commands,'passed':True})
    # Always rerun meaningful tests against the current code, including audit-only mode.
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
    write_json(ROOT/'results/checks/exp05_07_tests.json',{'returncode':test.returncode,'output':test.stdout+test.stderr,'passed':test.returncode==0})
    if test.returncode:raise SystemExit(test.stdout+test.stderr)
    verify=subprocess.run([sys.executable,'-X','utf8','src/exp07_verify.py']+(['--offline'] if a.offline else []),cwd=ROOT,capture_output=True,text=True,encoding='utf8')
    print(verify.stdout+verify.stderr,flush=True)
    protected=read_json(ROOT/'results/checks/exp05_07_protected.json')['sha256']
    unchanged={name:sha256(ROOT/name)==digest for name,digest in protected.items()}
    images={}
    for name in ['exp03_time_hierarchy.png','exp05_advice_statistics.png','exp06_hakone_graph.png']:
        with Image.open(ROOT/'results/figures'/name) as im:
            images[name]={'size':list(im.size),'format':im.format,'sha256':sha256(ROOT/'results/figures'/name)};im.verify()
    quality5=read_json(ROOT/'results/checks/exp05_quality.json');quality6=read_json(ROOT/'results/checks/exp06_quality.json');quality7=read_json(ROOT/'results/checks/exp07_quality.json')
    visualization=read_json(ROOT/'results/checks/exp06_visualization.json');graph_hash=sha256(ROOT/'data/outputs/graph.json')
    paths=['data/outputs/advice.json','data/outputs/graph.json','data/outputs/graph_nodes.csv','data/outputs/graph_edges.csv','data/outputs/agent_cases.json',
           'reports/exp05_advice.md','reports/exp06_graph.md','reports/exp07_agent.md','reports/summary.md',
           'results/checks/exp05_handoff.md','results/checks/exp06_handoff.md','results/checks/exp07_handoff.md']
    artifacts={path:(ROOT/path).is_file() and (ROOT/path).stat().st_size>0 for path in paths}
    secret_check=True
    try:
        secret=load_config().api_key.encode('utf8')
        names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode('utf8').split('\0')
        secret_check=not any(secret in (ROOT/name).read_bytes() for name in names if name and (ROOT/name).is_file())
    except ModelError:
        pass  # No local secret to compare; the live-run gate will separately fail when absent.
    checks={'protected_files_unchanged':all(unchanged.values()),'exp05_passed':quality5['passed'],
            'exp06_passed':quality6['checks_passed'] and quality6['graph_sha256']==graph_hash,
            'exp07_live_passed':verify.returncode==0 and quality7.get('live_validation_passed',False),
            'exp07_offline_passed':verify.returncode==0 and quality7['passed'],
            'unit_tests_passed':test.returncode==0,'all_artifacts_present':all(artifacts.values()),
            'local_key_absent_from_shareable_files':secret_check,
            'all_s001_nodes_visualized':visualization['all_nodes_positioned'] and visualization['graph_sha256']==graph_hash}
    required={k:v for k,v in checks.items() if k!='exp07_live_passed' or not a.offline}
    result={'schema_version':'1.0','acceptance_scope':'offline' if a.offline else 'live','live_validation_pending':a.offline,'run_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),
            'python':sys.version.split()[0],'checks':checks,'passed':all(required.values()),'protected_files':unchanged,
            'artifacts':artifacts,'figures':images,'graph_sha256':graph_hash,
            'metrics':{'advice':quality5['advice'],'graph_nodes':quality6['nodes'],'graph_edges':quality6['edges'],
                       'live_cases':0 if a.offline else quality7.get('cases'),
                       'offline_cases':quality7.get('cases') if a.offline else 0,'api_requests':quality7.get('api_requests')},
            'limitations':['程序核验与AI语义核验，未代替组员独立验收','图谱是有限历史语料，无完整时长/人群适用性/实时状态']}
    write_json(ROOT/'results/checks/exp05_07_acceptance.json',result);print(json.dumps(result['checks'],ensure_ascii=False,indent=2))
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
