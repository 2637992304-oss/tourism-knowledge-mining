"""实验 3：游览路线的层级结构挖掘。

负责人：YZH。
输入：data/processed/corpus.jsonl、data/outputs/entities.json（名称对齐）。
输出：data/outputs/routes.json。
待完成：多格式路线解析、时间层级、名称归一化和官方/游客路线对比。
字段规范见项目根目录的 三人分工.md。本文件仅为入口骨架。
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="实验 3：游览路线的层级结构挖掘（负责人 YZH，待实现）",
        epilog="输入：data/processed/corpus.jsonl、data/outputs/entities.json（名称对齐）；输出：data/outputs/routes.json。实现后请同步更新 README 和交接说明。",
    )
    parser.parse_args()
    # TODO(YZH): 多格式路线解析、时间层级、名称归一化和官方/游客路线对比。
    raise SystemExit("实验 3 尚未实现；请由 YZH 按分工文档完成。本次未生成实验结果。")


if __name__ == "__main__":
    main()
