"""Evidence roles describe text scope, not travel permission or suitability."""
import re

def entity_roles(item,doc,entities,related_ids):
    result={}
    for mention in entities['mentions']:
        ref=mention['span'];eid=mention['entity_id']
        if eid not in related_ids or ref['doc_id']!=doc['doc_id']:continue
        if not any(e['start']<=ref['start'] and ref['end']<=e['end'] for e in item['evidence']):continue
        roles=[]
        for field,role in [('condition_span','condition_reference'),('suggestion_span','suggestion_reference')]:
            s=item[field]
            if s['start']<=ref['start'] and ref['end']<=s['end']:roles.append(role)
        if not roles:roles=['supporting_context']
        text=doc['text'];start=max(text.rfind(c,0,ref['start']) for c in ',，。;；\n')+1
        end=min([p for c in ',，。;；\n' if (p:=text.find(c,ref['end']))>=0] or [len(text)])
        clause=text[start:end]
        polarity='negative' if re.search(r'不能|禁止|不可|不允许|没有|不需要',clause) else 'not_asserted'
        compare=re.search(r'比(?:坐|乘|搭乘)?',clause)
        if compare and ref['start']>=start+compare.end():
            roles=['comparison_reference']
        for role in roles:
            key=(eid,role,polarity)
            result.setdefault(key,[]).append(ref)
    return [dict(entity_id=eid,role=role,polarity=polarity,polarity_scope='evidence_clause_not_entity_permission',evidence=refs)
            for (eid,role,polarity),refs in sorted(result.items())]
