# 实验1数据质量检查

输入 18 条；输出 18 条；正文共 154930 字符。

| 景区 | 官方路线文档 | 有效游记 | 正文字符 |
| --- | ---: | ---: | ---: |
| 日本箱根 | 1 | 5 | 29795 |
| 美国优胜美地国家公园 | 1 | 5 | 93085 |
| 澳大利亚蓝山国家公园 | 1 | 5 | 32050 |

必填字段空值：0/216；完全重复：0；近重复候选：0；拒收：0。

字符数按 Python len(text) 统计，包含正文中的换行和空格，不等同于中文字数。官方路线的多个步骤页合计为一条路线文档。

正文不翻译；NFKC 统一兼容字符。跨语言实体别名需要后续实验维护；游客陈述保留原貌，不作为官方事实。

## 自动检查

- three_scenics: True
- one_main_scenic: True
- target_1_official_5_diaries_each: True
- no_rejections: True
- no_exact_duplicates: True
- no_near_duplicates_ge_0_75: True
- required_fields_complete: True
- no_platform_notice_residue: True
- all_raw_integrity_verified: True
