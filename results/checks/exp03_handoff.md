# YZH → DHT、FYH：实验 3 交接

- 版本：schema_version=1.0，corpus_version=v1。
- 文件：src/exp03_routes.py、src/exp03_rules.py、src/exp03_evaluate.py、data/outputs/routes.json、reports/exp03_routes.md；指标与参考顺序见 exp03_metrics.json、exp03_gold.json；正式图见 results/figures/exp03_time_hierarchy.png。
- 命令：python src/exp03_routes.py；python src/exp03_evaluate.py。算法入口无额外依赖。
- 统计：2 景区、4 文档、4 路线、30 步、31 段原文证据。开发集匹配修复前 29/30、修复后 30/30；未处理其余 14 篇。
- 输入输出例：S001_OFF_001 的 7:30 标题生成 R_S001_OFF_001_01 第 1 步，目的地“箱根汤本”，time_text=7:30，time_bucket=morning；证据按正文 [start,end) 可回查。
- 已接收 DHT 的 entities.json（exp02-v1），30 步中 28 步对齐，2 步未唯一匹配；具体证据见 exp06_alignment.json。短句过滤漏抽已修复并保存前后指标；参考标注参与过开发，需组员复核与新增独立测试。
- DHT 已确认早云山/早云山站、箱根汤本/箱根汤本站的目录映射，本次据此对齐。新增 2 个待确认名称由 exp06_alignment.json 交回，不擅自改写 DHT 目录。
- 实际读取样例和接收确认：待 DHT/FYH 完成，不代签。
