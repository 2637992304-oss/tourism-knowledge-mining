"""导出报告用路线层级图、主展示景区图谱 PNG；所有标签来自实际输出。"""
import argparse
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PALETTE = {"SCENIC": "#194b70", "ROUTE": "#376b96", "STEP": "#e5f0f7", "POI": "#e4f2e8"}


def font(path, size):
    return ImageFont.truetype(str(path), size)


def lines(draw, text, f, width):
    result, current = [], ""
    for char in text:
        if draw.textlength(current + char, font=f) > width and current:
            result.append(current)
            current = char
        else:
            current += char
    return result + [current]


def box(draw, center, text, f, fill, width=330, height=68, dark=False):
    x, y = center
    draw.rounded_rectangle((x-width/2, y-height/2, x+width/2, y+height/2),
                           radius=12, fill=fill, outline="#b6c6d0", width=2)
    wrapped = lines(draw, text, f, width-24)
    for i, line in enumerate(wrapped[:3]):
        draw.text((x, y + (i-(len(wrapped[:3])-1)/2)*28), line, font=f,
                  fill="white" if dark else "#183344", anchor="mm")


def arrow(draw, source, target, color="#9aaab5", width=2):
    x, y = source
    tx, ty = target
    draw.line((x, y, tx, ty), fill=color, width=width)
    angle = math.atan2(ty-y, tx-x)
    points = [(tx, ty)] + [(tx-11*math.cos(angle+a), ty-11*math.sin(angle+a)) for a in (-0.45, 0.45)]
    draw.polygon(points, fill=color)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, default=Path("C:/Windows/Fonts/msyh.ttc"))
    args = parser.parse_args()
    f, title = font(args.font, 23), font(args.font, 38)
    routes = json.loads(Path("data/outputs/routes.json").read_text(encoding="utf-8"))["routes"]
    output = Path("results/figures")
    output.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGB", (2400, 1600), "#f8fafc")
    draw = ImageDraw.Draw(im)
    draw.text((60, 35), "实验 3 · 路线与时间层级", font=title, fill="#183344")
    draw.text((60, 95), "语料 v1 / 时间均来自原文；unknown 表示没有明确钟点或时间段", font=f, fill="#486475")
    bucket_colors = {"morning": "#e5f0f7", "noon": "#fff2d8", "afternoon": "#e3f2e6",
                     "evening": "#ebe7f6", "unknown": "#edf0f2"}
    for col, route in enumerate(routes):
        x = 300 + col*600
        name = ("箱根" if route["scenic_id"] == "S001" else "蓝山") + (" · 官方" if route["text_type"] == "official_route" else " · 游客")
        box(draw, (x, 200), name, f, "#194b70", width=540, dark=True)
        draw.text((x, 250), route["doc_id"], font=f, fill="#486475", anchor="mm")
        for i, step in enumerate(route["steps"]):
            y = 330 + i*105
            if i:
                arrow(draw, (x, y-64), (x, y-41))
            label = f"{step['step_no']}. {step['time_text'] or 'unknown'} / {step['poi_name']}"
            box(draw, (x, y), label, f, bucket_colors[step["time_bucket"]], width=540, height=82)
    im.save(output / "exp03_time_hierarchy.png")

    graph = json.loads(Path("data/outputs/graph.json").read_text(encoding="utf-8"))
    nodes = {n["node_id"]: n for n in graph["nodes"] if n["scenic_id"] == "S001"}
    im = Image.new("RGB", (2100, 1900), "#f8fafc")
    draw = ImageDraw.Draw(im)
    draw.text((55, 30), "实验 6 · 箱根路线知识图谱", font=title, fill="#183344")
    draw.text((55, 95), "route_stage / 实体与条件建议尚未交付；地点按原文字面保留", font=f, fill="#8b4a27")
    draw.text((55, 145), "景区 → HAS_ROUTE → 路线 → HAS_STEP → 步骤 → VISITS → 地点；纵向箭头为 NEXT_STEP", font=f, fill="#486475")
    positions = {}
    kinds = ["SCENIC", "ROUTE", "STEP", "POI"]
    for layer, kind in enumerate(kinds):
        ids = [key for key, node in nodes.items() if node["node_type"] == kind]
        for i, key in enumerate(ids):
            positions[key] = (220 + layer*545, 280 + (i+0.5)*1450/max(len(ids), 1))
    for edge in graph["edges"]:
        if edge["source"] not in nodes or edge["target"] not in nodes:
            continue
        a, b = positions[edge["source"]], positions[edge["target"]]
        if edge["relation"] == "NEXT_STEP":
            arrow(draw, (a[0]-175, a[1]), (b[0]-175, b[1]), "#d19038", 3)
        else:
            arrow(draw, (a[0]+170, a[1]), (b[0]-170, b[1]))
    for key, node in nodes.items():
        kind = node["node_type"]
        text = node["name"]
        if kind == "ROUTE":
            text = node["attributes"]["route_id"].replace("R_S001_", "")
        if kind == "STEP":
            at = node["attributes"]
            text = f"{'官方' if 'OFF' in at['route_id'] else '游客'} 步骤 {at['step_no']} / {at['time_text'] or 'unknown'}"
        box(draw, positions[key], text, f, PALETTE[kind], dark=kind in ("SCENIC", "ROUTE"))
    draw.text((55, 1820), "数据源：data/outputs/graph.json；步骤与边的 attributes.evidence 可回查 corpus.jsonl", font=f, fill="#486475")
    im.save(output / "exp06_hakone_graph.png")
    print("saved exp03_time_hierarchy.png and exp06_hakone_graph.png")


if __name__ == "__main__":
    main()
