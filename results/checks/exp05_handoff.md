# 实验5交接说明

负责人与接收：FYH负责抽取并接管图谱/Agent。正式交付为21条条件建议；参考和修正均AI辅助，组员独立语义验收待进行。

- 版本：schema_version=1.0、corpus_version=v1、resource_version=exp05-v1.1；实体exp02-v1.1。
- 文件：data/outputs/advice.json、src/exp05_advice.py/exp05_verify.py/exp05_visualize.py、exp05_reference.json、exp05_corrections.json、exp05_quality.json、exp05_review.json/md、exp05_extraction_audit.json、exp05_advice_statistics.png、reports/exp05_advice.md。
- 范围：18篇完整正文中的42688字符相关区间，不是154930字符全量抽取。复用实验2范围并排除S003_VIS_004园外酒评。
- 数量：S001=9、S002=6、S003=6；weather=2、visitor_type=2、time=1、crowding=1、other=15。family=2，未明确19，无明确elderly/couple。
- 依赖：实测Python 3.12.6、Pillow 12.3.0；抽取/检查仅标准库；图可用MINING_FONT或--font指定中文字体。

根目录依次运行：

```powershell
py -3.12 src/exp05_advice.py --variant baseline
py -3.12 src/exp05_advice.py
py -3.12 src/exp05_verify.py
py -3.12 src/exp05_visualize.py
```

输入“如果您感到疲劳,还可以在馆区内泡足汤小憩。”对应A_S001_OFF_001_177547618944147，关联S001_POI_007，字符切片和上下文名称均可回到S001_OFF_001。所有证据用完整v1正文[start,end)，不要再次清洗。消费价格与服务是历史来源信息。

同文档精确/包含重复合并证据；近重复提示而不自动合并不同语义。跨来源保留独立记录和duplicate_group。不确定实体关联为[]，目前4条无实体对齐；这不妨碍按条件检索，不能擅自补ID。

参考32例在实现预测前保存，含11负例。优化规则TP19/FP2/FN2；留出9例TP4/FP2/FN2。两处审校修正后的同批一致性不能作为独立准确率。雨天FAQ为一个完整列表块，不代表每项都经独立活动边界核验。

接收检查：运行验证、读取该例、检查文档景区和全部活跃实体引用；读取graph.json确认20个CONDITION/ADVICE和21条TRIGGERS；最后使用Agent实际查询。不得将baseline或未经审校原始预测作为正式输入。

E5_013在2026年11月11日由负例改为情境条件正例，参考不是独立盲测；当前21个正关系、11个负例。请按当前quality文件引用指标。
