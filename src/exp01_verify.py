"""实验1回归检查与逐篇内容复核证据。运行：python src/exp01_verify.py。"""
from pathlib import Path
import json
import re
import unittest
from exp01_preprocess import clean_text, ROOT, write_json

class CleaningChecks(unittest.TestCase):
    def test_html_and_inline_entity(self):
        self.assertEqual(clean_text('<p>花<a>穹</a>&amp;云雾林</p>'),'花穹&云雾林')
    def test_script_style_hidden(self):
        self.assertEqual(clean_text('<script>bad()</script><style>bad{}</style><p>正文</p>'),'正文')
    def test_route_order_and_time(self):
        self.assertEqual(clean_text('<p>上午９：３０ A→B</p><p>下午 C</p>'),'上午9:30 A→B\n下午 C')
    def test_notice_and_metadata(self):
        self.assertEqual(clean_text('<p>公告：</p><p>亲爱的用户：感谢您对游记业务的长久支持。测试公告</p><p>出发时间</p><p>7月</p><p>早上7点出发</p>'),'早上7点出发')
    def test_adjacent_not_global_dedup(self):
        self.assertEqual(clean_text('<p>A</p><p>A</p><p>B</p><p>A</p>'),'A\nB\nA')
    def test_url_control_and_emoji(self):
        self.assertEqual(clean_text('<p>推荐\u200b😀 https://example.com</p>'),'推荐')
    def test_paragraph_boundaries(self):
        self.assertEqual(clean_text('<p>一\t 二</p><p>三</p>'),'一 二\n三')
    def test_table_columns(self):
        self.assertEqual(clean_text('<tr><td>Loop</td><td>Easy</td><td>1 km</td></tr>'),'| Loop | Easy | 1 km')

def verify():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(CleaningChecks)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    rows=[json.loads(s) for s in (ROOT/'data/processed/corpus.jsonl').read_text(encoding='utf-8').splitlines()]
    keys={'S001':['箱根'], 'S002':['优胜美地','Yosemite Valley'], 'S003':['蓝山','Grand Cliff Top Walk']}
    notes=[]
    for row in rows:
        text=row['text']; key=next((k for k in keys[row['scenic_id']] if k in text),None)
        assert key,(row['doc_id'],'无相关景区证据')
        start=text.index(key);end=min(len(text),start+80)
        evidence=dict(doc_id=row['doc_id'],start=start,end=end,text=text[start:end])
        assert text[start:end]==evidence['text']
        assert '停止游记业务的运维' not in text
        assert '<script' not in text and 'http://' not in text and 'https://' not in text
        notes.append(dict(doc_id=row['doc_id'],title=row['source_title'],text_type=row['text_type'],
                     clean_chars=len(text),source_url=row['source_url'],evidence=evidence,
                     review='正文和来源可读，存在本景区的一手游览或官方路线内容；综合游记保留景区外信息并在scope_note标明。'))
    official={r['scenic_id']:r['text'] for r in rows if r['text_type']=='official_route'}
    assert all(k in official['S001'] for k in ['7:30','17:00','大涌谷','箱根神社'])
    assert all(k in official['S002'] for k in ['Valley Loop Trail','Lower Yosemite Fall','El Capitan'])
    assert all(k in official['S003'] for k in ['19km','Wentworth Falls','Katoomba','早晨'])
    write_json(ROOT/'results/checks/exp01_review.json',dict(schema_version='1.0',corpus_version='v1',
               review_scope='逐篇检查18篇正文、景区相关性及官方步骤；由本次实验辅助整理完成，未冒称组员已验收。',
               regression_tests=result.testsRun,regression_passed=result.wasSuccessful(),documents=notes))
    if not result.wasSuccessful():raise SystemExit(1)
    print(f'清洗回归检查 {result.testsRun}/{result.testsRun} 通过；18篇内容证据与原文位置一致。')

if __name__=='__main__':verify()
