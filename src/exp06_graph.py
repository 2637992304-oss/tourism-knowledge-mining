"""实验 6：融合路线、实体和条件建议；缺少上游文件时标记阶段性图谱。"""

import argparse
import csv
import hashlib
import json
from pathlib import Path


def load(path, field, version):
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0" or data.get("corpus_version") != version:
        raise ValueError(f"{path} 与路线的版本不一致")
    if not isinstance(data.get(field), list):
        raise ValueError(f"{path} 缺少数组 {field}")
    if field == "entity_catalog" and not isinstance(data.get("mentions"), list):
        raise ValueError(f"{path} 缺少数组 mentions")
    return data


def name_id(scenic_id, name):
    digest = hashlib.sha1(f"{scenic_id}:{name}".encode("utf-8")).hexdigest()[:12]
    return f"N_POI_{scenic_id}_{digest}"


def build(routes_data, registry, entities=None, advice=None):
    version = routes_data["corpus_version"]
    if routes_data.get("schema_version") != "1.0" or not isinstance(routes_data.get("routes"), list):
        raise ValueError("路线文件结构错误")
    nodes, edges = {}, {}

    def node(node_id, kind, name, scenic_id, refs, attrs):
        if node_id in nodes:
            if nodes[node_id]["node_type"] != kind:
                raise ValueError(f"节点 ID 冲突：{node_id}")
            nodes[node_id]["source_refs"] = sorted(set(nodes[node_id]["source_refs"] + refs))
            return
        nodes[node_id] = {"node_id": node_id, "node_type": kind, "name": name,
                          "scenic_id": scenic_id, "source_refs": refs, "attributes": attrs}

    def edge(edge_id, source, target, relation, refs, attrs=None):
        if edge_id in edges:
            raise ValueError(f"边 ID 冲突：{edge_id}")
        edges[edge_id] = {"edge_id": edge_id, "source": source, "target": target,
                          "relation": relation, "source_refs": refs, "attributes": attrs or {}}

    scenics = {item["scenic_id"]: item["scenic_name"] for item in registry["scenics"]}
    if len(scenics) != len(registry["scenics"]):
        raise ValueError("景区 ID 重复")
    full_catalog = (entities or {}).get("entity_catalog", [])
    if len({item["entity_id"] for item in full_catalog}) != len(full_catalog):
        raise ValueError("实体 ID 重复")
    inactive = {item["entity_id"] for item in full_catalog if not item.get("active", True)}
    catalog = {item["entity_id"]: item for item in full_catalog if item["entity_id"] not in inactive}
    mentions = [m for m in (entities or {}).get("mentions", []) if m["entity_id"] not in inactive]
    entity_nodes = {}
    for entity_id, item in catalog.items():
        scenic_id, kind = item["scenic_id"], item["entity_type"]
        if scenic_id not in scenics or kind not in ("POI", "TRANSPORT", "TIME"):
            raise ValueError(f"实体景区或类型错误：{entity_id}")
        refs = [m["span"] for m in mentions if m["entity_id"] == entity_id]
        nid = f"N_ENTITY_{entity_id}"
        entity_nodes[entity_id] = nid
        node(nid, kind, item["canonical_name"], scenic_id,
             sorted({r["doc_id"] for r in refs}),
             {"entity_id": entity_id, "aliases": item.get("aliases", []),
              "alignment_status": "aligned", "scope": item.get("scope"),
              "note": item.get("note"), "evidence": refs})
    for mention in mentions:
        if mention["entity_id"] not in catalog:
            raise ValueError(f"提及引用不存在的实体：{mention['entity_id']}")
    aliases = {}
    ambiguous = set()
    for item in catalog.values():
        if item["entity_type"] != "POI":
            continue
        for alias in [item["canonical_name"], *item.get("aliases", [])]:
            key = (item["scenic_id"], alias)
            if key in ambiguous:
                continue
            if key in aliases and aliases[key] != item["entity_id"]:
                aliases[key] = None
                ambiguous.add(key)
            elif key not in aliases:
                aliases[key] = item["entity_id"]

    route_ids = set()
    for route in routes_data["routes"]:
        scenic_id, route_id, doc_id = route["scenic_id"], route["route_id"], route["doc_id"]
        if route_id in route_ids or not route["steps"]:
            raise ValueError(f"路线重复或为空：{route_id}")
        route_ids.add(route_id)
        if [s["step_no"] for s in route["steps"]] != list(range(1, len(route["steps"]) + 1)):
            raise ValueError(f"路线步骤不连续：{route_id}")
        if scenic_id not in scenics:
            raise ValueError(f"未知景区：{scenic_id}")
        sid, rid = f"N_SCENIC_{scenic_id}", f"N_ROUTE_{route_id}"
        node(sid, "SCENIC", scenics[scenic_id], scenic_id, [], {})
        node(rid, "ROUTE", route["route_name"], scenic_id, [doc_id],
             {"route_id": route_id, "text_type": route["text_type"],
              "scope_note": route.get("scope_note")})
        edge(f"EDGE_HAS_ROUTE_{route_id}", sid, rid, "HAS_ROUTE", [doc_id])
        previous = None
        for step in route["steps"]:
            no = step["step_no"]
            step_id = f"N_STEP_{route_id}_{no:03d}"
            node(step_id, "STEP", step["activity"], scenic_id, [doc_id],
                 {"route_id": route_id, "step_no": no, "time_bucket": step["time_bucket"],
                  "time_text": step["time_text"], "duration_minutes": step["duration_minutes"],
                  "evidence": step["evidence"]})
            edge(f"EDGE_HAS_STEP_{route_id}_{no:03d}", rid, step_id, "HAS_STEP", [doc_id])
            if previous:
                edge(f"EDGE_NEXT_STEP_{route_id}_{no-1:03d}", previous, step_id,
                     "NEXT_STEP", [doc_id], {"route_id": route_id})
            previous = step_id
            entity_id = step.get("poi_entity_id") or aliases.get((scenic_id, step["poi_name"]))
            if entity_id and entity_id not in catalog:
                raise ValueError(f"路线引用不存在的实体：{entity_id}")
            if entity_id and catalog[entity_id]["scenic_id"] != scenic_id:
                raise ValueError(f"路线实体跨景区：{entity_id}")
            canonical = catalog[entity_id]["canonical_name"] if entity_id else step["poi_name"]
            poi_id = entity_nodes[entity_id] if entity_id else name_id(scenic_id, canonical)
            node(poi_id, "POI", canonical, scenic_id, [doc_id],
                 {"entity_id": entity_id, "alignment_status": "aligned" if entity_id else "pending"})
            edge(f"EDGE_VISITS_{route_id}_{no:03d}", step_id, poi_id, "VISITS",
                 [doc_id], {"evidence": step["evidence"]})
            for mention in mentions:
                span = mention["span"]
                item = catalog[mention["entity_id"]]
                if item["entity_type"] not in ("TIME", "TRANSPORT") or span["doc_id"] != doc_id:
                    continue
                if item["scenic_id"] != scenic_id:
                    raise ValueError("实体提及跨景区")
                if any(ref["start"] <= span["start"] and span["end"] <= ref["end"] for ref in step["evidence"]):
                    relation = "AT_TIME" if item["entity_type"] == "TIME" else "USES_TRANSPORT"
                    edge(f"EDGE_{relation}_{route_id}_{no:03d}_{mention['mention_id']}",
                         step_id, entity_nodes[mention["entity_id"]], relation, [doc_id],
                         {"evidence": [span]})

    for item in (advice or {}).get("advice", []):
        scenic_id, advice_id, doc_id = item["scenic_id"], item["advice_id"], item["doc_id"]
        if scenic_id not in scenics:
            raise ValueError(f"建议引用未知景区：{scenic_id}")
        sid = f"N_SCENIC_{scenic_id}"
        node(sid, "SCENIC", scenics[scenic_id], scenic_id, [], {})
        condition_id, advice_node_id = f"N_CONDITION_{advice_id}", f"N_ADVICE_{advice_id}"
        node(condition_id, "CONDITION", item["condition_text"], scenic_id, [doc_id],
             {"advice_id": advice_id, "condition_type": item["condition_type"],
              "visitor_types": item.get("visitor_types", []), "evidence": item["evidence"]})
        node(advice_node_id, "ADVICE", item["suggestion_text"], scenic_id, [doc_id],
             {"advice_id": advice_id, "method": item.get("method"), "evidence": item["evidence"]})
        edge(f"EDGE_HAS_ADVICE_{advice_id}", sid, advice_node_id, "HAS_ADVICE", [doc_id])
        edge(f"EDGE_TRIGGERS_{advice_id}", condition_id, advice_node_id, "TRIGGERS", [doc_id])
        for entity_id in item.get("related_entity_ids", []):
            if entity_id not in catalog:
                raise ValueError(f"建议引用不存在的实体：{entity_id}")
            entity = catalog[entity_id]
            if entity["scenic_id"] != scenic_id:
                raise ValueError(f"建议实体跨景区：{entity_id}")
            if entity["entity_type"] != "POI":
                continue
            poi_id = entity_nodes[entity_id]
            node(poi_id, "POI", entity["canonical_name"], scenic_id, [doc_id],
                 {"entity_id": entity_id, "alignment_status": "aligned"})
            edge(f"EDGE_APPLIES_TO_{advice_id}_{entity_id}", advice_node_id, poi_id,
                 "APPLIES_TO", [doc_id])

    if any(e["source"] not in nodes or e["target"] not in nodes for e in edges.values()):
        raise ValueError("存在悬空边")
    used = {endpoint for e in edges.values() for endpoint in (e["source"], e["target"])}
    unused = [nid for nid in nodes if nid.startswith("N_ENTITY_") and nid not in used]
    for nid in unused:
        del nodes[nid]
    missing = [name for name, value in (("entities.json", entities), ("advice.json", advice)) if value is None]
    return {"schema_version": "1.0", "corpus_version": version, "graph_version": "v1",
            "completion_status": "route_stage" if entities is None else "entity_route_fused" if advice is None else "fused",
            "inactive_entities_skipped": sorted(inactive),
            "unused_entity_nodes_filtered": unused,
            "missing_inputs": missing, "nodes": list(nodes.values()), "edges": list(edges.values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs-dir", type=Path, default=Path("data/outputs"))
    parser.add_argument("--registry", type=Path, default=Path("data/processed/scenic_registry.json"))
    parser.add_argument("--output", type=Path, default=Path("data/outputs/graph.json"))
    parser.add_argument("--require-complete", action="store_true", help="正式验收：缺少实体或建议时返回非零状态")
    parser.add_argument("--require-entities", action="store_true", help="核心验收：要求真实实体已接入；条件建议可后续补充")
    args = parser.parse_args()
    try:
        routes = json.loads((args.outputs_dir / "routes.json").read_text(encoding="utf-8"))
        registry = json.loads(args.registry.read_text(encoding="utf-8"))
        entities = load(args.outputs_dir / "entities.json", "entity_catalog", routes["corpus_version"])
        advice = load(args.outputs_dir / "advice.json", "advice", routes["corpus_version"])
        graph = build(routes, registry, entities, advice)
        if args.require_entities and entities is None:
            raise ValueError("核心融合缺少 entities.json")
        if args.require_complete and graph["missing_inputs"]:
            raise ValueError("正式融合缺少输入：" + ", ".join(graph["missing_inputs"]))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for key in ("nodes", "edges"):
            path = args.output.with_name(f"{args.output.stem}_{key}.csv")
            if graph[key]:
                with path.open("w", encoding="utf-8-sig", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=list(graph[key][0]))
                    writer.writeheader()
                    for item in graph[key]:
                        writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                                         for k, v in item.items()})
        print(json.dumps({"status": graph["completion_status"], "nodes": len(graph["nodes"]),
                          "edges": len(graph["edges"]), "missing_inputs": graph["missing_inputs"]},
                         ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(1, f"图谱构建失败：{exc}\n")


if __name__ == "__main__":
    main()
