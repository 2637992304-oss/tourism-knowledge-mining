import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from mining_io import ROOT,read_json,corpus
from exp02_entities import extract_candidates
from noise_filter import effective_ranges,overlaps_noise
from graph_tools import GraphTools

class RemainingReviewTests(unittest.TestCase):
    def test_adjudicated_group_not_forced_into_a_rock_entity(self):
        c=next(c for c in read_json(ROOT/'data/resources/exp04_reference.json')['cases'] if c['case_id']=='CR_S003_VIS_001_00474')
        self.assertEqual(c['gold_antecedent'],{'text':'三位美貌的姐妹','entity_id':None})

    def test_local_alias_does_not_become_global_synonym(self):
        lex=read_json(ROOT/'data/resources/exp02_lexicon.json');text='往下看原来是硫磺谷'
        local={'doc_id':'S001_VIS_003','scenic_id':'S001','text':text}
        other=dict(local,doc_id='UNSEEN')
        ranges=[{'start':0,'end':len(text)}]
        self.assertTrue(any(c['entry']['canonical_name']=='大涌谷' for c in extract_candidates(local,lex,ranges)))
        self.assertFalse(any(c['entry']['canonical_name']=='大涌谷' for c in extract_candidates(other,lex,ranges)))

    def test_unknown_building_boundary_is_preserved_not_merged(self):
        cat={e['entity_id']:e for e in read_json(ROOT/'data/outputs/entities.json')['entity_catalog']}
        self.assertEqual(cat['S001_POI_043']['canonical_name'],'水中神社')
        self.assertEqual(cat['S001_POI_043']['scope'],'unknown')
        self.assertEqual(read_json(ROOT/'results/checks/exp02_pending_aliases.json'),[])

    def test_recommendation_tail_cannot_leak_into_extraction_scope(self):
        doc=corpus()['S003_OFF_001'];a=doc['text'].index('您可能也喜欢')
        ranges=effective_ranges(doc['doc_id'],[dict(start=0,end=len(doc['text']))])
        self.assertFalse(any(x['start']<=a<x['end'] for x in ranges))

    def test_transport_activities_have_no_fabricated_poi(self):
        row=next(r for r in GraphTools().query_routes('S003')['data'] if r['text_type']=='visitor_diary')
        rides=[s for s in row['steps'] if s['step_kind']=='transport_activity']
        self.assertEqual(len(rides),3)
        self.assertTrue(all(not s['pois'] and s['transport'] and s['display_name'] for s in rides))

    def test_comparison_and_context_roles_survive_actual_query(self):
        rows=GraphTools().query_advice('S001')['data']
        a=next(a for a in rows if '不想另外付费' in a['condition_text'])
        self.assertTrue(any(r['entity_id']=='S001_TRANSPORT_015' and r['role']=='comparison_reference' for r in a['entity_roles']))
        self.assertTrue(all(r['polarity_scope']=='evidence_clause_not_entity_permission' for r in a['entity_roles']))

if __name__=='__main__':unittest.main()
