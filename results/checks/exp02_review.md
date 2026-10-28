# 实验2 逐例核验清单

AI辅助逐例语义核验；参考标签由阅读原句编写，非随机独立测试集，未声称学生本人或组员已复核

目的抽样：三个景区各8例，覆盖官方及游记、三类实体、重复、边界、歧义和负例；用于开发诊断

指标仅用于同一目的抽样开发集的优化诊断，不能当作独立测试或全语料准确率。

## baseline
TP=35，FP=47，FN=49；P=42.68%，R=41.67%，F1=42.17%。

## optimized
TP=79，FP=0，FN=5；P=100.00%，R=94.05%，F1=96.93%。

## C01 S001_OFF_001 [222,246)
> 7:30 ~ 从新宿乘坐“浪漫”特快前往箱根汤本

- 初版预测：7:30→TIME/7:30 [222,226)；新宿→POI/新宿 [230,232)；箱根→POI/箱根 [242,244)；箱根汤本→POI/箱根汤本 [242,246)
- 优化预测：7:30→TIME/7:30 [222,226)；新宿→POI/新宿 [230,232)；“浪漫”特快→TRANSPORT/浪漫特快 [234,240)；箱根汤本→POI/箱根汤本 [242,246)
- 核验参考：7:30→TIME/7:30 [222,226)；新宿→POI/新宿 [230,232)；“浪漫”特快→TRANSPORT/浪漫特快 [234,240)；箱根汤本→POI/箱根汤本 [242,246)
- 判断：接驳起点新宿标记external；票券不属于交通方式。
- 误识别：无
- 漏识别或边界偏差：无

## C02 S001_OFF_001 [1342,1389)
> 首先,从箱根登山电车强罗站(OH57)换乘箱根登山缆车,乘坐洋溢复古风情的缆车咣当咣当地爬坡。

- 初版预测：箱根→POI/箱根 [1346,1348)；电车→TRANSPORT/列车 [1350,1352)；车→TRANSPORT/车 [1351,1352)；强罗→POI/强罗 [1352,1354)；箱根→POI/箱根 [1363,1365)；缆车→TRANSPORT/缆车 [1367,1369)；车→TRANSPORT/车 [1368,1369)；缆车→TRANSPORT/缆车 [1379,1381)；车→TRANSPORT/车 [1380,1381)
- 优化预测：箱根登山电车→TRANSPORT/箱根登山电车 [1346,1352)；强罗站→POI/强罗 [1352,1355)；箱根登山缆车→TRANSPORT/箱根登山缆车 [1363,1369)；缆车→TRANSPORT/缆车 [1379,1381)
- 核验参考：箱根登山电车→TRANSPORT/箱根登山电车 [1346,1352)；强罗站→POI/强罗 [1352,1355)；箱根登山缆车→TRANSPORT/箱根登山缆车 [1363,1369)；缆车→TRANSPORT/缆车 [1379,1381)
- 判断：专名取完整边界，末尾泛称缆车保留为未知具体制式，不与空中缆车合并。
- 误识别：无
- 漏识别或边界偏差：无

## C03 S001_OFF_001 [1419,1458)
> 到达缆车终点站—早云山站(OH62)后,再换乘箱根空中缆车。发车间隔约1分钟。

- 初版预测：缆车→TRANSPORT/缆车 [1421,1423)；车→TRANSPORT/车 [1422,1423)；箱根→POI/箱根 [1442,1444)；缆车→TRANSPORT/缆车 [1446,1448)；车→TRANSPORT/车 [1447,1448)；车→TRANSPORT/车 [1450,1451)；1分钟→TIME/1分钟 [1454,1457)
- 优化预测：缆车→TRANSPORT/缆车 [1421,1423)；早云山站→POI/早云山 [1427,1431)；箱根空中缆车→TRANSPORT/箱根空中缆车 [1442,1448)；1分钟→TIME/1分钟 [1454,1457)
- 核验参考：缆车→TRANSPORT/缆车 [1421,1423)；早云山站→POI/早云山 [1427,1431)；箱根空中缆车→TRANSPORT/箱根空中缆车 [1442,1448)；1分钟→TIME/1分钟 [1454,1457)
- 判断：区分登山缆车和空中缆车；时间为发车间隔，不是停留时间。
- 误识别：无
- 漏识别或边界偏差：无

## C04 S001_OFF_001 [1875,1895)
> 据说“吃一枚大涌谷的黑鸡蛋能延寿7年”。

- 初版预测：大涌谷→POI/大涌谷 [1881,1884)
- 优化预测：大涌谷→POI/大涌谷 [1881,1884)
- 核验参考：大涌谷→POI/大涌谷 [1881,1884)
- 判断：延寿7年是传说中的寿命，不是行程时间。
- 误识别：无
- 漏识别或边界偏差：无

## C05 S001_VIS_001 [15,68)
> 从早云山乘坐箱根登山吊舱(rope way)到终点桃源台下车,走出站外的湖边即能看见一个徒步路线的标识牌。

- 初版预测：箱根→POI/箱根 [21,23)；桃源台→POI/桃源台 [40,43)；车→TRANSPORT/车 [44,45)；徒步→TRANSPORT/步行 [59,61)
- 优化预测：早云山→POI/早云山 [16,19)；箱根登山吊舱→TRANSPORT/箱根空中缆车 [21,27)；rope way→TRANSPORT/箱根空中缆车 [28,36)；桃源台→POI/桃源台 [40,43)；徒步→TRANSPORT/步行 [59,61)
- 核验参考：早云山→POI/早云山 [16,19)；箱根登山吊舱→TRANSPORT/箱根空中缆车 [21,27)；rope way→TRANSPORT/箱根空中缆车 [28,36)；桃源台→POI/桃源台 [40,43)；徒步→TRANSPORT/步行 [59,61)
- 判断：中英文同义表述有两处提及，均保留，不能按相同实体ID去重。
- 误识别：无
- 漏识别或边界偏差：无

## C06 S001_VIS_003 [448,501)
> 再乘缆车就可以到桃源台了,因为时间尚早,我们的酒店下午3点才能办入住,所以在桃源台乘海贼船游览芦之湖全景.

- 初版预测：缆车→TRANSPORT/缆车 [450,452)；车→TRANSPORT/车 [451,452)；桃源台→POI/桃源台 [456,459)；下午→TIME/下午 [473,475)；桃源台→POI/桃源台 [486,489)；船→TRANSPORT/船 [492,493)；芦之湖→POI/芦之湖 [495,498)
- 优化预测：缆车→TRANSPORT/缆车 [450,452)；桃源台→POI/桃源台 [456,459)；下午3点→TIME/下午3点 [473,477)；桃源台→POI/桃源台 [486,489)；海贼船→TRANSPORT/箱根海贼观光船 [490,493)；芦之湖→POI/芦之湖 [495,498)
- 核验参考：缆车→TRANSPORT/缆车 [450,452)；桃源台→POI/桃源台 [456,459)；下午3点→TIME/下午3点 [473,477)；桃源台→POI/桃源台 [486,489)；海贼船→TRANSPORT/箱根海贼观光船 [490,493)；芦之湖→POI/芦之湖 [495,498)
- 判断：同句两次桃源台分别定位；下午3点取完整时刻。
- 误识别：无
- 漏识别或边界偏差：无

## C07 S001_VIS_005 [6393,6441)
> 【路线1】元箱根港Motohakone-ko--箱根汤本Hakone-Yomoto(30min)

- 初版预测：箱根→POI/箱根 [6399,6401)；箱根→POI/箱根 [6417,6419)；箱根汤本→POI/箱根汤本 [6417,6421)
- 优化预测：元箱根港→POI/元箱根港 [6398,6402)；Motohakone-ko→POI/元箱根港 [6402,6415)；箱根汤本→POI/箱根汤本 [6417,6421)；Hakone-Yomoto→POI/箱根汤本 [6421,6434)；30min→TIME/30分钟 [6435,6440)
- 核验参考：元箱根港→POI/元箱根港 [6398,6402)；Motohakone-ko→POI/元箱根港 [6402,6415)；箱根汤本→POI/箱根汤本 [6417,6421)；Hakone-Yomoto→POI/箱根汤本 [6421,6434)；30min→TIME/30分钟 [6435,6440)
- 判断：中文与英文连续出现均为独立提及；仅按语料原样登记其拼写。
- 误识别：无
- 漏识别或边界偏差：无

## C08 S001_VIS_003 [285,368)
> 缆车先是在树林上方前行,突然就可以看到左手方向的地貌陡然改变,浓烟滚滚,往下看原来是硫磺谷,谷里遍地都是燃烧着浓烟的硫磺洞,那情景恍惚让人置身于人间地狱一般,很震撼.

- 初版预测：缆车→TRANSPORT/缆车 [285,287)；车→TRANSPORT/车 [286,287)
- 优化预测：缆车→TRANSPORT/缆车 [285,287)
- 核验参考：缆车→TRANSPORT/缆车 [285,287)；硫磺谷→POI/硫磺谷 [327,330)
- 判断：硫磺谷是描述性地点提及，但尚无已确认目录项；保留漏识别，不能擅自合并大涌谷。
- 误识别：无
- 漏识别或边界偏差：硫磺谷→POI/硫磺谷 [327,330)

## C09 S002_OFF_001 [737,787)
> Time: 5-7 hours full loop, 2.5-3.5 hours half loop

- 初版预测：无
- 优化预测：5-7 hours→TIME/5-7小时 [743,752)；2.5-3.5 hours→TIME/2.5-3.5小时 [764,777)
- 核验参考：5-7 hours→TIME/5-7小时 [743,752)；2.5-3.5 hours→TIME/2.5-3.5小时 [764,777)
- 判断：英文时长范围完整保留；两条备选线路时长不能合并。
- 误识别：无
- 漏识别或边界偏差：无

## C10 S002_OFF_001 [788,835)
> Begin at: Lower Yosemite Fall (shuttle stop #6)

- 初版预测：shuttle→TRANSPORT/巴士 [819,826)
- 优化预测：Lower Yosemite Fall→POI/Lower Yosemite Fall [798,817)；shuttle→TRANSPORT/巴士 [819,826)
- 核验参考：Lower Yosemite Fall→POI/Lower Yosemite Fall [798,817)；shuttle→TRANSPORT/巴士 [819,826)
- 判断：Lower Yosemite Fall是下瀑，不合并父级Yosemite Falls；站点号不是时间。
- 误识别：无
- 漏识别或边界偏差：无

## C11 S002_OFF_001 [1702,1879)
> From the Lower Yosemite Fall area, head west along the base of the Three Brothers rock formation, past Camp 4, eventually working your way through Yosemite Valley to El Capitan.

- 初版预测：Yosemite Valley→POI/Yosemite Valley [1849,1864)；El Capitan→POI/El Capitan [1868,1878)
- 优化预测：Lower Yosemite Fall→POI/Lower Yosemite Fall [1711,1730)；Three Brothers→POI/Three Brothers [1769,1783)；Camp 4→POI/Camp 4 [1805,1811)；Yosemite Valley→POI/Yosemite Valley [1849,1864)；El Capitan→POI/El Capitan [1868,1878)
- 核验参考：Lower Yosemite Fall→POI/Lower Yosemite Fall [1711,1730)；Three Brothers→POI/Three Brothers [1769,1783)；Camp 4→POI/Camp 4 [1805,1811)；Yosemite Valley→POI/Yosemite Valley [1849,1864)；El Capitan→POI/El Capitan [1868,1878)
- 判断：多个相邻景点和父子区域分别建实体，不以相似名称合并。
- 误识别：无
- 漏识别或边界偏差：无

## C12 S002_OFF_001 [3972,4017)
> Pets, bicycles, and strollers are prohibited.

- 初版预测：无
- 优化预测：bicycles→TRANSPORT/自行车 [3978,3986)
- 核验参考：bicycles→TRANSPORT/自行车 [3978,3986)
- 判断：禁止自行车仍为交通提及，不能据此推导可使用；strollers为婴儿推车，当前体系不纳入主要交通方式。
- 误识别：无
- 漏识别或边界偏差：无

## C13 S002_VIS_001 [3482,3587)
> 这里有充裕的停车位,视野宽阔的观景台,向山谷望去近在眼前的是酋长岩,山谷尽头是标志性的Half Doom,大约20分钟后我们就离开景区前往Yosemite view lodge办理入住,结束了第一天的景区游览。

- 初版预测：车→TRANSPORT/车 [3489,3490)；观景台→POI/观景台 [3497,3500)；20分钟→TIME/20分钟 [3537,3541)；景区→POI/景区 [3547,3549)；一天→TIME/一天 [3579,3581)；景区→POI/景区 [3582,3584)
- 优化预测：酋长岩→POI/El Capitan [3512,3515)；20分钟→TIME/20分钟 [3537,3541)；Yosemite view lodge→POI/Yosemite View Lodge [3551,3570)；第一天→TIME/第一天 [3578,3581)
- 核验参考：酋长岩→POI/El Capitan [3512,3515)；Half Doom→POI/Half Dome [3525,3534)；20分钟→TIME/20分钟 [3537,3541)；Yosemite view lodge→POI/Yosemite View Lodge [3551,3570)；第一天→TIME/第一天 [3578,3581)
- 判断：Half Doom疑似错拼，需要语义核验；当前自动程序不擅自纠错，预期保留漏识别。
- 误识别：无
- 漏识别或边界偏差：Half Doom→POI/Half Dome [3525,3534)

## C14 S002_VIS_003 [2331,2523)
> 登顶Half Dome的15 miles,除了最后的绳索以及登顶的喜悦,沿途的景色也是非常可圈可点,我们按官方建议沿Mist Trail上,John Muir Trail下,经过了Nevada Falls,Vernal Falls,Clark Point、Little Yosemite Valley等多个景点,即使不去Half Dome,徒步到这几个景点也是国家公园重点推荐的线路。

- 初版预测：Half Dome→POI/Half Dome [2333,2342)；Yosemite Valley→POI/Yosemite Valley [2466,2481)；景点→POI/景点 [2484,2486)；Half Dome→POI/Half Dome [2491,2500)；徒步→TRANSPORT/步行 [2501,2503)；景点→POI/景点 [2507,2509)；公园→POI/公园 [2513,2515)
- 优化预测：Half Dome→POI/Half Dome [2333,2342)；Mist Trail→POI/Mist Trail [2389,2399)；John Muir Trail→POI/John Muir Trail [2401,2416)；Nevada Falls→POI/Nevada Fall [2421,2433)；Vernal Falls→POI/Vernal Fall [2434,2446)；Clark Point→POI/Clark Point [2447,2458)；Little Yosemite Valley→POI/Little Yosemite Valley [2459,2481)；Half Dome→POI/Half Dome [2491,2500)；徒步→TRANSPORT/步行 [2501,2503)
- 核验参考：Half Dome→POI/Half Dome [2333,2342)；Mist Trail→POI/Mist Trail [2389,2399)；John Muir Trail→POI/John Muir Trail [2401,2416)；Nevada Falls→POI/Nevada Fall [2421,2433)；Vernal Falls→POI/Vernal Fall [2434,2446)；Clark Point→POI/Clark Point [2447,2458)；Little Yosemite Valley→POI/Little Yosemite Valley [2459,2481)；Half Dome→POI/Half Dome [2491,2500)；徒步→TRANSPORT/步行 [2501,2503)
- 判断：距离15 miles排除；多个步道与瀑布分别登记，保留两次Half Dome。
- 误识别：无
- 漏识别或边界偏差：无

## C15 S002_VIS_005 [191,228)
> 同时风景很好的的Glacie Point和Tioga Road都尚未开放。

- 初版预测：Tioga Road→POI/Tioga Road [212,222)
- 优化预测：Tioga Road→POI/Tioga Road [212,222)
- 核验参考：Glacie Point→POI/Glacier Point [199,211)；Tioga Road→POI/Tioga Road [212,222)
- 判断：Glacie Point疑似错拼，当前不自动合并；不能因道路未开放就删除实体。
- 误识别：无
- 漏识别或边界偏差：Glacie Point→POI/Glacier Point [199,211)

## C16 S002_VIS_005 [872,900)
> 另一个惊喜来自于酋长岩东壁的马尾瀑布horsetail。

- 初版预测：瀑布→POI/瀑布 [888,890)
- 优化预测：酋长岩→POI/El Capitan [880,883)；马尾瀑布→POI/Horsetail Fall [886,890)
- 核验参考：酋长岩→POI/El Capitan [880,883)；马尾瀑布→POI/Horsetail Fall [886,890)；horsetail→POI/Horsetail Fall [890,899)
- 判断：horsetail作为已给中文名后的英文简称，词典未覆盖，记录漏识别。
- 误识别：无
- 漏识别或边界偏差：horsetail→POI/Horsetail Fall [890,899)

## C17 S003_OFF_001 [31,139)
> Hike 19km in 2 days along Grand Cliff Top Walk, which seamlessly links Wentworth Falls, Leura, and Katoomba.

- 初版预测：Hike→TRANSPORT/步行 [31,35)；Grand Cliff Top Walk→POI/Grand Cliff Top Walk [57,77)；Walk→TRANSPORT/步行 [73,77)；Wentworth Falls→POI/Wentworth Falls [102,117)；Leura→POI/Leura [119,124)；Katoomba→POI/Katoomba [130,138)
- 优化预测：Hike→TRANSPORT/步行 [31,35)；2 days→TIME/2天 [44,50)；Grand Cliff Top Walk→POI/Grand Cliff Top Walk [57,77)；Wentworth Falls→POI/Wentworth Falls [102,117)；Leura→POI/Leura [119,124)；Katoomba→POI/Katoomba [130,138)
- 核验参考：Hike→TRANSPORT/步行 [31,35)；2 days→TIME/2天 [44,50)；Grand Cliff Top Walk→POI/Grand Cliff Top Walk [57,77)；Wentworth Falls→POI/Wentworth Falls [102,117)；Leura→POI/Leura [119,124)；Katoomba→POI/Katoomba [130,138)
- 判断：19km是距离；Wentworth Falls在本句为接驳镇区，不直接合并瀑布景点。
- 误识别：无
- 漏识别或边界偏差：无

## C18 S003_OFF_001 [3787,3806)
> 巴士每天上午9点至下午5点每小时一班。

- 初版预测：巴士→TRANSPORT/巴士 [3787,3789)；上午→TIME/上午 [3791,3793)；下午→TIME/下午 [3796,3798)
- 优化预测：巴士→TRANSPORT/巴士 [3787,3789)；上午9点→TIME/上午9点 [3791,3795)；下午5点→TIME/下午5点 [3796,3800)
- 核验参考：巴士→TRANSPORT/巴士 [3787,3789)；上午9点→TIME/上午9点 [3791,3795)；下午5点→TIME/下午5点 [3796,3800)；每小时→TIME/每小时 [3800,3803)
- 判断：两端时刻独立提及；每小时是班次间隔，当前规则缺少该表达。
- 误识别：无
- 漏识别或边界偏差：每小时→TIME/每小时 [3800,3803)

## C19 S003_OFF_001 [3430,3455)
> 从特定的有利位置,您可以看到三姐妹峰在夜空下亮起。

- 初版预测：三姐妹峰→POI/三姐妹峰 [3444,3448)
- 优化预测：三姐妹峰→POI/三姐妹峰 [3444,3448)
- 核验参考：三姐妹峰→POI/三姐妹峰 [3444,3448)
- 判断：夜空是环境描述，不标为明确时间节点。
- 误识别：无
- 漏识别或边界偏差：无

## C20 S003_VIS_005 [198,247)
> 我们从悉尼驱车来到蓝山公园的伊丽莎白女王观景台(Queen Elizabeth Lookout)。

- 初版预测：悉尼→POI/悉尼 [201,203)；驱车→TRANSPORT/自驾 [203,205)；车→TRANSPORT/车 [204,205)；公园→POI/公园 [209,211)；观景台→POI/观景台 [218,221)
- 优化预测：悉尼→POI/悉尼 [201,203)；驱车→TRANSPORT/自驾 [203,205)；蓝山公园→POI/蓝山国家公园 [207,211)；伊丽莎白女王观景台→POI/伊丽莎白女王观景台 [212,221)；Queen Elizabeth Lookout→POI/伊丽莎白女王观景台 [222,245)
- 核验参考：悉尼→POI/悉尼 [201,203)；驱车→TRANSPORT/自驾 [203,205)；蓝山公园→POI/蓝山国家公园 [207,211)；伊丽莎白女王观景台→POI/伊丽莎白女王观景台 [212,221)；Queen Elizabeth Lookout→POI/伊丽莎白女王观景台 [222,245)
- 判断：中英文同名观景台合并目录ID，两次提及保留。
- 误识别：无
- 漏识别或边界偏差：无

## C21 S003_VIS_002 [1957,2029)
> 这几天我们坐车都是从悉尼中央火车站中转的,这次一样,先坐BUS到悉尼中央火车站,然后乘坐Blue Mountains Line铁路线到达蓝山公园

- 初版预测：车→TRANSPORT/车 [1963,1964)；悉尼→POI/悉尼 [1967,1969)；火车→TRANSPORT/列车 [1971,1973)；车→TRANSPORT/车 [1972,1973)；BUS→TRANSPORT/巴士 [1985,1988)；悉尼→POI/悉尼 [1989,1991)；火车→TRANSPORT/列车 [1993,1995)；车→TRANSPORT/车 [1994,1995)；公园→POI/公园 [2027,2029)
- 优化预测：悉尼中央火车站→POI/悉尼中央火车站 [1967,1974)；BUS→TRANSPORT/巴士 [1985,1988)；悉尼中央火车站→POI/悉尼中央火车站 [1989,1996)；Blue Mountains Line→TRANSPORT/Blue Mountains Line [2001,2020)；蓝山公园→POI/蓝山国家公园 [2025,2029)
- 核验参考：悉尼中央火车站→POI/悉尼中央火车站 [1967,1974)；BUS→TRANSPORT/巴士 [1985,1988)；悉尼中央火车站→POI/悉尼中央火车站 [1989,1996)；Blue Mountains Line→TRANSPORT/Blue Mountains Line [2001,2020)；蓝山公园→POI/蓝山国家公园 [2025,2029)
- 判断：坐车没有明确交通制式，不强制标为自驾；火车站中的火车不重复标为交通方式。
- 误识别：无
- 漏识别或边界偏差：无

## C22 S003_VIS_004 [2790,2855)
> 我们选择了Sydney HeliTours,这家公司提供很多行程,我们选择了悉尼 - 蓝山的单程行程,飞行时间大概在45分钟左右。

- 初版预测：悉尼→POI/悉尼 [2828,2830)；45分钟→TIME/45分钟 [2848,2852)
- 优化预测：悉尼→POI/悉尼 [2828,2830)；蓝山→POI/蓝山国家公园 [2833,2835)；45分钟→TIME/45分钟 [2848,2852)
- 核验参考：悉尼→POI/悉尼 [2828,2830)；蓝山→POI/蓝山国家公园 [2833,2835)；45分钟→TIME/45分钟 [2848,2852)
- 判断：Sydney HeliTours是运营商名称，不是悉尼地点提及；检查英文词边界仍可能不够。
- 误识别：无
- 漏识别或边界偏差：无

## C23 S003_VIS_004 [6354,6418)
> 另一款The Lost Shiraz更有趣一点,单宁味更重,红宝石颜色的酒液带有很复杂的黑加仑、黑莓和香草的气味,层次非常丰富。

- 初版预测：无
- 优化预测：无
- 核验参考：无
- 判断：一点表示程度，不能识别为凌晨或下午1点。
- 误识别：无
- 漏识别或边界偏差：无

## C24 S003_OFF_001 [5105,5112)
> 水疗盛宴下午茶

- 初版预测：下午→TIME/下午 [5109,5111)
- 优化预测：无
- 核验参考：无
- 判断：下午茶为餐饮名称，不能把下午切出作时间。
- 误识别：无
- 漏识别或边界偏差：无
