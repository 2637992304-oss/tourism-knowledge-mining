"""实验5：离线条件建议抽取；参考标签只由核验入口读取，不参与预测。"""
import argparse
import hashlib
import re
from collections import Counter
from difflib import SequenceMatcher
from mining_io import ROOT, corpus, read_json, write_json, sha256, span
from source_provenance import evidence_sources

CONDITION_TYPES = {'weather', 'visitor_type', 'time', 'crowding', 'other'}
VISITOR_TYPES = {'elderly', 'family', 'couple', 'general', 'other'}
TRIGGER = re.compile(r'如果(?!说)|假如|若是|若(?=有|要|想|带|遇)|对于带|条件允许的话')
ACTION = re.compile(r'则应该|则需|则只能|则可以|建议|推荐|请前往|一定要|一定不要|还可以|可享|可以|另一个最佳')


def classify(condition):
    visitors = []
    for pat, value in [(r'儿童|孩子|小孩|亲子|家庭','family'),(r'老人|老年|长者','elderly'),(r'情侣|恋人|夫妻','couple')]:
        if re.search(pat,condition): visitors.append(value)
    if visitors:return 'visitor_type', visitors
    if re.search(r'天气|下雨|雨天|下雪|冰雪|高温|寒冷|有些冷|大风',condition):return 'weather',[]
    if re.search(r'人挤人|人多|拥挤|排队|旺季|预约',condition):return 'crowding',[]
    if re.search(r'时间|早晨|晚上|周中|周末|冬季|夏季|季节',condition):return 'time',[]
    return 'other',[]


def units(text,start,end):
    for m in re.finditer(r'[^。！？!?\n]+(?:[。！？!?]+|$)',text[start:end],re.M):
        a,b=start+m.start(),start+m.end()
        while a<b and text[a].isspace():a+=1
        while b>a and text[b-1] in '。！？!? \t\r':b-=1
        if a<b:yield a,b


def extract_document(doc,ranges,variant='optimized'):
    text,did=doc['text'],doc['doc_id'];found=[];rejected=[]
    def add(ca,cb,sa,sb,ea,eb,rule):
        while cb>ca and text[cb-1] in ',， \t':cb-=1
        while sa<sb and text[sa] in ',， \t':sa+=1
        while sb>sa and text[sb-1] in '。！？!? \t\r\n':sb-=1
        if not ca<cb or not sa<sb:return
        condition,suggestion=text[ca:cb],text[sa:sb]
        if variant=='optimized' and (re.search(r'五星|好评|喜欢本文|如果说|若不是|如果不是因为',condition) or re.search(r'从车窗看到|在一天内高效地游览|那么估计|会增加.*期待',suggestion)):
            rejected.append({'evidence':span(did,text,ea,eb),'reason':'描述/总结/元话语，没有具体条件动作'});return
        ct,visitors=classify(condition)
        found.append({'condition_type':ct,'condition_text':condition,'visitor_types':visitors,
                      'suggestion_text':suggestion,'condition_span':span(did,text,ca,cb),
                      'suggestion_span':span(did,text,sa,sb),'evidence':[span(did,text,ea,eb)],'rule':rule})
    for interval in ranges:
        lo,hi=interval['start'],interval['end']
        for a,b in units(text,lo,hi):
            unit=text[a:b]
            if variant=='optimized':
                # Concessive context is a real condition even without 如果.
                implicit=re.search(r'虽然([^。！？]+?)[,，](但(?:是)?建议[^。！？]+)',unit)
                if implicit:
                    add(a+implicit.start(),a+implicit.start(2)-1,
                        a+implicit.start(2),a+implicit.end(2),
                        a+implicit.start(),a+implicit.end(2),'concessive_advice')
            if re.search(r'\bIf\s',unit):
                for m in re.finditer(r'\bIf\s+([^,.!?\n]+),\s*([^.!?\n]+)',unit):
                    add(a+m.start(),a+m.start(2),a+m.start(2),a+m.end(2),a+m.start(),a+m.end(),'english_if')
                continue
            triggers=list(TRIGGER.finditer(unit))
            for i,t in enumerate(triggers):
                ca=a+t.start();end=a+triggers[i+1].start() if i+1<len(triggers) else b
                body=text[ca:end];action=ACTION.search(body,t.end()-t.start())
                if variant=='baseline':
                    comma=re.search('[,，]',body)
                    if comma:add(ca,ca+comma.start(),ca+comma.end(),end,ca,end,'first_comma_baseline')
                elif action:add(ca,ca+action.start(),ca+action.start(),end,ca,end,'conditional_action')
                else:rejected.append({'evidence':span(did,text,ca,end),'reason':'未找到支持的建议动作，保留漏抽可能'})
        if variant=='optimized':
            for m in re.finditer(r'(?m)^([^\n]*(?:适合儿童游玩吗|下雨天还值得去[^\n]*吗)\?)\n',text[lo:hi]):
                ca=lo+m.start();cb=lo+m.end(1);sa=lo+m.end()
                heading=re.search(r'(?m)^[^\n]*[?？]\s*$|^您可能也喜欢',text[sa:hi])
                sb=sa+heading.start() if heading else hi
                add(ca,cb,sa,sb,ca,sb,'faq_condition_block')
    return found,rejected


def deduplicate(items):
    """同文档精确/包含重复合并；跨来源事实不互相覆盖。"""
    output=[];events=[];norm=lambda s:re.sub(r'[\s,，。;；:：]','',s).casefold()
    for item in sorted(items,key=lambda x:(x['evidence'][0]['start'],-len(x['suggestion_text']))):
        match=next((o for o in output if norm(o['condition_text'])==norm(item['condition_text']) and (norm(o['suggestion_text']) in norm(item['suggestion_text']) or norm(item['suggestion_text']) in norm(o['suggestion_text']))),None)
        if match:
            if len(item['suggestion_text'])>len(match['suggestion_text']):
                match['suggestion_text']=item['suggestion_text'];match['suggestion_span']=item['suggestion_span']
            match['evidence']=sorted({(s['start'],s['end']):s for s in match['evidence']+item['evidence']}.values(),key=lambda s:s['start'])
            events.append({'kept_condition':match['condition_span'],'merged':item['condition_span']})
        else:output.append(item)
    return output,events


def related(item,doc,entities):
    cat={e['entity_id']:e for e in entities['entity_catalog'] if e.get('active',True) and e['scenic_id']==doc['scenic_id']}
    ids=set();notes=[]
    for m in entities['mentions']:
        s=m['span']
        if m['entity_id'] in cat and s['doc_id']==doc['doc_id'] and any(e['start']<=s['start'] and s['end']<=e['end'] for e in item['evidence']):ids.add(m['entity_id'])
    if '馆区' in item['suggestion_text']:
        start=item['condition_span']['start'];context=doc['text'][max(0,start-800):start]
        museums=[e for e in cat.values() if '美术馆' in e['canonical_name'] and e['canonical_name'] in context]
        if len(museums)==1:
            e=museums[0];ids.add(e['entity_id']);pos=doc['text'].rfind(e['canonical_name'],max(0,start-800),start)
            item['evidence'].append(span(doc['doc_id'],doc['text'],pos,pos+len(e['canonical_name'])))
            notes.append('馆区由前800字符唯一具名美术馆回指；保留名称证据')
    return sorted(ids),notes


def run(variant='optimized',review=True):
    docs=corpus();entities=read_json(ROOT/'data/outputs/entities.json');scope=read_json(ROOT/'data/resources/exp02_scope.json')
    ranges={d['doc_id']:d['ranges'] for d in scope['documents']}
    if {d['corpus_version'] for d in docs.values()}!={'v1'} or entities['corpus_version']!='v1':raise ValueError('输入版本不是冻结v1')
    output=[];audit=[];duplicates=[]
    for did,doc in docs.items():
        selected=[s for s in ranges[did] if not (did=='S003_VIS_004' and s['start']==6195)]
        candidates,rejected=extract_document(doc,selected,variant);candidates,merged=deduplicate(candidates)
        audit.append({'doc_id':did,'ranges':selected,'candidates':len(candidates),'rejected':rejected,
                      'scope_note':'排除[6195,6418)园外酒评' if did=='S003_VIS_004' else '复用实验2相关区间；不修改原文'})
        duplicates.extend(merged)
        for item in candidates:
            if variant=='optimized' and review:
                for correction in read_json(ROOT/'data/resources/exp05_corrections.json')['corrections']:
                    if did==correction['doc_id'] and item['condition_text']==correction['condition_text']:
                        if item['suggestion_text']!=correction['old_suggestion']:raise ValueError('审校修正与规则预测不符')
                        sa=item['suggestion_span']['start'];fixed=correction['suggestion_text']
                        if doc['text'][sa:sa+len(fixed)]!=fixed:raise ValueError('审校修正无法切回原文')
                        item['raw_suggestion_text']=item['suggestion_text']
                        item['suggestion_text']=fixed;item['suggestion_span']=span(did,doc['text'],sa,sa+len(fixed))
                        item['review_correction']=correction['reason']
            ids,notes=related(item,doc,entities)
            source_pages=evidence_sources(docs,[did],item['evidence'])
            key=f"{item['condition_span']['start']}:{item['condition_text']}:{item['suggestion_text']}"
            suffix=int(hashlib.sha256(key.encode()).hexdigest()[:12],16)
            item.update(advice_id=f'A_{did}_{suffix:015d}',scenic_id=doc['scenic_id'],doc_id=did,
                        related_entity_ids=ids,alignment_notes=notes,method='rule:'+item.pop('rule')+('+ai_review' if 'review_correction' in item else ''),
                        source_text_type=doc['text_type'],source_title=source_pages[0]['title'],source_url=source_pages[0]['url'],source_pages=source_pages,
                        collected_at=doc['collected_at'],temporal_note='来源历史陈述；价格、开放和服务须出行前核实',
                        duplicate_group=hashlib.sha256(re.sub(r'\s+','',item['condition_text']+'|'+item['suggestion_text']).encode()).hexdigest()[:12])
            output.append(item)
    near_duplicates=[]
    for i,a in enumerate(output):
        for b in output[i+1:]:
            score=SequenceMatcher(None,a['condition_text']+a['suggestion_text'],b['condition_text']+b['suggestion_text']).ratio()
            if a['scenic_id']==b['scenic_id'] and score>=0.82:
                near_duplicates.append({'advice_ids':[a['advice_id'],b['advice_id']],'similarity':round(score,4),'action':'保留不同条件或来源；不自动语义合并'})
    payload={'schema_version':'1.0','corpus_version':'v1','resource_version':'exp05-v1.1',
             'reviewed':variant=='optimized' and review,
             'corpus_sha256':sha256(ROOT/'data/processed/corpus.jsonl'),'entities_sha256':sha256(ROOT/'data/outputs/entities.json'),
             'variant':variant,'scope_policy':'exp02相关区间，排除S003_VIS_004园外酒评；全文坐标。',
             'statistics':{'documents_scanned':len(docs),'advice':len(output),
                           'condition_types':dict(Counter(a['condition_type'] for a in output)),
                           'visitor_types':dict(Counter(v for a in output for v in (a['visitor_types'] or ['unspecified']))),
                           'scenics':dict(Counter(a['scenic_id'] for a in output))},'advice':output}
    destination='results/checks/exp05_baseline.json' if variant=='baseline' else 'data/outputs/advice.json' if review else 'results/checks/exp05_rule_predictions.json'
    write_json(ROOT/destination,payload)
    if variant=='optimized' and review:write_json(ROOT/'results/checks/exp05_extraction_audit.json',{'documents':audit,'deduplication':duplicates,'near_duplicates':near_duplicates})
    return payload


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--variant',choices=['baseline','optimized'],default='optimized');a=p.parse_args()
    try:print(run(a.variant)['statistics'])
    except (OSError,ValueError,KeyError) as exc:p.exit(1,f'实验5失败：{exc}\n')


if __name__=='__main__':main()
