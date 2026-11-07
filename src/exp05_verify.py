"""核验全量结构及32例AI辅助诊断参考；不把选样成绩当全量准确率。"""
import re
from collections import Counter
from exp05_advice import CONDITION_TYPES, VISITOR_TYPES, run
from mining_io import ROOT, corpus, read_json, write_json, sha256, check_span


def normalize(s):
    return re.sub(r'\s+','',s).strip('。！？!?，,')


def evaluate(payload,reference):
    predictions=payload['advice'];rows=[]
    for case in reference['cases']:
        e=case['evidence'];expected=case['expected']
        candidates=[p for p in predictions if p['doc_id']==e['doc_id'] and e['start']<=p['condition_span']['start']<e['end']]
        # One sentence can contain two references; attach each prediction to the nearest annotated anchor.
        peers=[c for c in reference['cases'] if c['evidence']['doc_id']==e['doc_id']]
        candidates=[p for p in candidates if min(peers,key=lambda c:abs(c['anchor']-p['condition_span']['start']))['case_id']==case['case_id']]
        tp=0;unmatched=list(candidates)
        for gold in expected:
            match=next((p for p in unmatched if normalize(p['condition_text'])==normalize(gold['condition_text']) and
                        (normalize(p['suggestion_text']).startswith(normalize(gold['suggestion_text'])) if gold['match']=='prefix' else normalize(p['suggestion_text'])==normalize(gold['suggestion_text']))),None)
            if match:tp+=1;unmatched.remove(match)
        rows.append({'case_id':case['case_id'],'split':case['split'],'evidence':e,'expected':expected,
                     'predicted':candidates,'tp':tp,'fp':len(candidates)-tp,'fn':len(expected)-tp,
                     'annotation_note':case['annotation_note']})
    metrics={}
    for split in ['development','document_holdout','all']:
        selected=[r for r in rows if split=='all' or r['split']==split]
        counts={k:sum(r[k] for r in selected) for k in ['tp','fp','fn']};tp,fp,fn=[counts[k] for k in ['tp','fp','fn']]
        metrics[split]=dict(counts,cases=len(selected),positive_relations=sum(len(r['expected']) for r in selected),
                            precision=tp/(tp+fp) if tp+fp else 0,recall=tp/(tp+fn) if tp+fn else 0,
                            f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0,
                            correct_negative_cases=sum(not r['expected'] and not r['predicted'] for r in selected))
    return {'metrics':metrics,'cases':rows}


def validate(payload,docs,entities):
    if payload['schema_version']!='1.0' or payload['corpus_version']!='v1':raise ValueError('版本错误')
    cat={e['entity_id']:e for e in entities['entity_catalog'] if e.get('active',True)}
    seen=set();keys=set();checked=0
    required={'advice_id','scenic_id','doc_id','condition_type','condition_text','visitor_types','suggestion_text','related_entity_ids','evidence','method'}
    for a in payload['advice']:
        if not required<=a.keys() or a['advice_id'] in seen:raise ValueError('缺字段或重复ID')
        seen.add(a['advice_id'])
        if a['condition_type'] not in CONDITION_TYPES or not set(a['visitor_types'])<=VISITOR_TYPES:raise ValueError('分类错误')
        if not a['condition_text'].strip() or not a['suggestion_text'].strip() or not a['evidence']:raise ValueError('空建议')
        doc=docs[a['doc_id']]
        if a['scenic_id']!=doc['scenic_id']:raise ValueError('文档景区错误')
        for e in a['evidence']+[a['condition_span'],a['suggestion_span']]:
            check_span(e,docs);checked+=1
            if e['doc_id']!=a['doc_id']:raise ValueError('证据跨文档')
        for field in ['condition','suggestion']:
            s=a[field+'_span']
            if s['text']!=a[field+'_text'] or not any(e['start']<=s['start'] and s['end']<=e['end'] for e in a['evidence']):raise ValueError('边界或证据覆盖错误')
        for eid in a['related_entity_ids']:
            if eid not in cat or cat[eid]['scenic_id']!=a['scenic_id']:raise ValueError('无效/停用/跨景区实体')
        key=(a['doc_id'],normalize(a['condition_text']),normalize(a['suggestion_text']))
        if key in keys:raise ValueError('重复关系')
        keys.add(key)
    return checked


def main():
    docs=corpus();entities=read_json(ROOT/'data/outputs/entities.json');p=read_json(ROOT/'data/outputs/advice.json')
    ref=read_json(ROOT/'data/resources/exp05_reference.json')
    assert ref['corpus_sha256']==p['corpus_sha256']==sha256(ROOT/'data/processed/corpus.jsonl')
    assert p['entities_sha256']==sha256(ROOT/'data/outputs/entities.json')
    for c in ref['cases']:
        check_span(c['evidence'],docs)
        for e in c['expected']:
            check_span(e['condition_span'],docs);check_span(e['suggestion_span'],docs)
    checked=validate(p,docs,entities)
    assert run()==p,'正式复跑变化'
    raw=run('optimized',review=False)
    review={v:evaluate(o,ref) for v,o in [('baseline',read_json(ROOT/'results/checks/exp05_baseline.json')),('optimized',raw),('reviewed_delivery',p)]}
    write_json(ROOT/'results/checks/exp05_review.json',review)
    quality={'passed':True,'checked_evidence_spans':checked,'advice':len(p['advice']),'statistics':p['statistics'],
             'corpus_sha256':p['corpus_sha256'],'entities_sha256':p['entities_sha256'],'deterministic_rerun':True,
             'reference_provenance':ref['annotation_provenance'],'selection':ref['selection'],
             'review_metrics':{v:r['metrics'] for v,r in review.items()},
             'without_entity_alignment':[a['advice_id'] for a in p['advice'] if not a['related_entity_ids']]}
    write_json(ROOT/'results/checks/exp05_quality.json',quality)
    md=['# 实验5逐例核验','',ref['annotation_provenance'],ref['selection'],'',
        '严格边界：条件和建议归一空白/终止标点后匹配；雨天FAQ按预先标注的最小建议前缀匹配，完整列表另做切片检查。边界错同时计FP和FN。','']
    for v,r in review.items():md += [f'## {v}',str(r['metrics']),'']
    for c in review['optimized']['cases']:
        md += [f"## {c['case_id']} / {c['split']}",f"> {c['evidence']['text']}",'',
               '参考：'+str([(e['condition_text'],e['suggestion_text']) for e in c['expected']]),
               '预测：'+str([(e['condition_text'],e['suggestion_text']) for e in c['predicted']]),
               f"TP={c['tp']} FP={c['fp']} FN={c['fn']}；{c['annotation_note']}",'']
    (ROOT/'results/checks/exp05_review.md').write_text('\n'.join(md),encoding='utf8')
    print(quality['statistics']);print({v:r['metrics'] for v,r in review.items()})


if __name__=='__main__':main()
