"""核验正式图谱的连通性、来源、步骤顺序，保存真实查询证据。"""
import json
from collections import Counter
from pathlib import Path
import networkx as nx


def main():
    data = json.loads(Path("data/outputs/graph.json").read_text(encoding="utf-8"))
    routes = json.loads(Path("data/outputs/routes.json").read_text(encoding="utf-8"))["routes"]
    docs = {d["doc_id"]: d for d in map(json.loads, Path("data/processed/corpus.jsonl").read_text(encoding="utf-8").splitlines())}
    assert {d["corpus_version"] for d in docs.values()} == {data["corpus_version"]}, "图谱与语料版本不同"
    graph = nx.MultiDiGraph()
    for node in data["nodes"]:
        assert node["node_id"] not in graph, "重复节点"
        graph.add_node(node["node_id"], **node)
        for ref in node["source_refs"]:
            assert ref in docs, "节点来源不存在"
        for ref in node["attributes"].get("evidence", []):
            assert docs[ref["doc_id"]]["text"][ref["start"]:ref["end"]] == ref["text"]
    for edge in data["edges"]:
        assert edge["source"] in graph and edge["target"] in graph, "悬空边"
        assert all(ref in docs for ref in edge["source_refs"]), "边来源不存在"
        graph.add_edge(edge["source"], edge["target"], key=edge["edge_id"], **edge)
        for ref in edge["attributes"].get("evidence", []):
            assert docs[ref["doc_id"]]["text"][ref["start"]:ref["end"]] == ref["text"]
    next_edges = [e for e in data["edges"] if e["relation"] == "NEXT_STEP"]
    chain_results = []
    for route in routes:
        rid = route["route_id"]
        ids = [f"N_STEP_{rid}_{s['step_no']:03d}" for s in route["steps"]]
        chain = nx.DiGraph()
        chain.add_nodes_from(ids)
        chain.add_edges_from((e["source"], e["target"]) for e in next_edges if e["attributes"]["route_id"] == rid)
        assert nx.is_directed_acyclic_graph(chain)
        assert list(nx.topological_sort(chain)) == ids, "步骤顺序错误"
        assert chain.number_of_edges() == len(ids) - 1
        assert len(ids) == 1 or nx.is_weakly_connected(chain)
        chain_results.append({"route_id": rid, "steps": len(ids), "next_edges": chain.number_of_edges()})
    route_nodes = [target for _, target, attr in graph.out_edges("N_SCENIC_S001", data=True)
                   if attr["relation"] == "HAS_ROUTE"]
    steps = [target for _, target, attr in graph.out_edges("N_ROUTE_R_S001_OFF_001_01", data=True)
             if attr["relation"] == "HAS_STEP"]
    steps.sort(key=lambda key: graph.nodes[key]["attributes"]["step_no"])
    ordered_pois = [graph.nodes[target]["name"] for step in steps
                    for _, target, attr in graph.out_edges(step, data=True) if attr["relation"] == "VISITS"]
    queries = [
        {"query": "S001 的路线", "result": [graph.nodes[key]["attributes"]["route_id"] for key in route_nodes]},
        {"query": "官方箱根路线的有序地点", "result": ordered_pois},
        {"query": "访问大涌谷的步骤", "result": [e["source"] for e in data["edges"]
         if e["relation"] == "VISITS" and graph.nodes[e["target"]]["name"] == "大涌谷"]},
        {"query": "条件建议", "result": [n["node_id"] for n in data["nodes"] if n["node_type"] == "ADVICE"],
         "availability": "missing_upstream" if "advice.json" in data["missing_inputs"] else "available"},
    ]
    result = {"graph_status": data["completion_status"], "missing_inputs": data["missing_inputs"],
              "nodes": graph.number_of_nodes(), "edges": graph.number_of_edges(),
              "node_types": dict(Counter(n["node_type"] for n in data["nodes"])),
              "relations": dict(Counter(e["relation"] for e in data["edges"])),
              "isolated_nodes": list(nx.isolates(graph)),
              "weak_components": nx.number_weakly_connected_components(graph),
              "route_checks": chain_results, "queries": queries, "checks_passed": True}
    Path("results/checks/exp06_quality.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"nodes": graph.number_of_nodes(), "edges": graph.number_of_edges(),
                      "route_checks": len(chain_results), "checks_passed": True}))


if __name__ == "__main__":
    main()
