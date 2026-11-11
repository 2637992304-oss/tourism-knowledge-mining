"""Verify closure evidence for R05/R06/R09/R10/R11/R12."""
import zipfile
from PIL import Image
from mining_io import ROOT,read_json,write_json,sha256,corpus,check_span
from noise_filter import overlaps_noise

def main():
    docs=corpus();entities=read_json(ROOT/'data/outputs/entities.json')
    cat={e['entity_id']:e for e in entities['entity_catalog']}
    ref=read_json(ROOT/'data/resources/exp04_reference.json')
    case=next(c for c in ref['cases'] if c['case_id']=='CR_S003_VIS_001_00474')
    assert case['gold_status']=='resolved' and case['gold_antecedent']['text']=='三位美貌的姐妹'
    check_span(case['gold_evidence'],docs)
    decisions=read_json(ROOT/'data/resources/exp02_alias_adjudications.json')['decisions']
    assert len(decisions)==5 and read_json(ROOT/'results/checks/exp02_pending_aliases.json')==[]
    assert cat['S001_POI_043']['canonical_name']=='水中神社'
    assert cat['S001_POI_043']['entity_id'] not in {'S001_POI_014','S001_POI_015'}
    for decision in decisions:
        assert all(any(m['entity_id']==decision['entity_id'] and m['span']['doc_id']==e['doc_id'] and m['span']['start']==e['start'] and m['span']['end']==e['end'] for m in entities['mentions']) for e in decision['evidence'])
    noise=read_json(ROOT/'data/resources/noise_exclusions.json')
    assert set(noise['documents'])==set(docs)
    assert noise['corpus_sha256']==sha256(ROOT/'data/processed/corpus.jsonl')
    for did,cuts in noise['documents'].items():
        for cut in cuts:assert docs[did]['text'][cut['start']:cut['end']]==cut['text']
    references=[m['span'] for m in entities['mentions']]
    routes=read_json(ROOT/'data/outputs/routes.json')['routes']
    references += [e for r in routes for s in r['steps'] for e in s['evidence']]
    advice=read_json(ROOT/'data/outputs/advice.json')['advice']
    references += [e for a in advice for e in a['evidence']]
    assert not [e for e in references if overlaps_noise(e['doc_id'],e['start'],e['end'])], '下游证据仍穿过已排除噪声'
    rides=[s for r in routes for s in r['steps'] if s.get('step_kind')=='transport_activity']
    assert len(rides)==3 and all(s['poi_entity_id'] is None for s in rides)
    graph=read_json(ROOT/'data/outputs/graph.json')
    for r in routes:
        for s in r['steps']:
            if s.get('step_kind')=='transport_activity':
                nid=f"N_STEP_{r['route_id']}_{s['step_no']:03d}"
                assert not any(e['source']==nid and e['relation']=='VISITS' for e in graph['edges'])
                assert any(e['source']==nid and e['relation']=='USES_TRANSPORT' for e in graph['edges'])
    roles=[r for a in advice for r in a['entity_roles']]
    assert any(r['role']=='comparison_reference' and r['entity_id']=='S001_TRANSPORT_015' for r in roles)
    assert any(r['role']=='supporting_context' and r['entity_id']=='S002_POI_002' for r in roles)
    for a in advice:
        assert {r['entity_id'] for r in a['entity_roles']}==set(a['related_entity_ids'])
    panels=read_json(ROOT/'results/checks/exp06_report_panels.json')
    assert panels['graph_sha256']==sha256(ROOT/'data/outputs/graph.json')
    assert sum(len(p.get('step_numbers',[])) for p in panels['panels'])==sum(len(r['steps']) for r in routes)
    assert sum(len(p.get('advice_ids',[])) for p in panels['panels'])==len(advice)
    for p in panels['panels']:
        with Image.open(ROOT/p['file']) as im:
            assert list(im.size)==p['size'] and im.width==1800;im.verify()
        assert sha256(ROOT/p['file'])==p['sha256'] and not p['labels_truncated']
    # Prove ID preservation and explicitly authorize only versioned upstream output changes.
    with zipfile.ZipFile(ROOT/'results/checks/history/pre_remaining_review_fix.zip') as z:
        import json
        old=json.loads(z.read('data/outputs/entities.json'))
    assert all(e['entity_id'] in cat and cat[e['entity_id']]['canonical_name']==e['canonical_name'] for e in old['entity_catalog'])
    approved={}
    baseline=read_json(ROOT/'results/checks/exp05_07_protected.json')['sha256']
    for name,digest in baseline.items():
        current=sha256(ROOT/name)
        if current!=digest:
            assert name in {'data/outputs/entities.json','data/outputs/coreference.json','data/outputs/coreference_resolved_documents.json'}
            approved[name]=dict(previous_sha256=digest,sha256=current,reason='R05/R06/R09已授权的版本化修订；冻结正文、景区登记、任务书、模板均未改')
    write_json(ROOT/'results/checks/approved_upstream_revisions.json',dict(revisions=approved,old_entity_ids_preserved=True,archive='results/checks/history/pre_remaining_review_fix.zip'))
    write_json(ROOT/'results/checks/review_round2_closure.json',dict(passed=True,reviewer='AI辅助复核，不代签组员',
        issues={k:'closed_with_evidence' for k in ['R05','R06','R09','R10','R11','R12']},
        graph_sha256=sha256(ROOT/'data/outputs/graph.json'),
        source_referent_policy='水中神社保留原文ID，不断言建筑身份，不再作为待确认别名',
        frozen_corpus_sha256=noise['corpus_sha256'],documents_audited=len(docs),
        evidence_spans_checked=len(references),excluded_noise_spans=sum(map(len,noise['documents'].values())),
        transport_steps=len(rides),roles=len(roles),report_panels=len(panels['panels']),old_entity_ids_preserved=True))
    print('R05/R06/R09/R10/R11/R12关闭证据通过；冻结语料及旧实体ID保持。')

if __name__=='__main__':main()
