"""实验 6：多源程序性知识融合与图谱可视化。

负责人：YZH。
输入：data/outputs/entities.json、routes.json、advice.json。
输出：data/outputs/graph.json。
待完成：图谱 Schema、对齐与融合、来源追溯、图谱绘制和查询验证。
字段规范见项目根目录的 三人分工.md。本文件仅为入口骨架。
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="实验 6：多源程序性知识融合与图谱可视化（负责人 YZH，待实现）",
        epilog="输入：data/outputs/entities.json、routes.json、advice.json；输出：data/outputs/graph.json。实现后请同步更新 README 和交接说明。",
    )
    parser.parse_args()
    # TODO(YZH): 图谱 Schema、对齐与融合、来源追溯、图谱绘制和查询验证。
    raise SystemExit("实验 6 尚未实现；请由 YZH 按分工文档完成。本次未生成实验结果。")


if __name__ == "__main__":
    main()
