"""真实数据接口回归及合成协议异常；合成响应不写入正式Agent案例。"""
import copy
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from mining_io import ROOT,corpus,read_json,check_span
from exp05_advice import extract_document,deduplicate
from exp05_verify import validate
from exp06_graph import build
from graph_tools import GraphTools
from llm_client import Config,ChatClient,load_config,ModelError
from exp07_agent import TourismAgent,grounded_plan,run_cases


def constraints(**kwargs):
    c={'scenic_id':'S001','visitor_type':None,'time_bucket':None,'duration_days':None,
       'condition_type':None,'missing_information':[],'conflicts':[],'decision_summary':'查询箱根实际图谱'}
    c.update(kwargs);return c


class ExtractionTests(unittest.TestCase):
    def extract(self,text):
        doc={'doc_id':'TEST','text':text,'scenic_id':'S001'}
        return extract_document(doc,[{'start':0,'end':len(text)}])[0]

    def test_explicit_weather_action_and_exact_unicode_offsets(self):
        text='😀注意。如果下雨,建议改去室内馆。'
        a=self.extract(text)[0]
        self.assertEqual(a['condition_type'],'weather')
        self.assertEqual(a['suggestion_text'],'建议改去室内馆')
        for s in a['evidence']+[a['condition_span'],a['suggestion_span']]:self.assertEqual(text[s['start']:s['end']],s['text'])

    def test_long_condition_not_split_at_first_comma(self):
        a=self.extract('如果想走长线,例如峡谷步道,或者去其他村庄,则应该过夜。')[0]
        self.assertEqual(a['condition_text'],'如果想走长线,例如峡谷步道,或者去其他村庄')

    def test_plain_advice_and_counterfactual_not_conditional(self):
        self.assertEqual(self.extract('建议多带水。若不是下雨,我肯定拍了照片。'),[])

    def test_english_alternatives_not_concatenated(self):
        a=self.extract('If you plan a half loop, turn east. If you plan a full loop, turn west.')
        self.assertEqual([x['suggestion_text'] for x in a],['turn east','turn west'])

    def test_same_condition_multiple_actions_preserved(self):
        a=self.extract('如果带孩子,建议先看展,还可以去花园。')[0]
        self.assertEqual(a['visitor_types'],['family']);self.assertIn('还可以去花园',a['suggestion_text'])

    def test_repeated_and_prefix_duplicates_keep_full_evidence(self):
        items=self.extract('如果下雨,建议去室内馆。如果下雨,建议去室内馆,还可以休息。')
        merged,events=deduplicate(items)
        self.assertEqual(len(merged),1);self.assertEqual(len(events),1);self.assertEqual(len(merged[0]['evidence']),2)
        self.assertIn('还可以休息',merged[0]['suggestion_text'])

    def test_cross_document_dedup_not_applied_by_pipeline(self):
        p=read_json(ROOT/'data/outputs/advice.json')
        self.assertTrue(any(x['doc_id']=='S001_OFF_001' for x in p['advice']))
        self.assertTrue(any(x['doc_id']=='S001_VIS_005' for x in p['advice']))

    def test_corrupted_span_and_cross_scenic_entity_rejected(self):
        docs=corpus();entities=read_json(ROOT/'data/outputs/entities.json');p=read_json(ROOT/'data/outputs/advice.json')
        broken=copy.deepcopy(p);broken['advice'][0]['evidence'][0]['start']+=1
        with self.assertRaises(ValueError):validate(broken,docs,entities)
        broken=copy.deepcopy(p);broken['advice'][0]['related_entity_ids']=['S003_POI_001']
        with self.assertRaises(ValueError):validate(broken,docs,entities)


class QueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.tools=GraphTools()

    def test_morning_filter_and_sequence(self):
        r=self.tools.query_routes('S001','morning');self.assertEqual(r['status'],'ok')
        for route in r['data']:
            self.assertTrue(all(s['time_bucket']=='morning' for s in route['steps']))
            self.assertEqual([s['step_no'] for s in route['steps']],sorted(s['step_no'] for s in route['steps']))

    def test_unknown_scenic_and_extra_arguments_rejected(self):
        self.assertEqual(self.tools.query_routes('S999')['status'],'error')
        self.assertEqual(self.tools.dispatch('query_routes',{'scenic_id':'S001','sql':'DROP'})['status'],'error')
        self.assertEqual(self.tools.dispatch('__class__',{})['status'],'error')
        self.assertEqual(self.tools.dispatch('query_advice',[])['status'],'error')

    def test_general_not_used_for_unspecified(self):
        self.assertEqual(self.tools.query_advice('S001',visitor_type='general')['status'],'no_match')
        self.assertEqual(self.tools.query_advice('S001',visitor_type='elderly')['status'],'no_match')
        self.assertTrue(all('family' in a['visitor_types'] for a in self.tools.query_advice('S001',visitor_type='family')['data']))

    def test_missing_upstream_differs_from_empty_and_no_match(self):
        t=copy.deepcopy(self.tools);t.graph['missing_inputs']=['advice.json']
        self.assertEqual(t.query_advice('S001')['status'],'error')
        t.graph['missing_inputs']=[];t.graph['advice_availability']='available_empty';t.nodes={k:n for k,n in t.nodes.items() if n['node_type']!='ADVICE'}
        self.assertEqual(t.query_advice('S001')['status'],'no_match')

    def test_no_yosemite_route_but_real_crowding_advice(self):
        self.assertEqual(self.tools.query_routes('S002')['status'],'no_match')
        self.assertEqual(self.tools.query_advice('S002',condition_type='crowding')['status'],'ok')

    def test_all_related_entity_types_are_retained(self):
        graph=self.tools.graph
        a=next(n for n in graph['nodes'] if n['node_type']=='ADVICE' and n['attributes']['advice_id'].startswith('A_S001_VIS_005_228'))
        target_types={self.tools.nodes[e['target']]['node_type'] for e in graph['edges'] if e['source']==a['node_id'] and e['relation']=='APPLIES_TO'}
        self.assertEqual(target_types,{'POI','TRANSPORT','TIME'})

    def test_duplicate_advice_id_and_incorrect_evidence_rejected(self):
        routes=read_json(ROOT/'data/outputs/routes.json');reg=read_json(ROOT/'data/processed/scenic_registry.json');ent=read_json(ROOT/'data/outputs/entities.json');advice=read_json(ROOT/'data/outputs/advice.json')
        broken=copy.deepcopy(advice);broken['advice'].append(broken['advice'][0])
        with self.assertRaises(ValueError):build(routes,reg,ent,broken,corpus())
        broken=copy.deepcopy(advice);broken['advice'][0]['evidence'][0]['start']=-1
        with self.assertRaises(ValueError):build(routes,reg,ent,broken,corpus())

    def test_stale_graph_rejected_and_loaded_hash_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'graph.json';data=copy.deepcopy(self.tools.graph)
            data['input_sha256']['entities.json']='0'*64;p.write_text(json.dumps(data),encoding='utf8')
            with self.assertRaises(ValueError):GraphTools(p)
            data['input_sha256']={};p.write_text(json.dumps(data),encoding='utf8');t=GraphTools(p)
            before=t.graph_sha256;p.write_text('{}',encoding='utf8')
            self.assertEqual(t.graph_sha256,before)


class ConfigTests(unittest.TestCase):
    def test_file_load_environment_override_no_secret_repr(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'.env';p.write_text('LLM_API_KEY="secret-for-test"\nLLM_BASE_URL=https://example.test/v1\nLLM_MODEL=test\n',encoding='utf8')
            c=load_config(p,{'LLM_MODEL':'override'})
            self.assertEqual(c.api_key,'secret-for-test');self.assertEqual(c.model,'override');self.assertNotIn('secret-for-test',repr(c))

    def test_models_endpoint_and_missing_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'missing'
            with self.assertRaises(ModelError):load_config(p,{})
            with self.assertRaises(ModelError):load_config(p,{'LLM_API_KEY':'x','LLM_BASE_URL':'https://example.test/models','LLM_MODEL':'x'})

    def test_http_response_body_never_exposed(self):
        client=ChatClient(Config('SECRET','https://example.test/v1','test'))
        error=urllib.error.HTTPError('https://example.test/v1',401,'body SECRET',{},io.BytesIO(b'SECRET'))
        with patch('urllib.request.urlopen',side_effect=error):
            with self.assertRaises(ModelError) as caught:client.complete([])
        self.assertNotIn('SECRET',str(caught.exception))

    def test_private_reasoning_is_discarded(self):
        class Response(io.BytesIO):
            def __enter__(self):return self
            def __exit__(self,*args):self.close()
        response=Response(json.dumps({'choices':[{'message':{'role':'assistant','content':'ok','reasoning_content':'private'},'finish_reason':'stop'}]}).encode())
        with patch('urllib.request.urlopen',return_value=response):r=ChatClient(Config('x','https://example.test/v1','test')).complete([])
        self.assertNotIn('reasoning_content',r)

    def test_transient_network_error_retried_once(self):
        class Response(io.BytesIO):
            def __enter__(self):return self
            def __exit__(self,*args):self.close()
        response=Response(json.dumps({'choices':[{'message':{'role':'assistant','content':'ok'}}]}).encode())
        client=ChatClient(Config('x','https://example.test/v1','test'))
        with patch('urllib.request.urlopen',side_effect=[urllib.error.URLError('temporary'),response]),patch('time.sleep'):
            self.assertEqual(client.complete([])['content'],'ok')
        self.assertEqual(client.requests,2)

    def test_invalid_provider_envelope_retried_once(self):
        class Response(io.BytesIO):
            def __enter__(self):return self
            def __exit__(self,*args):self.close()
        invalid=Response(b'{"choices":[]}');valid=Response(b'{"choices":[{"message":{"role":"assistant","content":"ok"}}]}')
        client=ChatClient(Config('x','https://example.test/v1','test'))
        with patch('urllib.request.urlopen',side_effect=[invalid,valid]),patch('time.sleep'):
            self.assertEqual(client.complete([])['content'],'ok')
        self.assertEqual(client.requests,2)


class ScriptedClient:
    execution_mode='synthetic_protocol_test';model='scripted-test'
    def __init__(self,items):self.items=iter(items)
    def complete(self,*args,**kwargs):
        item=next(self.items)
        if isinstance(item,Exception):raise item
        return item


def message(obj):return {'role':'assistant','content':json.dumps(obj,ensure_ascii=False)}
def call(name='query_routes',args=None):return {'role':'assistant','content':None,'tool_calls':[{'id':'test_call','type':'function','function':{'name':name,'arguments':json.dumps(args if args is not None else {'scenic_id':'S001'})}}]}


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tools=GraphTools();r=self.tools.query_routes('S001')['data'][0];s=r['steps'][0]
        self.final={'status':'success','decision_summary':'返回有来源的路线片段','final_plan':{'route_id':r['route_id'],
                    'steps':[{'step_no':s['step_no'],'poi_name':s['pois'][0]['name'],'time_text':s['time_text'],'source_refs':s['source_refs']}],
                    'advice':[],'supplementary_advice':[],'limitations':[],'source_refs':s['source_refs']}}

    def test_tool_result_used_in_final(self):
        r=TourismAgent(self.tools,ScriptedClient([message(constraints()),call(),message(self.final)])).run('测试箱根')
        self.assertEqual(r['status'],'success');self.assertTrue(r['tool_calls']);self.assertFalse(r['real_llm']);self.assertTrue(r['final_plan']['steps'][0]['evidence'])

    def test_hallucinated_step_rejected_then_retry(self):
        bad=copy.deepcopy(self.final);bad['final_plan']['steps'][0]['poi_name']='不存在的景点'
        r=TourismAgent(self.tools,ScriptedClient([message(constraints()),call(),message(bad),message(self.final)])).run('测试箱根')
        self.assertEqual(r['status'],'success');self.assertIn('final_validation: unsupported_step_fact',r['check_notes'])

    def test_no_tool_cannot_claim_grounded_answer(self):
        r=TourismAgent(self.tools,ScriptedClient([message(constraints()),message(self.final)]),1).run('测试箱根')
        self.assertEqual(r['status'],'error');self.assertIn('final_validation: tool_query_required',r['check_notes'])

    def test_unknown_and_conflict_require_clarification(self):
        for c in [constraints(scenic_id=None),constraints(conflicts=['总时长同时一天和两天'])]:
            r=TourismAgent(self.tools,ScriptedClient([message(c)])).run('测试请求')
            self.assertEqual(r['status'],'partial');self.assertEqual(r['tool_calls'],[])

    def test_optional_missing_details_do_not_block_known_scenic(self):
        r=TourismAgent(self.tools,ScriptedClient([message(constraints(missing_information=['未给日期'])),call(),message(self.final)])).run('测试箱根')
        self.assertEqual(r['status'],'success');self.assertTrue(r['tool_calls'])

    def test_model_network_failure_preserved(self):
        r=TourismAgent(self.tools,ScriptedClient([ModelError('llm_network_error_or_timeout')])).run('测试请求')
        self.assertEqual(r['status'],'error');self.assertIsNone(r['final_plan'])

    def test_wrong_scenic_and_nonobject_arguments_do_not_crash(self):
        r=TourismAgent(self.tools,ScriptedClient([message(constraints()),call(args={'scenic_id':'S003'}),call(args=[])]),2).run('测试请求')
        self.assertEqual(r['status'],'error');self.assertTrue(all(c['result']['status']=='error' for c in r['tool_calls']))

    def test_duration_and_suitability_not_guaranteed(self):
        calls=[{'result':self.tools.query_routes('S001'),'tool':'query_routes'}]
        obj=grounded_plan(copy.deepcopy(self.final),calls,constraints(visitor_type='elderly',duration_days=1))
        self.assertEqual(obj['status'],'partial');self.assertGreaterEqual(len(obj['final_plan']['limitations']),2)

    def test_retry_preserves_failed_attempt_and_other_cases(self):
        spec=read_json(ROOT/'data/resources/exp07_scenarios.json')
        old=[{'case_id':s['case_id'],'user_request':s['user_request'],'status':'error' if i==0 else 'partial',
              'check_notes':['original failure'] if i==0 else ['unchanged'],'tool_calls':[]} for i,s in enumerate(spec['cases'])]
        history={'execution_mode':'live_api','graph_sha256':self.tools.graph_sha256,'api_requests':16,'run_at':'test','cases':old}
        fixed={**old[0],'status':'partial','check_notes':['synthetic retry'],'real_llm':False}
        fake=type('Client',(),{'model':'synthetic-test','requests':3})()
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'cases.json';p.write_text(json.dumps(history),encoding='utf8')
            with patch('exp07_agent.load_config',return_value=Config('x','https://example.test/v1','test')),patch('exp07_agent.ChatClient',return_value=fake),patch.object(TourismAgent,'run',return_value=fixed) as run:
                result=run_cases(output=p,retry_errors=True)
            self.assertEqual(run.call_count,1);self.assertEqual(result['api_requests'],19)
            self.assertEqual(result['cases'][0]['previous_attempts'][0],old[0]);self.assertEqual(result['cases'][1:],old[1:])


if __name__=='__main__':unittest.main()
