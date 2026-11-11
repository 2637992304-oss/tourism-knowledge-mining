"""Offset-preserving extraction exclusions; frozen corpus is never rewritten."""
from mining_io import ROOT, read_json

def exclusions(doc_id):
    path=ROOT/'data/resources/noise_exclusions.json'
    return read_json(path)['documents'].get(doc_id,[]) if path.exists() else []

def overlaps_noise(doc_id,start,end):
    return any(start<x['end'] and x['start']<end for x in exclusions(doc_id))

def effective_ranges(doc_id,ranges):
    result=[]
    for interval in ranges:
        parts=[(interval['start'],interval['end'])]
        for cut in exclusions(doc_id):
            parts=[piece for a,b in parts for piece in
                   ([(a,b)] if b<=cut['start'] or a>=cut['end'] else
                    [(a,min(b,cut['start'])),(max(a,cut['end']),b)]) if piece[0]<piece[1]]
        result.extend(dict(interval,start=a,end=b,start_marker=None,end_marker=None) for a,b in parts)
    return result
