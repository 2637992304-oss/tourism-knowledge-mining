"""Regression checks for source attribution, route meaning and review corrections."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from mining_io import ROOT,corpus,read_json
from graph_tools import GraphTools
from exp03_routes import official_route
from exp05_advice import extract_document
from exp07_agent import clarification_questions
from exp07_verify import verify
from exp06_graph import build

class ReviewFixTests(unittest.TestCase):
    def test_actual_source_page_follows_evidence_not_primary_url(self):
        tools=GraphTools()
        rain=tools.query_advice('S003',condition_type='weather')['data'][0]
        self.assertTrue(all('visitnsw.com/cn/articles/' in s['url'] for s in rain['sources']))
        doc=corpus()['S003_OFF_001'];pages=read_json(ROOT/'data/resources/source_page_spans.json')['documents'][doc['doc_id']]
        refs=[{'doc_id':doc['doc_id'],'start':pages[0]['start'],'end':pages[-1]['end']}]
        self.assertEqual(len(tools.sources([doc['doc_id']],refs)),2)
        first=tools.sources([doc['doc_id']],[dict(doc_id=doc['doc_id'],start=0,end=10)])
        self.assertIn('nationalparks.nsw.gov.au',first[0]['url'])

    def test_transport_target_is_not_current_location(self):
        route=official_route(corpus()['S001_OFF_001']);step=route['steps'][4]
        self.assertEqual(step['poi_name'],'早云山站')
        self.assertEqual(step['destination_poi_name'],'大涌谷')
        self.assertEqual(step['time_text'],'11:20')

    def test_candidate_order_survives_graph_and_tool(self):
        routes=read_json(ROOT/'data/outputs/routes.json')
        blue=next(r for r in routes['routes'] if r['doc_id']=='S003_OFF_001')
        self.assertEqual(blue['sequence_semantics'],'source_order_only')
        data=GraphTools().query_routes('S003')['data']
        row=next(r for r in data if r['route_id']==blue['route_id'])
        self.assertEqual(row['sequence_semantics'],'source_order_only')
        self.assertTrue(all(s['step_kind']=='candidate_activity' for s in row['steps']))
        graph=read_json(ROOT/'data/outputs/graph.json')
        edges=[e for e in graph['edges'] if e['relation']=='NEXT_STEP' and e['attributes']['route_id']==blue['route_id']]
        self.assertTrue(all(e['attributes']['sequence_semantics']=='source_order_only' for e in edges))

    def test_concessive_advice_and_negative_observation(self):
        text='虽然刚出发稍有些冷,但建议还是不要增加衣服,因为很快就会感到热了。'
        doc=dict(doc_id='TEST',scenic_id='S001',text=text)
        rows,_=extract_document(doc,[dict(start=0,end=len(text))])
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['condition_text'],'虽然刚出发稍有些冷')
        self.assertEqual(rows[0]['suggestion_text'],'但建议还是不要增加衣服,因为很快就会感到热了')
        for key in ['condition_span','suggestion_span']:
            ref=rows[0][key];self.assertEqual(text[ref['start']:ref['end']],ref['text'])
        text='虽然刚出发有些冷,但我们继续走。'
        doc['text']=text
        self.assertEqual(extract_document(doc,[dict(start=0,end=len(text))])[0],[])

    def test_unknown_destination_gets_coverage_and_question(self):
        c={'scenic_id':None,'conflicts':[],'missing_information':['黄山']}
        answer=clarification_questions(c,'给我黄山的路线')[0]
        self.assertIn('黄山',answer);self.assertIn('尚未',answer)
        self.assertIn('箱根',answer);self.assertIn('？',answer)
        c['missing_information']=['黄山未在登记景区中，无法确定scenic_id']
        self.assertIn('你指定的“黄山”尚未被知识库覆盖',clarification_questions(c,'给我黄山的路线')[0])
        c['missing_information']=['未登记景区：黄山']
        self.assertTrue(clarification_questions(c,'给我黄山的路线')[0].startswith('你请求的目的地尚未'))

    def test_revalidated_history_cannot_pass_as_new_live_run(self):
        data=read_json(ROOT/'data/outputs/agent_revalidated_cases.json')
        with self.assertRaises(ValueError):verify(data,GraphTools())
        quality=verify(data,GraphTools(),allow_offline=True)
        self.assertFalse(quality['live_validation_passed'])
        plan=next(c for c in data['cases'] if c['case_id']=='AG_003')['final_plan']
        self.assertEqual(plan['sequence_semantics'],'source_order_only')

if __name__=='__main__':unittest.main()
