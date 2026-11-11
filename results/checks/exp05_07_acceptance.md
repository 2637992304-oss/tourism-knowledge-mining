> 本轮最终结果：graph v4为156节点218边、33步骤、21建议；55项测试通过，本轮7例deepseek-flash真实调用15次、最终partial。R01—R13关闭证据见reports/复核问题关闭清单.md。下方保留原验收框架与历史记录，数值以最新JSON为准。

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

## 当前验收结果

2026年11月11日当前v3通过：49项测试、21条条件建议、153节点207边、7类deepseek-flash真实案例。累计20次API请求，最终7例均partial；黄山回归的早期结果保留。程序门禁和原文引用检查不代表全部旅游约束满足。

--offline重建并进行历史提案离线复验；--live重建并真实生成新案例；--audit-only仅核对已有当前真实案例。子进程固定UTF-8。来源映射与候选活动语义新增回归测试，冻结语料、实体与共指输出保持不变。
