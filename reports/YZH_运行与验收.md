# YZH 实验 3/6 运行与验收

## 环境与顺序

代码使用 Python 3.11+ 语法；本次实际验证环境为 Python 3.12.14、NetworkX 3.4.2、Pillow 12.3.0，尚未在 Python 3.11 环境另行验证。入口均从项目根目录运行。

    python -m pip install -r requirements-yzh.txt
    python src/exp03_routes.py
    python src/exp03_evaluate.py
    python src/exp06_graph.py
    python src/exp06_verify.py
    python src/yzh_figures.py
    python -m unittest discover -s tests -v

图表默认使用 Windows 字体 C:/Windows/Fonts/msyh.ttc；其他系统执行 python src/yzh_figures.py --font /实际路径/支持中文的字体.ttf。

若只希望依赖安装到当前目录，可执行 python -m pip install --target .deps -r requirements-yzh.txt，并在 PowerShell 运行脚本前设置 $env:PYTHONPATH = (Join-Path (Get-Location) '.deps')。.deps 已被 Git 忽略。本次 NetworkX 使用该安装方式，Pillow 使用本地运行环境已有包。

## 当前验收记录

| 检查项 | 结果与证据 |
| --- | --- |
| 两个景区、两类官方格式 | 已实现钟点标题和时间段标题；4 条路线、30 步 |
| 官方与游客多维比较 | 地点 Jaccard、顺序 LCS、时间表达覆盖，见 exp03_comparison.md |
| 开发集参考顺序 | 参考 30 步，修复前匹配 29、修复后匹配 30；31 段原文证据有效，见 exp03_metrics.json |
| 正式图谱基本质量 | 83 节点、119 边；4 条步骤链顺序、连通、来源检查通过；无孤立节点 |
| 合成接口测试 | 9 项通过；仅验证代码与异常分支，不计为正式实验数据 |
| 图表 | 两张 PNG 已生成并查看：路线层级图、箱根图谱 |
| 名称归一化 | 已接入 DHT 正式目录，25/30 步对齐，5 步待确认，见 exp06_alignment.json |
| 多源融合实测 | 实体、路线、交通、时间融合通过；条件建议等待 FYH 的可选输入 |
| 人员验收 | 参考标注及接收样例待组员复核 |

## 上游到位后的操作

1. DHT 的 data/outputs/entities.json 已接收；FYH 后续放入 data/outputs/advice.json。版本须与 corpus.jsonl 的 v1 相同。若升级语料，需重建参考标注与全部证据偏移。
2. 从路线抽取开始复跑整条流程；程序会在唯一别名匹配时补齐 poi_entity_id，图谱会导入景点、交通、时间和条件建议。
   核心验收执行 python src/exp06_graph.py --require-entities，再运行 exp06_verify.py。包含条件建议的组内全链路验收执行 --require-complete；缺少建议时会明确返回失败。
3. 人工核对早云山/早云山站、箱根汤本/箱根汤本站、跨景区同名、父子景点及交通提及。不得仅因名称相似自动合并。
4. 检查图谱来源、关系覆盖、孤立节点和建议方向，更新报告与图表，再交给 FYH 实际读取样例确认。

参考顺序按原文名称记录，评价脚本使用 raw_poi_name；跨来源比较采用 poi_name 标准名称，不把别名变化计成抽取错误。当前核心代码、真实融合、图表及检查已达到仓库成果提交条件，参考标注仍待组员独立复核。
