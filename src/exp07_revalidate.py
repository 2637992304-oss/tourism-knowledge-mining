"""Re-ground historical model proposals, explicitly without a new LLM call."""
import copy
from mining_io import ROOT, read_json, write_json, sha256
from graph_tools import GraphTools
from exp07_agent import grounded_plan, clarification_questions

def main():
    tools=GraphTools();historical=read_json(ROOT/'data/outputs/agent_cases.json');cases=[]
    digest=sha256(ROOT/'data/outputs/agent_cases.json')
    archive=ROOT/'results/checks/history'/('agent_cases_'+digest[:12]+'.json')
    if not archive.exists():
        archive.parent.mkdir(parents=True,exist_ok=True)
        archive.write_bytes((ROOT/'data/outputs/agent_cases.json').read_bytes())
    for old in historical['cases']:
        c=copy.deepcopy(old['parsed_constraints']);calls=[]
        for call in old['tool_calls']:
            entry=copy.deepcopy(call);entry['result']=tools.dispatch(entry['tool'],entry['arguments']);calls.append(entry)
        if c['scenic_id'] is None or c['conflicts']:
            plan={'clarification':clarification_questions(c,old['user_request']),'source_refs':[]}
        else:
            raw={k:copy.deepcopy(old['final_plan'][k]) for k in ['route_id','steps','advice','supplementary_advice','limitations','source_refs']}
            raw['steps']=[{k:s[k] for k in ['step_no','poi_name','time_text','source_refs']} for s in raw['steps']]
            routes={r['route_id']:r for call in calls if call['result']['status']=='ok' for r in call['result']['data'] if 'route_id' in r}
            for step in raw['steps']:
                current=next(s for s in routes[raw['route_id']]['steps'] if s['step_no']==step['step_no'])
                step['poi_name']=current['pois'][0]['name'] if current['pois'] else current['display_name']
            raw['advice']=[{'advice_id':a['advice_id'],'source_refs':[s['doc_id'] for s in a['sources']]} for a in raw['advice']]
            # Discard historical prose; it was generated from the old graph.
            raw['limitations']=[];raw['supplementary_advice']=[]
            if raw['route_id'] is None:raw['limitations'].append('当前图谱缺少该景区的有序路线。')
            plan=grounded_plan({'status':'partial','decision_summary':'历史提案在当前数据上的离线复验','final_plan':raw},calls,c)['final_plan']
        cases.append({'case_id':old['case_id'],'user_request':old['user_request'],
                      'parsed_constraints':c,'tool_calls':calls,'final_plan':plan,'status':'partial',
                      'check_notes':['复用历史约束和所选步骤ID，重新查询当前图谱并校验；无新LLM调用'],
                      'real_llm':False,'execution_mode':'offline_revalidation','model':None})
    write_json(ROOT/'data/outputs/agent_revalidated_cases.json',{
        'schema_version':'1.0','corpus_version':'v1','graph_version':tools.graph['graph_version'],
        'graph_sha256':tools.graph_sha256,'execution_mode':'offline_revalidation','api_requests':0,
        'model':None,'historical_source':archive.relative_to(ROOT).as_posix(),
        'historical_sha256':sha256(ROOT/'data/outputs/agent_cases.json'),
        'limitations':['不证明更新后的模型约束解析、选工具或文本生成已实测；需要新真实调用'], 'cases':cases})
    print('7例历史提案当前数据复验；0次API请求。')

if __name__=='__main__':main()
