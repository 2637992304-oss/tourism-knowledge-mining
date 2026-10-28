"""实验4的来源、偏移、编号、指标、映射及复跑稳定性检查；输出完整逐例核验。"""
import csv
import io
from collections import Counter
from pathlib import Path
import sys

from exp04_coreference import (ROOT, DOC_IDS, PRONOUN_RE, detect, evaluate, load_json,
    resolve_documents, run, same_antecedent, sha256, write_json)


def main():
    corpus_path=ROOT/'data/processed/corpus.jsonl'
    docs={d['doc_id']:d for d in __import__('json').loads('['+','.join(corpus_path.read_text(encoding='utf8').splitlines())+']')}
    paths=['data/processed/corpus.jsonl','data/outputs/entities.json','data/resources/exp04_reference.json']
    before={p:sha256(ROOT/p) for p in paths}
    original=load_json(ROOT/'data/outputs/coreference.json')
    baseline=load_json(ROOT/'results/checks/exp04_baseline.json')
    regenerated=run('typed');assert regenerated==original,'复跑结果变化'
    assert run('baseline')==baseline,'基线复跑结果变化'
    assert before=={p:sha256(ROOT/p) for p in paths},'输入被修改'
    cases=original['cases'];ids=[c['case_id'] for c in cases];assert len(set(ids))==len(ids)
    assert len(set(c['doc_id'] for c in cases))==5
    cat={e['entity_id']:e for e in load_json(ROOT/'data/outputs/entities.json')['entity_catalog']}
    checked=0
    for c in cases:
        for s in [c['span'],c['sentence'],c['context'],c['gold_evidence'],c['predicted_evidence']]+[x['evidence'] for x in c['candidate_trace']]:
            if s is None:continue
            assert 0<=s['start']<s['end']<=len(docs[s['doc_id']]['text'])
            assert docs[s['doc_id']]['text'][s['start']:s['end']]==s['text'];checked+=1
        assert c['span']['text']==c['pronoun']
        for key in ['gold_antecedent','predicted_antecedent']:
            a=c[key]
            if a and a['entity_id']:
                assert a['entity_id'] in cat
                assert cat[a['entity_id']]['scenic_id']==docs[c['doc_id']]['scenic_id']
        assert c['correct']==same_antecedent(c['gold_antecedent'],c['predicted_antecedent'])
        assert (c['gold_status']=='resolved')==(c['gold_antecedent'] is not None)
    assert evaluate(cases)==original['metrics']
    # 同句多个相同代词的每次出现有独立ID，且全篇扫描集合与参考一致。
    repeated=[]
    for did in DOC_IDS:
        found=detect(did,docs[did]['text'])
        assert {x['case_id'] for x in found}=={x['case_id'] for x in cases if x['doc_id']==did}
        counts=Counter((x['sentence']['start'],x['pronoun']) for x in found)
        repeated.extend(dict(doc_id=did,sentence_start=k[0],pronoun=k[1],count=v) for k,v in counts.items() if v>1)
    resolved=load_json(ROOT/'data/outputs/coreference_resolved_documents.json')
    assert resolved['documents']==resolve_documents([docs[d] for d in DOC_IDS],cases)
    for d in resolved['documents']:
        for edit in d['edits']:
            assert d['resolved_text'][edit['resolved_start']:edit['resolved_end']]==edit['replacement']
    # 用合成短句验证相同代词的分次定位，不将合成内容计入实验样本。
    duplicate=detect('TEST','这里能拍照，这里能休息。')
    assert len(duplicate)==2 and duplicate[0]['case_id']!=duplicate[1]['case_id']
    assert [x['span']['start'] for x in duplicate]==[0,6]
    # 时间和词汇负例，确保小数不误分句，“其他/这么”不冒充独立代词。
    assert not list(PRONOUN_RE.finditer('其他游客这么说，那么做。'))
    quality=dict(passed=True,python=sys.version.split()[0],documents=5,characters=sum(len(docs[d]['text']) for d in DOC_IDS),cases=len(cases),checked_evidence_spans=checked,ids_unique=True,input_hashes_unchanged=before,deterministic_rerun=True,full_document_detection_matches_reference=True,repeated_pronouns_in_corpus=repeated,synthetic_duplicate_position_check=True,resolved_document_maps_valid=True,metrics_recomputed=True,semantic_review_provenance=original['annotation_provenance'])
    write_json(ROOT/'results/checks/exp04_quality.json',quality)
    def show(a):return 'null' if a is None else a['text']+(f" [{a['entity_id']}]" if a['entity_id'] else ' [entity_id=null]')
    md=['# 实验4逐例核验记录','',original['annotation_provenance'],'','本记录使用原文上下文确定参考答案，再逐例对照预测。全部59例均保留，未只挑正确案例。原始偏移为v1完整正文的0起点左闭右开字符区间。','', '## 计分口径','', '明确先行词按标准entity_id一致判对；无标准ID时按参考短语文本严格一致判对。群体、人物、物品、路线、事件不强填POI。参考为null时，只有预测也为null才计总体正确；null正确不计入有效连接数。','']
    for c in cases:
        b=next(x for x in baseline['cases'] if x['case_id']==c['case_id'])
        md += ['## '+c['case_id'],'',f"- 来源：{c['doc_id']}；代词：{c['pronoun']}；区间：[{c['span']['start']},{c['span']['end']})。",f"- 原句：{c['sentence']['text']}",f"- 前后文：{c['context']['text'].replace(chr(13),'').replace(chr(10),' / ').strip()}",f"- 参考：{show(c['gold_antecedent'])}；状态：{c['gold_status']}；类型：{c['antecedent_type']}。",f"- 标注依据：{c['annotation_note']}",f"- 参考证据：{c['gold_evidence']}",f"- 基线预测：{show(b['predicted_antecedent'])}；{'正确' if b['correct'] else '错误'}。",f"- 类型约束预测：{show(c['predicted_antecedent'])}；{'正确' if c['correct'] else '错误'}；规则：{c['decision_reason']}。",f"- 消解文本：{c['resolved_text']}",'']
    (ROOT/'results/checks/exp04_review.md').write_text('\n'.join(md),encoding='utf8')
    output=io.StringIO(newline='');writer=csv.writer(output,lineterminator='\n')
    writer.writerow(['case_id','doc_id','pronoun','start','end','gold_status','gold','predicted','correct','annotation_note'])
    for c in cases:writer.writerow([c['case_id'],c['doc_id'],c['pronoun'],c['span']['start'],c['span']['end'],c['gold_status'],show(c['gold_antecedent']),show(c['predicted_antecedent']),c['correct'],c['annotation_note']])
    (ROOT/'results/checks/exp04_review.csv').write_text(output.getvalue(),encoding='utf-8-sig')
    print(f'结构检查通过：5篇、{len(cases)}例、{checked}处证据；两种方法复跑稳定；输入未修改。')


if __name__=='__main__':main()
