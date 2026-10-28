"""实验 1：景区指南数据采集与预处理。

负责人：DHT。
输入：data/raw/ 原始文本与来源记录。
输出：data/processed/scenic_registry.json、data/processed/corpus.jsonl。
待完成：采集与来源登记、清洗、去重、结构化和质量检查。
字段规范见项目根目录的 三人分工.md。本文件仅为入口骨架。
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="实验 1：景区指南数据采集与预处理（负责人 DHT，待实现）",
        epilog="输入：data/raw/ 原始文本与来源记录；输出：data/processed/scenic_registry.json、data/processed/corpus.jsonl。实现后请同步更新 README 和交接说明。",
    )
    parser.parse_args()
    # TODO(DHT): 采集与来源登记、清洗、去重、结构化和质量检查。
    raise SystemExit("实验 1 尚未实现；请由 DHT 按分工文档完成。本次未生成实验结果。")


if __name__ == "__main__":
    main()
