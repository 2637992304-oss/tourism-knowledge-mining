"""由语料核对的地点词表与通用行进子句规则；不创建 DHT 的实体 ID。"""
import re

LEXICONS = {
    "S001": ["早云山", "桃源台", "芦之湖", "金太郎展望台", "姥子缆车站",
             "姥子站", "大涌谷", "强罗", "箱根汤本", "宫之下", "小田原",
             "箱根町港", "元箱根港", "芦之湖花织酒店"],
    "S003": ["三姐妹峰", "Jenolan Caves珍罗兰洞", "珍罗兰洞",
             "温特沃斯(Wentworth)瀑布野餐区", "杰米森瞭望台", "弗莱彻瞭望台",
             "温特沃斯(Wentworth)瀑布步道",
             "劳森黑凤头鹦鹉面包店", "Josophan's Fine Chocolates",
             "凯特·索迪画廊", "布莱克希思(Blackheath)", "埃文斯瞭望台",
             "大峡谷步道", "戈维茨跳跃瞭望台", "山地文化啤酒公司",
             "风景世界(Scenic World)", "卡通巴瀑布自然保护区夜间灯光步道"],
}
MOTION = re.compile(r"从|来到|到达|到终点|前往|向|驱车|走进|去|出发|(?<!看)到")
NEGATIVE = re.compile(r"没有去|没去|不去|未去|打算|计划|如果|或者|可以走岔路")
BUCKET = {"早晨": "morning", "上午": "morning", "中午": "noon",
          "下午": "afternoon", "晚上": "evening", "傍晚": "evening"}


def extract(doc, make_step, start=0, end=None, inherit_bucket=False):
    text = doc["text"]
    end = len(text) if end is None else end
    lexicon = sorted(LEXICONS[doc["scenic_id"]], key=len, reverse=True)
    pattern = re.compile("|".join(map(re.escape, lexicon)))
    steps, rejected = [], []
    bucket, time_text = "unknown", None
    for sentence in re.finditer(r"[^。！？\n]+", text[start:end]):
        base = start + sentence.start()
        content = sentence[0]
        heading = re.match(r"(早晨|上午|中午|下午|晚上|傍晚)[:：]", content)
        if heading and inherit_bucket:
            time_text, bucket = heading[1], BUCKET[heading[1]]
            continue
        if inherit_bucket and (NEGATIVE.search(content) or "图片来源" in content
                               or (len(content) < 40 and not re.search(r"推荐|享用|不容错过|被公认为|理想场所", content))):
            continue
        for clause in re.finditer(r"[^,，;；]+", content):
            fragment = clause[0]
            matches = list(pattern.finditer(fragment))
            if not matches or (not inherit_bucket and not MOTION.search(fragment)):
                continue
            if re.search(r"只有.*直通|可以看到|眺望.*景色|快到", fragment):
                continue
            if NEGATIVE.search(fragment):
                rejected.append({"reason": "optional_or_negated", "text": fragment,
                                 "start": base + clause.start()})
                continue
            # 从 A 到 B 保留出发点和终点；一般行进描述取最后一个地点，
            # 避免把“眺望芦之湖的金太郎展望台”拆成两站。
            chosen = matches if inherit_bucket else ([matches[0], matches[-1]] if not steps and fragment.lstrip().startswith("从")
                      and len(matches) > 1 else [matches[-1]])
            for hit in chosen:
                if steps and steps[-1]["poi_name"] == hit[0]:
                    continue
                absolute = base + clause.start()
                step = make_step(doc, len(steps) + 1, hit[0], fragment.strip(),
                                 absolute, absolute + len(fragment))
                if inherit_bucket:
                    step.update(time_bucket=bucket, time_text=time_text)
                steps.append(step)
    return steps, rejected
