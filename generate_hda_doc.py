#!/usr/bin/env python3
"""
HDA 文档生成器
基于节点列表 JSON，对所有节点类型进行 RAG 查询并生成文档
"""

import sys
import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'houdini_rag'))

from rag_engine import HoudiniRAG

if len(sys.argv) < 2:
    print("用法: python generate_hda_doc.py <节点列表JSON文件>")
    sys.exit(1)

json_file = sys.argv[1]

print("=" * 80)
print("HDA 文档生成器")
print("=" * 80)
print(f"输入文件: {json_file}")
print()

# 读取节点列表
with open(json_file, 'r', encoding='utf-8') as f:
    nodes_data = json.load(f)

print(f"✓ 读取到 {len(nodes_data)} 个节点")
print()

# 统计节点类型
node_types = defaultdict(list)
for node in nodes_data:
    node_type = node['type']
    node_types[node_type].append(node)

print(f"共使用了 {len(node_types)} 种不同的节点类型")
print()

# 初始化 RAG
print("初始化 RAG 系统...")
config_path = Path('houdini_rag/config.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

config['vectordb']['persist_directory'] = str(
    Path('houdini_rag') / config['vectordb']['persist_directory'].lstrip('./')
)

rag = HoudiniRAG(config)
print("✓ RAG 系统初始化成功")
print()

# 对每种节点类型进行 RAG 查询（只查询前10个最常用的）
print("=" * 80)
print("开始 RAG 查询（前 10 个最常用的节点类型）")
print("=" * 80)
print()

node_type_docs = {}

# 只查询前10个最常用的节点类型
top_node_types = sorted(node_types.items(), key=lambda x: len(x[1]), reverse=True)[:10]

for i, (node_type, instances) in enumerate(top_node_types, 1):
    print(f"[{i}/10] 查询节点类型: {node_type} ({len(instances)} 个实例)")

    # 构建查询
    query = f"What is the {node_type} node in Houdini? What does it do and what are its main parameters?"

    try:
        response = rag.query(query)
        node_type_docs[node_type] = {
            'answer': response['answer'],
            'sources': response['sources'][:3],  # 只保留前3个来源
            'instance_count': len(instances)
        }
        print(f"  ✓ 查询成功")
    except Exception as e:
        print(f"  ✗ 查询失败: {e}")
        node_type_docs[node_type] = {
            'answer': f"查询失败: {e}",
            'sources': [],
            'instance_count': len(instances)
        }

    print()

# 对于其他节点类型，添加占位符
for node_type, instances in node_types.items():
    if node_type not in node_type_docs:
        node_type_docs[node_type] = {
            'answer': '（未查询 - 仅对前10个最常用节点类型进行了 RAG 查询）',
            'sources': [],
            'instance_count': len(instances)
        }

# 生成 Markdown 文档
print("=" * 80)
print("生成 Markdown 文档")
print("=" * 80)
print()

output_dir = Path("hda_docs") / datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir.mkdir(parents=True, exist_ok=True)

doc_file = output_dir / "HDA_Complete_Documentation.md"

with open(doc_file, 'w', encoding='utf-8') as f:
    f.write("# HDA 完整文档\n\n")
    f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write("---\n\n")

    # 目录
    f.write("## 📋 目录\n\n")
    f.write("1. [概览](#概览)\n")
    f.write("2. [节点结构](#节点结构)\n")
    f.write("3. [节点类型说明](#节点类型说明)\n")
    f.write("4. [完整节点列表](#完整节点列表)\n\n")
    f.write("---\n\n")

    # 概览
    f.write("## 📊 概览\n\n")
    f.write(f"- **总节点数**: {len(nodes_data)}\n")
    f.write(f"- **节点类型数**: {len(node_types)}\n")
    f.write(f"- **最大嵌套深度**: {max(n['depth'] for n in nodes_data)}\n\n")

    # 节点类型统计
    f.write("### 节点类型统计\n\n")
    f.write("| 节点类型 | 数量 |\n")
    f.write("|---------|------|\n")
    for node_type, instances in sorted(node_types.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
        f.write(f"| `{node_type}` | {len(instances)} |\n")

    if len(node_types) > 20:
        f.write(f"\n*还有 {len(node_types) - 20} 种其他节点类型...*\n")

    f.write("\n---\n\n")

    # 节点结构
    f.write("## 🌳 节点结构\n\n")
    f.write("HDA 内部节点的层级结构：\n\n")
    f.write("```\n")

    # 按深度分组显示
    by_depth = defaultdict(list)
    for node in nodes_data:
        by_depth[node['depth']].append(node)

    for depth in sorted(by_depth.keys())[:3]:  # 只显示前3层
        f.write(f"深度 {depth}: {len(by_depth[depth])} 个节点\n")
        for node in by_depth[depth][:5]:  # 每层只显示前5个
            indent = "  " * depth
            f.write(f"{indent}- {node['name']} ({node['type']})\n")
        if len(by_depth[depth]) > 5:
            f.write(f"{'  ' * depth}  ... 还有 {len(by_depth[depth]) - 5} 个节点\n")

    f.write("```\n\n")
    f.write("---\n\n")

    # 节点类型说明
    f.write("## 📚 节点类型说明\n\n")
    f.write("以下是 HDA 中使用的所有节点类型的详细说明（按使用频率排序）：\n\n")

    for i, (node_type, doc_info) in enumerate(sorted(node_type_docs.items(), key=lambda x: x[1]['instance_count'], reverse=True), 1):
        f.write(f"### {i}. {node_type}\n\n")
        f.write(f"**使用次数**: {doc_info['instance_count']} 个实例\n\n")

        # RAG 生成的说明
        f.write("**功能说明**:\n\n")
        f.write(doc_info['answer'])
        f.write("\n\n")

        # 参考文档
        if doc_info['sources']:
            f.write("**参考文档**:\n")
            for src in doc_info['sources']:
                f.write(f"- [{src['title']}]({src['url']})\n")
            f.write("\n")

        f.write("---\n\n")

    # 完整节点列表
    f.write("## 📝 完整节点列表\n\n")
    f.write("HDA 内部所有节点的完整列表：\n\n")
    f.write("| 序号 | 节点名称 | 节点类型 | 路径 | 深度 |\n")
    f.write("|------|---------|---------|------|------|\n")

    for i, node in enumerate(nodes_data, 1):
        f.write(f"| {i} | `{node['name']}` | `{node['type']}` | `{node['path']}` | {node['depth']} |\n")

    f.write("\n---\n\n")

    # 生成信息
    f.write("## 📝 生成信息\n\n")
    f.write("- **生成工具**: HDA 文档生成器 v2.0\n")
    f.write("- **RAG 模型**: gemini-3-flash-preview\n")
    f.write("- **Embedding 模型**: text-embedding-3-large\n")
    f.write(f"- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write("---\n\n")
    f.write("*本文档由 Houdini MCP + RAG 系统自动生成*\n")

print(f"✓ 文档已生成: {doc_file}")

# 同时保存节点类型文档为 JSON
json_doc_file = output_dir / "node_types_documentation.json"
with open(json_doc_file, 'w', encoding='utf-8') as f:
    json.dump(node_type_docs, f, indent=2, ensure_ascii=False)

print(f"✓ JSON 文档已保存: {json_doc_file}")

print()
print("=" * 80)
print("✓ 完成！")
print("=" * 80)
print(f"输出目录: {output_dir}")
