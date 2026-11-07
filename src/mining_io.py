"""实验5—7公共读写；不修改冻结语料或上游结果。"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def corpus(path=None):
    path = path or ROOT / "data/processed/corpus.jsonl"
    rows = [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]
    if len({r["doc_id"] for r in rows}) != len(rows):
        raise ValueError("重复文档ID")
    return {r["doc_id"]: r for r in rows}


def span(doc_id, text, start, end):
    return {"doc_id": doc_id, "start": start, "end": end, "text": text[start:end]}


def check_span(ref, docs):
    if not isinstance(ref, dict) or ref.get("doc_id") not in docs:
        raise ValueError("证据文档不存在")
    a, b = ref.get("start"), ref.get("end")
    text = docs[ref["doc_id"]]["text"]
    if type(a) is not int or type(b) is not int or not 0 <= a < b <= len(text):
        raise ValueError("证据区间非法")
    if text[a:b] != ref.get("text"):
        raise ValueError("证据无法切回原文")
