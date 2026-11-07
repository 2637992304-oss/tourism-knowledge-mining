# 实验5—7验收清单

接管：FYH；复用 YZH 提交 `60a7dda` 的实验3/6及测试，不改实验1/2/4数据。课程要求来自根目录任务书第10—15页；以下证据只有实际运行后才算通过。

| 要求 | 实现位置 | 结果证据 | 验证方式 |
| --- | --- | --- | --- |
| 5：批量条件/建议边界、规则优先级、多分句 | src/exp05_advice.py | advice.json、报告 | 先存参考再预测；正负例及边界逐例比较 |
| 5：分类、来源、稳定ID、去重 | 同上、exp05_verify.py | exp05_quality.json、review.md、频次图 | 全量证据切片、同景区活跃实体、去重检查 |
| 5：误抽/漏抽/样本稀疏 | exp05_reference.json、报告 | 两版评价及真实失败 | 报告分子分母、选样范围、AI标注局限 |
| 6：复用路线实体，融合条件建议 | exp06_graph.py | graph.json、CSV | 版本、边端点、关系方向、来源、活跃实体 |
| 6：图模式与实际图结构 | exp06_verify.py | exp06_quality.json | NetworkX及步骤链、建议关联检查 |
| 6：完整主展示图、3个以上查询 | exp06_visualize.py、graph_tools.py | PNG、查询记录 | 查看实际图；查询回到原文 |
| 7：真实LLM接入及配置加载 | llm_client.py、exp07_agent.py | agent_cases.json | 实际API调用；无配置明确阻塞 |
| 7：真实图谱工具Schema与过滤 | graph_tools.py | 查询及测试记录 | ok/no_match/error、缺输入、未知参数 |
| 7：约束解析/决策/工具/回答闭环 | exp07_agent.py | 带工具轨迹的真实案例 | 参数校验、有限轮次、来源约束 |
| 7：至少3类约束和异常场景 | exp07_scenarios.json、exp07_verify.py | agent_cases.json、review | 真实运行与合成协议测试严格分开 |
| 5/6/7：报告、交接、真实失败 | reports/exp05、06、07、summary.md | 各handoff | 数字/版本/命令与本次结果一致 |
| 全链路及上游不变 | exp05_07_verify.py | exp05_07_acceptance.json | 完整命令、哈希、图表清单、真实运行状态 |

## 证据使用说明

- 已整合原分支；原12项测试保留，新增边界/引用/工具/模型协议回归。当前实际运行数量和输出见exp05_07_tests.json。
- 已修正用户本地base_url并真实调用qwen3.8-flash。最终正式7例、图谱指纹和门禁状态以exp07_quality.json及exp05_07_acceptance.json为准；历史失败/恢复运行不替代最终门禁。
- 默认命令`py -3.12 src/exp05_07_verify.py`离线复建并核对已有真实案例；加`--live`串行重跑真实模型，避免图谱重建与场景查询并发。
- 字符坐标、输入指纹、分类和结构由程序全量核对；参考语义与自由补充文本由AI辅助核对，尚未代替组员独立复核。不把审校后同批一致性或partial状态写成泛化准确率或全部约束满足。
