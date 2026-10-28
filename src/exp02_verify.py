"""检查实验2接口、字符位置、稳定ID，并对24例原文参考标签作严格匹配评价。"""
from collections import Counter
import re
from exp02_entities import ROOT,TYPES,load_inputs,read_json,write_json,build_output


def key(m, catalog):
    span=m['span']
    return (span['start'],span['end'],m['entity_type'],catalog[m['entity_id']]['canonical_name'])


def scores(tp,fp,fn):
    p=tp/(tp+fp) if tp+fp else 0
    r=tp/(tp+fn) if tp+fn else 0
    return dict(tp=tp,fp=fp,fn=fn,precision=p,recall=r,f1=2*p*r/(p+r) if p+r else 0)


def evaluate(output,reference,rows):
    catalog={e['entity_id']:e for e in output['entity_catalog']}
    total=Counter(); by_type={t:Counter() for t in TYPES}; cases=[]
    for case in reference['cases']:
        gold={(e['start'],e['end'],e['entity_type'],e['canonical_name']) for e in case['expected']}
        pred={key(m,catalog) for m in output['mentions'] if m['span']['doc_id']==case['doc_id']
              and case['start']<=m['span']['start'] and m['span']['end']<=case['end']}
        tp,fp,fn=gold&pred,pred-gold,gold-pred
        total.update(tp=len(tp),fp=len(fp),fn=len(fn))
        for t in TYPES:
            by_type[t].update(tp=sum(x[2]==t for x in tp),fp=sum(x[2]==t for x in fp),fn=sum(x[2]==t for x in fn))
        text=next(x['text'] for x in rows if x['doc_id']==case['doc_id'])
        def describe(items):
            return [dict(start=x[0],end=x[1],text=text[x[0]:x[1]],entity_type=x[2],canonical_name=x[3]) for x in sorted(items)]
        cases.append(dict(case_id=case['case_id'],doc_id=case['doc_id'],text=case['text'],start=case['start'],end=case['end'],
                          judgment=case['judgment'],expected=case['expected'],predicted=describe(pred),
                          false_positive=describe(fp),false_negative=describe(fn),**scores(len(tp),len(fp),len(fn))))
    return dict(variant=output['variant'],matching='原文起止位置、类型、标准名称四项完全一致；微平均，非全语料准确率',
                review_method=reference['review_method'],cases_count=len(cases),reference_mentions=sum(len(x['expected']) for x in reference['cases']),
                metrics=scores(**{k:total[k] for k in ['tp','fp','fn']}),
                per_type={t:scores(**{k:c[k] for k in ['tp','fp','fn']}) for t,c in by_type.items()},cases=cases)


def main():
    rows,lex,scopes,h=load_inputs(); docs={r['doc_id']:r for r in rows}
    output=read_json(ROOT/'data/outputs/entities.json')
    catalog={e['entity_id']:e for e in output['entity_catalog']}
    ms=output['mentions']; seen=set(); previous_end={}; counts=Counter(m['entity_id'] for m in ms)
    assert output['schema_version']=='1.0' and output['corpus_version']=='v1' and output['corpus_sha256']==h
    assert len(catalog)==len(output['entity_catalog'])
    assert len({m['mention_id'] for m in ms})==len(ms)
    for e in catalog.values():
        assert all(k in e for k in ['entity_id','scenic_id','entity_type','canonical_name','aliases'])
        assert e['entity_type'] in TYPES
        assert re.fullmatch(r'S00[123]_(POI|TIME|TRANSPORT)_\d{3,}',e['entity_id'])
        assert e['mention_count']==counts[e['entity_id']]
    for m in ms:
        s=m['span']; row=docs[s['doc_id']]; e=catalog[m['entity_id']]
        assert 0<=s['start']<s['end']<=len(row['text'])
        assert row['text'][s['start']:s['end']]==s['text']
        assert m['entity_type']==e['entity_type'] and row['scenic_id']==e['scenic_id']
        assert any(i['start']<=s['start'] and s['end']<=i['end'] for i in scopes[s['doc_id']])
        k=(s['doc_id'],s['start'],s['end'],m['entity_id']); assert k not in seen; seen.add(k)
        assert previous_end.get(s['doc_id'],-1)<=s['start']; previous_end[s['doc_id']]=s['end']
        assert m['method'] in ['dictionary','rule']
        assert s['text'] not in lex['stopwords'].get(m['entity_type'],[])
        if e['canonical_name']=='箱根':
            assert not re.match(r'\s*(?:\d+日)?周游[券劵]',row['text'][s['end']:s['end']+16]),'票券名被误作地点'
    # Re-run from current published IDs, and reorder input documents to detect accidental renumbering.
    regenerated=build_output(rows,lex,scopes,h,'optimized',output)
    assert regenerated==output,'复跑结果不稳定'
    reordered=build_output(list(reversed(rows)),lex,scopes,h,'optimized',output)
    ids=lambda obj:{(m['span']['doc_id'],m['span']['start'],m['span']['end'],m['entity_id']):m['mention_id'] for m in obj['mentions']}
    assert ids(reordered)==ids(output),'顺序变化导致ID变化'
    assert {m['span']['doc_id'] for m in ms}==set(docs)
    # YZH反馈的车站别名及独立野餐区，按完整地点边界核对，防止退回短词或误合并。
    confirmations=read_json(ROOT/'data/resources/exp02_alignment_confirmations.json')
    assert confirmations['corpus_sha256']==h
    assert confirmations['resource_version']==lex['resource_version']==output['resource_version']
    for mapping in confirmations['mappings']:
        e=catalog[mapping['entity_id']]
        assert e['active'] and e['entity_type']=='POI'
        assert e['canonical_name']==mapping['canonical_name']
        assert mapping['surface'] in [e['canonical_name']]+e['aliases']
        for field in ['evidence','context']:
            s=mapping[field]
            assert docs[s['doc_id']]['text'][s['start']:s['end']]==s['text']
        matches=[m for m in ms if m['span']==mapping['evidence']]
        assert len(matches)==1 and matches[0]['entity_id']==mapping['entity_id']
        for other_id in mapping.get('distinct_from',[]):
            assert other_id!=e['entity_id'] and catalog[other_id]['active']
            assert any(m['entity_id']==other_id for m in ms)
    # Each reference label is checked against frozen original text, including empty negative cases.
    reference=read_json(ROOT/'data/resources/exp02_review_reference.json')
    assert reference['corpus_sha256']==h
    for c in reference['cases']:
        text=docs[c['doc_id']]['text']; assert text[c['start']:c['end']]==c['text']
        for e in c['expected']:
            assert text[e['start']:e['end']]==e['text']
            assert c['start']<=e['start']<e['end']<=c['end']
    review={v:evaluate(read_json(ROOT/p),reference,rows) for v,p in [
        ('baseline','results/checks/exp02_baseline_entities.json'),('optimized','data/outputs/entities.json')]}
    write_json(ROOT/'results/checks/exp02_review.json',review)
    quality=dict(status='passed',documents=len(rows),mentions=len(ms),checks={
        'schema_and_corpus_hash':True,'unique_entity_and_mention_ids':True,'exact_source_spans':len(ms),
        'valid_entity_references':len(ms),'same_scenic_mapping':True,'within_declared_scope':True,
        'no_duplicate_or_overlapping_mentions':True,'no_exact_stopwords':True,
        'deterministic_rerun':True,'ids_stable_after_document_reordering':True,'review_reference_source_spans':True},
        corpus_sha256=h,review_metrics={v:r['metrics'] for v,r in review.items()})
    quality['checks']['confirmed_poi_mappings']=len(confirmations['mappings'])
    write_json(ROOT/'results/checks/exp02_quality.json',quality)
    pending=[]
    for item in lex['ambiguous_names']:
        hits=[]
        for row in rows:
            for m in re.finditer(re.escape(item['surface']),row['text'],re.I):
                if any(i['start']<=m.start() and m.end()<=i['end'] for i in scopes[row['doc_id']]):
                    hits.append(dict(doc_id=row['doc_id'],start=m.start(),end=m.end(),text=m.group(),
                                     context=row['text'][max(0,m.start()-30):m.end()+30]))
        pending.append(dict(item,evidence=hits))
    write_json(ROOT/'results/checks/exp02_pending_aliases.json',pending)
    md=['# 实验2 逐例核验清单','',reference['review_method'],'',reference['selection'],
        '\n指标仅用于同一目的抽样开发集的优化诊断，不能当作独立测试或全语料准确率。\n']
    for v,r in review.items():
        md += [f'## {v}',f"TP={r['metrics']['tp']}，FP={r['metrics']['fp']}，FN={r['metrics']['fn']}；P={r['metrics']['precision']:.2%}，R={r['metrics']['recall']:.2%}，F1={r['metrics']['f1']:.2%}。",'']
    for c in review['optimized']['cases']:
        b=next(x for x in review['baseline']['cases'] if x['case_id']==c['case_id'])
        fmt=lambda es:'；'.join(f"{e['text']}→{e['entity_type']}/{e['canonical_name']} [{e['start']},{e['end']})" for e in es) or '无'
        md += [f"## {c['case_id']} {c['doc_id']} [{c['start']},{c['end']})",f"> {c['text']}",'',
               f"- 初版预测：{fmt(b['predicted'])}",f"- 优化预测：{fmt(c['predicted'])}",
               f"- 核验参考：{fmt(c['expected'])}",f"- 判断：{c['judgment']}",
               f"- 误识别：{fmt(c['false_positive'])}",f"- 漏识别或边界偏差：{fmt(c['false_negative'])}",'']
    (ROOT/'results/checks/exp02_review.md').write_text('\n'.join(md),encoding='utf-8')
    print('结构和位置检查通过；',len(ms),'处提及；24例逐例核验：')
    for v,r in review.items(): print(v,r['metrics'])
    for c in review['optimized']['cases']:
        if c['fp'] or c['fn']: print(c['case_id'],'FP',[(x['text'],x['canonical_name']) for x in c['false_positive']], 'FN',[(x['text'],x['canonical_name']) for x in c['false_negative']])


if __name__=='__main__': main()
