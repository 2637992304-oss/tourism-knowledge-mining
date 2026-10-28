"""实验 2：游览步骤的实体识别。

负责人：DHT。
输入：data/processed/corpus.jsonl。
输出：data/outputs/entities.json。
待完成：定义实体类型、词典/规则/Prompt、实体位置、词频图和迭代优化。
字段规范见项目根目录的 三人分工.md。本文件仅为入口骨架。
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="实验 2：游览步骤的实体识别（负责人 DHT，待实现）",
        epilog="输入：data/processed/corpus.jsonl；输出：data/outputs/entities.json。实现后请同步更新 README 和交接说明。",
    )
    parser.parse_args()
    # TODO(DHT): 定义实体类型、词典/规则/Prompt、实体位置、词频图和迭代优化。
    raise SystemExit("实验 2 尚未实现；请由 DHT 按分工文档完成。本次未生成实验结果。")


if __name__ == "__main__":
    main()
