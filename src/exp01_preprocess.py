"""实验1：离线批量清洗、去重、结构化与质量检查。Python 3.11+，仅标准库。"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
from datetime import date
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BLOCKS = {'p','div','section','article','main','li','ul','ol','br','h1','h2','h3','h4','h5','h6','tr','blockquote'}
REQUIRED = ('schema_version','corpus_version','doc_id','scenic_id','scenic_name','text_type',
            'source_title','source_url','source_note','collected_at','raw_path','text')

class TextExtractor(HTMLParser):
    """保留块边界与行内链接文字；脚本和样式内容不进入正文。"""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.hidden = [], 0
    def handle_starttag(self, tag, attrs):
        if tag in {'script','style','noscript','iframe'}: self.hidden += 1
        if not self.hidden and tag in BLOCKS: self.parts.append('\n')
        if not self.hidden and tag in {'td','th'}: self.parts.append(' | ')
    def handle_startendtag(self, tag, attrs):
        if tag == 'br' and not self.hidden: self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in {'script','style','noscript','iframe'}: self.hidden = max(0, self.hidden - 1)
        if not self.hidden and tag in BLOCKS: self.parts.append('\n')
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)

def extract_text(fragment: str) -> str:
    p = TextExtractor(); p.feed(fragment)
    return ''.join(p.parts)

def clean_text(fragment: str) -> str:
    text = unicodedata.normalize('NFKC', extract_text(fragment))
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    text = text.replace('\r\n','\n').replace('\r','\n')
    text = ''.join(c for c in text if c in '\n\t' or
                   (unicodedata.category(c) not in {'Cc','Cf','Co','Cs'} and
                    not (0x1F300 <= ord(c) <= 0x1FAFF) and ord(c) != 0xFFFD))
    text = re.sub(r'https?://[^\s<>\u3000]+', '', text)
    lines, skip_value = [], False
    for raw in text.splitlines():
        line = re.sub(r'[^\S\n]+', ' ', raw).strip()
        if not line: continue
        if re.fullmatch(r'[|\s]+',line): continue
        if skip_value:
            skip_value = False
            continue
        if line in {'出发时间','行程天数','人均花费','和谁出行'}:
            skip_value = True
            continue
        if line in {'公告:','Home','Plan your visit','Itinerary Planner','Back to Home','Explore','Visitor Trails','Start'}: continue
        if line.startswith('亲爱的用户:感谢您对游记业务的长久支持。'): continue
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}发布 阅读量.*',line): continue
        if re.fullmatch(r'Read the PDF\.pdf.*',line): continue
        # 只匹配整行元数据，避免删除“下午5点闭馆”等有用正文。
        if re.fullmatch(r'(点击查看原图|展开全文|收起全文|目录|分享|收藏|点赞|Spot It|Capture It|Discover the highlights in this area|>|Image)',line): continue
        if lines and line == lines[-1]: continue
        lines.append(line)
    return '\n'.join(lines)

def digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def shingle_set(text: str) -> set[str]:
    text = re.sub(r'\s+', '', text)
    return {text[i:i+5] for i in range(max(0,len(text)-4))}

def process(root: Path, version: str = 'v1') -> dict:
    manifest = json.loads((root/'data/raw/source_manifest.json').read_text(encoding='utf-8'))
    registry = json.loads((root/'data/raw/scenic_registry.json').read_text(encoding='utf-8'))
    assert len(registry['scenics']) == 3 and sum(s['is_main'] for s in registry['scenics']) == 1
    scenic_map = {s['scenic_id']: s for s in registry['scenics']}
    records, rejected, audits, duplicates = [], [], [], []
    hashes, ids, urls = {}, set(), set()
    for source in manifest['sources']:
        try:
            did = source['doc_id']
            if did in ids: raise ValueError('duplicate doc_id')
            ids.add(did)
            if source['scenic_id'] not in scenic_map: raise ValueError('unknown scenic_id')
            if source['text_type'] not in {'official_route','visitor_diary'}: raise ValueError('invalid text_type')
            if not re.fullmatch(r'S\d{3}_(OFF|VIS)_\d{3}',did): raise ValueError('invalid doc_id format')
            if ('_OFF_' in did) != (source['text_type']=='official_route'): raise ValueError('ID/type mismatch')
            if not source['source_title'].strip() or not source['source_note'].strip(): raise ValueError('missing source metadata')
            date.fromisoformat(source['collected_at'])
            u = urlparse(source['source_url'])
            if u.scheme not in {'https','http'} or not u.netloc: raise ValueError('invalid source URL')
            if source['source_url'] in urls: raise ValueError('duplicate source URL')
            urls.add(source['source_url'])
            raw_path = root/source['raw_path']
            if not raw_path.resolve().is_relative_to((root/'data/raw').resolve()): raise ValueError('unsafe raw path')
            fragment = raw_path.read_text(encoding='utf-8')
            if digest(fragment) != source['fragment_sha256']: raise ValueError('raw fragment hash mismatch')
            for page in source['pages']:
                if hashlib.sha256((root/page['path']).read_bytes()).hexdigest() != page['sha256']:
                    raise ValueError('raw webpage hash mismatch: '+page['path'])
            text = clean_text(fragment)
            if len(text) < 150: raise ValueError('empty or too-short body')
            if re.search(r'<\s*/?(?:p|div|script|style)\b',text): raise ValueError('HTML residue')
            h = digest(re.sub(r'\s+', '', text))
            if h in hashes:
                duplicates.append({'doc_id':did,'same_as':hashes[h]})
                raise ValueError('duplicate cleaned body')
            hashes[h] = did
            rec = {k:source[k] for k in REQUIRED if k in source}
            rec.update(schema_version='1.0',corpus_version=version,text=text,
                       language=source['language'],scope_note=source['scope_note'],content_sha256=digest(text))
            if any(not isinstance(rec.get(k),str) or not rec[k].strip() for k in REQUIRED): raise ValueError('invalid required field')
            records.append(rec)
            audits.append({'doc_id':did,'raw_fragment_chars':len(fragment),'extracted_chars':len(extract_text(fragment)),
                           'clean_chars':len(text),'raw_urls':len(re.findall(r'https?://',fragment)),
                           'clean_urls':len(re.findall(r'https?://',text)),'replacement_char_count':fragment.count('\ufffd'),
                           'removed_platform_notice':int('亲爱的用户：感谢您对游记业务的长久支持。' in fragment),
                           'preserved_arrow_count':sum(text.count(c) for c in '→⇒'),
                           'paragraphs':len(text.splitlines()),'content_sha256':digest(text)})
        except (ValueError,KeyError,OSError) as e:
            rejected.append({'doc_id':source.get('doc_id'), 'reason':str(e)})
    near=[]; sets=[shingle_set(r['text']) for r in records]
    for i in range(len(records)):
        for j in range(i+1,len(records)):
            score=len(sets[i]&sets[j])/len(sets[i]|sets[j])
            if score >= .75: near.append({'doc_a':records[i]['doc_id'],'doc_b':records[j]['doc_id'],'jaccard_5gram':round(score,4)})
    counts=Counter((r['scenic_id'],r['text_type']) for r in records)
    per_scenic=[{'scenic_id':sid,'scenic_name':s['scenic_name'],'official_route':counts[sid,'official_route'],
                 'visitor_diary':counts[sid,'visitor_diary'],
                 'clean_chars':sum(len(r['text']) for r in records if r['scenic_id']==sid)} for sid,s in scenic_map.items()]
    checks={'three_scenics':len(per_scenic)==3,'one_main_scenic':sum(s['is_main'] for s in registry['scenics'])==1,
            'target_1_official_5_diaries_each':all(s['official_route']>=1 and s['visitor_diary']>=5 for s in per_scenic),
            'no_rejections':not rejected,'no_exact_duplicates':not duplicates,'no_near_duplicates_ge_0_75':not near,
            'required_fields_complete':all(all(r.get(k) for k in REQUIRED) for r in records),
            'no_platform_notice_residue':all('停止游记业务的运维' not in r['text'] for r in records),
            'all_raw_integrity_verified':not rejected}
    report=dict(schema_version='1.0',corpus_version=version,input_records=len(manifest['sources']),output_records=len(records),
                rejected_records=rejected,exact_duplicates=duplicates,near_duplicates=near,
                near_duplicate_method='whitespace-free character 5-gram Jaccard >= 0.75; flag for review',
                required_field_missing_cells=sum(not r.get(k) for r in records for k in REQUIRED),
                required_field_cells=len(records)*len(REQUIRED),total_clean_chars=sum(len(r['text']) for r in records),
                per_scenic=per_scenic,checks=checks,passed=all(checks.values()),record_audit=audits)
    dest=root/'data/processed';dest.mkdir(parents=True,exist_ok=True)
    write_json(dest/'scenic_registry.json',registry)
    (dest/'corpus.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records),encoding='utf-8')
    with (dest/'corpus.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(REQUIRED)+['original_text','language','scope_note','content_sha256']);writer.writeheader()
        for r in records: writer.writerow(dict(r,original_text=extract_text((root/r['raw_path']).read_text(encoding='utf-8'))))
    write_json(root/'results/checks/exp01_quality.json',report)
    examples=[]
    for did in ['S001_OFF_001','S001_VIS_002','S002_VIS_005','S003_VIS_005']:
        r=next((r for r in records if r['doc_id']==did),None)
        if r is None: continue
        fragment=(root/r['raw_path']).read_text(encoding='utf-8')
        examples.append({'doc_id':did,'raw_path':r['raw_path'],'raw_html_prefix':fragment[:850],'clean_text_prefix':r['text'][:450],
                         'encoding_note':'网页原始编码见collection_plan与pages/*.meta.json；完整快照保留未解码字节。'})
    write_json(root/'results/checks/exp01_before_after.json',examples)
    lines=['# 实验1数据质量检查','',f'输入 {len(manifest["sources"])} 条；输出 {len(records)} 条；正文共 {report["total_clean_chars"]} 字符。','',
           '| 景区 | 官方路线文档 | 有效游记 | 正文字符 |','| --- | ---: | ---: | ---: |']
    lines += [f'| {s["scenic_name"]} | {s["official_route"]} | {s["visitor_diary"]} | {s["clean_chars"]} |' for s in per_scenic]
    lines += ['',f'必填字段空值：{report["required_field_missing_cells"]}/{report["required_field_cells"]}；完全重复：{len(duplicates)}；近重复候选：{len(near)}；拒收：{len(rejected)}。',
              '', '字符数按 Python len(text) 统计，包含正文中的换行和空格，不等同于中文字数。官方路线的多个步骤页合计为一条路线文档。',
              '', '正文不翻译；NFKC 统一兼容字符。跨语言实体别名需要后续实验维护；游客陈述保留原貌，不作为官方事实。',
              '', '## 自动检查','']+[f'- {k}: {v}' for k,v in checks.items()]
    (root/'results/checks/exp01_quality.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--corpus-version',default='v1');args=parser.parse_args();report=process(args.root,args.corpus_version)
    print(json.dumps({k:report[k] for k in ['input_records','output_records','total_clean_chars','per_scenic','checks','passed']},ensure_ascii=False,indent=2))
    if not report['passed']: raise SystemExit(1)

if __name__=='__main__':main()
