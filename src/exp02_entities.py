"""实验2：离线词典、最长匹配和时间规则。默认生成优化结果，--variant baseline生成初版。

仅在v1正文的已登记区间内查找，位置始终指向完整原文；不修改公共语料。
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TYPES = ('POI', 'TRANSPORT', 'TIME')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def load_inputs():
    corpus = ROOT / 'data/processed/corpus.jsonl'
    rows = [json.loads(x) for x in corpus.read_text(encoding='utf-8').splitlines() if x.strip()]
    lex = read_json(ROOT / 'data/resources/exp02_lexicon.json')
    spec = read_json(ROOT / 'data/resources/exp02_scope.json')
    scopes = {x['doc_id']: x['ranges'] for x in spec['documents']}
    if len({r['doc_id'] for r in rows}) != len(rows) or set(scopes) != {r['doc_id'] for r in rows}:
        raise ValueError('文档ID重复或范围清单与语料不一致')
    if any(r['corpus_version'] != spec['corpus_version'] for r in rows):
        raise ValueError('语料版本与范围配置不一致')
    for row in rows:
        previous_end = -1
        for interval in sorted(scopes[row['doc_id']], key=lambda x:x['start']):
            a,b=interval['start'],interval['end']
            if not 0 <= a < b <= len(row['text']) or a < previous_end:
                raise ValueError(f"非法或重叠范围 {row['doc_id']}: {a}:{b}")
            if interval['start_marker'] and not row['text'][a:].startswith(interval['start_marker']):
                raise ValueError('范围起点与原文不符')
            if interval['end_marker'] and not row['text'][b:].startswith(interval['end_marker']):
                raise ValueError('范围终点与原文不符')
            previous_end=b
    return rows,lex,scopes,hashlib.sha256(corpus.read_bytes()).hexdigest()


def alias_pattern(alias):
    # Do not normalize the source string, since this would invalidate offsets.
    pat = r'[ \t]*'.join(re.escape(x) for x in alias.split(' '))
    if re.match(r'[A-Za-z]', alias): pat = r'(?<![A-Za-z])' + pat
    if re.search(r'[A-Za-z]$', alias): pat += r'(?![A-Za-z])'
    return re.compile(pat, re.I)


def dictionaries(lex, sid, variant):
    items=[]
    for entry in lex['poi_entries']:
        if entry['scenic_id'] != sid or (variant == 'baseline' and not entry['baseline']): continue
        aliases=[entry['canonical_name']] + (entry['aliases'] if variant != 'baseline' else [])
        items.append((entry,aliases))
    for item in lex['transport_entries']:
        if sid not in item['scenic_ids'] or (variant == 'baseline' and not item['baseline']): continue
        entry=dict(entity_id=f"{sid}_TRANSPORT_{item['index']:03d}", scenic_id=sid,
                   entity_type='TRANSPORT',canonical_name=item['canonical_name'],aliases=item['aliases'],scope='not_applicable')
        items.append((entry,[entry['canonical_name']]+entry['aliases']))
    if variant == 'baseline':
        for typ, words in lex['stopwords'].items():
            if typ == 'TIME': continue
            for word in words:
                entry=dict(entity_id=f'{sid}_{typ}_NOISE_{word}',scenic_id=sid,entity_type=typ,
                           canonical_name=word,aliases=[],scope='unknown')
                items.append((entry,[word]))
    return items


NUM=r'(?:\d+(?:\.\d+)?|[零〇一二两三四五六七八九十百]+)'
RANGE=rf'{NUM}(?:\s*[-~至到]\s*{NUM})?'
DAYPART=r'(?:凌晨|清晨|早晨|早上|上午|中午|下午|傍晚|晚上|夜间|午夜|黄昏)'
TIME_RULES=[
    ('clock',rf'(?<![\d.])(?:{DAYPART}\s*)?(?:[01]?\d|2[0-3]):[0-5]\d(?!\d)'),
    ('clock',rf'(?:{DAYPART}\s*)?{NUM}\s*点(?:半|\d{{1,2}}分)?'),
    ('calendar_date',r'(?<!\d)(?:\d{4}年)?(?:1[0-2]|0?[1-9])月(?:[12]?\d|3[01])日'),
    ('day_index',r'第[一二三四五六七八九十\d]+天|\bDay\s*\d+\b'),
    ('duration',rf'{RANGE}\s*个?半?小时(?:\s*{NUM}\s*分钟)?|半个?小时|{RANGE}\s*分钟|{RANGE}\s*天|{RANGE}\s*日(?=游|\n|$)'),
    ('duration',rf'(?<![\d.]){RANGE}\s*(?:hours?|hrs?|hr|minutes?|mins?|min|days?|nights?)(?![A-Za-z])'),
    ('daypart',DAYPART),
]


def normalize_time(surface, subtype):
    compact=re.sub(r'\s+','',surface).lower()
    if subtype=='day_index': return re.sub(r'^day', 'Day ', compact)
    if subtype=='daypart': return {'早晨':'早上','清晨':'早上'}.get(compact,compact)
    # Conservative surface normalization, not a guessed calendar or arrival time.
    return compact.replace('hours','小时').replace('hour','小时').replace('hrs','小时').replace('hr','小时').replace('minutes','分钟').replace('minute','分钟').replace('mins','分钟').replace('min','分钟').replace('days','天').replace('day','天').replace('nights','晚').replace('night','晚')


def extract_candidates(row, lex, intervals, variant='optimized'):
    text,sid=row['text'],row['scenic_id']; found=[]
    for entry,aliases in dictionaries(lex,sid,variant):
        for alias in aliases:
            pat=alias_pattern(alias)
            for interval in intervals:
                for m in pat.finditer(text,interval['start'],interval['end']):
                    if variant=='optimized' and entry['entity_type']=='POI':
                        # Product/operator names containing a location are not physical-place mentions.
                        suffix=text[m.end():m.end()+16]
                        if entry['canonical_name']=='Half Dome' and re.match(r'\s+(?:Pizza|View)\b',suffix,re.I): continue
                        if entry['canonical_name']=='悉尼' and re.match(r'\s+HeliTours\b',suffix,re.I): continue
                        if entry['canonical_name']=='箱根' and re.match(r'\s*(?:\d+日)?周游[券劵]',suffix): continue
                    found.append(dict(start=m.start(),end=m.end(),text=m.group(),entry=entry,method='dictionary'))
    rules=TIME_RULES if variant=='optimized' else [TIME_RULES[0],TIME_RULES[4],TIME_RULES[-1]]
    for subtype,pattern in rules:
        for interval in intervals:
            for m in re.finditer(pattern,text[interval['start']:interval['end']],re.I):
                a,b=m.start()+interval['start'],m.end()+interval['start']; surface=text[a:b]
                if variant=='optimized':
                    if subtype=='daypart' and text[b:b+1]=='茶': continue
                    if subtype=='clock' and surface=='一点' and re.search(r'(?:没有|有趣|有|多|少|差|好|难|不止)$',text[max(0,a-3):a]): continue
                    nearby=text[max(interval['start'],a-12):min(interval['end'],b+12)]
                    if subtype=='duration' and re.search(r'历史|树龄|延寿|形成于|形成并|年前|万年',nearby): continue
                    if a>0 and text[a-1].isdigit(): continue
                canonical=normalize_time(surface,subtype)
                entry=dict(entity_id=None,scenic_id=sid,entity_type='TIME',canonical_name=canonical,
                           aliases=[surface],scope='not_applicable',time_subtype=subtype)
                found.append(dict(start=a,end=b,text=surface,entry=entry,method='rule'))
    if variant=='baseline':
        unique={(x['start'],x['end'],x['entry']['entity_type'],x['entry']['canonical_name']):x for x in found}
        return sorted(unique.values(),key=lambda x:(x['start'],x['end'],x['entry']['canonical_name']))
    selected=[]; occupied=set()
    for item in sorted(found,key=lambda x:(-(x['end']-x['start']),x['start'],x['entry']['entity_type'],x['entry']['canonical_name'])):
        indexes=range(item['start'],item['end'])
        if any(i in occupied for i in indexes): continue
        occupied.update(indexes); selected.append(item)
    return sorted(selected,key=lambda x:(x['start'],x['end']))


def build_output(rows,lex,scopes,corpus_hash,variant,previous=None):
    catalog={}; time_ids={}; next_time=defaultdict(int)
    # IDs survive reordering and additions; retired entities remain as inactive records.
    for entry in (previous or {}).get('entity_catalog',[]):
        if entry['entity_type']=='TIME':
            key=(entry['scenic_id'],entry.get('time_subtype'),entry['canonical_name'])
            time_ids[key]=entry['entity_id']
            next_time[entry['scenic_id']]=max(next_time[entry['scenic_id']],int(entry['entity_id'].rsplit('_',1)[1]))
        catalog[entry['entity_id']]=dict(entry,active=False,mention_count=0)
    prior_mentions={}; seqs=defaultdict(int)
    for m in (previous or {}).get('mentions',[]):
        span=m['span']; key=(span['doc_id'],span['start'],span['end'],m['entity_id'])
        prior_mentions[key]=m['mention_id']
        seqs[span['doc_id']]=max(seqs[span['doc_id']],int(m['mention_id'].rsplit('_',1)[1]))
    mentions=[]
    for row in rows:
        for item in extract_candidates(row,lex,scopes[row['doc_id']],variant):
            entry=dict(item['entry']); sid=entry['scenic_id']
            if entry['entity_type']=='TIME':
                key=(sid,entry['time_subtype'],entry['canonical_name'])
                if key not in time_ids:
                    next_time[sid]+=1; time_ids[key]=f'{sid}_TIME_{next_time[sid]:03d}'
                entry['entity_id']=time_ids[key]
            eid=entry['entity_id']
            if eid not in catalog or not catalog[eid]['active']: catalog[eid]=dict(entry,active=True,mention_count=0)
            cat=catalog[eid]; cat['mention_count']+=1
            cat['aliases']=sorted(set(cat['aliases']+[item['text']])-{cat['canonical_name']})
            key=(row['doc_id'],item['start'],item['end'],eid); mid=prior_mentions.get(key)
            if mid is None:
                seqs[row['doc_id']]+=1; mid=f"M_{row['doc_id']}_{seqs[row['doc_id']]:04d}"
            mentions.append(dict(mention_id=mid,entity_id=eid,entity_type=entry['entity_type'],
                                 span=dict(doc_id=row['doc_id'],start=item['start'],end=item['end'],text=item['text']),
                                 method=item['method'],scenic_id=sid,text_type=row['text_type']))
    return dict(schema_version='1.0',corpus_version='v1',resource_version=lex['resource_version'],variant=variant,
                corpus_sha256=corpus_hash,offset_convention='Python Unicode characters; zero-based [start,end) in full corpus text',
                scope_file='data/resources/exp02_scope.json',entity_catalog=sorted(catalog.values(),key=lambda x:x['entity_id']),mentions=mentions)


def statistics(output,rows,scopes):
    catalog={x['entity_id']:x for x in output['entity_catalog']}; mentions=output['mentions']
    freq=Counter(m['entity_id'] for m in mentions); per_scenic=[]
    for sid in sorted({x['scenic_id'] for x in rows}):
        relevant=[m for m in mentions if catalog[m['entity_id']]['scenic_id']==sid]
        per_scenic.append(dict(scenic_id=sid,scenic_name=next(x['scenic_name'] for x in rows if x['scenic_id']==sid),
            docs=sum(x['scenic_id']==sid for x in rows),
            scoped_chars=sum(v['end']-v['start'] for r in rows if r['scenic_id']==sid for v in scopes[r['doc_id']]),
            mentions_by_type={t:sum(m['entity_type']==t for m in relevant) for t in TYPES},
            entities_by_type={t:sum(catalog[e]['entity_type']==t for e in {m['entity_id'] for m in relevant}) for t in TYPES}))
    top={t:[dict(entity_id=e,canonical_name=catalog[e]['canonical_name'],scenic_id=catalog[e]['scenic_id'],count=n)
            for e,n in freq.most_common() if catalog[e]['entity_type']==t][:12] for t in TYPES}
    return dict(variant=output['variant'],documents=len(rows),mentions=len(mentions),active_entities=len(freq),
                by_type={t:sum(m['entity_type']==t for m in mentions) for t in TYPES},per_scenic=per_scenic,top_entities=top)


def frequency_csv(output,path):
    catalog={x['entity_id']:x for x in output['entity_catalog']}
    counts=Counter((m['entity_id'],m['text_type']) for m in output['mentions'])
    with Path(path).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f); writer.writerow(['entity_id','scenic_id','entity_type','canonical_name','scope','text_type','count'])
        for (eid,source_type),n in sorted(counts.items()):
            e=catalog[eid]; writer.writerow([eid,e['scenic_id'],e['entity_type'],e['canonical_name'],e['scope'],source_type,n])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant',choices=['baseline','optimized'],default='optimized'); args=parser.parse_args()
    try:
        rows,lex,scopes,corpus_hash=load_inputs()
        path=ROOT/('data/outputs/entities.json' if args.variant=='optimized' else 'results/checks/exp02_baseline_entities.json')
        previous=read_json(path) if path.exists() and args.variant=='optimized' else None
        output=build_output(rows,lex,scopes,corpus_hash,args.variant,previous); write_json(path,output)
        stats=statistics(output,rows,scopes); write_json(ROOT/f'results/checks/exp02_{args.variant}_stats.json',stats)
        frequency_csv(output,ROOT/f'results/checks/exp02_{args.variant}_frequency.csv')
        print(json.dumps({k:stats[k] for k in ['variant','documents','active_entities','mentions','by_type']},ensure_ascii=False))
    except (OSError,ValueError,KeyError) as error:
        print(f'实验2失败：{error}',file=sys.stderr); raise SystemExit(1)


if __name__=='__main__': main()
