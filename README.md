# 景区游览指南的程序性知识挖掘

数据挖掘课程三人小组项目：从官方路线与游客游记中提取实体、路线层级、共指和条件建议，融合知识图谱，并实现旅游规划 Agent。

- 仓库：[2637992304-oss/tourism-knowledge-mining](https://github.com/2637992304-oss/tourism-knowledge-mining)
- 克隆地址：`https://github.com/2637992304-oss/tourism-knowledge-mining.git`
- 成员：DHT、YZH、FYH。
- 分工、字段格式和交接标准：[三人分工.md](三人分工.md)。
- 正式提交截止：2026 年 11 月 20 日 24:00，提交方式以任务书为准。

## 当前状态

已搭建项目目录、实验入口、报告与交接模板。**七个实验入口目前均为待实现骨架，没有真实数据、抽取结果、图谱或可用 Agent。** 原任务书 PDF 和报告模板 DOCX 保留在根目录。

## 分工与运行顺序

| 实验 | 负责人 | 入口 | 主要输出 |
| --- | --- | --- | --- |
| 1 数据采集与预处理 | DHT | `src/exp01_preprocess.py` | `data/processed/scenic_registry.json`、`corpus.jsonl` |
| 2 实体识别 | DHT | `src/exp02_entities.py` | `data/outputs/entities.json` |
| 3 路线层级结构 | YZH | `src/exp03_routes.py` | `data/outputs/routes.json` |
| 4 共指消解 | DHT | `src/exp04_coreference.py` | `data/outputs/coreference.json` |
| 5 条件建议抽取 | FYH | `src/exp05_advice.py` | `data/outputs/advice.json` |
| 6 图谱融合与可视化 | YZH | `src/exp06_graph.py` | `data/outputs/graph.json` |
| 7 旅游规划 Agent | FYH | `src/exp07_agent.py` | `data/outputs/agent_cases.json` |

先完成实验 1 的公共语料；实验 2、3、4、5 可逐步并行；实验 6 汇总实体、路线和条件建议后交给实验 7。实验 4 结果可按需融入。实验 7 可提前验证模型调用并开发工具接口。

## 项目目录

```text
项目根目录/
├─ README.md                         # 项目入口与运行说明
├─ 三人分工.md                       # 职责、字段规范、交接检查
├─ requirements.txt                  # 依赖清单，当前为待确认模板
├─ .env.example                      # 模型配置示例，不含真实密钥
├─ .gitignore                        # 排除本地环境、密钥与缓存
├─ .gitattributes                     # 统一文本换行
├─ data/
│  ├─ README.md                      # 数据存放说明
│  ├─ raw/                           # 原文与来源记录
│  ├─ processed/                     # 景区登记表与清洗语料
│  └─ outputs/                       # 实验 2—7 的正式结果
├─ src/                              # 七个实验的待实现入口
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

当前 `requirements.txt` 仅包含待确认依赖注释；各模块负责人选定方法后补充实际依赖和版本，DHT 汇总兼容性。上面的安装命令目前不会安装任何实验依赖。

需要模型配置时，在本地复制示例，再填写自己的值：

```powershell
Copy-Item .env.example .env
```

`.env` 已被 Git 忽略。示例变量名为本组约定，具体 SDK 由 FYH 在实现时适配；Python 不会自动读取 `.env`，需由 FYH 明确实现加载方式。密钥通过本地配置提供，不写入源码或报告。

## 实验入口

从项目根目录执行，例如：

```powershell
.\.venv\Scripts\python.exe src/exp01_preprocess.py --help
```

当前 `--help` 可查看模块职责、输入与输出；不带参数运行会提示“尚未实现”并退出，不生成实验结果。各人实现后应同步更新本 README 中的实际运行命令、必要参数、依赖和检查方法。

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
