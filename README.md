# 景区游览指南的程序性知识挖掘

从官方指南和游客游记中抽取实体、路线、共指与条件建议，融合知识图谱，并通过模型与图谱工具实现旅游规划。成员：DHT、YZH、FYH。

## 当前状态

实验1–7代码与结构化成果已整合到main，实验2、4完整Markdown报告已补齐。最终小组Word报告、人工签署与版式验收仍待完成。课程截止为2026年11月20日24:00，以任务书为准。

2026年11月11日复核修复后：冻结v1语料仍为3景区18篇、20个网页快照；实体目录exp02-v1.2保留327个活跃实体、1395次提及；共指59例按修订参考内部核验39/59。实验5当前exp05-v1.1有21条建议，图谱v4有156节点218边。

| 实验 | 负责人和交付 | 当前说明 |
| --- | --- | --- |
| 1 采集与预处理 | DHT，冻结语料、来源与快照 | 正文保留历史及部分外围内容，下游按范围处理 |
| 2 实体识别 | DHT，正式目录、证据、统计图与报告 | 24例开发诊断，不代表全语料准确率 |
| 3 路线层级 | YZH，4条来源序列33步 | 蓝山官方12项是候选活动，不是全部必经路线；箱根换乘位置与目的地分开 |
| 4 共指消解 | DHT，59例参考与预测、报告 | 不将未经复核的错误预测直接写入图谱事实 |
| 5 条件建议 | FYH，21条建议及32例评价 | E5_013修订为情境条件正例，当前参考21正关系、11负例 |
| 6 图谱与展示 | YZH基础，FYH完整融合，本轮复核修正 | v4，156节点218边；来源按字符证据映射到具体网页 |
| 7 Agent | FYH，模型调用、图谱工具与案例 | 当前v4真实模型与离线复验均通过 |

本轮55项测试、当前v4的7个真实模型案例与历史提案离线复验通过，见[当前验收](results/checks/exp05_07_acceptance.json)。真实运行模型deepseek-flash，本轮15次请求，最终7例均partial；不表示全部旅行约束满足。

[agent_cases.json](data/outputs/agent_cases.json)是当前v4真实模型记录，包含全部工具轨迹及黄山两次早期提示结果。旧v2/v3真实日志按内容指纹完整归档至results/checks/history。另有[agent_revalidated_cases.json](data/outputs/agent_revalidated_cases.json)记录旧提案在v4的离线复验，real_llm=false、0次API请求；与新真实运行分开。

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

## R01至R13关闭状态

本轮已关闭R05、R06、R09、R10、R11、R12，先前七项修复保持。逐项证据见[关闭清单](reports/复核问题关闭清单.md)与[机器检查](results/checks/review_round2_closure.json)。

三姐妹指代参考已仲裁；五个名称已正式裁定，其中“水中神社”保留作者原词独立ID、不强认建筑身份。18篇语料的46个噪声片段通过保留偏移的排除层屏蔽。蓝山游客路线补入三段缆车活动，不伪造车站POI。建议实体区分条件/建议/比较/上下文角色及子句否定。

[报告分图索引](results/figures/report_panels/README.md)含19张清晰PNG，覆盖33个步骤与21条建议，可按图题插入Word；全图和可检索HTML另保留。
