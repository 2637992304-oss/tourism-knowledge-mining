"""实验 3：抽取箱根官方时间表和游客实走路线，保留原文位置。"""

import argparse
import json
import re
from pathlib import Path
from exp03_rules import extract
from exp03_alignment import align_poi

OFFICIAL_ID = "S001_OFF_001"
VISITOR_ID = "S001_VIS_001"
POIS = ("箱根雕刻森林美术馆", "箱根登山名产店 汤本店", "箱根汤本站", "箱根汤本",
        "早云山站", "箱根神社", "大涌谷", "芦之湖", "新宿")
HEADING = re.compile(r"(?m)^(\d{1,2}):(\d{2})\s*~\s*([^\n]+)")


def load_corpus(path):
    docs = {}
    versions = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        doc = json.loads(line)
        for field in ("doc_id", "scenic_id", "text_type", "text", "schema_version", "corpus_version"):
            if field not in doc:
                raise ValueError(f"语料缺少 {field}")
        if doc["schema_version"] != "1.0" or not isinstance(doc["text"], str):
            raise ValueError(f"语料格式错误：{doc['doc_id']}")
        if doc["doc_id"] in docs:
            raise ValueError(f"重复 doc_id：{doc['doc_id']}")
        docs[doc["doc_id"]] = doc
        versions.add(doc["corpus_version"])
    if len(versions) != 1:
        raise ValueError("语料版本不唯一")
    for doc_id in (OFFICIAL_ID, VISITOR_ID):
        if doc_id not in docs:
            raise ValueError(f"缺少所选文档：{doc_id}")
    return docs, versions.pop()


def make_step(doc, no, poi, activity, start, end, time_text=None):
    hour = int(time_text.split(":")[0]) if time_text else None
    bucket = ("morning" if hour < 11 else "noon" if hour < 13
              else "afternoon" if hour < 18 else "evening") if hour is not None else "unknown"
    return {
        "step_no": no, "time_bucket": bucket, "time_text": time_text,
        "poi_entity_id": None, "poi_name": poi, "raw_poi_name": poi, "activity": activity,
        "duration_minutes": None,
        "evidence": [{"doc_id": doc["doc_id"], "start": start, "end": end,
                      "text": doc["text"][start:end]}],
    }


def make_route(doc, name, matches):
    return {
        "route_id": f"R_{doc['doc_id']}_01", "scenic_id": doc["scenic_id"],
        "doc_id": doc["doc_id"], "text_type": doc["text_type"],
        "route_name": name, "steps": matches, "scope_note": doc.get("scope_note"),
    }


def official_route(doc):
    text = doc["text"]
    steps = []
    for match in HEADING.finditer(text):
        hour, minute = int(match[1]), int(match[2])
        if hour > 23 or minute > 59:
            continue
        title = match[3].strip()
        destination = title.split("前往", 1)[-1] if "前往" in title else title
        poi = next((name for name in POIS if name in destination), None)
        if poi is None:
            body = text[match.end():match.end() + 130]
            poi = next((name for name in POIS if name in body), None)
        if poi:
            step = make_step(doc, len(steps) + 1, poi, title,
                             match.start(), match.end(), f"{match[1]}:{match[2]}")
            if poi not in title:
                pos = text.index(poi, match.end(), match.end() + 130)
                step["evidence"].append({"doc_id": doc["doc_id"], "start": pos,
                                         "end": pos + len(poi), "text": poi})
            steps.append(step)
    if not steps:
        raise ValueError("官方路线未找到时间标题")
    return make_route(doc, "初游箱根当日往返路线", steps)


def visitor_route(doc):
    steps, _ = extract(doc, make_step)
    return make_route(doc, doc["source_title"] + "（行进片段）", steps)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=Path("data/processed/corpus.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/outputs/routes.json"))
    parser.add_argument("--entities", type=Path, default=Path("data/outputs/entities.json"))
    args = parser.parse_args()
    try:
        docs, version = load_corpus(args.corpus)
        routes = [official_route(docs[OFFICIAL_ID]), visitor_route(docs[VISITOR_ID])]
        blue = docs["S003_OFF_001"]
        start, end = blue["text"].index("早晨:咖啡"), blue["text"].index("到达那里")
        steps, _ = extract(blue, make_step, start, end, inherit_bucket=True)
        routes.append(make_route(blue, "蓝山一日游时间分段路线", steps))
        routes.append(visitor_route(docs["S003_VIS_001"]))
        if args.entities.exists():
            entities = json.loads(args.entities.read_text(encoding="utf-8"))
            if entities.get("schema_version") != "1.0" or entities.get("corpus_version") != version:
                raise ValueError("实体与语料版本不一致")
            for route in routes:
                for step in route["steps"]:
                    entity, method = align_poi(step["raw_poi_name"], route["scenic_id"],
                                               entities["entity_catalog"])
                    step["alignment_method"] = method
                    if entity:
                        step["poi_entity_id"] = entity["entity_id"]
                        step["poi_name"] = entity["canonical_name"]
        for route in routes:
            if not route["steps"]:
                raise ValueError(f"路线为空：{route['route_id']}")
            doc = docs[route["doc_id"]]
            for no, step in enumerate(route["steps"], 1):
                if step["step_no"] != no:
                    raise ValueError("步骤序号不连续")
                for ref in step["evidence"]:
                    if doc["text"][ref["start"]:ref["end"]] != ref["text"]:
                        raise ValueError(f"原文位置错误：{route['route_id']} 第 {no} 步")
        result = {"schema_version": "1.0", "corpus_version": version, "routes": routes}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"routes": len(routes), "steps": [len(r["steps"]) for r in routes],
                          "output": str(args.output)}, ensure_ascii=False))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(1, f"路线抽取失败：{exc}\n")


if __name__ == "__main__":
    main()
