# 实验5逐例核验

AI辅助阅读原文后、抽取器实现与预测前形成；未由组员独立复核。
32例目的选样诊断集；两个文档留出于调参，文本此前已浏览，不是随机样本或独立盲测。雨天列表用最小前缀语义匹配，另做结构完整性检查。

严格边界：条件和建议归一空白/终止标点后匹配；雨天FAQ按预先标注的最小建议前缀匹配，完整列表另做切片检查。边界错同时计FP和FN。

## baseline
{'development': {'tp': 11, 'fp': 4, 'fn': 3, 'cases': 23, 'positive_relations': 14, 'precision': 0.7333333333333333, 'recall': 0.7857142857142857, 'f1': 0.7586206896551724, 'correct_negative_cases': 6}, 'document_holdout': {'tp': 4, 'fp': 3, 'fn': 2, 'cases': 9, 'positive_relations': 6, 'precision': 0.5714285714285714, 'recall': 0.6666666666666666, 'f1': 0.6153846153846154, 'correct_negative_cases': 2}, 'all': {'tp': 15, 'fp': 7, 'fn': 5, 'cases': 32, 'positive_relations': 20, 'precision': 0.6818181818181818, 'recall': 0.75, 'f1': 0.7142857142857143, 'correct_negative_cases': 8}}

## optimized
{'development': {'tp': 14, 'fp': 0, 'fn': 0, 'cases': 23, 'positive_relations': 14, 'precision': 1.0, 'recall': 1.0, 'f1': 1.0, 'correct_negative_cases': 9}, 'document_holdout': {'tp': 4, 'fp': 2, 'fn': 2, 'cases': 9, 'positive_relations': 6, 'precision': 0.6666666666666666, 'recall': 0.6666666666666666, 'f1': 0.6666666666666666, 'correct_negative_cases': 3}, 'all': {'tp': 18, 'fp': 2, 'fn': 2, 'cases': 32, 'positive_relations': 20, 'precision': 0.9, 'recall': 0.9, 'f1': 0.9, 'correct_negative_cases': 12}}

## reviewed_delivery
{'development': {'tp': 14, 'fp': 0, 'fn': 0, 'cases': 23, 'positive_relations': 14, 'precision': 1.0, 'recall': 1.0, 'f1': 1.0, 'correct_negative_cases': 9}, 'document_holdout': {'tp': 6, 'fp': 0, 'fn': 0, 'cases': 9, 'positive_relations': 6, 'precision': 1.0, 'recall': 1.0, 'f1': 1.0, 'correct_negative_cases': 3}, 'all': {'tp': 20, 'fp': 0, 'fn': 0, 'cases': 32, 'positive_relations': 20, 'precision': 1.0, 'recall': 1.0, 'f1': 1.0, 'correct_negative_cases': 12}}

## E5_001 / development
> 如果遇上好天气,还可以从车窗看到富士山,这无疑会增加您对旅行的期待哦。

参考：[]
预测：[]
TP=0 FP=0 FN=0；描述可见景色，未给出游览动作

## E5_002 / development
> ※1:从新宿站到箱根汤本站,如果使用“箱根周游券”乘坐“浪漫”特快,则需另外支付特快费(1,200日币)。

参考：[('如果使用“箱根周游券”乘坐“浪漫”特快', '则需另外支付特快费(1,200日币)')]
预测：[('如果使用“箱根周游券”乘坐“浪漫”特快', '则需另外支付特快费(1,200日币)')]
TP=1 FP=0 FN=0；带条件的票务操作；历史价格需标记

## E5_003 / development
> 如果在车站内部的服务柜台寄存包裹,则可以帮您运送到住处,因此您可以轻松地享受观光之旅(含税900日币~)。

参考：[('如果在车站内部的服务柜台寄存包裹', '则可以帮您运送到住处,因此您可以轻松地享受观光之旅(含税900日币~)')]
预测：[('如果在车站内部的服务柜台寄存包裹', '则可以帮您运送到住处,因此您可以轻松地享受观光之旅(含税900日币~)')]
TP=1 FP=0 FN=0；寄存条件与服务

## E5_004 / development
> 对于带儿童的家庭,推荐您体验大号的密封舱,还可以在网中体验能够感受艺术的“泡泡城堡”和“网之森林”等。

参考：[('对于带儿童的家庭', '推荐您体验大号的密封舱,还可以在网中体验能够感受艺术的“泡泡城堡”和“网之森林”等')]
预测：[('对于带儿童的家庭', '推荐您体验大号的密封舱,还可以在网中体验能够感受艺术的“泡泡城堡”和“网之森林”等')]
TP=1 FP=0 FN=0；同条件多活动整体保留

## E5_005 / development
> 如果您感到疲劳,还可以在馆区内泡足汤小憩。

参考：[('如果您感到疲劳', '还可以在馆区内泡足汤小憩')]
预测：[('如果您感到疲劳', '还可以在馆区内泡足汤小憩')]
TP=1 FP=0 FN=0；馆区具体关联需上下文

## E5_006 / development
> 如果出示“箱根周游券”,可享优惠价成人1,900日币、高中生大学生1,500日币、中小学生700日币(均含税)。

参考：[('如果出示“箱根周游券”', '可享优惠价成人1,900日币、高中生大学生1,500日币、中小学生700日币(均含税)')]
预测：[('如果出示“箱根周游券”', '可享优惠价成人1,900日币、高中生大学生1,500日币、中小学生700日币(均含税)')]
TP=1 FP=0 FN=0；票券条件优惠，不作现价保证

## E5_007 / development
> 最后,如果购买伴手礼,可以前往位于箱根汤本站的“箱根登山名产店 汤本店”。

参考：[('如果购买伴手礼', '可以前往位于箱根汤本站的“箱根登山名产店 汤本店”')]
预测：[('如果购买伴手礼', '可以前往位于箱根汤本站的“箱根登山名产店 汤本店”')]
TP=1 FP=0 FN=0；购买目的对应建议

## E5_008 / development
> 如果能像这样充分地利用箱根空中缆车和箱根海贼观光船等,您可以在一天内高效地游览很多景点哦。

参考：[]
预测：[]
TP=0 FP=0 FN=0；总结效率，不是具体条件建议

## E5_009 / development
> 走过小花园看见一片草坪运动场,看见一对夫妇带着三个孩子在玩类似棒球的游戏,真得好羡慕他们。

参考：[]
预测：[]
TP=0 FP=0 FN=0；游客观察儿童不等于亲子推荐

## E5_010 / development
> 再乘缆车就可以到桃源台了,因为时间尚早,我们的酒店下午3点才能办入住,所以在桃源台乘海贼船游览芦之湖全景.因为有周游券,所以每个停靠点都随意下来,看看美景,当天天气不太好,在箱根町港没能看到富士山.在元箱根港看了水中神社,这个拍照打卡点人气太旺,排队排到半山腰.


参考：[]
预测：[]
TP=0 FP=0 FN=0；作者经历，不应由排队描述推断避峰建议

## E5_011 / development
> From the Lower Yosemite Fall area, head west along the base of the Three Brothers rock formation, past Camp 4, eventually working your way through Yosemite Valley to El Capitan. If you are planning to hike the half loop, cross the Merced River at El Capitan Bridge and continue by heading east back toward Yosemite Village. If you are planning to hike the full loop, continue west past El Capitan toward Bridalveil Fall. While most of the trail is flat, there are some hilly sections throughout the hike. Additionally, you will find mixed trail surfaces: dirt, rocks, sand, and old pavement.


参考：[('If you are planning to hike the half loop', 'cross the Merced River at El Capitan Bridge and continue by heading east back toward Yosemite Village')]
预测：[('If you are planning to hike the half loop', 'cross the Merced River at El Capitan Bridge and continue by heading east back toward Yosemite Village')]
TP=1 FP=0 FN=0；英文条件路线

## E5_012 / development
> From the Lower Yosemite Fall area, head west along the base of the Three Brothers rock formation, past Camp 4, eventually working your way through Yosemite Valley to El Capitan. If you are planning to hike the half loop, cross the Merced River at El Capitan Bridge and continue by heading east back toward Yosemite Village. If you are planning to hike the full loop, continue west past El Capitan toward Bridalveil Fall. While most of the trail is flat, there are some hilly sections throughout the hike. Additionally, you will find mixed trail surfaces: dirt, rocks, sand, and old pavement.


参考：[('If you are planning to hike the full loop', 'continue west past El Capitan toward Bridalveil Fall')]
预测：[('If you are planning to hike the full loop', 'continue west past El Capitan toward Bridalveil Fall')]
TP=1 FP=0 FN=0；两个备选不可拼接

## E5_013 / development
> 趁着时间还早(早晨也很冷,大约10摄氏度左右)在车上吃了早餐,大约7点换好了登山鞋我们徒步出发,虽然刚出发穿着短裤、T恤稍有些冷,但建议还是不要增加衣服,因为很快就会感到热了。

参考：[]
预测：[]
TP=0 FP=0 FN=0；上下文冷暖为经历，未显式匹配通用条件句；记录边界局限

## E5_014 / development
> 不过停车场不大,感觉旺季会比较难停车。

参考：[]
预测：[]
TP=0 FP=0 FN=0；预测停车困难而非建议动作

## E5_015 / development
> 教堂很小,却在阳光的照射下很温馨,若是在这里举办幸福的婚礼,一定浪漫不已。

参考：[]
预测：[]
TP=0 FP=0 FN=0；主观想象婚礼不等于情侣适用性

## E5_016 / development
> 我们按照官方建议每人带了4L水,爬cable那天不算特别热还基本全喝完了,现在想想有些后怕,所以应该建议没人带5-6L。

参考：[]
预测：[]
TP=0 FP=0 FN=0；普通补水建议，未显式条件，不强填条件

## E5_017 / development
> 如果您想近距离观赏,可以走岔路前往弗莱彻瞭望台 (Fletchers Lookout),近距离欣赏瀑布。

参考：[('如果您想近距离观赏', '可以走岔路前往弗莱彻瞭望台 (Fletchers Lookout),近距离欣赏瀑布')]
预测：[('如果您想近距离观赏', '可以走岔路前往弗莱彻瞭望台 (Fletchers Lookout),近距离欣赏瀑布')]
TP=1 FP=0 FN=0；目的条件

## E5_018 / development
> 或者,如果想在旅途中享用美食,请前往这家小猪熟食店这里有琳琅满目的糕点、沙拉和其他自制美食。

参考：[('如果想在旅途中享用美食', '请前往这家小猪熟食店这里有琳琅满目的糕点、沙拉和其他自制美食')]
预测：[('如果想在旅途中享用美食', '请前往这家小猪熟食店这里有琳琅满目的糕点、沙拉和其他自制美食')]
TP=1 FP=0 FN=0；原文转写不顺保留原貌

## E5_019 / development
> 如果你有时间,另一个最佳观景点是戈维茨跳跃瞭望台布莱克希思(Blackheath)附近:蓝山海拔最高的城镇之一。

参考：[('如果你有时间', '另一个最佳观景点是戈维茨跳跃瞭望台布莱克希思(Blackheath)附近:蓝山海拔最高的城镇之一')]
预测：[('如果你有时间', '另一个最佳观景点是戈维茨跳跃瞭望台布莱克希思(Blackheath)附近:蓝山海拔最高的城镇之一')]
TP=1 FP=0 FN=0；没有可以/建议词但语义为条件推荐

## E5_020 / development
> 不过,如果游客想要体验更长的徒步旅行,例如壮观的大峡谷步道,或者想游览其他村庄,则应该在此过夜。

参考：[('如果游客想要体验更长的徒步旅行,例如壮观的大峡谷步道,或者想游览其他村庄', '则应该在此过夜')]
预测：[('如果游客想要体验更长的徒步旅行,例如壮观的大峡谷步道,或者想游览其他村庄', '则应该在此过夜')]
TP=1 FP=0 FN=0；条件跨多个逗号；不可截成第一个分句

## E5_021 / development
> 蓝山适合儿童游玩吗?
当然! 蓝山有很多适合家庭的趣味活动,包括观星、骑自行车、露营、徒步旅行和风景世界(Scenic World)。


参考：[('蓝山适合儿童游玩吗?', '当然! 蓝山有很多适合家庭的趣味活动,包括观星、骑自行车、露营、徒步旅行和风景世界(Scenic World)。')]
预测：[('蓝山适合儿童游玩吗?', '当然! 蓝山有很多适合家庭的趣味活动,包括观星、骑自行车、露营、徒步旅行和风景世界(Scenic World)')]
TP=1 FP=0 FN=0；问答跨句，含家庭适用信息

## E5_022 / development
> 下雨天还值得去蓝山吗?
在蓝山,即使下雨天也有很多室内活动可以参加,包括:
山地文化啤酒公司在卡通巴
午餐阿特斯, 罗拉(Leura) Gourmet或小妹妹
在罗拉(Leura)逛橱窗
日本温泉浴场蓝山
蓝山桑拿
昔日美人珍藏茶壶博物馆和茶室(罗拉(Leura)
莉莲菲尔斯日间水疗中心
诺曼·林赛画廊及博物馆
蓝山文化中心
维多利亚山博物馆
伍德福德学院
维多利亚山电影
阿普萨拉日间水疗中心(卡通巴)
水疗盛宴下午茶
梅加隆谷茶室
下午茶热情莉莲费尔斯蓝山


参考：[('下雨天还值得去蓝山吗?', '在蓝山,即使下雨天也有很多室内活动可以参加,包括:')]
预测：[('下雨天还值得去蓝山吗?', '在蓝山,即使下雨天也有很多室内活动可以参加,包括:\n山地文化啤酒公司在卡通巴\n午餐阿特斯, 罗拉(Leura) Gourmet或小妹妹\n在罗拉(Leura)逛橱窗\n日本温泉浴场蓝山\n蓝山桑拿\n昔日美人珍藏茶壶博物馆和茶室(罗拉(Leura)\n莉莲菲尔斯日间水疗中心\n诺曼·林赛画廊及博物馆\n蓝山文化中心\n维多利亚山博物馆\n伍德福德学院\n维多利亚山电影\n阿普萨拉日间水疗中心(卡通巴)\n水疗盛宴下午茶\n梅加隆谷茶室\n下午茶热情莉莲费尔斯蓝山')]
TP=1 FP=0 FN=0；问答列表应保留后续活动；此处仅标注最小建议前缀以作语义匹配

## E5_023 / development
> 很喜欢酒单上的Pinot Grigio,是非常清爽的开胃酒,入口很柔滑,有梨子和柑橘的香气,很适合女孩子。

参考：[]
预测：[]
TP=0 FP=0 FN=0；园外餐厅酒评，不能误归蓝山亲子建议

## E5_024 / document_holdout
> 如果乘坐小田急浪漫特快前往箱根汤本,则需另外购买特快车票,1200日元/人/单程


参考：[('如果乘坐小田急浪漫特快前往箱根汤本', '则需另外购买特快车票,1200日元/人/单程')]
预测：[('如果乘坐小田急浪漫特快前往箱根汤本', '则需另外购买特快车票,1200日元/人/单程')]
TP=1 FP=0 FN=0；交通票务

## E5_025 / document_holdout
> 如果不想另外付费,则只能乘坐普通小田急线,小田急线不能直接到箱根汤本,只能乘到小田原,再从小田原坐箱根登山电车到箱根汤本,这样会比坐浪漫特快多花20分钟左右


参考：[('如果不想另外付费', '则只能乘坐普通小田急线,小田急线不能直接到箱根汤本,只能乘到小田原,再从小田原坐箱根登山电车到箱根汤本,这样会比坐浪漫特快多花20分钟左右')]
预测：[('如果不想另外付费', '则只能乘坐普通小田急线,小田急线不能直接到箱根汤本,只能乘到小田原,再从小田原坐箱根登山电车到箱根汤本,这样会比坐浪漫特快多花20分钟左右')]
TP=1 FP=0 FN=0；条件后的多步骤完整保留

## E5_026 / document_holdout
> 如果座位有空的话,一定要坐在靠窗边,因为窗外可以看到宽广的芦之湖和停泊在湖上的海贼船,一边欣赏美景一边吃美食。

参考：[('如果座位有空的话', '一定要坐在靠窗边,因为窗外可以看到宽广的芦之湖和停泊在湖上的海贼船,一边欣赏美景一边吃美食')]
预测：[('如果座位有空的话', '一定要坐在靠窗边,因为窗外可以看到宽广的芦之湖和停泊在湖上的海贼船,一边欣赏美景一边吃美食')]
TP=1 FP=0 FN=0；座位条件建议

## E5_027 / document_holdout
> 瀑布的水流量可以根据最近Sierra Nevada的降雪推算,你也可以通过国家公园的在线摄像头查看Yosemite Fall的情况,如果后者几乎没有水,那么估计Horsetail Fall的水也不大。

参考：[]
预测：[]
TP=0 FP=0 FN=0；水量推断，无建议动作

## E5_028 / document_holdout
> 如果你不想人挤人、也不想早起抢预约的话,建议计划周中去,人会少很多。

参考：[('如果你不想人挤人、也不想早起抢预约的话', '建议计划周中去,人会少很多')]
预测：[('如果你不想人挤人、也不想早起抢预约的话', '建议计划周中去,人会少很多')]
TP=1 FP=0 FN=0；避人群条件

## E5_029 / document_holdout
> 更妙的是Tunnel View就在CA 41号路旁,路边有两个停车场,你不需要走trail就可以饱览美景,何乐而不为?建议大家条件允许的话,一定要沿41号路由南往北,从Oakhurst进入优胜美地,路上如果你感兴趣的话还可以去Mariposa Grove看看巨大的红杉树,当车从隧道穿出,Yosemite Valley一览无余的感觉非常震撼人心。

参考：[('条件允许的话', '一定要沿41号路由南往北,从Oakhurst进入优胜美地')]
预测：[('条件允许的话', '一定要沿41号路由南往北,从Oakhurst进入优胜美地,路上')]
TP=0 FP=1 FN=1；前置建议与内嵌条件，另一个条件需拆开

## E5_030 / document_holdout
> 更妙的是Tunnel View就在CA 41号路旁,路边有两个停车场,你不需要走trail就可以饱览美景,何乐而不为?建议大家条件允许的话,一定要沿41号路由南往北,从Oakhurst进入优胜美地,路上如果你感兴趣的话还可以去Mariposa Grove看看巨大的红杉树,当车从隧道穿出,Yosemite Valley一览无余的感觉非常震撼人心。

参考：[('如果你感兴趣的话', '还可以去Mariposa Grove看看巨大的红杉树')]
预测：[('如果你感兴趣的话', '还可以去Mariposa Grove看看巨大的红杉树,当车从隧道穿出,Yosemite Valley一览无余的感觉非常震撼人心')]
TP=0 FP=1 FN=1；同句第二个条件建议

## E5_031 / document_holdout
> 如果说Tunnel View是从峡谷的谷底平视的话,那么另一个不得不去的观景点就是位于峭壁之上的Glacier Point了,这里有观看Half Dome的绝佳视角。

参考：[]
预测：[]
TP=0 FP=0 FN=0；比喻比较不是条件

## E5_032 / document_holdout
> 若喜欢本文,别忘了给个五星好评哦!


参考：[]
预测：[]
TP=0 FP=0 FN=0；站点求好评无关旅游建议
