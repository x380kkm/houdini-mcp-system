#!/usr/bin/env python3
"""
HDA 教程生成技能脚本

自动化流程：
1. 连接 Houdini MCP
2. 加载 HDA 文件
3. 提取节点（可选择层级）
4. 生成教程文档

使用方法：
    python generate_hda_tutorial.py <HDA文件路径> [选项]

选项：
    --depth <N>     提取深度（0=表层, -1=所有层，默认=0）
    --output <DIR>  输出目录（默认=blog_YYYYMMDD_HHMMSS）
    --host <HOST>   Houdini 主机（默认=localhost）
    --port <PORT>   Houdini 端口（默认=18811）
"""

import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# 添加 MCP 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'houdini_mcp_380kkm/core'))

def main():
    parser = argparse.ArgumentParser(description='HDA 教程生成工具')
    parser.add_argument('hda_path', help='HDA 文件路径')
    parser.add_argument('--depth', type=int, default=0, help='提取深度（0=表层, -1=所有层）')
    parser.add_argument('--output', help='输出目录')
    parser.add_argument('--host', default='localhost', help='Houdini 主机')
    parser.add_argument('--port', type=int, default=18811, help='Houdini 端口')

    args = parser.parse_args()

    # 生成输出目录名
    if not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f'blog_{timestamp}'

    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    print("=" * 80)
    print("HDA 教程生成工具")
    print("=" * 80)
    print(f"HDA 文件: {args.hda_path}")
    print(f"提取深度: {args.depth if args.depth >= 0 else '所有层'}")
    print(f"输出目录: {output_dir}")
    print(f"Houdini: {args.host}:{args.port}")
    print()

    # 步骤 1: 提取节点
    print("步骤 1: 提取节点数据...")
    extract_cmd = f'python extract_hda_nodes.py "{args.hda_path}" {args.depth}'
    os.system(extract_cmd)

    if not Path('hda_nodes_list.json').exists():
        print("✗ 节点提取失败")
        return 1

    print("✓ 节点数据已提取")
    print()

    # 步骤 2: 生成完整文档（使用 RAG）
    print("步骤 2: 生成完整文档（RAG + LLM）...")
    doc_cmd = 'python generate_hda_doc.py hda_nodes_list.json'
    os.system(doc_cmd)

    # 查找最新的文档目录
    hda_docs_dir = Path('hda_docs')
    if hda_docs_dir.exists():
        doc_dirs = sorted(hda_docs_dir.glob('*'), key=lambda x: x.stat().st_mtime, reverse=True)
        if doc_dirs:
            latest_doc = doc_dirs[0]
            print(f"✓ 完整文档已生成: {latest_doc}")
        else:
            print("✗ 未找到生成的文档")
            return 1
    else:
        print("✗ 文档生成失败")
        return 1

    print()

    # 步骤 3: 生成教程章节
    print("步骤 3: 生成教程章节...")
    print("（此步骤需要手动执行或使用 Claude Code）")
    print()
    print("建议流程：")
    print("1. 在 Claude Code 中打开项目")
    print("2. 提供以下信息：")
    print(f"   - 节点数据: hda_nodes_list.json")
    print(f"   - 完整文档: {latest_doc}/HDA_Complete_Documentation.md")
    print("3. 要求生成教程章节到指定目录")
    print()

    # 创建任务记录
    task_file = output_dir / 'TASK.md'
    with open(task_file, 'w', encoding='utf-8') as f:
        f.write(f"# HDA 教程生成任务\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 输入\n\n")
        f.write(f"- HDA 文件: `{args.hda_path}`\n")
        f.write(f"- 提取深度: {args.depth}\n")
        f.write(f"- 节点数据: `hda_nodes_list.json`\n")
        f.write(f"- 完整文档: `{latest_doc}/HDA_Complete_Documentation.md`\n\n")
        f.write(f"## 输出\n\n")
        f.write(f"- 输出目录: `{output_dir}`\n")
        f.write(f"- 教程章节: 待生成\n\n")
        f.write(f"## 状态\n\n")
        f.write(f"- [x] 节点提取\n")
        f.write(f"- [x] 完整文档生成\n")
        f.write(f"- [ ] 教程章节生成\n")

    print(f"✓ 任务记录已保存: {task_file}")
    print()
    print("=" * 80)
    print("准备工作完成！")
    print("=" * 80)

    return 0

if __name__ == '__main__':
    sys.exit(main())
