# YZH → DHT、FYH：实验 3 交接

- 版本：schema_version=1.0，corpus_version=v1。
- 文件：src/exp03_routes.py、src/exp03_rules.py、src/exp03_evaluate.py、data/outputs/routes.json、reports/exp03_routes.md；指标与参考顺序见 exp03_metrics.json、exp03_gold.json；正式图见 results/figures/exp03_time_hierarchy.png。
- 命令：python src/exp03_routes.py；python src/exp03_evaluate.py。算法入口无额外依赖。
- 统计：2 景区、4 文档、4 路线、30 步、31 段原文证据。开发集匹配修复前 29/30、修复后 30/30；未处理其余 14 篇。
- 输入输出例：S001_OFF_001 的 7:30 标题生成 R_S001_OFF_001_01 第 1 步，目的地“箱根汤本”，time_text=7:30，time_bucket=morning；证据按正文 [start,end) 可回查。
- 已知问题：实体目录尚未交付，poi_entity_id 均为 null；短句过滤曾漏抽山地文化啤酒公司，现已修复并保存前后指标；参考标注参与过规则开发，需组员复核与新增独立测试。
- 给 DHT 的名称反馈：R_S001_VIS_001_01 第 1 步“早云山”和 R_S001_OFF_001_01 第 6 步“早云山站”；官方第 1、2 步“箱根汤本/箱根汤本站”。请按站点、地域语义确认合并与否，勿只按字面相似度处理。
- 实际读取样例和接收确认：待 DHT/FYH 完成，不代签。
