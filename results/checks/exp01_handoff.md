# 实验1交接说明

负责人：DHT。接收人：YZH、FYH。状态：实验1交付文件已准备，通过GitHub分支及合并请求交接；组员验收待确认。填写后的Word报告仅留本地。

## 正式范围与版本

- `schema_version: "1.0"`，`corpus_version: "v1"`。
- S001 日本箱根，唯一主展示景区；S002 美国优胜美地国家公园；S003 澳大利亚蓝山国家公园。
- 每景区1份官方路线文档、5篇有效游客游记，18篇文档对应20个网页快照。
- 初轮备选语料不属于正式v1，不随本次交付上传。

## 组员如何接收

无需另外传送附件，本文件、数据和代码都在同一仓库中。实验1交付分支为`codex/exp01-preprocess`；合并前可在GitHub切换该分支查看，或在本地执行：

```powershell
git fetch origin
git switch --track origin/codex/exp01-preprocess
```

如果本地已存在此分支，使用`git switch codex/exp01-preprocess`，再执行`git pull --ff-only`。已在自己分支做开发的组员应先提交或妥善保存自己的改动。合并请求通过后，切到`main`并执行`git pull --ff-only`即可取得同一批交付数据，再继续各自实验。

YZH重点确认箱根官方路线的时间、景点与交通字段能被读取；FYH重点检查游客游记中条件建议的覆盖情况。两人都先运行下方读取样例或验证入口，有问题按文档ID反馈。只需在组内告知“实验1已上传，请先看本交接说明并跑样例”，不必重复发送整包文件。

## 文件与运行

```powershell
python -m pip install -r requirements.txt
python src/exp01_collect.py
python src/exp01_preprocess.py
python src/exp01_verify.py
```

实测Python 3.12.14、lxml 6.1.1；Python 3.11+为兼容目标，尚未在3.11实测。清洗和验证只用标准库。采集默认离线；首次从头下载可增加`--download`，需要网络，网页变化时应重新核对选择器和内容，不保证未来网页不变。

原始HTML在`.gitattributes`中关闭文本换行转换，防止Windows和其他系统之间下载后哈希不一致；正文片段固定使用LF。

| 文件 | 用途 |
| --- | --- |
| `data/raw/collection_plan.json` | 确定的URL、编码、正文XPath和预期匹配数量 |
| `data/raw/pages/` | 原始响应字节及采集时间、SHA-256元信息 |
| `data/raw/fragments/` | 按网站定位后的HTML正文片段 |
| `data/raw/source_manifest.json` | 18篇文档完整来源链及网页映射 |
| `data/processed/scenic_registry.json` | 景区与唯一主展示标记 |
| `data/processed/corpus.jsonl` | 后续实验使用的完整清洗正文 |
| `data/processed/corpus.csv` | Excel可读，含original_text对照 |
| `results/checks/exp01_sources.csv` | 18篇标题、网址和编号目录 |
| `results/checks/exp01_quality.json` | 数量、空值、重复、哈希及逐篇统计 |
| `results/checks/exp01_before_after.json` | 可追溯的清洗前后样例 |
| `results/checks/exp01_review.json` | 18篇相关性证据、字符位置与回归检查 |
| `reports/exp01_preprocess.md` | 已填写报告的可检索文字版 |

## 输入输出样例

输入是`S001_OFF_001_01.html`的公开官网快照。按计划定位正文后，预处理保留时间、交通和景点。读取样例：

```python
import json
from pathlib import Path
rows = [json.loads(line) for line in Path('data/processed/corpus.jsonl').read_text(encoding='utf-8').splitlines()]
doc = next(r for r in rows if r['doc_id'] == 'S001_OFF_001')
assert doc['text_type'] == 'official_route'
assert '7:30' in doc['text'] and '箱根神社' in doc['text']
print(doc['doc_id'], doc['scenic_name'], len(doc['text']))
```

本次返回`S001_OFF_001 日本箱根 3339`。总正文154930字符；箱根29795、优胜美地93085、蓝山32050。12项必填字段空值0/216，完全重复0、近重复候选0，8项清洗回归检查通过。字符数包含空格和换行。

## 接收注意事项

所有位置基于JSONL中v1的`text`，Python字符区间`[start,end)`，从0开始；不要自行清洗后继续使用旧偏移量。字段及编号遵守分工文档。所有记录的`raw_path`是正文片段，完整未清洗响应由来源清单中的`pages`追溯。

箱根官方行程有明确时刻；NPS谷地指南包含互相独立的备选步道；蓝山19km两日步道和中文一日游也应分别解析。官方文档计数不等于已完成路线抽取，不要将两个备选路线误拼成一条。

综合游记保留园外行程。优胜美地长篇美西行记较长，词频等统计应先选相关段落；新宿、悉尼、接驳镇区与公园内部景点需分开。英文与中文别名、繁简名称尚未做实体对齐。原文历史价格、路况和个人观点不是当前官方事实，需保留来源及时间属性。

接收人请实际读取上述样例，并确认版本、路径和所需字段；若发现问题，反馈具体`doc_id`、原句和预期结果。当前并未冒称任何组员已验收。
