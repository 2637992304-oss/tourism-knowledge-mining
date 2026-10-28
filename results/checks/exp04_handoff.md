# 实验4交接说明

负责人：DHT。接收人：YZH、FYH。实验4初次成果已由main的c258291交付；YZH在其分支的exp06_exp04_receipt.md记录了程序接收检查，FYH接收及组员独立语义复核仍待确认。

## 输入与版本

- 输入：`data/processed/corpus.jsonl`、`data/outputs/entities.json`。公共语料 `schema_version=1.0`、`corpus_version=v1`，实验2实体目录编号不改。
- 实验2当前资源版本为`exp02-v1.1`：补充姥子缆车站别名及独立野餐区。已同步重跑实验4的基线、正式预测与验证，更新实体输入SHA-256；59例预测、指标及404处证据检查数量不变。基线候选轨迹中的两处旧“缆车”候选改为完整站点证据，不能误称所有中间候选未变化。此次实测Python 3.13.9；JSON输出固定LF以保持跨平台输入指纹一致。
- 5篇游记：`S001_VIS_001`、`S001_VIS_003`、`S002_VIS_005`、`S003_VIS_001`、`S003_VIS_005`；三个景区均覆盖，共6053个完整正文字符。
- 字符位置：完整v1正文的Python字符串索引，0起点，`end`不含在内。每个`case_id`含来源文档ID及代词起点。

## 交付文件

| 用途 | 文件 |
| --- | --- |
| 实现 | `src/exp04_coreference.py` |
| 核验入口 | `src/exp04_verify.py` |
| 全部59例AI辅助语义参考 | `data/resources/exp04_reference.json` |
| 59例参考与预测 | `data/outputs/coreference.json` |
| 带位置映射的5篇消解示例全文 | `data/outputs/coreference_resolved_documents.json` |
| 最近实体基线 | `results/checks/exp04_baseline.json` |
| 指标及结构检查 | `results/checks/exp04_metrics.json`、`exp04_quality.json` |
| 全部逐例审阅与可筛选记录 | `results/checks/exp04_review.md`、`exp04_review.csv` |

报告章节文字 `reports/exp04_coreference.md` 与按模板填写的根目录 `实验4报告.docx` 仅保留本地，本次不上传。

## 运行与依赖

在项目根目录依次运行：

```powershell
python src/exp04_coreference.py --variant baseline
python src/exp04_coreference.py
python src/exp04_verify.py
```

实验4仅依赖Python标准库，无联网、模型或密钥。实测Python 3.12.14；以3.11+为兼容目标，未在3.11实测。输出路径默认固定，复跑应稳定。需先有实验1、2的正式结果。

## 数量、例子与判定

检测59处，参考中明确先行词48例、歧义2例、照片／现场指示5例、非回指4例。正式规则正确连接32/48=66.67%，正确保留无明确先行词6/11=54.55%，总体准确率(32+6)/59=64.41%，覆盖率47/59=79.66%。基线总体准确率16/59=27.12%。这是目的选样的开发／核验集合内比较，不能外推到全语料。

输入例：`S001_VIS_003`的“因为我订了桃源台的酒店,所以出游的方向就那里”，代词位置`[270,272)`；输出`CR_S001_VIS_003_00270`预测`桃源台`，关联`S001_POI_010`，与参考一致。消解示例用括注显示“那里（指：桃源台）”，保留原句和原始位置。

## 接收检查与已知问题

读取`coreference.json`核对顶层版本和`cases`，任选`CR_S001_VIS_003_00270`检查`span`、`gold_evidence`和`predicted_evidence`能切回语料；运行核验脚本后，应显示5篇、59例、404处证据位置通过。实验4非图谱融合强制前置；若下游采用括注文本，需保留原句与case映射，并人工审查`correct=false`的候选。

真实失败`CR_S002_VIS_005_01740`把“这个水库”错连到Tioga Road，参考为Hetch Hetchy，显示插入比较对象干扰最近实体规则。`CR_S003_VIS_001_00981`为“这里被叫做凯蒂的宴客厅”的后指，前向搜索弃答。部分图像指示或群体边界无法唯一判断，保持null。参考标签由AI辅助逐例阅读，未由组员独立复核；尤其歧义样本的判断仍有主观性。接收人需抽查并反馈争议ID，不能把这批结果未经核验直接当成图谱事实。
