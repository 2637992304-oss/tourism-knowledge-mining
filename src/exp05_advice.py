"""实验 5：条件性游览建议抽取。

负责人：FYH。
输入：data/processed/corpus.jsonl、data/outputs/entities.json（实体对齐）。
输出：data/outputs/advice.json。
待完成：条件与建议切分、类型映射、去重、人工校验和统计。
字段规范见项目根目录的 三人分工.md。本文件仅为入口骨架。
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="实验 5：条件性游览建议抽取（负责人 FYH，待实现）",
        epilog="输入：data/processed/corpus.jsonl、data/outputs/entities.json（实体对齐）；输出：data/outputs/advice.json。实现后请同步更新 README 和交接说明。",
    )
    parser.parse_args()
    # TODO(FYH): 条件与建议切分、类型映射、去重、人工校验和统计。
    raise SystemExit("实验 5 尚未实现；请由 FYH 按分工文档完成。本次未生成实验结果。")


if __name__ == "__main__":
    main()
