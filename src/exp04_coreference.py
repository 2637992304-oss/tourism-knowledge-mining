"""实验4：离线检测、类型约束规则及评价。预测不读取参考标签。

位置均为冻结v1原文的Python字符区间[start,end)，消解文本另存，不覆盖语料。
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DOC_IDS = ('S001_VIS_001','S001_VIS_003','S002_VIS_005','S003_VIS_001','S003_VIS_005')
PRONOUN_PATTERN = r'(?<!其)(?:他们|她们|它们|这里|那里|此处|这儿|那儿|这位|那位|这个|那个|这些|那些|它|他|她|这(?!么|样)|那(?!么|样))'
PRONOUN_RE = re.compile(PRONOUN_PATTERN)
WINDOW, MAX_SENTENCES = 320, 4

def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write_json(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def sha256(path):
    # 仓库将文本归一为LF；Windows工作区中已有JSON可能为CRLF。
    # 按仓库规范化后的字节计算，保证克隆到不同平台后结果哈希一致。
    content=Path(path).read_bytes().replace(b'\r\n',b'\n')
    return hashlib.sha256(content).hexdigest()

def span(doc_id,text,start,end):
    return dict(doc_id=doc_id,start=start,end=end,text=text[start:end])

def sentences(doc_id,text):
    """中文终止标点/换行分句；英文句点只在非数字且后接空白/中文时切分。"""
    result=[]
    for m in re.finditer(r'[^。！？!?\n]+[。！？!?]?|\n+',text):
        if not m.group().strip():continue
        start=m.start()
        for cut in re.finditer(r'(?<!\d)\.(?=\s|[\u4e00-\u9fff])',m.group()):
            end=m.start()+cut.end();result.append(span(doc_id,text,start,end));start=end
        if start<m.end():result.append(span(doc_id,text,start,m.end()))
    return result

def detect(doc_id,text):
    sents=sentences(doc_id,text);result=[]
    for m in PRONOUN_RE.finditer(text):
        index,sentence=next((i,s) for i,s in enumerate(sents) if s['start']<=m.start()<s['end'])
        result.append(dict(case_id=f'CR_{doc_id}_{m.start():05d}',doc_id=doc_id,pronoun=m.group(),
            span=span(doc_id,text,m.start(),m.end()),sentence=sentence,sentence_index=index,
            context=span(doc_id,text,max(0,m.start()-WINDOW),min(len(text),m.end()+100))))
    return result

def candidates(doc_id,text,entities):
    catalog={e['entity_id']:e for e in entities['entity_catalog']};result=[]
    for m in entities['mentions']:
        s=m['span']
        if s['doc_id']!=doc_id or m['entity_type']=='TIME':continue
        result.append(dict(text=catalog[m['entity_id']]['canonical_name'],entity_id=m['entity_id'],
            candidate_type=m['entity_type'],evidence=s,origin='exp02_entity'))
    # 票券、人物、路线、物品另建候选，不修改公共实体目录。
    rules=[
      ('TICKET',r'(?:[\u4e00-\u9fff]{1,6}的)?[\u4e00-\u9fff]{1,4}\d日周游券|周游券'),
      ('PERSON',r'一对夫妇(?:带着[一二三四五六七八九十\d]+个孩子)?'),
      ('PERSON',r'一(?:位|名)[^。！？!?，,\n.]{1,16}?(?:大姐|大叔|巫师|导游|司机)'),
      ('PERSON',r'[三两二\d]位[^。！？!?，,\n.]{0,8}?姐妹|三姐妹(?!峰|岩)'),
      ('ROUTE',r'徒步路线|徒步线路|步道|离开[^。！？!?，,\n.]{1,16}向[^。！？!?，,\n.]{1,12}进发|[^。！？!?，,\n.]{0,3}森林浴的徒步道'),
      ('POI',r'水中神社'),('OBJECT',r'一个通道|硫磺洞')]
    for typ,pattern in rules:
        for m in re.finditer(pattern,text):
            name=m.group();begin=m.start()
            if typ=='TICKET':
                clean=re.sub(r'^.*?(?:购买了|购买|买了|买)','',name)
                begin+=len(name)-len(clean);name=clean
            prior=[c for c in result if c['candidate_type']==typ and c['evidence']['end']<=m.start()]
            if typ=='TICKET' and name=='周游券' and prior:
                name=max(prior,key=lambda c:c['evidence']['end'])['text']
            if typ=='PERSON' and name.endswith('姐妹'):
                family=[c for c in prior if c['text'].endswith('姐妹')]
                if family:name=max(family,key=lambda c:c['evidence']['end'])['text']
            result.append(dict(text=name,entity_id=None,candidate_type=typ,
                evidence=span(doc_id,text,begin,m.end()),origin='noun_phrase_rule'))
    # 捕获未登记的同句餐馆名称，例如“的某某这个中国餐馆”，不依赖参考标签。
    for m in re.finditer(r'(?:名为|叫做|的)([\u4e00-\u9fff]{2,8})(?=这个(?:中国)?餐馆)',text):
        result.append(dict(text=m.group(1),entity_id=None,candidate_type='POI',evidence=span(doc_id,text,m.start(1),m.end(1)),origin='noun_phrase_rule'))
    pois=sorted((c for c in result if c['candidate_type']=='POI' and c['entity_id']),key=lambda c:c['evidence']['start'])
    for a,b in zip(pois,pois[1:]):
        if text[a['evidence']['end']:b['evidence']['start']] in ('和','与','、'):
            s=span(doc_id,text,a['evidence']['start'],b['evidence']['end'])
            result.append(dict(text=s['text'],entity_id=None,candidate_type='GROUP',evidence=s,origin='coordinated_pois'))
    return sorted(result,key=lambda c:(c['evidence']['start'],c['evidence']['end'],c['text']))

def predict(case,text,pool,variant='typed'):
    start=case['span']['start'];after=text[case['span']['end']:case['span']['end']+22]
    cutoff=sentences(case['doc_id'],text)[max(0,case['sentence_index']-MAX_SENTENCES)]['start']
    available=[c for c in pool if c['evidence']['end']<=start and start-c['evidence']['end']<=WINDOW and c['evidence']['start']>=cutoff]
    reason='nearest_entity'
    if variant=='baseline':
        available=[c for c in available if c['origin']=='exp02_entity']
    else:
        p=case['pronoun']
        if re.match(r'(?:次|一程|美妙|机会|时候|情景|是.*时间)',after):
            return None,None,'event_or_temporal_deixis',[]
        if p in ('他','她','他们','她们','这位','那位') or re.match(r'[三两二\d]位',after):
            preferred={'PERSON'};reason='person_type'
        elif p in ('这里','那里','此处','这儿','那儿'):
            preferred={'POI'};reason='location_type'
        elif re.match(r'(?:段路|段森林浴|条.*路线)',after) or (p=='这' and after.startswith('是一条')):
            preferred={'ROUTE'};reason='route_type'
        elif re.match(r'(?:周游券|券)',after):preferred={'TICKET'};reason='ticket_type'
        elif after.startswith('通道'):preferred={'OBJECT'};reason='object_type'
        elif p in ('这些','那些'):preferred={'GROUP'};reason='plural_group'
        elif p=='它':
            preferred={'TICKET'} if any(c['candidate_type']=='TICKET' for c in available) else {'POI','OBJECT'}
            reason='inanimate_type'
        else:preferred={'POI'};reason='poi_default'
        available=[c for c in available if c['candidate_type'] in preferred]
    if not available:return None,None,'no_compatible_candidate',[]
    ranked=sorted(available,key=lambda c:(start-c['evidence']['end'],-len(c['evidence']['text']),c['text']))
    chosen=ranked[0]
    trace=[dict(text=c['text'],entity_id=c['entity_id'],candidate_type=c['candidate_type'],distance=start-c['evidence']['end'],evidence=c['evidence']) for c in ranked[:5]]
    return dict(text=chosen['text'],entity_id=chosen['entity_id']),chosen['evidence'],reason,trace

def same_antecedent(a,b):
    if a is None or b is None:return a is b
    if a['entity_id'] is not None and b['entity_id'] is not None:return a['entity_id']==b['entity_id']
    return a['entity_id']==b['entity_id'] and a['text']==b['text']

def evaluate(cases):
    n=len(cases);positive=[c for c in cases if c['gold_antecedent'] is not None]
    answered=[c for c in cases if c['predicted_antecedent'] is not None]
    correct=[c for c in positive if same_antecedent(c['gold_antecedent'],c['predicted_antecedent'])]
    nulls=[c for c in cases if c['gold_antecedent'] is None];null_ok=[c for c in nulls if c['predicted_antecedent'] is None]
    metrics={}
    for key,num,den in [('overall_accuracy',len(correct)+len(null_ok),n),('positive_accuracy',len(correct),len(positive)),('coverage',len(answered),n),('answered_precision',len(correct),len(answered)),('null_rejection_accuracy',len(null_ok),len(nulls)),('unresolved_rate',n-len(answered),n)]:
        metrics[key]=dict(numerator=num,denominator=den,value=num/den if den else None)
    return dict(total=n,positive=len(positive),gold_null=len(nulls),answered=len(answered),correct_links=len(correct),correct_nulls=len(null_ok),metrics=metrics,status_counts=dict(Counter(c['gold_status'] for c in cases)))

def resolve_documents(docs,cases):
    result=[]
    for d in docs:
        text=d['text'];edits=[];cursor=0;pieces=[];new_cursor=0
        selected=sorted((x for x in cases if x['doc_id']==d['doc_id'] and x['predicted_antecedent'] is not None),key=lambda x:x['span']['start'])
        for c in selected:
            s=c['span'];prefix=text[cursor:s['start']];pieces.append(prefix);new_cursor+=len(prefix)
            replacement=c['pronoun']+'（指：'+c['predicted_antecedent']['text']+'）';pieces.append(replacement)
            edits.append(dict(case_id=c['case_id'],original_span=s,resolved_start=new_cursor,resolved_end=new_cursor+len(replacement),replacement=replacement))
            new_cursor+=len(replacement);cursor=s['end']
        pieces.append(text[cursor:])
        result.append(dict(doc_id=d['doc_id'],original_text=text,resolved_text=''.join(pieces),edits=edits,warning='自动规则文本含真实误消解；须核验后使用，不得覆盖公共语料或直接视为图谱事实。'))
    return result

def run(variant='typed'):
    corpus_path=ROOT/'data/processed/corpus.jsonl'
    all_docs=[json.loads(x) for x in corpus_path.read_text(encoding='utf-8').splitlines()]
    docs=[next(d for d in all_docs if d['doc_id']==did) for did in DOC_IDS]
    entities=load_json(ROOT/'data/outputs/entities.json')
    if entities['corpus_version']!='v1' or any(d['corpus_version']!='v1' for d in docs):raise ValueError('仅支持冻结v1语料。')
    cases=[]
    for d in docs:
        pool=candidates(d['doc_id'],d['text'],entities)
        for c in detect(d['doc_id'],d['text']):
            prediction,evidence,reason,trace=predict(c,d['text'],pool,variant)
            c.update(predicted_antecedent=prediction,predicted_evidence=evidence,prediction_status='resolved' if prediction else 'abstain',method='nearest_entity' if variant=='baseline' else 'typed_nearest_rule',decision_reason=reason,candidate_trace=trace)
            s=c['span'];sentence=c['sentence'];local=s['start']-sentence['start']
            replacement=c['pronoun']+'（指：'+prediction['text']+'）' if prediction else c['pronoun']
            c['resolved_text']=sentence['text'][:local]+replacement+sentence['text'][local+len(s['text']):]
            cases.append(c)
    # 到此预测已完成；此后才读取标签，不能将真实答案作为预测。
    reference_path=ROOT/'data/resources/exp04_reference.json';reference=load_json(reference_path)
    if reference['corpus_sha256']!=sha256(corpus_path):raise ValueError('语料哈希改变，请重新标注。')
    gold={c['case_id']:c for c in reference['cases']}
    if {c['case_id'] for c in cases}!=set(gold):raise ValueError('检测与参考样本不一致。')
    for c in cases:
        for key in ('gold_status','antecedent_type','gold_antecedent','gold_evidence','annotation_note'):c[key]=gold[c['case_id']][key]
        c['correct']=same_antecedent(c['gold_antecedent'],c['predicted_antecedent'])
    output=dict(schema_version='1.0',corpus_version='v1',corpus_sha256=sha256(corpus_path),entities_sha256=sha256(ROOT/'data/outputs/entities.json'),reference_sha256=sha256(reference_path),annotation_provenance=reference['annotation_provenance'],parameters=dict(variant=variant,window_characters=WINDOW,max_previous_sentences=MAX_SENTENCES,pronoun_pattern=PRONOUN_PATTERN),documents=[dict(doc_id=d['doc_id'],scenic_id=d['scenic_id'],source_title=d['source_title'],source_url=d['source_url'],characters=len(d['text'])) for d in docs],metrics=evaluate(cases),cases=cases)
    write_json(ROOT/('data/outputs/coreference.json' if variant=='typed' else 'results/checks/exp04_baseline.json'),output)
    if variant=='typed':
        write_json(ROOT/'data/outputs/coreference_resolved_documents.json',dict(schema_version='1.0',corpus_version='v1',corpus_sha256=sha256(corpus_path),documents=resolve_documents(docs,cases)))
        write_json(ROOT/'results/checks/exp04_metrics.json',output['metrics'])
    return output

def main():
    parser=argparse.ArgumentParser(description='实验4：5篇游记的离线代词检测与共指消解')
    parser.add_argument('--variant',choices=['baseline','typed'],default='typed');args=parser.parse_args()
    try:result=run(args.variant)
    except (ValueError,KeyError,StopIteration,FileNotFoundError) as exc:parser.exit(1,f'实验4失败：{exc}\n')
    print(f"Python {sys.version.split()[0]} | {args.variant} | {len(result['documents'])}篇 | {len(result['cases'])}例")
    print(json.dumps(result['metrics'],ensure_ascii=False,indent=2))

if __name__=='__main__':main()
