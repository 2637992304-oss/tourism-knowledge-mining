"""Resolve frozen-document character spans to the contributing source pages."""
from mining_io import ROOT, read_json, sha256


def evidence_sources(docs, refs, evidence):
    path = ROOT/'data/resources/source_page_spans.json'
    mapping = read_json(path)
    if mapping['corpus_sha256'] != sha256(ROOT/'data/processed/corpus.jsonl'):
        raise ValueError('来源映射已过期')
    rows = []
    for did in sorted(set(refs)):
        if did not in docs:
            continue
        doc = docs[did]
        spans = [s for s in evidence if s['doc_id'] == did]
        pages = mapping['documents'].get(did, [])
        selected = [p for p in pages if not spans or any(
            s['start'] < p['end'] and p['start'] < s['end'] for s in spans)]
        if spans and pages and not selected:
            raise ValueError('证据没有对应网页：'+did)
        # Synthetic fixtures / single-page documents keep their declared source.
        for page in selected or [{'url':doc['source_url'],'title':doc['source_title']}]:
            row = {'doc_id':did,'title':page['title'],'url':page['url'],
                   'text_type':doc['text_type'],'collected_at':doc['collected_at']}
            if row not in rows:
                rows.append(row)
    return rows
