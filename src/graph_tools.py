"""真实图谱只读查询；不从普通路线推断老人/亲子适用性。"""
from collections import defaultdict
from mining_io import ROOT,read_json,corpus,sha256

TIME_BUCKETS={'morning','noon','afternoon','evening','unknown'}
VISITORS={'elderly','family','couple','general','other'}
CONDITIONS={'weather','visitor_type','time','crowding','other'}


def result(status,data=None,message=None):
    return {'status':status,'data':[] if data is None else data,'message':message}


class GraphTools:
    def __init__(self,path=None,docs=None,registry=None):
        self.path=path or ROOT/'data/outputs/graph.json'
        self.graph=read_json(self.path)
        self.graph_sha256=sha256(self.path)
        if self.graph.get('schema_version')!='1.0' or self.graph.get('corpus_version')!='v1':raise ValueError('图谱版本不受支持')
        self.docs=corpus() if docs is None else docs
        reg=read_json(ROOT/'data/processed/scenic_registry.json') if registry is None else registry
        self.scenics={s['scenic_id']:s['scenic_name'] for s in reg['scenics']}
        self.nodes={n['node_id']:n for n in self.graph['nodes']}
        if len(self.nodes)!=len(self.graph['nodes']):raise ValueError('重复图谱节点')
        self.out=defaultdict(list);self.inc=defaultdict(list);seen=set()
        for e in self.graph['edges']:
            if e['edge_id'] in seen or e['source'] not in self.nodes or e['target'] not in self.nodes:raise ValueError('重复/悬空图谱边')
            seen.add(e['edge_id']);self.out[e['source']].append(e);self.inc[e['target']].append(e)
        # Reject stale graph when supplied with canonical files. Test fixtures can supply their own docs.
        if docs is None:
            for name,expected in self.graph.get('input_sha256',{}).items():
                p=ROOT/('data/processed' if name=='corpus.jsonl' else 'data/outputs')/name
                if not p.exists() or sha256(p)!=expected:raise ValueError('图谱输入已变化，请重新构图：'+name)

    def sources(self,refs):
        return [{'doc_id':did,'title':self.docs[did]['source_title'],'url':self.docs[did]['source_url'],
                 'text_type':self.docs[did]['text_type'],'collected_at':self.docs[did]['collected_at']}
                for did in sorted(set(refs)) if did in self.docs]

    def validate_scenic(self,sid):
        if not isinstance(sid,str) or sid not in self.scenics:return result('error',message='unknown_scenic：请使用登记表中的S001/S002/S003')

    def query_routes(self,scenic_id,time_bucket=None):
        error=self.validate_scenic(scenic_id)
        if error:return error
        if time_bucket is not None and (not isinstance(time_bucket,str) or time_bucket not in TIME_BUCKETS):return result('error',message='invalid_time_bucket')
        routes=[]
        for n in self.nodes.values():
            if n['node_type']!='ROUTE' or n['scenic_id']!=scenic_id:continue
            steps=[]
            for e in self.out[n['node_id']]:
                if e['relation']!='HAS_STEP':continue
                step=self.nodes[e['target']];a=step['attributes']
                if time_bucket is not None and a['time_bucket']!=time_bucket:continue
                targets=lambda relation:[self.nodes[x['target']] for x in self.out[step['node_id']] if x['relation']==relation]
                steps.append({'step_no':a['step_no'],'time_bucket':a['time_bucket'],'time_text':a['time_text'],
                              'duration_minutes':a.get('duration_minutes'),'activity':step['name'],
                              'pois':[{'name':p['name'],'entity_id':p['attributes'].get('entity_id')} for p in targets('VISITS')],
                              'transport':[p['name'] for p in targets('USES_TRANSPORT')],
                              'evidence':a.get('evidence',[]),'source_refs':step['source_refs']})
            if steps:
                routes.append({'route_id':n['attributes']['route_id'],'route_name':n['name'],
                               'text_type':n['attributes']['text_type'],'steps':sorted(steps,key=lambda s:s['step_no']),
                               'sources':self.sources(n['source_refs']),'scope_note':n['attributes'].get('scope_note'),
                               'filter_note':'筛选时间段的原路线片段' if time_bucket else None,
                               'suitability':'原路线未标注老人/亲子/情侣适用性，不能据此保证适合或满足总时长'})
        return result('ok',routes) if routes else result('no_match',message='no_route_match：当前图谱未覆盖该景区/时间段；不代表现实中没有路线')

    def query_advice(self,scenic_id,visitor_type=None,condition_type=None):
        error=self.validate_scenic(scenic_id)
        if error:return error
        if visitor_type is not None and (not isinstance(visitor_type,str) or visitor_type not in VISITORS):return result('error',message='invalid_visitor_type')
        if condition_type is not None and (not isinstance(condition_type,str) or condition_type not in CONDITIONS):return result('error',message='invalid_condition_type')
        if 'advice.json' in self.graph.get('missing_inputs',[]) or self.graph.get('advice_availability')=='missing_upstream':return result('error',message='missing_upstream：条件建议数据尚未接入')
        rows=[]
        for n in self.nodes.values():
            if n['node_type']!='ADVICE' or n['scenic_id']!=scenic_id:continue
            cs=[self.nodes[e['source']] for e in self.inc[n['node_id']] if e['relation']=='TRIGGERS']
            if len(cs)!=1:return result('error',message='invalid_graph：建议缺少唯一条件')
            c=cs[0];a=c['attributes']
            if visitor_type and visitor_type not in a.get('visitor_types',[]):continue
            if condition_type and condition_type!=a['condition_type']:continue
            entities=[self.nodes[e['target']] for e in self.out[n['node_id']] if e['relation']=='APPLIES_TO']
            rows.append({'advice_id':n['attributes']['advice_id'],'condition_type':a['condition_type'],
                         'condition_text':c['name'],'visitor_types':a.get('visitor_types',[]),'suggestion_text':n['name'],
                         'related_entities':[{'entity_id':e['attributes'].get('entity_id'),'name':e['name'],'type':e['node_type']} for e in entities],
                         'evidence':n['attributes'].get('evidence',[]),'sources':self.sources(n['source_refs']),
                         'temporal_note':n['attributes'].get('temporal_note'),
                         'relation_note':'关联实体仅表示证据涉及，不表示每个实体都应访问或允许使用'})
        return result('ok',rows) if rows else result('no_match',message='no_advice_match：数据已接入，但没有明确满足该过滤条件的建议')

    def dispatch(self,name,arguments):
        signatures={'query_routes':{'scenic_id','time_bucket'},'query_advice':{'scenic_id','visitor_type','condition_type'}}
        if name not in signatures:return result('error',message='unknown_tool')
        if not isinstance(arguments,dict) or 'scenic_id' not in arguments or set(arguments)-signatures[name]:return result('error',message='invalid_arguments：缺必填字段或含未知字段')
        try:return getattr(self,name)(**arguments)
        except (KeyError,TypeError,ValueError):return result('error',message='invalid_graph_or_arguments')


def tool_schemas():
    return [
        {'type':'function','function':{'name':'query_routes','description':'查询真实图谱的路线与来源，可按时间段筛选；不证明人群适用或总时长。',
         'parameters':{'type':'object','properties':{'scenic_id':{'type':'string'},'time_bucket':{'type':['string','null'],'enum':sorted(TIME_BUCKETS)+[None]}},'required':['scenic_id'],'additionalProperties':False}}},
        {'type':'function','function':{'name':'query_advice','description':'查询真实条件建议与来源，visitor_type只匹配明确标签；缺上游数据与无匹配不同。',
         'parameters':{'type':'object','properties':{'scenic_id':{'type':'string'},'visitor_type':{'type':['string','null'],'enum':sorted(VISITORS)+[None]},'condition_type':{'type':['string','null'],'enum':sorted(CONDITIONS)+[None]}},'required':['scenic_id'],'additionalProperties':False}}}
    ]


if __name__=='__main__':
    import json
    tools=GraphTools()
    print(json.dumps({'routes':tools.query_routes('S001'),'family':tools.query_advice('S001',visitor_type='family'),
                      'rain':tools.query_advice('S003',condition_type='weather')},ensure_ascii=False,indent=2))
