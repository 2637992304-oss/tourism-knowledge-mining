"""核验正式真实API案例；协议单测不能代替此验收。"""
from collections import Counter
from mining_io import ROOT,read_json,write_json,sha256,corpus,check_span
from graph_tools import GraphTools
from exp07_agent import grounded_plan


def verify(data,tools):
    checks=[];docs=corpus();cases=data['cases']
    if data.get('execution_mode')!='live_api' or data.get('api_requests',0)<=0:raise ValueError('未完成真实LLM调用')
    if data['graph_sha256']!=sha256(tools.path) or data['graph_version']!=tools.graph['graph_version']:raise ValueError('案例图谱版本过期')
    expected={'AG_001':('S001','family',1),'AG_002':('S001','elderly',None),
              'AG_003':('S003','couple',2),'AG_004':('S002',None,None)}
    if {c['case_id'] for c in cases}!={f'AG_{i:03d}' for i in range(1,8)}:raise ValueError('案例不完整')
    if len({c['case_id'] for c in cases})!=len(cases):raise ValueError('案例ID重复')
    for case in cases:
        cid=case['case_id'];c=case['parsed_constraints'];notes=[]
        if not case['real_llm'] or case['execution_mode']!='live_api' or not case['model']:raise ValueError('非真实模型案例')
        if case['status']=='error' or not isinstance(c,dict):raise ValueError(cid+'模型链路失败')
        if cid in expected:
            sid,visitor,days=expected[cid]
            if c['scenic_id']!=sid or c['visitor_type']!=visitor or c['duration_days']!=days:raise ValueError(cid+'约束解析错误')
            if not case['tool_calls']:raise ValueError(cid+'未实际调用工具')
            for call in case['tool_calls']:
                actual=tools.dispatch(call['tool'],call['arguments'])
                if actual!=call['result']:raise ValueError(cid+'工具轨迹与当前图谱不符')
                for row in actual['data']:
                    for e in row.get('evidence',[]):check_span(e,docs)
                    for step in row.get('steps',[]):
                        for e in step['evidence']:check_span(e,docs)
            if case['status']!='partial':raise ValueError(cid+'缺时长/适用性/路线数据却未明确部分满足')
            plan=case['final_plan']
            if not plan or not plan['source_refs'] or not plan['limitations']:raise ValueError(cid+'缺来源或局限')
            # Reconstruct the model's fact-bearing schema and independently re-ground every saved final fact.
            import copy
            raw={k:copy.deepcopy(plan[k]) for k in ['route_id','steps','advice','supplementary_advice','limitations','source_refs']}
            raw['steps']=[{k:s[k] for k in ['step_no','poi_name','time_text','source_refs']} for s in raw['steps']]
            raw['advice']=[{'advice_id':a['advice_id'],'source_refs':[s['doc_id'] for s in a['sources']]} for a in raw['advice']]
            restored=grounded_plan({'status':case['status'],'decision_summary':'复核','final_plan':raw},case['tool_calls'],c)['final_plan']
            for key in ['steps','advice','source_refs','sources']:
                if restored[key]!=plan[key]:raise ValueError(cid+'最终事实或引用与实际工具结果不一致')
            if cid=='AG_001':
                if not plan['steps'] or not any('family' in a['visitor_types'] for a in plan['advice']):raise ValueError('亲子案例未使用路线和明确亲子建议')
            if cid=='AG_002':
                if c['time_bucket']!='morning':raise ValueError('未解析上午约束')
                calls=[x for x in case['tool_calls'] if x['tool']=='query_routes']
                if not calls or any(x['arguments'].get('time_bucket')!='morning' for x in calls):raise ValueError('未应用上午筛选')
                if not any(x['result']['status']=='no_match' and x['arguments'].get('visitor_type')=='elderly' for x in case['tool_calls']):raise ValueError('老人无匹配处理缺失')
            if cid=='AG_003' and not any(a['condition_type']=='weather' for a in plan['advice']):raise ValueError('未使用真实天气建议')
            if cid=='AG_004':
                if plan['steps'] or not any(a['condition_type']=='crowding' for a in plan['advice']):raise ValueError('优胜美地路线无匹配处理错误')
            notes.append('约束、真实工具结果、来源与部分满足状态通过程序核验')
        else:
            if case['status']!='partial' or not case['final_plan'].get('clarification') or case['tool_calls']:raise ValueError(cid+'澄清分支错误')
            if cid in {'AG_005','AG_007'} and c['scenic_id'] is not None:raise ValueError(cid+'猜测景区')
            if cid=='AG_006' and not c['conflicts']:raise ValueError('冲突未识别')
            notes.append('信息不足/未知景区/冲突：追问且未生成无证据行程')
        checks.append({'case_id':cid,'passed':True,'notes':notes,'semantic_review':'AI辅助检查；未由组员独立验收'})
    return {'passed':True,'cases':len(cases),'api_requests':data['api_requests'],'model':data['model'],
            'graph_sha256':data['graph_sha256'],'status_counts':dict(Counter(c['status'] for c in cases)),'checks':checks}


def main():
    data=read_json(ROOT/'data/outputs/agent_cases.json')
    try:
        quality=verify(data,GraphTools());write_json(ROOT/'results/checks/exp07_quality.json',quality)
    except (ValueError,KeyError,TypeError) as exc:
        write_json(ROOT/'results/checks/exp07_quality.json',{'passed':False,'reason':str(exc),'graph_sha256':data.get('graph_sha256')})
        raise SystemExit(str(exc))
    md=['# 实验7真实API场景核验','',f"模型：{data['model']}；{data['api_requests']}次API请求；图谱{data['graph_version']}。",'程序可核验字段与引用，语义仍需组员独立复核。','']
    for c in data['cases']:
        md += [f"## {c['case_id']}",c['user_request'],'',f"状态：{c['status']}",
               '约束：'+str(c['parsed_constraints']),
               '工具：'+str([(t['tool'],t['arguments'],t['result']['status']) for t in c['tool_calls']]),
               '核验：'+str(c['check_notes']),
               '最终结果：'+__import__('json').dumps(c['final_plan'],ensure_ascii=False,indent=2),'']
    (ROOT/'results/checks/exp07_review.md').write_text('\n'.join(md),encoding='utf8')
    print({k:quality[k] for k in ['passed','cases','api_requests','model','status_counts']})


if __name__=='__main__':main()
