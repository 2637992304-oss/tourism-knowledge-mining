"""只根据 DHT 活跃目录对齐名称，不新增别名或删去地点后缀。"""
import re


def align_poi(surface, scenic_id, catalog):
    active = [e for e in catalog if e.get("active", True)
              and e["scenic_id"] == scenic_id and e["entity_type"] == "POI"]

    def matches(name):
        return [e for e in active if name in [e["canonical_name"], *e.get("aliases", [])]]

    direct = matches(surface)
    if len(direct) == 1:
        return direct[0], "exact_alias"
    if direct:
        return None, "ambiguous"
    bracket = re.fullmatch(r"(.+?)\s*[(（]([^()（）]+)[)）]", surface)
    joined = re.fullmatch(r"([A-Za-z][A-Za-z '\-]+)([\u3400-\u9fff]+)", surface)
    match = bracket or joined
    if match is None:
        return None, "pending"
    parts = [part.strip() for part in match.groups()]
    if not any(re.search(r"[A-Za-z]", part) for part in parts) or not any(
            re.search(r"[\u3400-\u9fff]", part) for part in parts):
        return None, "pending"
    candidates = [matches(part) for part in parts]
    # 每个组成部分必须单独、唯一指向相同 ID；不允许仅凭一个子串命中。
    if all(len(items) == 1 for items in candidates):
        first, second = [items[0] for items in candidates]
        if first["entity_id"] == second["entity_id"]:
            return first, "bilingual_components"
    return None, "pending"
