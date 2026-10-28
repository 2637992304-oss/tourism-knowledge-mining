"""合成数据仅用于接口与异常测试，不写入正式实验数据。"""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from exp06_graph import build
from exp03_routes import make_step
from exp03_rules import extract
from exp03_alignment import align_poi


class AlignmentTests(unittest.TestCase):
    def setUp(self):
        self.catalog = [{"entity_id": "P", "scenic_id": "S003", "entity_type": "POI",
                         "canonical_name": "Scenic World", "aliases": ["风景世界"]}]

    def test_both_languages_must_map_to_same_id(self):
        entity, method = align_poi("风景世界(Scenic World)", "S003", self.catalog)
        self.assertEqual(entity["entity_id"], "P")
        self.assertEqual(method, "bilingual_components")
        entity, _ = align_poi("Scenic World风景世界", "S003", self.catalog)
        self.assertEqual(entity["entity_id"], "P")

    def test_parent_child_suffix_not_dropped(self):
        entity, _ = align_poi("风景世界(Scenic World)野餐区", "S003", self.catalog)
        self.assertIsNone(entity)

    def test_conflicting_aliases_not_merged(self):
        self.catalog.append({"entity_id": "Q", "scenic_id": "S003", "entity_type": "POI",
                             "canonical_name": "其他景点", "aliases": ["风景世界"]})
        entity, _ = align_poi("风景世界(Scenic World)", "S003", self.catalog)
        self.assertIsNone(entity)


class FusionTests(unittest.TestCase):
    def setUp(self):
        self.registry = {"scenics": [{"scenic_id": "S001", "scenic_name": "测试景区"}]}
        self.doc = {"doc_id": "TEST", "scenic_id": "S001", "text": "上午乘巴士去甲景点"}
        step = make_step(self.doc, 1, "甲景点", self.doc["text"], 0, 9)
        route = {"route_id": "TEST_R", "scenic_id": "S001", "doc_id": "TEST",
                 "route_name": "测试路线", "text_type": "official_route", "steps": [step]}
        self.routes = {"schema_version": "1.0", "corpus_version": "test", "routes": [route]}
        self.entities = {"entity_catalog": [
            {"entity_id": "P", "scenic_id": "S001", "entity_type": "POI", "canonical_name": "甲景点", "aliases": []},
            {"entity_id": "T", "scenic_id": "S001", "entity_type": "TRANSPORT", "canonical_name": "巴士", "aliases": []},
            {"entity_id": "H", "scenic_id": "S001", "entity_type": "TIME", "canonical_name": "上午", "aliases": []}],
            "mentions": [
                {"mention_id": "MT", "entity_id": "T", "span": {"doc_id": "TEST", "start": 3, "end": 5, "text": "巴士"}},
                {"mention_id": "MH", "entity_id": "H", "span": {"doc_id": "TEST", "start": 0, "end": 2, "text": "上午"}}]}
        self.advice = {"advice": [{"advice_id": "A_TEST", "scenic_id": "S001", "doc_id": "TEST",
                                  "condition_text": "测试条件", "condition_type": "other",
                                  "suggestion_text": "测试建议", "related_entity_ids": ["P"], "evidence": []}]}

    def test_full_fusion_relations(self):
        graph = build(self.routes, self.registry, self.entities, self.advice)
        self.assertEqual(graph["completion_status"], "fused")
        relations = {e["relation"] for e in graph["edges"]}
        self.assertTrue({"VISITS", "USES_TRANSPORT", "AT_TIME", "TRIGGERS", "APPLIES_TO"} <= relations)
        visits = next(e for e in graph["edges"] if e["relation"] == "VISITS")
        self.assertEqual(visits["target"], "N_ENTITY_P")

    def test_missing_inputs_explicit(self):
        graph = build(self.routes, self.registry)
        self.assertEqual(graph["missing_inputs"], ["entities.json", "advice.json"])
        self.assertEqual(graph["completion_status"], "route_stage")

    def test_duplicate_route_rejected(self):
        self.routes["routes"] *= 2
        with self.assertRaises(ValueError):
            build(self.routes, self.registry)

    def test_noncontinuous_steps_rejected(self):
        self.routes["routes"][0]["steps"][0]["step_no"] = 2
        with self.assertRaises(ValueError):
            build(self.routes, self.registry)

    def test_unknown_advice_reference_rejected(self):
        self.advice["advice"][0]["related_entity_ids"] = ["NOT_EXISTS"]
        with self.assertRaises(ValueError):
            build(self.routes, self.registry, self.entities, self.advice)

    def test_cross_scenic_reference_rejected(self):
        self.registry["scenics"].append({"scenic_id": "S002", "scenic_name": "另一个景区"})
        self.entities["entity_catalog"][0]["scenic_id"] = "S002"
        self.routes["routes"][0]["steps"][0]["poi_entity_id"] = "P"
        with self.assertRaises(ValueError):
            build(self.routes, self.registry, self.entities)

    def test_ambiguous_alias_kept_pending(self):
        second = copy.deepcopy(self.entities["entity_catalog"][0])
        second.update(entity_id="P2", canonical_name="另一个景点", aliases=["甲景点"])
        self.entities["entity_catalog"].append(second)
        graph = build(self.routes, self.registry, self.entities)
        visits = next(e for e in graph["edges"] if e["relation"] == "VISITS")
        node = next(n for n in graph["nodes"] if n["node_id"] == visits["target"])
        self.assertIsNone(node["attributes"]["entity_id"])

    def test_negated_or_view_only_locations_excluded(self):
        doc = {"doc_id": "TEST", "scenic_id": "S003",
               "text": "我们没有去三姐妹峰。您可以看到三姐妹峰。我们驱车前往珍罗兰洞。"}
        steps, _ = extract(doc, make_step)
        self.assertEqual([s["poi_name"] for s in steps], ["珍罗兰洞"])

    def test_short_recommendation_not_treated_as_caption(self):
        doc = {"doc_id": "TEST", "scenic_id": "S003",
               "text": "晚上:啤酒厂\n当地被公认为优秀的啤酒厂之一,山地文化啤酒公司。"}
        steps, _ = extract(doc, make_step, inherit_bucket=True)
        self.assertEqual([s["poi_name"] for s in steps], ["山地文化啤酒公司"])
        self.assertEqual(steps[0]["time_bucket"], "evening")


if __name__ == "__main__":
    unittest.main()
