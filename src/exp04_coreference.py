"""实验 4：程序性知识的共指消解。

负责人：DHT。
输入：data/processed/corpus.jsonl，可使用实体识别结果。
输出：data/outputs/coreference.json。
待完成：代词检测、人工标注、消解方法和准确率/覆盖率评估。
字段规范见项目根目录的 三人分工.md。本文件仅为入口骨架。
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="实验 4：程序性知识的共指消解（负责人 DHT，待实现）",
        epilog="输入：data/processed/corpus.jsonl，可使用实体识别结果；输出：data/outputs/coreference.json。实现后请同步更新 README 和交接说明。",
    )
    parser.parse_args()
    # TODO(DHT): 代词检测、人工标注、消解方法和准确率/覆盖率评估。
    raise SystemExit("实验 4 尚未实现；请由 DHT 按分工文档完成。本次未生成实验结果。")


if __name__ == "__main__":
    main()
