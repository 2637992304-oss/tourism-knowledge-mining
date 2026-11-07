# 实验6完整融合交接

FYH接管，接收DHT/YZH及全组。复用YZH提交60a7dda路线/实体融合、图和12项测试，保留其贡献；新增FYH条件建议、查询、完整布局及验证。

- 版本：schema_version=1.0、corpus_version=v1、entity_resource_version=exp02-v1.1、graph_version=v2。
- 正式输出：graph.json、graph_nodes.csv、graph_edges.csv；151节点、205边，4条路线30步、20个条件和20条建议。completion_status=fused，missing_inputs=[]，advice_availability=available。
- 代码：src/exp06_graph.py、exp06_verify.py、exp06_visualize.py、graph_tools.py。报告reports/exp06_graph.md，检查exp06_quality.json、exp06_alignment.json、exp06_visualization.json。
- 图：exp06_hakone_graph.png及同名HTML，箱根69节点、103边，所有节点类型和关系均展示。路线层级图仍由yzh_figures.py导出，该入口图谱部分已改为完整v2布局。
- 实测Python 3.12.6、NetworkX 3.4.2、Pillow 12.3.0；依赖汇总requirements.txt。

根目录运行：

```powershell
py -3.12 src/exp03_routes.py
py -3.12 src/exp03_evaluate.py
py -3.12 src/exp06_graph.py --require-complete
py -3.12 src/exp06_verify.py
py -3.12 src/yzh_figures.py
```

建议先生成正式advice.json；缺失、空数组和可用数据分别记录，输入齐全不等于语义覆盖完整。若输入被更新，先重构图再查询，工具会拒绝输入指纹过期的图谱。

v2的APPLIES_TO由建议指向POI/TRANSPORT/TIME，语义为原文证据涉及的实体，不等于必访、允许使用或人群适用性。其他关系方向、ID和来源约定见报告；NEXT_STEP始终是同路线步骤相邻链。

读取示例：GraphTools().query_routes('S001','morning')返回官方前4步；query_advice('S001',visitor_type='family')返回1条带原文与网址的亲子建议；query_advice('S003',condition_type='weather')返回1条完整雨天活动块。S001 elderly为no_match；缺advice输入则为error/missing_upstream。至少3个真实查询及完整返回保存在exp06_quality.json。

验收通过来源切片、唯一ID、活跃同景区实体、205条关系类型与方向、20条建议的完整实体引用、4条精确步骤链和无孤立节点。独立人员语义复核仍待进行；不代签DHT/YZH接收。

限制：无完整耗时/无障碍/实时状态；优胜美地只有建议网络，没有结构化路线。相关实体缺角色区分，不能用于生成无证据交通许可。数据及图表的数量以本次JSON和质量记录为准。
