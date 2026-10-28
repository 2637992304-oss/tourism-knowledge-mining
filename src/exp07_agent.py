"""实验 7：旅游规划 Agent。

负责人：FYH。
输入：data/outputs/graph.json、本地模型配置。
输出：data/outputs/agent_cases.json。
待完成：LLM 接入、真实图谱工具、调用闭环、异常处理和多场景测试。
字段规范见项目根目录的 三人分工.md。本文件仅为入口骨架。
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="实验 7：旅游规划 Agent（负责人 FYH，待实现）",
        epilog="输入：data/outputs/graph.json、本地模型配置；输出：data/outputs/agent_cases.json。实现后请同步更新 README 和交接说明。",
    )
    parser.parse_args()
    # TODO(FYH): LLM 接入、真实图谱工具、调用闭环、异常处理和多场景测试。
    raise SystemExit("实验 7 尚未实现；请由 FYH 按分工文档完成。本次未生成实验结果。")


if __name__ == "__main__":
    main()
