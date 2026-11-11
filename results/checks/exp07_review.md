# 实验7场景核验

执行模式：live_api；20次本轮API请求；图谱v3。
offline_revalidation为对历史模型提案的程序复验，不是新模型调用；语义仍需组员独立复核。

## AG_001
我想带孩子在箱根玩一天，请基于图谱安排路线，并找明确适合亲子的建议。

状态：partial
约束：{'scenic_id': 'S001', 'visitor_type': 'family', 'time_bucket': None, 'duration_days': 1, 'condition_type': 'visitor_type', 'missing_information': [], 'conflicts': [], 'decision_summary': '用户明确带孩子在箱根游玩一天，需基于图谱安排亲子路线并优先明确适合亲子的建议。'}
工具：[('query_routes', {'scenic_id': 'S001'}, 'ok'), ('query_advice', {'scenic_id': 'S001', 'visitor_type': 'family', 'condition_type': 'visitor_type'}, 'ok')]
核验：['通过程序核对路线/步骤/建议ID和引用；尚需组员独立语义验收']
最终结果：{
  "route_id": "R_S001_OFF_001_01",
  "steps": [
    {
      "step_no": 1,
      "poi_name": "箱根汤本",
      "time_text": "7:30",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 222,
          "end": 246,
          "text": "7:30 ~ 从新宿乘坐“浪漫”特快前往箱根汤本"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 2,
      "poi_name": "箱根汤本",
      "time_text": "9:20",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 544,
          "end": 564,
          "text": "9:20 ~ 在箱根入口·箱根汤本站换乘"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 3,
      "poi_name": "箱根雕刻森林美术馆",
      "time_text": "9:25",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 712,
          "end": 738,
          "text": "9:25 ~ 乘坐箱根登山电车前往箱根雕刻森林美术馆"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 4,
      "poi_name": "箱根雕刻森林美术馆",
      "time_text": "10:00",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 942,
          "end": 966,
          "text": "10:00 ~ 在箱根雕刻森林美术馆享受艺术漫步"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 5,
      "poi_name": "早云山",
      "time_text": "11:20",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 1276,
          "end": 1297,
          "text": "11:20 ~ 乘坐箱根登山缆车前往大涌谷"
        },
        {
          "doc_id": "S001_OFF_001",
          "start": 1427,
          "end": 1431,
          "text": "早云山站"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "transfer_target",
      "destination_poi_name": "大涌谷"
    },
    {
      "step_no": 6,
      "poi_name": "早云山",
      "time_text": "11:45",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 1395,
          "end": 1418,
          "text": "11:45 ~ 能眺望富士山美景的箱根空中缆车"
        },
        {
          "doc_id": "S001_OFF_001",
          "start": 1427,
          "end": 1431,
          "text": "早云山站"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 7,
      "poi_name": "大涌谷",
      "time_text": "12:55",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 1560,
          "end": 1592,
          "text": "12:55 ~ 在大涌谷尽情欣赏动人心弦的自然美景&品尝特色美食"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 8,
      "poi_name": "芦之湖",
      "time_text": "14:20",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 2051,
          "end": 2085,
          "text": "14:20 ~ 从大涌谷前往芦之湖,乘坐箱根海贼观光船游览芦之湖吧!"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 9,
      "poi_name": "箱根神社",
      "time_text": "15:40",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 2316,
          "end": 2337,
          "text": "15:40 ~ 参拜具有历史渊源的箱根神社"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 10,
      "poi_name": "箱根登山名产店 汤本店",
      "time_text": "17:00",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 2686,
          "end": 2715,
          "text": "17:00 ~ 购买伴手礼推荐去“箱根登山名产店 汤本店”"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    }
  ],
  "advice": [
    {
      "advice_id": "A_S001_OFF_001_247169266140315",
      "condition_type": "visitor_type",
      "condition_text": "对于带儿童的家庭",
      "visitor_types": [
        "family"
      ],
      "suggestion_text": "推荐您体验大号的密封舱,还可以在网中体验能够感受艺术的“泡泡城堡”和“网之森林”等",
      "related_entities": [
        {
          "entity_id": "S001_POI_020",
          "name": "泡泡城堡",
          "type": "POI"
        },
        {
          "entity_id": "S001_POI_021",
          "name": "网之森林",
          "type": "POI"
        }
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 1084,
          "end": 1134,
          "text": "对于带儿童的家庭,推荐您体验大号的密封舱,还可以在网中体验能够感受艺术的“泡泡城堡”和“网之森林”等"
        }
      ],
      "sources": [
        {
          "doc_id": "S001_OFF_001",
          "title": "初游箱根！推荐当日往返的标准路线—特定景点环游之旅 - 箱根｜箱根完整攻略",
          "url": "https://www.hakonenavi.jp/international/cn/course/515",
          "text_type": "official_route",
          "collected_at": "2026-10-28"
        }
      ],
      "temporal_note": "来源历史陈述；价格、开放和服务须出行前核实",
      "relation_note": "关联实体仅表示证据涉及，不表示每个实体都应访问或允许使用"
    }
  ],
  "supplementary_advice": [
    {
      "text": "按来源时刻从7:30新宿出发至17:00汤本购物，全天行程约为9.5小时（含交通与游览，实际以当日交通和停留时间为准）。",
      "basis": "estimate"
    },
    {
      "text": "文中时刻为来源的历史推荐时间，非实时班次或路况；建议出行前核实交通班次、设施开放情况与人流。",
      "basis": "general_suggestion"
    }
  ],
  "limitations": [
    "官方路线未标注老人、亲子或情侣适用性，不能据此保证整条路线适合亲子。",
    "明确的亲子建议只针对相关实体“泡泡城堡”“网之森林”；图谱未证明其属于本路线步骤，也未证明可替换或新增到该路线。",
    "无各步骤预计用时数据，无法验证一天内实际可完成的时长。",
    "路线包含新宿至箱根汤本的景区外接驳起点。",
    "图谱不是实时路况或运营服务，价格、开放与服务需出行前核实。",
    "原路线未标注整体人群适用性；条件建议的明确标签不证明全路线适合该人群。",
    "图谱缺少完整停留及交通耗时，不能保证满足请求总时长；原文钟点仅为历史推荐。"
  ],
  "source_refs": [
    "S001_OFF_001"
  ],
  "sources": [
    {
      "doc_id": "S001_OFF_001",
      "title": "初游箱根！推荐当日往返的标准路线—特定景点环游之旅 - 箱根｜箱根完整攻略",
      "url": "https://www.hakonenavi.jp/international/cn/course/515",
      "text_type": "official_route",
      "collected_at": "2026-10-28"
    }
  ]
}

## AG_002
带老人去箱根，只看上午路线，有适合老人的建议吗？

状态：partial
约束：{'scenic_id': 'S001', 'visitor_type': 'elderly', 'time_bucket': 'morning', 'duration_days': None, 'condition_type': 'visitor_type', 'missing_information': [], 'conflicts': [], 'decision_summary': '用户明确带老人前往箱根，并只看上午路线；景区已登记为S001，未提及其他互斥时长或缺失景区。'}
工具：[('query_routes', {'scenic_id': 'S001', 'time_bucket': 'morning'}, 'ok'), ('query_advice', {'scenic_id': 'S001', 'visitor_type': 'elderly', 'condition_type': 'visitor_type'}, 'no_match'), ('query_advice', {'condition_type': 'visitor_type', 'scenic_id': 'S001', 'visitor_type': 'general'}, 'no_match'), ('query_advice', {'condition_type': 'time', 'scenic_id': 'S001', 'visitor_type': None}, 'no_match')]
核验：['通过程序核对路线/步骤/建议ID和引用；尚需组员独立语义验收']
最终结果：{
  "route_id": "R_S001_OFF_001_01",
  "steps": [
    {
      "step_no": 1,
      "poi_name": "箱根汤本",
      "time_text": "7:30",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 222,
          "end": 246,
          "text": "7:30 ~ 从新宿乘坐“浪漫”特快前往箱根汤本"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 2,
      "poi_name": "箱根汤本",
      "time_text": "9:20",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 544,
          "end": 564,
          "text": "9:20 ~ 在箱根入口·箱根汤本站换乘"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 3,
      "poi_name": "箱根雕刻森林美术馆",
      "time_text": "9:25",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 712,
          "end": 738,
          "text": "9:25 ~ 乘坐箱根登山电车前往箱根雕刻森林美术馆"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 4,
      "poi_name": "箱根雕刻森林美术馆",
      "time_text": "10:00",
      "source_refs": [
        "S001_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S001_OFF_001",
          "start": 942,
          "end": 966,
          "text": "10:00 ~ 在箱根雕刻森林美术馆享受艺术漫步"
        }
      ],
      "step_kind": "route_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    }
  ],
  "advice": [],
  "supplementary_advice": [
    {
      "text": "上述时刻为原路线中的历史推荐时间，不是实时班次或路况；该上午片段为“初游箱根当日往返路线”的一部分，原路线整体为7:30新宿出发至17:00汤本购物，未提供各步骤或整体的预计用时，需另行核实。",
      "basis": "general_suggestion"
    },
    {
      "text": "按原路线时刻推算，上午片段自7:30出发至10:00抵达美术馆，行程历时约为2.5小时（估计值，不含返程与停留时长）。",
      "basis": "estimate"
    }
  ],
  "limitations": [
    "原路线未标注老人适用性，不能据此保证适合老人（步行量、台阶、换乘便利性均无证据）",
    "老人专属条件建议查询结果为no_match（数据已接入但无匹配建议），无可引用的适老建议",
    "上午时段条件建议查询结果同样为no_match",
    "各步骤duration_minutes为空，无法给出有依据的停留或总时长",
    "列表仅为原路线上午片段，不能视为完整一日路线；未纳入午后及傍晚行程",
    "图谱非实时服务，不反映当日列车班次、拥挤或天气情况",
    "query_advice：no_advice_match：数据已接入，但没有明确满足该过滤条件的建议",
    "query_advice：no_advice_match：数据已接入，但没有明确满足该过滤条件的建议",
    "query_advice：no_advice_match：数据已接入，但没有明确满足该过滤条件的建议",
    "原路线未标注整体人群适用性；条件建议的明确标签不证明全路线适合该人群。"
  ],
  "source_refs": [
    "S001_OFF_001"
  ],
  "sources": [
    {
      "doc_id": "S001_OFF_001",
      "title": "初游箱根！推荐当日往返的标准路线—特定景点环游之旅 - 箱根｜箱根完整攻略",
      "url": "https://www.hakonenavi.jp/international/cn/course/515",
      "text_type": "official_route",
      "collected_at": "2026-10-28"
    }
  ]
}

## AG_003
情侣去蓝山两天，如果下雨，有哪些建议和可参考路线？

状态：partial
约束：{'scenic_id': 'S003', 'visitor_type': 'couple', 'time_bucket': None, 'duration_days': 2, 'condition_type': 'weather', 'missing_information': [], 'conflicts': [], 'decision_summary': '情侣计划前往澳大利亚蓝山国家公园游玩两天，并询问下雨情况下的建议和可参考路线。'}
工具：[('query_routes', {'scenic_id': 'S003', 'time_bucket': None}, 'ok'), ('query_advice', {'scenic_id': 'S003', 'visitor_type': 'couple', 'condition_type': 'visitor_type'}, 'no_match'), ('query_advice', {'scenic_id': 'S003', 'visitor_type': None, 'condition_type': 'weather'}, 'ok'), ('query_advice', {'scenic_id': 'S003', 'visitor_type': 'general', 'condition_type': None}, 'no_match')]
核验：['final_validation: invalid_final_schema', '通过程序核对路线/步骤/建议ID和引用；尚需组员独立语义验收']
最终结果：{
  "route_id": "R_S003_OFF_001_01",
  "steps": [
    {
      "step_no": 1,
      "poi_name": "黑凤头鹦鹉面包店",
      "time_text": "早晨",
      "source_refs": [
        "S003_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S003_OFF_001",
          "start": 1876,
          "end": 1924,
          "text": "劳森黑凤头鹦鹉面包店 (Lawson's Black Cockatoo Bakery) 不容错过"
        }
      ],
      "step_kind": "candidate_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 2,
      "poi_name": "温特沃斯瀑布野餐区",
      "time_text": "早晨",
      "source_refs": [
        "S003_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S003_OFF_001",
          "start": 2021,
          "end": 2061,
          "text": "只需 10 分钟车程穿过原始丛林即可到达温特沃斯(Wentworth)瀑布野餐区"
        }
      ],
      "step_kind": "candidate_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 3,
      "poi_name": "Jamison Lookout",
      "time_text": "早晨",
      "source_refs": [
        "S003_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S003_OFF_001",
          "start": 2072,
          "end": 2100,
          "text": "从杰米森瞭望台 (Jamison Lookout) 出发"
        }
      ],
      "step_kind": "candidate_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 4,
      "poi_name": "Wentworth Falls Track",
      "time_text": "早晨",
      "source_refs": [
        "S003_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S003_OFF_001",
          "start": 2132,
          "end": 2180,
          "text": "然后前往温特沃斯(Wentworth)瀑布步道 (Wentworth Falls Track) "
        }
      ],
      "step_kind": "candidate_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 5,
      "poi_name": "Josophan's Fine Chocolates",
      "time_text": "早晨",
      "source_refs": [
        "S003_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S003_OFF_001",
          "start": 2363,
          "end": 2412,
          "text": "不妨前往Josophan's Fine Chocolates品尝纯正的比利时巧克力和手工松露巧克力"
        }
      ],
      "step_kind": "candidate_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 6,
      "poi_name": "Kate Soady Gallery",
      "time_text": "早晨",
      "source_refs": [
        "S003_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S003_OFF_001",
          "start": 2416,
          "end": 2464,
          "text": "您可以参观罗拉(Leura)购物中心的凯特·索迪画廊 (Kate Soady Gallery) "
        }
      ],
      "step_kind": "candidate_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 7,
      "poi_name": "Blackheath",
      "time_text": "下午",
      "source_refs": [
        "S003_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S003_OFF_001",
          "start": 2618,
          "end": 2649,
          "text": "驾车前往布莱克希思(Blackheath)享用美味的地中海午餐"
        }
      ],
      "step_kind": "candidate_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 8,
      "poi_name": "埃文斯瞭望台",
      "time_text": "下午",
      "source_refs": [
        "S003_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S003_OFF_001",
          "start": 2724,
          "end": 2747,
          "text": "您可以去附近的埃文斯瞭望台呼吸着清新的山间空气"
        }
      ],
      "step_kind": "candidate_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 9,
      "poi_name": "大峡谷步道",
      "time_text": "下午",
      "source_refs": [
        "S003_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S003_OFF_001",
          "start": 2788,
          "end": 2799,
          "text": "可以轻松前往大峡谷步道"
        }
      ],
      "step_kind": "candidate_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 10,
      "poi_name": "山地文化啤酒公司",
      "time_text": "晚上",
      "source_refs": [
        "S003_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S003_OFF_001",
          "start": 3045,
          "end": 3054,
          "text": " 山地文化啤酒公司"
        }
      ],
      "step_kind": "candidate_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 11,
      "poi_name": "Scenic World",
      "time_text": "晚上",
      "source_refs": [
        "S003_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S003_OFF_001",
          "start": 3156,
          "end": 3239,
          "text": "卡通巴另一个不容错过的活动是 Beyond Skyway 体验风景世界(Scenic World). Beyond Skyway 是全球首创的 90 分钟屋顶缆车体验"
        }
      ],
      "step_kind": "candidate_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    },
    {
      "step_no": 12,
      "poi_name": "卡通巴瀑布自然保护区夜间灯光步道",
      "time_text": "晚上",
      "source_refs": [
        "S003_OFF_001"
      ],
      "evidence": [
        {
          "doc_id": "S003_OFF_001",
          "start": 3365,
          "end": 3387,
          "text": "感受卡通巴瀑布自然保护区夜间灯光步道黄昏时分"
        }
      ],
      "step_kind": "candidate_activity",
      "location_role": "activity_location",
      "destination_poi_name": null
    }
  ],
  "advice": [
    {
      "advice_id": "A_S003_OFF_001_231897423423565",
      "condition_type": "weather",
      "condition_text": "下雨天还值得去蓝山吗?",
      "visitor_types": [],
      "suggestion_text": "在蓝山,即使下雨天也有很多室内活动可以参加,包括:\n山地文化啤酒公司在卡通巴\n午餐阿特斯, 罗拉(Leura) Gourmet或小妹妹\n在罗拉(Leura)逛橱窗\n日本温泉浴场蓝山\n蓝山桑拿\n昔日美人珍藏茶壶博物馆和茶室(罗拉(Leura)\n莉莲菲尔斯日间水疗中心\n诺曼·林赛画廊及博物馆\n蓝山文化中心\n维多利亚山博物馆\n伍德福德学院\n维多利亚山电影\n阿普萨拉日间水疗中心(卡通巴)\n水疗盛宴下午茶\n梅加隆谷茶室\n下午茶热情莉莲费尔斯蓝山",
      "related_entities": [
        {
          "entity_id": "S003_POI_001",
          "name": "蓝山国家公园",
          "type": "POI"
        },
        {
          "entity_id": "S003_POI_004",
          "name": "Katoomba",
          "type": "POI"
        },
        {
          "entity_id": "S003_POI_005",
          "name": "Leura",
          "type": "POI"
        },
        {
          "entity_id": "S003_POI_026",
          "name": "山地文化啤酒公司",
          "type": "POI"
        },
        {
          "entity_id": "S003_POI_045",
          "name": "蓝山文化中心",
          "type": "POI"
        },
        {
          "entity_id": "S003_POI_046",
          "name": "诺曼·林赛画廊及博物馆",
          "type": "POI"
        },
        {
          "entity_id": "S003_POI_047",
          "name": "维多利亚山博物馆",
          "type": "POI"
        },
        {
          "entity_id": "S003_POI_048",
          "name": "伍德福德学院",
          "type": "POI"
        },
        {
          "entity_id": "S003_POI_049",
          "name": "莉莲菲尔斯日间水疗中心",
          "type": "POI"
        },
        {
          "entity_id": "S003_POI_050",
          "name": "昔日美人珍藏茶壶博物馆和茶室",
          "type": "POI"
        },
        {
          "entity_id": "S003_POI_051",
          "name": "梅加隆谷茶室",
          "type": "POI"
        }
      ],
      "evidence": [
        {
          "doc_id": "S003_OFF_001",
          "start": 4901,
          "end": 5132,
          "text": "下雨天还值得去蓝山吗?\n在蓝山,即使下雨天也有很多室内活动可以参加,包括:\n山地文化啤酒公司在卡通巴\n午餐阿特斯, 罗拉(Leura) Gourmet或小妹妹\n在罗拉(Leura)逛橱窗\n日本温泉浴场蓝山\n蓝山桑拿\n昔日美人珍藏茶壶博物馆和茶室(罗拉(Leura)\n莉莲菲尔斯日间水疗中心\n诺曼·林赛画廊及博物馆\n蓝山文化中心\n维多利亚山博物馆\n伍德福德学院\n维多利亚山电影\n阿普萨拉日间水疗中心(卡通巴)\n水疗盛宴下午茶\n梅加隆谷茶室\n下午茶热情莉莲费尔斯蓝山"
        }
      ],
      "sources": [
        {
          "doc_id": "S003_OFF_001",
          "title": "从悉尼出发，蓝山风景一日游 | 访问新南威尔士州",
          "url": "https://www.visitnsw.com/cn/articles/blue-mountains-scenic-day-trip",
          "text_type": "official_route",
          "collected_at": "2026-10-28"
        }
      ],
      "temporal_note": "来源历史陈述；价格、开放和服务须出行前核实",
      "relation_note": "关联实体仅表示证据涉及，不表示每个实体都应访问或允许使用"
    }
  ],
  "supplementary_advice": [
    {
      "text": "上述步骤为来源列出的一日游候选活动清单，按原文时间分段与顺序呈现，并非两日连续行程；无法据此估计两天各段用时，需自行取舍并在出行前核实开放与服务。",
      "basis": "general_suggestion"
    }
  ],
  "limitations": [
    "情侣专属建议查询无匹配（no_advice_match），无法确认路线或活动的情侣适用性。",
    "图谱仅提供一日游候选活动，没有两日完整路线，无法满足两天时长安排。",
    "原路线未标注老人/亲子/情侣适用性，列出步骤不表示适合情侣或雨天适用。",
    "雨天建议为来源历史陈述，价格、开放时间与服务须出行前核实。",
    "本规划不提供实时天气或路况判断，雨天户外步骤（瀑布步道、瞭望台、夜间灯光步道）的可行性未经验证。",
    "以下仅为原文顺序的候选活动，含可选推荐；不是必须依次完成的固定路线。",
    "query_advice：no_advice_match：数据已接入，但没有明确满足该过滤条件的建议",
    "query_advice：no_advice_match：数据已接入，但没有明确满足该过滤条件的建议",
    "原路线未标注整体人群适用性；条件建议的明确标签不证明全路线适合该人群。",
    "图谱缺少完整停留及交通耗时，不能保证满足请求总时长；原文钟点仅为历史推荐。",
    "天气建议仅在原文条件成立时适用；无实时天气、开放或路况信息。"
  ],
  "source_refs": [
    "S003_OFF_001"
  ],
  "sequence_semantics": "source_order_only",
  "sources": [
    {
      "doc_id": "S003_OFF_001",
      "title": "从悉尼出发，蓝山风景一日游 | 访问新南威尔士州",
      "url": "https://www.visitnsw.com/cn/articles/blue-mountains-scenic-day-trip",
      "text_type": "official_route",
      "collected_at": "2026-10-28"
    }
  ]
}

## AG_004
请给我优胜美地的路线和避免拥挤的建议。

状态：partial
约束：{'scenic_id': 'S002', 'visitor_type': None, 'time_bucket': None, 'duration_days': None, 'condition_type': 'crowding', 'missing_information': [], 'conflicts': [], 'decision_summary': '用户明确查询优胜美地国家公园的路线，并希望避免拥挤。'}
工具：[('query_routes', {'scenic_id': 'S002'}, 'no_match'), ('query_advice', {'scenic_id': 'S002', 'condition_type': 'crowding'}, 'ok')]
核验：['通过程序核对路线/步骤/建议ID和引用；尚需组员独立语义验收']
最终结果：{
  "route_id": null,
  "steps": [],
  "advice": [
    {
      "advice_id": "A_S002_VIS_004_072958652312044",
      "condition_type": "crowding",
      "condition_text": "如果你不想人挤人、也不想早起抢预约的话",
      "visitor_types": [],
      "suggestion_text": "建议计划周中去,人会少很多",
      "related_entities": [],
      "evidence": [
        {
          "doc_id": "S002_VIS_004",
          "start": 1802,
          "end": 1835,
          "text": "如果你不想人挤人、也不想早起抢预约的话,建议计划周中去,人会少很多"
        }
      ],
      "sources": [
        {
          "doc_id": "S002_VIS_004",
          "title": "疑是熔岩落九天——优胜美地火瀑布外加夏日游记一则 - 美国信用卡指南",
          "url": "https://www.uscreditcardguide.com/yosemite-firefall-2021/",
          "text_type": "visitor_diary",
          "collected_at": "2026-10-28"
        }
      ],
      "temporal_note": "来源历史陈述；价格、开放和服务须出行前核实",
      "relation_note": "关联实体仅表示证据涉及，不表示每个实体都应访问或允许使用"
    }
  ],
  "supplementary_advice": [
    {
      "text": "该建议来自游客游记，属于历史经验；预约政策、开放情况和实际人流须出行前另行核实。",
      "basis": "general_suggestion"
    }
  ],
  "limitations": [
    "路线查询无匹配：当前图谱未覆盖该景区或时间段，不代表现实中没有路线",
    "图谱不是实时路况或人流服务，无法提供实时拥挤程度",
    "未查询人群适用性（用户未指定人群），无适用性证据",
    "来源为游客日记类历史陈述，价格、开放、预约要求须出行前核实",
    "query_routes：no_route_match：当前图谱未覆盖该景区/时间段；不代表现实中没有路线"
  ],
  "source_refs": [
    "S002_VIS_004"
  ],
  "sources": [
    {
      "doc_id": "S002_VIS_004",
      "title": "疑是熔岩落九天——优胜美地火瀑布外加夏日游记一则 - 美国信用卡指南",
      "url": "https://www.uscreditcardguide.com/yosemite-firefall-2021/",
      "text_type": "visitor_diary",
      "collected_at": "2026-10-28"
    }
  ]
}

## AG_005
带孩子玩一天，帮我规划。

状态：partial
约束：{'scenic_id': None, 'visitor_type': 'family', 'time_bucket': None, 'duration_days': 1, 'condition_type': 'visitor_type', 'missing_information': ['未指定景区'], 'conflicts': [], 'decision_summary': '用户带孩子出行，计划游玩1天，但未指定景区，需先确认景区后再检索。'}
工具：[]
核验：['需澄清后再查询；未生成无证据行程']
最终结果：{
  "clarification": [
    "请先指定想游览的景区。当前知识库仅覆盖日本箱根、美国优胜美地和澳大利亚蓝山。你希望查询其中哪个景区？当前不能为未覆盖景区生成有来源的路线。"
  ],
  "source_refs": []
}

## AG_006
去箱根，必须总共一天完成，但同时总共必须两天完成，不接受放宽。

状态：partial
约束：{'scenic_id': 'S001', 'visitor_type': None, 'time_bucket': None, 'duration_days': None, 'condition_type': 'time', 'missing_information': [], 'conflicts': ['用户同时要求总行程必须一天完成和必须两天完成，二者互斥且不接受放宽'], 'decision_summary': '识别景区为日本箱根，但行程天数约束存在一天与两天互斥冲突，无法确定duration_days。'}
工具：[]
核验：['需澄清后再查询；未生成无证据行程']
最终结果：{
  "clarification": [
    "你的要求存在冲突：用户同时要求总行程必须一天完成和必须两天完成，二者互斥且不接受放宽。请确认采用哪一种时长要求？"
  ],
  "source_refs": []
}

## AG_007
给我黄山的游览路线。

状态：partial
约束：{'scenic_id': None, 'visitor_type': None, 'time_bucket': None, 'duration_days': None, 'condition_type': None, 'missing_information': ['黄山不在已登记景区列表'], 'conflicts': [], 'decision_summary': '用户请求黄山游览路线，但黄山未登记在已知景区列表中，无法映射到scenic_id。'}
工具：[]
核验：['需澄清后再查询；未生成无证据行程']
最终结果：{
  "clarification": [
    "你指定的“黄山”尚未被知识库覆盖。当前知识库仅覆盖日本箱根、美国优胜美地和澳大利亚蓝山。你希望查询其中哪个景区？当前不能为未覆盖景区生成有来源的路线。"
  ],
  "source_refs": []
}
