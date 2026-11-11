"""Build page attribution without changing frozen v1 text or offsets."""
from lxml import html
from exp01_collect import fragment
from exp01_preprocess import clean_text
from mining_io import ROOT, corpus, read_json, write_json, sha256

def main():
    docs=corpus();mapping={}
    for spec in read_json(ROOT/'data/raw/collection_plan.json')['sources']:
        did=spec['doc_id'];text=docs[did]['text'];pages=[];cursor=0
        for i,entry in enumerate(spec['pages'],1):
            path=ROOT/'data/raw/pages'/f'{did}_{i:02d}.html'
            tree=html.fromstring(path.read_bytes().decode(entry['encoding']))
            part=clean_text('\n'.join(fragment(n) for n in tree.xpath(entry['xpath'])))
            start=text.find(part,cursor)
            if start<0 or not part:raise ValueError('网页正文无法完整定位：'+did)
            pages.append({'start':start,'end':start+len(part),'url':entry['url'],
                          'title':tree.findtext('.//title') or docs[did]['source_title'],
                          'snapshot':path.relative_to(ROOT).as_posix(),'snapshot_sha256':sha256(path)})
            cursor=start+len(part)
        mapping[did]=pages
    write_json(ROOT/'data/resources/source_page_spans.json',{
        'corpus_version':'v1','corpus_sha256':sha256(ROOT/'data/processed/corpus.jsonl'),
        'method':'逐网页正文独立清洗后在冻结全文精确定位；不改全文', 'documents':mapping})
    print('网页来源范围：',sum(map(len,mapping.values())))

if __name__=='__main__':main()
