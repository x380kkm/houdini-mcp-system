"""
命令行接口
"""

import argparse
import json
import sys
from pathlib import Path

from .evaluator import ImageEvaluator
from .prompt_manager import PromptManager


def main():
    parser = argparse.ArgumentParser(description='图片评估代理工具')
    parser.add_argument('image', help='要评估的图片路径')
    parser.add_argument('--config', default='config.yaml', help='配置文件路径')
    parser.add_argument('--stage', help='评估阶段（如 main_mountain, mid_detail）')
    parser.add_argument('--params', help='参数 JSON 字符串或文件路径')
    parser.add_argument('--output', help='输出结果到文件')
    parser.add_argument('--list-stages', action='store_true', help='列出所有可用阶段')

    args = parser.parse_args()

    # 列出阶段
    if args.list_stages:
        pm = PromptManager()
        print("可用的评估阶段:")
        for stage in pm.get_stages():
            print(f"  - {stage}: {pm.get_description(stage)}")
        sys.exit(0)

    # 解析参数
    parameters = {}
    if args.params:
        if Path(args.params).exists():
            with open(args.params, 'r', encoding='utf-8') as f:
                parameters = json.load(f)
        else:
            try:
                parameters = json.loads(args.params)
            except json.JSONDecodeError:
                print(f"错误: 无法解析参数 JSON: {args.params}", file=sys.stderr)
                sys.exit(1)

    # 创建评估器
    try:
        evaluator = ImageEvaluator(args.config)
    except Exception as e:
        print(f"错误: 初始化评估器失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 执行评估
    try:
        if args.stage:
            # 使用阶段专用 Prompt
            result = evaluator.evaluate_stage(args.image, args.stage, parameters)
        else:
            # 使用通用 Prompt
            result = evaluator.evaluate(args.image, parameters)

        if result['success']:
            print("=" * 60)
            print("评估结果")
            if args.stage:
                print(f"阶段: {args.stage}")
            print("=" * 60)
            print(result['evaluation'])
            print("=" * 60)

            # 保存到文件
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"\n✅ 结果已保存到: {args.output}")

            sys.exit(0)
        else:
            print(f"错误: {result.get('error', '未知错误')}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"错误: 评估失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
