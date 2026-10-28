# YZH → FYH、DHT：实验 6 阶段交接

- 版本：schema_version=1.0、corpus_version=v1、graph_version=v1；当前 completion_status=route_stage。
- 交付：src/exp06_graph.py、src/exp06_verify.py、src/yzh_figures.py；data/outputs/graph.json、graph_nodes.csv、graph_edges.csv；reports/exp06_graph.md；results/figures/exp06_hakone_graph.png；质量与查询证据 exp06_quality.json。
- 输入：景区登记表和 routes.json。缺少 entities.json、advice.json，待 DHT/FYH 交付。
- 数量：62 节点、90 边，覆盖箱根与蓝山的 4 条路线；具体类型计数由 exp06_quality.json 提供。
- 依赖与命令：pip install -r requirements-yzh.txt；python src/exp03_routes.py；python src/exp06_graph.py；python src/exp06_verify.py；python src/yzh_figures.py。
- 输入输出例：R_S001_OFF_001_01 生成 N_ROUTE_R_S001_OFF_001_01；第 1 步生成 N_STEP_R_S001_OFF_001_01_001，由 HAS_STEP 连接，步骤再沿 VISITS 指向地点。
- 查询样例：① S001 沿 HAS_ROUTE → 2 条路线；② 官方箱根路线沿 HAS_STEP → 10 步；③ 大涌谷入向 VISITS → 3 个步骤。查询在 NetworkX 图上执行并保存真实返回值，见 exp06_quality.json。
- FYH 读取：json.load 后遍历 nodes/edges，或使用 exp06_verify.py 的 MultiDiGraph 加载方式。先检查 completion_status、missing_inputs；尚未接入建议时不要把空结果表述为“没有相关建议”。本次未改写 FYH 的 Agent 或工具代码。
- Schema 方向见 reports/exp06_graph.md。节点与边均有 source_refs，步骤和提取边的 attributes.evidence 可核对原文。不同路线的 NEXT_STEP 分开保留。
- 已知问题：未对齐地点的 entity_id 为 null；正式实体到位后阶段性地点节点 ID 可能变化，按标准实体 ID 或路线 ID 查询。没有可靠停留时长，不支持据此计算精确行程耗时；历史原文不代表当前开放/价格状态。
- 接收人样例读取与确认：待 FYH/DHT 完成，不代签。
