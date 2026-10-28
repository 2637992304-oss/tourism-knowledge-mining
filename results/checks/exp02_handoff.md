# 实验2交接说明

负责人：DHT。接收人：YZH、FYH。实现、核验和报告已完成；代码、数据、图表与本说明作为实验2成果交付到main，组员接收尚未确认。实验报告仅留本地。

## 版本与运行

- `schema_version: "1.0"`，`corpus_version: "v1"`，词典资源`exp02-v1`。完整输入18篇、154930字符，实际相关游览及接驳抽取范围42911字符；没有修改实验1公共正文。
- 实测Python 3.12.14、Pillow 12.3.0。识别与检查只需标准库；绘图依赖Pillow和中文字体，Windows默认宋体，其他系统可设置`EXP02_FONT`为中文字体文件。
- 代码以Python 3.11+为兼容目标，尚未在3.11实测。无需密钥、LLM调用或联网服务。报告制作使用的Word排版环境不属于算法运行依赖。

```powershell
python -m pip install -r requirements.txt
python src/exp02_entities.py --variant baseline
python src/exp02_entities.py
python src/exp02_verify.py
python src/exp02_visualize.py
```

## 文件与结果

| 文件 | 作用 |
| --- | --- |
| `src/exp02_entities.py` | 三类实体词典／规则、偏移与稳定ID |
| `src/exp02_verify.py` | 结构、范围、引用、字符位置、确定性和24例评价 |
| `src/exp02_visualize.py` | 初版词频、优化词频及迭代对比彩色图 |
| `data/resources/exp02_lexicon.json` | 169条POI登记、19条交通规则、停用词及已知歧义 |
| `data/resources/exp02_scope.json` | 18篇原文的抽取起止、来源标记及范围说明 |
| `data/resources/exp02_review_reference.json` | AI辅助逐例核验的24例参考标签，84处提及 |
| `data/outputs/entities.json` | 327条目录记录，326条活跃、1条停用；1403次提及 |
| `results/checks/exp02_baseline_entities.json` | 可复现初版输出，包含泛词和重叠候选，禁止作为正式图谱输入 |
| `results/checks/exp02_*_stats.json`、`exp02_*_frequency.csv` | 两版统计、按实体及官方／游客分组的频次 |
| `results/checks/exp02_scenic_density.csv` | 每10000字符提及数，辅助比较不同长度文本 |
| `results/checks/exp02_quality.json` | 1403条原文位置、ID、引用及稳定复跑检查 |
| `results/checks/exp02_review.json`、`exp02_review.md` | 24例两版预测、原句、参考判断与逐例误漏 |
| `results/checks/exp02_pending_aliases.json` | 未确认名称、建议对齐及实际原文证据 |
| `results/figures/exp02_baseline_frequency.png` | 图2-1 初版词频 |
| `results/figures/exp02_entity_frequency.png` | 图2-2 优化后三类词频 |
| `results/figures/exp02_iteration_comparison.png` | 图2-3 两版数量与抽查指标 |
| `reports/exp02_entity_definitions.md` | 实体定义规范表、归一化与边界说明 |

Word报告`实验2报告.docx`及其完整文字稿`reports/exp02_entities.md`仅留本地，本次不上传报告内容。`reports/exp02_entity_definitions.md`作为实体数据接口规范单独交付。仓库中原有的报告章节占位文件不代表本次报告上传状态。

## 组员接收

在本地妥善保存自己的改动后更新main，再按上方命令运行检查或下方样例读取实体。当前工作已在main的成员可执行：

```powershell
git pull --ff-only origin main
python src/exp02_verify.py
```

在个人开发分支上的成员应先更新本地main，再将main合并进自己的分支；有冲突时核对具体文件，不覆盖其他成员的工作。YZH优先核对路线中的景点与实体ID，FYH优先核对条件建议中的实体关联。

| 景区 | 抽取字符 | POI提及 | 交通提及 | 时间提及 | 活跃实体 |
| --- | ---: | ---: | ---: | ---: | ---: |
| S001 箱根 | 10082 | 295 | 95 | 41 | 92 |
| S002 优胜美地 | 24494 | 424 | 64 | 107 | 148 |
| S003 蓝山 | 8335 | 262 | 62 | 53 | 86 |
| 合计 | 42911 | 981 | 221 | 201 | 326 |

## 读取样例

```python
import json
from pathlib import Path
payload = json.loads(Path('data/outputs/entities.json').read_text(encoding='utf-8'))
corpus = {r['doc_id']: r for r in map(json.loads, Path('data/processed/corpus.jsonl').read_text(encoding='utf-8').splitlines())}
catalog = {e['entity_id']: e for e in payload['entity_catalog'] if e.get('active', True)}
mention = next(m for m in payload['mentions'] if m['span']['doc_id'] == 'S001_OFF_001' and m['span']['text'] == '7:30')
span = mention['span']
assert corpus[span['doc_id']]['text'][span['start']:span['end']] == span['text']
print(mention['entity_id'], catalog[mention['entity_id']]['canonical_name'], span)
```

返回`S001_TIME_003 7:30`，span指向`S001_OFF_001`中实际“7:30”；实际字符起止以文件记录为准。来源标题和URL通过doc_id回到公共语料读取，不重复复制另一套来源。

## 接收重点与局限

1. YZH读取**正式**entities.json，过滤`active:false`。实体目录ID按景区隔离；同名跨景区不能按字符串直接合并。图谱与路线引用`entity_id`，原文证据使用`mentions[].span`；不要重新清洗正文后沿用旧位置。
2. FYH需了解POI含步道、站港、镇区及服务设施，并非全部在公园内部。根据`scope`区分园外接驳与景点；条件建议涉及未知名称时反馈原词、doc_id、区间和理由。
3. 不删除正式结果重建ID。正常复跑读取既有结果保留ID，停用目录项作为旧ID记录保留。目录拆分或合并需单独登记ID迁移，不能直接给旧ID换含义。
4. 抽样核验由AI辅助完成，24例是目的抽样开发诊断集，含用于优化的错误例；初版TP35/FP47/FN49，优化TP79/FP0/FN5。P/R/F1由实际计数计算，仅反映该样本，不能声称全语料准确率100%或学生已独立复核。
5. 五处样本漏识别为硫磺谷、Half Doom、Glacie Point、horsetail、每小时。名称待确认、频率规则待扩充；TIME尚未完整归并中文数量同义写法。抽取结果也不包含每一类可能的地点与季节表达。
6. 泛称缆车不能强行推断为某条具体线路。箱根汤本区域与站点暂用入口节点；Wentworth Falls裸名有镇区／瀑布歧义。这些粒度问题已在目录note与定义表中记录。
7. 提及不表示实际到访、当前开放或允许使用。例如“bicycles are prohibited”仍有自行车实体，但必须保留否定语境，不能生成“可以骑行”的事实。

本次交付不代表已经通知其他成员或完成组员验收；接收人实际运行样例后再确认。
