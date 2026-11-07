# 实验7交接说明

负责人：FYH。正式案例由真实qwen3.8-flash API调用生成，图谱为v2；当前数量、调用次数、图谱指纹、程序验收以agent_cases.json和exp07_quality.json为准。不代替组员独立验收。

本次最终7例通过，43项单元测试通过。正式案例累计20次API请求（16次全量+4次仅重跑AG_001）；全部最终为partial，表示不能保证满足全部旅行约束。AG_001原失败保存在previous_attempts，不能只统计重跑后的结果。

文件：src/exp07_agent.py、llm_client.py、graph_tools.py、exp07_verify.py，data/resources/exp07_scenarios.json，data/outputs/agent_cases.json，results/checks/exp07_quality.json、exp07_review.md，reports/exp07_agent.md。失败复跑记录另保留exp07_failed_live_run.json，不能与正式案例混算。

环境：Python 3.12.6，HTTP与配置加载使用标准库；调用外部OpenAI兼容Chat Completions接口。实际模型、服务和权限依赖本地配置，禁止提交.env。只复制示例一次，不覆盖已有配置：

```powershell
py -3.12 src/exp07_agent.py --check-config
py -3.12 src/exp07_agent.py --request "带孩子在箱根玩一天，给我路线和明确亲子建议"
py -3.12 src/exp07_agent.py
py -3.12 src/exp07_agent.py --cases
py -3.12 src/exp07_verify.py
```

配置为LLM_API_KEY、LLM_BASE_URL、LLM_MODEL；LLM_BASE_URL填服务商API根路径（例如/v1），不是/models。具体加载优先级、超时和脱敏规则见报告及.env.example。--check-config不联网，--cases真实调用模型并覆盖正式案例，有接口费用。

示例输入AG_001解析为S001/family/1天，调用query_routes和query_advice并使用实际返回生成方案。图谱没有完整耗时和整体亲子适用证据时partial，不冒充全部满足。AG_002老人建议无匹配、AG_003情侣雨天与两日覆盖不足、AG_004优胜美地无路线但有避峰建议；另3例处理景区缺失、互斥时长和未知景区。

工具返回统一status/data/message，合法状态ok/no_match/error。模型可选择工具、读取错误重试，最多6轮。原文来源、路线步骤和建议ID程序核验，估计与一般补充单独标注。API失败时返回脱敏错误，不用离线模板冒充真实生成。

已知限制：自由补充文本仍需语义审核；历史数据缺实时开放、距离和无障碍信息。明确景区即可检索，不能因缺少非必要日期/偏好而停止；未知景区和真实冲突仍需追问。独立语义验收由接收人实际跑样例后记录，不预先代签。

同图谱有error案例时可用`--cases --retry-errors`仅重跑失败项，保留旧尝试和累计调用数；图谱或场景变化时会拒绝复用。全部案例的成功路径和异常路径仍需验证，不以重试掩盖首次失败。
