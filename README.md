# 景区游览指南的程序性知识挖掘

从官方指南和游客游记中抽取实体、路线、共指与条件建议，融合知识图谱，并通过模型与图谱工具实现旅游规划。成员：DHT、YZH、FYH。

## 当前状态

实验1–7代码与结构化成果已整合到main，实验2、4完整Markdown报告已补齐。最终小组Word报告、人工签署与版式验收仍待完成。课程截止为2026年11月20日24:00，以任务书为准。

2026年11月11日复核修复后：冻结v1语料仍为3景区18篇、20个网页快照；实体目录exp02-v1.1保留327个活跃实体、1403次提及；共指59例旧参考内部核验38/59。实验5当前exp05-v1.1有21条建议，图谱v3有153节点207边。

| 实验 | 负责人和交付 | 当前说明 |
| --- | --- | --- |
| 1 采集与预处理 | DHT，冻结语料、来源与快照 | 正文保留历史及部分外围内容，下游按范围处理 |
| 2 实体识别 | DHT，正式目录、证据、统计图与报告 | 24例开发诊断，不代表全语料准确率 |
| 3 路线层级 | YZH，4条来源序列30步 | 蓝山官方12项是候选活动，不是全部必经路线；箱根换乘位置与目的地分开 |
| 4 共指消解 | DHT，59例参考与预测、报告 | 不将未经复核的错误预测直接写入图谱事实 |
| 5 条件建议 | FYH，21条建议及32例评价 | E5_013修订为情境条件正例，当前参考21正关系、11负例 |
| 6 图谱与展示 | YZH基础，FYH完整融合，本轮复核修正 | v3，153节点207边；来源按字符证据映射到具体网页 |
| 7 Agent | FYH，模型调用、图谱工具与案例 | 当前离线复验通过；新图谱真实模型验证待配置 |

本轮49项测试和7例历史提案离线复验通过，见[当前验收](results/checks/exp05_07_acceptance.json)。acceptance_scope=offline、exp07_live_passed=false；不能称修复后真实模型验收通过。模型配置尚未提供，本轮没有新API请求。

原[data/outputs/agent_cases.json](data/outputs/agent_cases.json)保留旧图谱v2的真实调用记录（7例最终partial、累计20次请求），不能验收新v3图谱。新增[agent_revalidated_cases.json](data/outputs/agent_revalidated_cases.json)为当前工具对历史模型提案的离线重验证，real_llm=false、0次API请求。没有把旧日志的图谱指纹替换成新值。

## 环境与运行

推荐Python3.12。已在Python3.13.9执行本轮验证；Python3.11兼容目标未单独实测。依赖见requirements.txt（lxml、Pillow、NetworkX）。

首次获取：

```powershell
git clone https://github.com/2637992304-oss/tourism-knowledge-mining.git
cd tourism-knowledge-mining
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

已有仓库先保存自己的修改，再更新：

```powershell
git switch main
git pull --ff-only origin main
```

无需模型的完整离线重建、测试与历史提案复验：

```powershell
.\.venv\Scripts\python.exe src/exp05_07_verify.py --offline
```

此命令重建来源映射、实验3/5/6和图表，并核对当前离线案例。默认不联网。单独验收实验1/2/4：

```powershell
.\.venv\Scripts\python.exe src/exp01_verify.py
.\.venv\Scripts\python.exe src/exp02_verify.py
.\.venv\Scripts\python.exe src/exp04_verify.py
```

## 配置真实模型

在项目根目录复制.env.example为.env，只在本地填自己的API密钥、服务商兼容API根地址和可用模型标识。不要覆盖已有.env，不要把密钥发到聊天或提交Git。完整步骤见[模型配置与更新](reports/模型配置与更新.md)。

```powershell
Copy-Item .env.example .env
.\.venv\Scripts\python.exe src/exp07_agent.py --check-config
.\.venv\Scripts\python.exe src/exp07_agent.py --request "带孩子去箱根一天，有哪些路线和明确亲子建议？"
```

--check-config只检查字段；真实请求可能产生服务商费用。模型必须支持兼容Chat Completions的JSON输出与函数工具调用。配置完成后运行：

```powershell
.\.venv\Scripts\python.exe src/exp05_07_verify.py --live
```

--live将真实生成当前图谱的7个案例；程序在覆盖前自动将既有正式日志按内容指纹归档到results/checks/history。缺配置时保留旧日志，不生成假成功。部分失败可在同图谱使用--cases --retry-errors，保留旧尝试。图谱变动后不能复用旧指纹验收。

## 数据语义与局限

- 来源使用data/resources/source_page_spans.json逐网页映射，保持冻结正文与原偏移不变。跨页证据返回多个来源。
- 蓝山官方sequence_semantics=source_order_only，candidate_activity仅代表原文顺序候选；NEXT_STEP边不意味着必须连续游完。
- 箱根11:20步骤为早云山换乘位置，最终目的地大涌谷单独存放；保留历史原标题和时刻。
- 条件建议中的关联实体不等于必访或允许使用。历史价格、钟点、开放与路况均不保证现状。
- 无完整时长、距离、无障碍或全路线人群适用性证据。老人/情侣专属建议未覆盖；优胜美地尚无结构化路线。partial应保留约束不足说明。
- 样本与参考由AI辅助开发和复核，不声称组员独立盲标或泛化准确率100%。

## 报告与协作

[修复记录](reports/修复记录_20261111.md)列出本轮六类问题的处理方式。当前章节入口为reports/exp01_preprocess.md至reports/exp07_agent.md；总结见reports/summary.md。YZH旧提交稿与旧运行记录标明历史状态，不能引用其中旧数量替代当前结果。

目录：src为实现，data/raw为快照，data/processed为冻结语料，data/outputs为成果，data/resources为版本化规则与参考，results/checks为核验及交接，results/figures为图表。

后续开发请从最新main创建个人分支，通过PR核对接口后合并。保持实体ID含义和v1字符偏移，不在冻结语料上原地删字。完整分工见[三人分工](三人分工.md)。
