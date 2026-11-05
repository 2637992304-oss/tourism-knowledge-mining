# FYH ↔ YZH 交接 README

整理人：YZH；接收人：FYH。整理日期：2026-11-05。

FYH 在实验 5 有可用结果后，把条件建议交给 YZH；YZH 完成实验 6 建议融合后，再把更新图谱交回 FYH，供实验 7 Agent 使用。可先交少量真实样例联调，不必等实验 7 完成。

本文依据仓库《三人分工》与现有图谱接口整理，不代表已经通知对方或完成接收确认。文中数量是本分支交接基线，后续以实际输出为准。

## 1. 已有基础与分工

| 成员 | 当前交接职责 |
| --- | --- |
| DHT | 维护公共语料、正式实体目录与实体 ID；新别名、实体粒度和缺失地点交 DHT 确认 |
| YZH | 维护实验 3 路线和实验 6 图谱，读取 FYH 建议后构建条件与建议关系 |
| FYH | 维护实验 5 条件建议与实验 7 Agent，提供建议数据、抽取说明和质量检查 |

YZH 已完成 4 条路线、30 个步骤，30/30 步完成正式实体对齐。实体路线图谱基线为 82 节点、118 边，包含景点、步骤、时间和交通，原文证据及步骤链检查通过，12 项测试通过。开发集参考标注仍需组员独立复核。

| 文件 | 用途与版本 |
| --- | --- |
| data/processed/corpus.jsonl | 全组共同正文；schema_version=1.0、corpus_version=v1 |
| data/processed/scenic_registry.json | 景区编号及名称；S001 箱根为主展示景区 |
| data/outputs/entities.json | DHT 正式目录；resource_version=exp02-v1.1，过滤 active:false |
| data/outputs/routes.json | YZH 的 4 条路线、30 个步骤 |
| data/outputs/graph.json | YZH 图谱；graph_version=v1 |
| results/checks/exp06_quality.json | 图谱检查与实际查询结果 |
| reports/YZH_运行与验收.md | 环境、完整运行顺序及限制 |

上述 YZH 成果在 yzh/routes-graph 分支。接收前先获取该分支最新提交；若已合入 main，可直接使用合入后的 main。不要覆盖自己未提交的修改。

## 2. FYH 需要交付什么

核心文件：**data/outputs/advice.json**，UTF-8 编码，顶层必须为对象：

- schema_version：字符串 "1.0"。
- corpus_version：字符串 "v1"，必须与公共语料及路线一致。
- advice：条件建议记录数组；确实没有有效样本时可为 []，同时说明检查范围与原因。

每条记录按以下字段交付：

| 字段 | 类型与要求 |
| --- | --- |
| advice_id | 唯一、稳定字符串，如 A_S001_VIS_001_0001；不要因排序改变而重编号 |
| scenic_id | 景区 ID，与来源文档和登记表一致 |
| doc_id | corpus.jsonl 中存在的文档 ID |
| condition_type | weather / visitor_type / time / crowding / other |
| condition_text | 原文条件，如“如果下雨”；保留必要语义 |
| visitor_types | 数组，值可为 elderly / family / couple / general / other；无法判断时 [] |
| suggestion_text | 条件对应的完整建议，不混入无关段落 |
| related_entity_ids | DHT 活跃目录中已确认的实体 ID 数组；无法确定时 [] 并反馈 |
| evidence | 原文证据数组，每项包含 doc_id、start、end、text |
| method | 实际抽取方法，如 rule、llm、manual 或组合说明 |

evidence 的 start 从 0 开始、end 不包含在内，按 Python 字符计数，并满足：

    corpus_text[start:end] == evidence["text"]

位置基于完整清洗正文，不基于网页、分词结果或插入括注后的消解全文。条件和建议跨句时提供足够证据覆盖二者。不能把“不存在建议数据”与“已检索但没有匹配”混为同一种状态。

随数据交一份 **results/checks/exp05_handoff.md**，写明版本、抽取范围、运行命令、依赖、记录数量、条件分类、去重方法、真实输入输出样例、质量检查及已知问题。已有报告或检查文件可用链接引用，避免复制出多套版本。

## 3. 真实原文格式样例

下面仅展示交接格式，已核对 v1 原文位置。它不是 FYH 已交付的正式结果，也没有写入正式 advice.json。正式交付时须自行核验、去重并按已有编号分配 ID；method 应填写实际方法。

S001_OFF_001 中该句位于箱根雕刻森林美术馆的介绍段，“馆区”关联 S001_POI_007。此关联依赖上下文，不能只凭“馆区”二字推广到其他记录。

```json
{
  "schema_version": "1.0",
  "corpus_version": "v1",
  "advice": [
    {
      "advice_id": "A_S001_OFF_001_0001",
      "scenic_id": "S001",
      "doc_id": "S001_OFF_001",
      "condition_type": "other",
      "condition_text": "如果您感到疲劳",
      "visitor_types": [],
      "suggestion_text": "还可以在馆区内泡足汤小憩",
      "related_entity_ids": ["S001_POI_007"],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 1135,
          "end": 1156,
          "text": "如果您感到疲劳,还可以在馆区内泡足汤小憩。"
        }
      ],
      "method": "manual_example"
    }
  ]
}
```

## 4. 在哪个阶段交付

| 阶段 | FYH 交付 | YZH 随后完成 |
| --- | --- | --- |
| 实验 5 可用初版 | 少量已核对的真实建议；优先 S001 箱根，数量按实际语料，不凑样本 | 检查版本、字段、ID、证据与实体关联，打通一次融合 |
| 实验 5 正式版 | 完整 advice.json、exp05_handoff.md、质量记录与未对齐问题 | 融合正式建议，复查关系、去重及来源，更新图谱、查询证据和报告 |
| 实验 7 联调 | FYH 用更新后的真实图谱实现查询工具并反馈问题 ID | 配合定位图谱字段、关系与来源问题 |

建议可来自多个景区。S001 优先用于完整演示，其余景区保留 scenic_id 隔离。没有足够有效条件句时如实说明；本交接不额外规定记录数。

“建议”“可以”本身不足以证明存在条件。同一条件含多项独立建议可拆分，保留完整语义并去重。不要把历史天气、价格或开放情况作为当前事实。普通无条件建议可以另存分析文件。

## 5. 数据到位后的运行与验收

FYH 提交数据后，YZH 在项目根目录执行：

```powershell
python -m pip install -r requirements-yzh.txt
python src/exp03_routes.py
python src/exp03_evaluate.py
python src/exp06_graph.py --require-complete
python src/exp06_verify.py
python src/yzh_figures.py
python -m unittest discover -s tests -v
```

--require-complete 检查实体与建议输入齐备；不能单凭该命令成功就判定建议语义正确。还需核对：

图表注意：现有 yzh_figures.py 仅布局路线、地点、交通和时间节点。正式建议到位后，YZH 需补齐 CONDITION/ADVICE 节点的布局，再执行上列图表导出步骤；不能直接把当前路线图称为含条件建议的最终图。

- 版本、文档和景区引用一致，advice_id 唯一。
- 所有证据能切回原文，条件与建议有完整支撑。
- related_entity_ids 有效、活跃且不跨景区；未知 ID 不用猜测补齐。
- 没有重复碎片、错误否定或把可选建议变成必经路线。
- CONDITION → ADVICE 的 TRIGGERS 方向正确，ADVICE → POI 的 APPLIES_TO 关联正确。
- 有实体关联的样例能在图谱中查到，并提供至少一个可核对的真实建议查询结果。

当前构建器仅把 related_entity_ids 中的 POI 连为 APPLIES_TO；非 POI 引用不会生成该边。需要交通、时间等建议关系时先与 YZH 对齐 Schema，避免假定现有构建器已支持。

样例联调期间 YZH 的临时输出不替代正式全量图谱。若文件已提交但 advice=[]，需明确“输入已接入、有效建议为零”，不得将状态 fused 解释为建议覆盖完整。

## 6. YZH 交回 FYH 的内容

交回更新后的 graph.json、graph_nodes.csv、graph_edges.csv、图谱质量与查询记录、exp06_handoff.md；同步说明输入版本、实际数量、缺失关系和已知限制。

图谱保留以下关系：

| 关系 | 方向 |
| --- | --- |
| HAS_ROUTE / HAS_STEP | 景区 → 路线 / 路线 → 步骤 |
| NEXT_STEP / VISITS | 同一路线前步 → 后步 / 步骤 → 地点 |
| AT_TIME / USES_TRANSPORT | 步骤 → 时间 / 步骤 → 交通 |
| HAS_ADVICE | 景区 → 建议 |
| TRIGGERS / APPLIES_TO | 条件 → 建议 / 建议 → 已确认景点 |

FYH 先检查 graph.json 的 completion_status、missing_inputs、corpus_version 和 graph_version。entity_route_fused 表示实体路线已融合但建议尚未接入；fused 表示两类输入齐备，仍须结合质量记录判断覆盖。

按组内分工，FYH 在实验 7 实现真正读取图谱的 query_routes(scenic_id, time_bucket=None) 和 query_advice(scenic_id, visitor_type=None, condition_type=None)。统一返回 status、data、message，status 为 ok / no_match / error；缺上游数据时应明确说明，不能宣称“没有相关建议”。路线存在不等于已证明适合老人或亲子。

## 7. 交接确认

- FYH：提交分支/提交号、数据版本、数量、命令和已知问题。
- YZH：实际读取一条记录，验证原文、实体和图谱关系，记录通过或具体问题 ID。
- FYH：实际读取更新图谱，运行一条路线查询和一条建议查询，确认返回及来源。

任一步有问题，提供 doc_id / advice_id / entity_id、原文证据、实际行为和预期行为。双方接收确认由实际运行后填写，不预先代签。
