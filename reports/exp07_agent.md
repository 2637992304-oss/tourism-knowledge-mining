# 实验7：旅游规划Agent

负责人：FYH。实现真实LLM约束解析、图谱函数工具、有限轮次决策闭环和命令行交互。正式运行记录为data/outputs/agent_cases.json；运行时间、模型、API请求数和图谱指纹以该文件为准，语义尚待组员独立验收。

## 架构与配置

src/llm_client.py使用标准库HTTP调用OpenAI-compatible Chat Completions，模型为本地实际配置的qwen3.8-flash。端点为服务商/v1/chat/completions，曾用简单响应实测路径；仅证明本次账户调用成功，不承诺其他服务商或模型兼容。

配置字段LLM_API_KEY、LLM_BASE_URL、LLM_MODEL来自根目录.env；进程环境变量覆盖文件，CLI明确实现加载，不依赖Python自动加载。配置不执行、不插值，密钥不进入日志/报告，.env被Git忽略。base_url应填API根路径/v1或完整/chat/completions，/models是模型列表，程序明确报错。默认90秒超时，临时网络错误及429/502/503/504最多重试一次，其他HTTP异常返回脱敏错误码；首次45秒超时的失败运行另保留。

协议依据[官方函数调用文档](https://developers.openai.com/api/docs/guides/function-calling)。本项目自行编排流程，未引入LangChain等框架；技术等价不影响课程功能要求。

## Prompt与流程

完整Prompt保存在src/exp07_agent.py的PARSER_PROMPT和PLANNER_PROMPT。未设置temperature以兼容模型默认参数；stream=false，约束解析用response_format=json_object。API私有reasoning_content丢弃，不落盘；保存可观察决策摘要。

1. LLM解析景区、人群、时段、天数、条件类型、缺失信息和冲突；字段值由程序校验。未知景区不替换为已知景区。
2. 景区缺失或互斥冲突时请求澄清，不生成无来源行程。
3. LLM根据约束自主选择query_routes/query_advice，程序只允许这两个只读工具和约定参数。工具真实读取graph.json，并核对其输入指纹。
4. 工具结果作为role=tool消息返回模型；错误可修正参数重试。最多6轮、每轮最多6个工具调用。无结果和缺上游分开处理。
5. 模型输出结构化方案，程序核对route_id、同一路线顺序、原地点名、原钟点、advice_id和doc_id。建议正文从已查询的真实结果回填，不接受改写后冒充原文。非法输出反馈有限错误码，在轮次内修正；不能生成成功结果时status=error。
6. 需要老人/亲子/情侣或总时长保证而图谱无证据时，强制partial，保留限制。一般补充建议和估计分别标记basis，不作为图谱事实。

统一工具返回status/data/message，status取ok/no_match/error。time_bucket仅表示原路线片段，不自动推导整日可行性。人群过滤只匹配明确标签，不把visitor_types=[]当general。

## 场景与真实结果

预先保存7类场景（exp07_scenarios.json）：箱根亲子一天、箱根老人上午、蓝山情侣两天雨天、优胜美地路线及避拥挤、缺景区、一天两天冲突、未知黄山。前4类实际查询图谱，后3类请求澄清。

最终正式7例均partial，累计20次API请求：全量运行16次，其中AG_001遇无效服务端响应；仅重跑该error案例增加4次，先前失败保存在该例previous_attempts，全部运行计数见run_attempts。模型无效响应格式也最多重试一次。partial不等于工具失败：完整人群适用性、总时长或路线覆盖不足，应如实报告部分满足。不能把7例写成“首次规划成功率100%”。程序核验关注约束解析、工具参数/返回、最终事实、引用、必要追问和状态；不替代人工旅游可行性审核。

典型AG_001：输入“带孩子在箱根玩一天”，LLM解析S001/family/1天，调用query_routes(S001)和query_advice(S001,visitor_type=family,condition_type=visitor_type)，返回官方10步历史路线及1条明确儿童建议。方案保留原文7:30—17:00钟点和S001_OFF_001来源，明确缺完整耗时、不能证明全路线适合儿童，因此partial。这个案例证明真实请求→模型解析→实际图谱→模型生成的闭环，不是固定模板。

AG_002老人建议no_match而上午路线有数据；AG_003有一般雨天建议但无couple专属建议与完整两日路线；AG_004无优胜美地路线而有避峰建议。不能用其他人群或景区替代满足请求。

## 真实失败与鲁棒性

恢复运行AG_003将可选time_bucket/condition_type/visitor_type传为空字符串；工具返回invalid_*，模型下一轮改为JSON null或省略后查询成功。恢复轨迹exp07_recovery_live_run.json保留这些真实错误，但该历史运行期间图谱曾重建，因此不用于最终精确指纹验收。根因是可选值序列化，改进为参数枚举、错误反馈和有限轮次；不把任意异常字符串吞成null。

失败复跑exp07_failed_live_run.json实际有12次API请求：AG_001/004因模型虚报非必要信息缺失而错误停止，AG_003在读取图谱后网络超时。现将“必须追问”限制为缺景区或真实冲突，缺日期/偏好等仍可查询；增加临时网络错误的一次重试及90秒默认超时。最终再次串行执行完整链路，不把早先成功或失败的日志替代本次验收。

另有真实配置问题：初次地址/models不能作为聊天根路径，已验证/v1并修正本地配置。网络超时、HTTP错误、未知工具、错误参数、模型虚构步骤、无工具直接回答及循环耗尽均有协议单测；合成响应只在tests内存中，不写正式案例。

局限：约束解析和自由补充文本仍有模型误判风险；程序核对结构化事实，但不证明所有自然语言语义。图谱缺老人/情侣证据、距离、完整耗时和实时状态，系统选择说明不足，无法凭LLM常识补出确定可执行性。不同模型对函数工具和JSON输出支持不同，换模型须重跑真实验收。

## 运行与验收

从根目录，先完成实验5、6：

```powershell
Copy-Item .env.example .env  # 仅首次，已有.env不要覆盖
# 在本地编辑.env，不要把密钥发到聊天或提交
py -3.12 src/exp07_agent.py --check-config
py -3.12 src/exp07_agent.py --request "带孩子在箱根玩一天，给我路线和明确亲子建议"
py -3.12 src/exp07_agent.py
py -3.12 src/exp07_agent.py --cases
py -3.12 src/exp07_verify.py
```

--check-config只校验配置，不声称联网成功。--cases会真实请求模型、产生接口费用并覆盖正式案例。交接见results/checks/exp07_handoff.md；全链路验收见exp05_07_acceptance.json。

若同一图谱某例为error，可执行`py -3.12 src/exp07_agent.py --cases --retry-errors`，只重跑失败案例，保留失败记录并累计API次数；图谱指纹或场景变化时拒绝复用旧案例。不能用手工删除失败记录代替复跑。
