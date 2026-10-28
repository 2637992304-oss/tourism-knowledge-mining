"""可复现的路线开发集评估、来源检查与同景区对比。"""
import json
from collections import Counter
from pathlib import Path


def lcs(a, b):
    row = [0] * (len(b) + 1)
    for x in a:
        new = [0]
        for j, y in enumerate(b):
            new.append(row[j] + 1 if x == y else max(new[-1], row[j + 1]))
        row = new
    return row[-1]


def main():
    routes = json.loads(Path("data/outputs/routes.json").read_text(encoding="utf-8"))["routes"]
    gold = json.loads(Path("results/checks/exp03_gold.json").read_text(encoding="utf-8"))
    docs = {d["doc_id"]: d for d in map(json.loads, Path("data/processed/corpus.jsonl").read_text(encoding="utf-8").splitlines())}
    metrics, comparisons = [], []
    refs = 0
    for route in routes:
        predicted = [s["poi_name"] for s in route["steps"]]
        expected = gold["routes"][route["route_id"]]
        hits = sum((Counter(predicted) & Counter(expected)).values())
        ordered = lcs(predicted, expected)
        metrics.append({"route_id": route["route_id"], "predicted": len(predicted),
                        "gold": len(expected), "matched": hits,
                        "precision": hits / len(predicted), "recall": hits / len(expected),
                        "ordered_matched": ordered,
                        "sequence_recall": ordered / len(expected),
                        "missing": list((Counter(expected) - Counter(predicted)).elements())})
        for s in route["steps"]:
            assert any(s["poi_name"] in ref["text"] for ref in s["evidence"]) or s["poi_entity_id"], s
            for ref in s["evidence"]:
                assert docs[ref["doc_id"]]["text"][ref["start"]:ref["end"]] == ref["text"]
                refs += 1
    for scenic in sorted({r["scenic_id"] for r in routes}):
        off = next(r for r in routes if r["scenic_id"] == scenic and r["text_type"] == "official_route")
        vis = next(r for r in routes if r["scenic_id"] == scenic and r["text_type"] == "visitor_diary")
        a, b = [set(s["poi_name"] for s in r["steps"]) for r in (off, vis)]
        comparisons.append({"scenic_id": scenic, "official_unique": len(a), "visitor_unique": len(b),
                            "shared": sorted(a & b), "jaccard": len(a & b) / len(a | b),
                            "ordered_overlap": lcs([s["poi_name"] for s in off["steps"]],
                                                   [s["poi_name"] for s in vis["steps"]]),
                            "official_time_known": sum(s["time_bucket"] != "unknown" for s in off["steps"]),
                            "official_steps": len(off["steps"]),
                            "visitor_time_known": sum(s["time_bucket"] != "unknown" for s in vis["steps"]),
                            "visitor_steps": len(vis["steps"])})
    result = {"dataset_role": "development", "annotation_note": gold["annotation_note"],
              "routes": metrics, "evidence_checked": refs, "comparisons": comparisons}
    Path("results/checks/exp03_metrics.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"routes": len(metrics), "matched": sum(m["matched"] for m in metrics),
                      "gold": sum(m["gold"] for m in metrics), "evidence_checked": refs}))


if __name__ == "__main__":
    main()
