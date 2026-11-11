> 本轮更新：实体exp02-v1.2、1395提及，共指39/59；4条路线33步，图谱v4为156节点218边，55项测试及7例新真实运行通过（本轮15次请求）。旧交接过程与数量保留历史；当前证据见reports/复核问题关闭清单.md及最新quality JSON。

# 实验7当前交接

当前图谱v3、模型deepseek-flash。agent_cases.json为本轮7个真实案例，18次完整运行加黄山两次单例回归共20次API请求，最终均partial。49项测试和真实链路验收通过。黄山旧提示结果保存在previous_attempts，历史v2真实记录完整保存在results/checks/history/agent_cases_5f0efd5058dc.json。

agent_revalidated_cases.json为独立的旧提案离线复验，real_llm=false、请求0，不混同真实运行。exp07_quality.json与exp05_07_acceptance.json明确执行模式与门禁。

用户私有.env仅保留本地，不入库。模型配置及更新步骤见reports/模型配置与更新.md。
