# 景区游览指南的程序性知识挖掘

数据挖掘课程三人小组项目：从官方路线与游客游记中提取实体、路线层级、共指和条件建议，融合知识图谱，并实现旅游规划 Agent。

- 仓库：[2637992304-oss/tourism-knowledge-mining](https://github.com/2637992304-oss/tourism-knowledge-mining)
- 克隆地址：`https://github.com/2637992304-oss/tourism-knowledge-mining.git`
- 成员：DHT、YZH、FYH。
- 分工、字段格式和交接标准：[三人分工.md](三人分工.md)。
- 正式提交截止：2026 年 11 月 20 日 24:00，提交方式以任务书为准。

## 当前状态

**本工作分支已整合实验3，并由FYH接管实验5、6、7。** 实验1/2/4来自DHT的main交付，路线与原图谱来自YZH提交60a7dda；本分支不自动推送或表示已合入远端main。正式语料为箱根（主展示）、优胜美地、蓝山，每景区1份官方文档和5篇游记，共18篇、20个网页快照。实体exp02-v1.1有327个活跃实体、1403次提及；共指59例内部核验38/59。当前新增20条条件建议，复用4条30步路线，融合图谱v2为151节点/205边。Agent已接入真实模型并提供7类场景，最终运行结果与验证状态见[实验7核验](results/checks/exp07_quality.json)。原任务书、报告模板、冻结语料及实验1/2/4输出保持不变；各模块AI辅助标注尚待组员独立复核。

从项目根目录运行：

```powershell
python src/exp01_collect.py
python src/exp01_preprocess.py
python src/exp01_verify.py
```

采集与正文定位使用`lxml==6.1.1`，默认读取已保存的本地网页；只有缺少快照并显式增加`--download`时才联网。离线预处理和验证只使用Python标准库。本次实测Python 3.12.14；代码兼容写法以3.11+为目标，尚未在3.11实测。完整输出、来源与局限见[实验1交接说明](results/checks/exp01_handoff.md)。

## 分工与运行顺序

| 实验 | 负责人 | 入口 | 主要输出 |
| --- | --- | --- | --- |
| 1 数据采集与预处理 | DHT | `src/exp01_preprocess.py` | `data/processed/scenic_registry.json`、`corpus.jsonl` |
| 2 实体识别 | DHT | `src/exp02_entities.py` | `data/outputs/entities.json` |
| 3 路线层级结构 | YZH | `src/exp03_routes.py` | `data/outputs/routes.json` |
| 4 共指消解 | DHT | `src/exp04_coreference.py` | `data/outputs/coreference.json` |
| 5 条件建议抽取 | FYH | `src/exp05_advice.py` | `data/outputs/advice.json` |
| 6 图谱融合与可视化 | FYH接管，复用YZH基础 | `src/exp06_graph.py` | `data/outputs/graph.json` |
| 7 旅游规划 Agent | FYH | `src/exp07_agent.py` | `data/outputs/agent_cases.json` |

先完成实验 1 的公共语料；实验 2、3、4、5 可逐步并行；实验 6 汇总实体、路线和条件建议后交给实验 7。实验 4 结果可按需融入。实验 7 可提前验证模型调用并开发工具接口。

## 项目目录

```text
项目根目录/
├─ README.md                         # 项目入口与运行说明
├─ 三人分工.md                       # 职责、字段规范、交接检查
├─ requirements.txt                  # lxml、Pillow、NetworkX实际依赖
├─ .env.example                      # 模型配置示例，不含真实密钥
├─ .gitignore                        # 排除本地环境、密钥与缓存
├─ .gitattributes                     # 统一文本换行
├─ data/
│  ├─ README.md                      # 数据存放说明
│  ├─ raw/                           # 原文与来源记录
│  ├─ processed/                     # 景区登记表与清洗语料
│  └─ outputs/                       # 实验 2—7 的正式结果
├─ src/                              # 实验1—7入口、图谱工具和全链路验证
├─ reports/                          # 各实验章节和总结反思模板
└─ results/
   ├─ figures/                       # 图表与运行截图
   └─ checks/                        # 检查结果与交接模板
```

空目录通过 `.gitkeep` 保留；该文件不属于实验数据。正式输出由负责人运行代码生成，不使用空 JSON 冒充已完成结果。

## 环境准备（Windows PowerShell）

约定使用 Python 3.11。首次加入项目时克隆仓库；已有本工作目录的成员直接使用当前目录，不要再在目录内重复克隆。

```powershell
git clone https://github.com/2637992304-oss/tourism-knowledge-mining.git
cd tourism-knowledge-mining
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

当前requirements.txt汇总lxml 6.1.1、Pillow 12.3.0、NetworkX 3.4.2。实验5抽取和实验7 HTTP/配置加载只使用标准库。此次接管实际验证Python 3.12.6；本机可使用`py -3.12`，Python 3.11尚未另行实测。

需要模型配置时，在本地复制示例，再填写自己的值：

```powershell
Copy-Item .env.example .env
```

`.env`被Git忽略，已有配置不要覆盖；只在本地.env填写密钥，不在.env.example填写。Agent已明确实现根目录.env加载，进程环境变量优先。需要LLM_API_KEY、LLM_BASE_URL、LLM_MODEL，base_url填兼容API根路径（如/v1），不要填/models。模型支持Chat Completions函数工具和JSON输出后才能运行；已验证本地配置的qwen3.8-flash，换模型应重新验收。

## 实验入口

从项目根目录执行，例如：

```powershell
.\.venv\Scripts\python.exe src/exp01_preprocess.py --help
```

实验1不带参数即可离线生成结果。实验2从根目录执行：

```powershell
python src/exp02_entities.py --variant baseline
python src/exp02_entities.py
python src/exp02_verify.py
python src/exp02_visualize.py
```

实验2采用离线领域词典和时间规则，在18篇文档的42911字符相关范围内处理，位置始终对应v1完整正文。正常复跑读取既有实体目录维持ID，请勿删除正式输出后重新编号。实测Python 3.12.14、Pillow 12.3.0；绘图默认用Windows宋体，其他系统可通过`EXP02_FONT`设置中文字体。完整数据接口、范围、24例核验和局限见[实验2交接说明](results/checks/exp02_handoff.md)，三类实体规范见[定义表](reports/exp02_entity_definitions.md)。核验由AI辅助完成，抽样诊断指标不代表全语料准确率。

实验4从项目根目录运行：

```powershell
python src/exp04_coreference.py --variant baseline
python src/exp04_coreference.py
python src/exp04_verify.py
```

实验4只使用Python标准库，原交付实测Python 3.12.14。参考标签由AI辅助逐例阅读原文形成，未由组员独立复核；59例准确率只代表这5篇目的选样内部结果。完整字段与局限见[实验4交接说明](results/checks/exp04_handoff.md)。本次接管不重写实验4结果。

实验5—7从项目根目录运行：

```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 src/exp05_07_verify.py
py -3.12 src/exp07_agent.py --request "带孩子在箱根玩一天，给我路线和明确亲子建议"
py -3.12 src/exp07_agent.py
```

默认全链路脚本离线重建实验3/5/6、运行测试，并核对已有真实Agent案例；图谱或来源变化使旧案例过期时会明确失败。需要重新真实调用模型并覆盖正式案例时运行`py -3.12 src/exp05_07_verify.py --live`；只有核验现状可使用`--audit-only`。真实API调用有接口费用，7场景可能运行数分钟。各模块单独命令及已知局限见[实验5交接](results/checks/exp05_handoff.md)、[实验6交接](results/checks/exp06_handoff.md)、[实验7交接](results/checks/exp07_handoff.md)。

图表使用Windows微软雅黑，可用MINING_FONT或绘图入口--font指定中文字体。完整箱根图及节点边检索在results/figures/exp06_hakone_graph.png/html。Agent的partial表示数据无法保证全部约束，不能把普通路线当成已证实适合老人或亲子；估计和一般补充建议单独标记，历史资料不代表实时开放或价格。

同一图谱下仅有个别error案例，可使用`py -3.12 src/exp07_agent.py --cases --retry-errors`继续；失败尝试和累计调用数会保留，图谱或场景变更时拒绝复用。当前正式7例、累计20次API请求（含一次失败案例重跑），43项测试通过；详细门禁见results/checks/exp05_07_acceptance.json。

## 三人协作

1. 先阅读分工文档，并确认景区、公共语料和数据格式。
2. `main` 保存已经检查、可交接的内容；个人开发使用 `dht/任务名`、`yzh/任务名`、`fyh/任务名` 分支。
3. 修改自己的模块；公共语料和实体目录由 DHT 更新，其他成员提交具体反馈。
4. 提交时只加入本次修改的文件，避免把个人配置或无关文件一起上传。共享结果要能追溯来源和版本。
5. 将分支推送到仓库后发起 Pull Request（合并请求），由相关接收人核对样例和接口后合并。
6. 交接时复制 `results/checks/_handoff_template.md` 为对应的 `expXX_handoff.md` 并填写，不能只发截图。

首次开始自己的任务时，例如 DHT：

```powershell
git switch main
git pull --ff-only origin main
git switch -c dht/exp01-preprocess
```

只有首次上传后远端存在 `main`，上述拉取命令才可使用。分支前缀以实际负责成员为准。

## 数据与结果约定

- 使用 UTF-8；JSON 字段、枚举、ID 和字符位置严格遵守分工文档。
- 不再清洗已冻结的语料后沿用旧位置；公共语料变动由 DHT 升级版本并通知受影响成员。
- 保留来源，区分官方与游客信息；无依据的时间、路线适用人群等不能写成确定事实。
- 报告、代码、结构化结果应一致。每人提供真实失败案例和改进分析，最终汇入 `reports/summary.md`。
