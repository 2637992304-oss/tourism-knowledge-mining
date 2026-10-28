"""实验1网页采集与正文定位。默认使用本地快照；--download 仅下载缺少的页面。

来源为官方景区/旅游机构及多个公开游记平台。采集请求顺序执行，间隔1秒，最多重试3次。
不会绕过登录或验证码。冻结v1后不要覆盖快照后继续使用旧字符偏移量。
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
from lxml import html

ROOT=Path(__file__).resolve().parents[1]

def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')

def get_page(root, did, no, url, download, encoding="utf-8"):
    p=root/'data/raw/pages'/f'{did}_{no:02d}.html';meta=p.with_suffix('.meta.json')
    if not p.exists():
        if not download:raise FileNotFoundError(f'{p}: 缺少快照，请加 --download')
        error=None
        for attempt in range(3):
            try:
                with urlopen(Request(url,headers={'User-Agent':'CourseExperiment/1.0 (educational text collection)'}),timeout=40) as r:
                    data=r.read();resolved=r.url
                data.decode(encoding,errors='strict')
                p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
                dump(meta,dict(request_url=url,resolved_url=resolved,downloaded_at=now(),http_status=200,encoding=encoding,sha256=sha(data)))
                time.sleep(1);break
            except Exception as e:error=e;time.sleep(attempt+1)
        else:raise RuntimeError(f'采集失败 {url}: {error}')
    if not meta.exists():raise ValueError(f'缺少采集时间与校验信息 {meta}')
    m=json.loads(meta.read_text(encoding='utf-8'));data=p.read_bytes()
    if sha(data)!=m['sha256']:raise ValueError(f'快照被修改 {p}')
    return html.fromstring(data.decode(m.get('encoding',encoding))),dict(url=m['request_url'],path=p.relative_to(root).as_posix(),sha256=sha(data),downloaded_at=m['downloaded_at'])

def fragment(node):
    node=deepcopy(node)
    for n in node.xpath('.//script|.//style|.//noscript|.//iframe|.//button|.//img|.//svg|.//*[@class="post-meta" or @class="post-info"]'):
        n.drop_tree()
    # 页面图片操作、位置标签不属于作者正文；保留其他段落和图片后的正文。
    for n in node.xpath('.//div[contains(concat(" ",normalize-space(@class)," ")," img ")]'):
        n.drop_tree()
    for n in node.xpath('.//nav|.//div[contains(@class,"breadcrumbs-component") or @class="itinerary-map-container" or @class="itinerary-breadcrumb--container"]'):
        if n.getparent() is not None: n.drop_tree()
    return html.tostring(node,encoding='unicode',with_tail=False)

def collect(root,download=False):
    plan=json.loads((root/'data/raw/collection_plan.json').read_text(encoding='utf-8'))
    sources=[]
    for spec in plan['sources']:
        pages,parts=[],[]
        for no,entry in enumerate(spec['pages'],1):
            tree,page=get_page(root,spec['doc_id'],no,entry['url'],download,entry['encoding'])
            nodes=tree.xpath(entry['xpath'])
            if len(nodes)!=entry.get('expected_nodes',1): raise ValueError(f"正文定位失效 {spec['doc_id']} page {no}: {len(nodes)} matches")
            parts.extend(fragment(n) for n in nodes);pages.append(page)
        source=save_source(root,spec,spec['doc_id'],spec['text_type'],spec['source_title'],pages[0]['url'],
                           '\n'.join(parts),pages,spec['language'],spec['scope_note'])
        if spec['text_type']=='visitor_diary':
            source['source_note']='游客一手亲历文章；原始平台 '+pages[0]['url'].split('/')[2]
        sources.append(source)
    dump(root/'data/raw/source_manifest.json',dict(schema_version='1.0',corpus_version='v1',sources=sources))
    print(f"来源登记完成：{len(sources)}篇文档，{sum(len(s['pages']) for s in sources)}个网页快照。")

def save_source(root,scenic,did,kind,title,url,body,pages,language,note):
    body=body.replace('\r\n','\n').replace('\r','\n')
    raw=f'data/raw/fragments/{did}.html';p=root/raw;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body.encode('utf-8'))
    return dict(doc_id=did,scenic_id=scenic['scenic_id'],scenic_name=scenic['scenic_name'],text_type=kind,
        source_title=title,source_url=pages[0]['url'],source_note=('携程攻略社区，原始游记编号'+str(url.split('/')[-1].split('.')[0]) if kind=='visitor_diary' else note),
        collected_at=pages[0]['downloaded_at'][:10],raw_path=raw,fragment_sha256=sha(body.encode('utf-8')),
        pages=pages,language=language,scope_note=note)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--download',action='store_true',help='只下载缺少的公开网页；离线复现无需此选项')
    a=p.parse_args();collect(a.root,a.download)

if __name__=='__main__':main()
