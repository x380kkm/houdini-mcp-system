#!/usr/bin/env python3
"""
HDA 文档生成器 - 并行版本
使用多线程加速 RAG 查询
"""

import sys
import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'houdini_rag'))

from rag_engine import HoudiniRAG

print("=" * 80)
print("HDA 文档生成器 (并行版本)")
print("=" * 80)

if len(sys.argv) < 2:
    print("用法: python generate_hda_doc_parallel.py <节点列表JSON文件> [并发数]")
    sys.exit(1)

json_file = sys.argv[1]
max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 5  # 默认5个并发

print(f"输入文件: {json_file}")
print(f"并发数: {max_workers}")
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
print("  - 加载配置文件...")
config_path = Path('houdini_rag/config.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

config['vectordb']['persist_directory'] = str(
    Path('houdini_rag') / config['vectordb']['persist_directory'].lstrip('./')
)
print("  - 初始化 embeddings 和向量数据库（可能需要几分钟）...")

rag = HoudiniRAG(config)
print("✓ RAG 系统初始化成功")
print()

# 线程安全的计数器和锁
progress_lock = Lock()
completed_count = [0]  # 使用列表以便在函数内修改

def query_node_type(node_type, instances):
    """查询单个节点类型"""
    try:
        query = f"What is the {node_type} node in Houdini? Please explain its purpose, main parameters, and common use cases."
        response = rag.query(query)

        result = {
            'answer': response['answer'],
            'sources': response['sources'][:3],
            'instance_count': len(instances)
        }

        with progress_lock:
            completed_count[0] += 1
            print(f"[{completed_count[0]}/{len(node_types)}] ✓ {node_type} ({len(instances)} 个实例)")

        return node_type, result, None
    except Exception as e:
        with progress_lock:
            completed_count[0] += 1
            print(f"[{completed_count[0]}/{len(node_types)}] ✗ {node_type}: {e}")

        return node_type, None, str(e)

def query_vex_code(node):
    """查询单个 VEX 代码"""
    try:
        prompt = f"""Explain this VEX code in Houdini:

```vex
{node['vex_code']}
```

Please explain:
1. What does this code do?
2. What are the key VEX functions used?
3. What attributes or parameters does it work with?
"""

        answer = rag.llm.invoke(prompt).content

        result = {
            'node_name': node['name'],
            'node_type': node['type'],
            'node_path': node['path'],
            'vex_code': node['vex_code'],
            'explanation': answer,
            'sources': []
        }

        with progress_lock:
            completed_count[0] += 1
            print(f"[{completed_count[0]}/{len(vex_nodes)}] ✓ VEX: {node['name']} ({node['type']})")

        return node['path'], result, None
    except Exception as e:
        with progress_lock:
            completed_count[0] += 1
            print(f"[{completed_count[0]}/{len(vex_nodes)}] ✗ VEX: {node['name']}: {e}")

        return node['path'], None, str(e)

# 并行查询节点类型
print("=" * 80)
print(f"开始并行查询节点类型 (并发数: {max_workers})")
print("=" * 80)
print()

node_type_docs = {}
completed_count[0] = 0

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {
        executor.submit(query_node_type, node_type, instances): node_type
        for node_type, instances in node_types.items()
    }

    for future in as_completed(futures):
        node_type, result, error = future.result()
        if result:
            node_type_docs[node_type] = result
        else:
            node_type_docs[node_type] = {
                'answer': f"查询失败: {error}",
                'sources': [],
                'instance_count': len(node_types[node_type])
            }

print()
print(f"✓ 节点类型查询完成 ({len(node_type_docs)}/{len(node_types)})")
print()

# 并行查询 VEX 代码
print("=" * 80)
print(f"开始并行查询 VEX 代码 (并发数: {max_workers})")
print("=" * 80)
print()

vex_nodes = [node for node in nodes_data if node.get('vex_code')]
vex_docs = {}
completed_count[0] = 0

if vex_nodes:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(query_vex_code, node): node['path']
            for node in vex_nodes
        }

        for future in as_completed(futures):
            node_path, result, error = future.result()
            if result:
                vex_docs[node_path] = result
            else:
                # 找到对应的节点
                node = next(n for n in vex_nodes if n['path'] == node_path)
                vex_docs[node_path] = {
                    'node_name': node['name'],
                    'node_type': node['type'],
                    'node_path': node['path'],
                    'vex_code': node['vex_code'],
                    'explanation': f"查询失败: {error}",
                    'sources': []
                }

print()
print(f"✓ VEX 代码查询完成 ({len(vex_docs)}/{len(vex_nodes)})")
print()

# 生成文档（与原版本相同的逻辑）
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
    f.write("3. [VEX 代码说明](#vex-代码说明)\n")
    f.write("4. [节点类型说明](#节点类型说明)\n")
    f.write("5. [完整节点列表](#完整节点列表)\n\n")
    f.write("---\n\n")

    # 概览
    f.write("## 📊 概览\n\n")
    f.write(f"- **总节点数**: {len(nodes_data)}\n")
    f.write(f"- **节点类型数**: {len(node_types)}\n")
    f.write(f"- **VEX 节点数**: {len(vex_docs)}\n")
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

    # VEX 代码说明
    if vex_docs:
        f.write("## 💻 VEX 代码说明\n\n")
        f.write(f"HDA 中包含 {len(vex_docs)} 个 VEX 节点，以下是详细说明：\n\n")

        for i, (node_path, vex_info) in enumerate(vex_docs.items(), 1):
            f.write(f"### {i}. {vex_info['node_name']} ({vex_info['node_type']})\n\n")
            f.write(f"**节点路径**: `{vex_info['node_path']}`\n\n")

            f.write("**VEX 代码**:\n\n")
            f.write("```vex\n")
            f.write(vex_info['vex_code'])
            f.write("\n```\n\n")

            f.write("**代码说明**:\n\n")
            f.write(vex_info['explanation'])
            f.write("\n\n")

            if vex_info['sources']:
                f.write("**参考文档**:\n")
                for src in vex_info['sources']:
                    f.write(f"- [{src['title']}]({src['url']})\n")
                f.write("\n")

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
    f.write("- **生成工具**: HDA 文档生成器 v3.0 (并行版本)\n")
    f.write("- **RAG 模型**: gemini-3-pro-preview\n")
    f.write("- **Embedding 模型**: text-embedding-3-large\n")
    f.write(f"- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"- **查询的节点类型数**: {len(node_type_docs)}\n")
    f.write(f"- **查询的 VEX 节点数**: {len(vex_docs)}\n")
    f.write(f"- **并发数**: {max_workers}\n\n")
    f.write("---\n\n")
    f.write("*本文档由 Houdini MCP + RAG 系统自动生成*\n")
    f.write("\n**注意**: VEX 代码说明和节点类型说明已分别保存到独立文件中，便于单独查阅。\n")

print(f"✓ 主文档已生成: {doc_file}")

# 单独保存 VEX 代码文档
if vex_docs:
    vex_doc_file = output_dir / "VEX_Code_Documentation.md"
    with open(vex_doc_file, 'w', encoding='utf-8') as f:
        f.write("# VEX 代码文档\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        f.write(f"## 概览\n\n")
        f.write(f"HDA 中包含 {len(vex_docs)} 个 VEX 节点\n\n")
        f.write("---\n\n")

        for i, (node_path, vex_info) in enumerate(vex_docs.items(), 1):
            f.write(f"## {i}. {vex_info['node_name']} ({vex_info['node_type']})\n\n")
            f.write(f"**节点路径**: `{vex_info['node_path']}`\n\n")

            f.write("### VEX 代码\n\n")
            f.write("```vex\n")
            f.write(vex_info['vex_code'])
            f.write("\n```\n\n")

            f.write("### 代码说明\n\n")
            f.write(vex_info['explanation'])
            f.write("\n\n")

            if vex_info['sources']:
                f.write("### 参考文档\n\n")
                for src in vex_info['sources']:
                    f.write(f"- [{src['title']}]({src['url']})\n")
                f.write("\n")

            f.write("---\n\n")

        f.write("## 生成信息\n\n")
        f.write("- **生成工具**: HDA 文档生成器 v3.0 (并行版本)\n")
        f.write("- **RAG 模型**: gemini-3-pro-preview\n")
        f.write(f"- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **并发数**: {max_workers}\n\n")
        f.write("*本文档由 Houdini MCP + RAG 系统自动生成*\n")

    print(f"✓ VEX 代码文档已生成: {vex_doc_file}")

    # 保存 VEX 文档为 JSON
    vex_json_file = output_dir / "vex_documentation.json"
    with open(vex_json_file, 'w', encoding='utf-8') as f:
        json.dump(vex_docs, f, indent=2, ensure_ascii=False)
    print(f"✓ VEX JSON 文档已保存: {vex_json_file}")

# 单独保存节点类型文档
node_types_doc_file = output_dir / "Node_Types_Documentation.md"
with open(node_types_doc_file, 'w', encoding='utf-8') as f:
    f.write("# 节点类型文档\n\n")
    f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write("---\n\n")

    f.write(f"## 概览\n\n")
    f.write(f"HDA 中使用了 {len(node_types)} 种不同的节点类型\n\n")
    f.write("---\n\n")

    for i, (node_type, doc_info) in enumerate(sorted(node_type_docs.items(), key=lambda x: x[1]['instance_count'], reverse=True), 1):
        f.write(f"## {i}. {node_type}\n\n")
        f.write(f"**使用次数**: {doc_info['instance_count']} 个实例\n\n")

        f.write("### 功能说明\n\n")
        f.write(doc_info['answer'])
        f.write("\n\n")

        if doc_info['sources']:
            f.write("### 参考文档\n\n")
            for src in doc_info['sources']:
                f.write(f"- [{src['title']}]({src['url']})\n")
            f.write("\n")

        f.write("---\n\n")

    f.write("## 生成信息\n\n")
    f.write("- **生成工具**: HDA 文档生成器 v3.0 (并行版本)\n")
    f.write("- **RAG 模型**: gemini-3-pro-preview\n")
    f.write(f"- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"- **并发数**: {max_workers}\n\n")
    f.write("*本文档由 Houdini MCP + RAG 系统自动生成*\n")

print(f"✓ 节点类型文档已生成: {node_types_doc_file}")

# 同时保存节点类型文档为 JSON
json_doc_file = output_dir / "node_types_documentation.json"
with open(json_doc_file, 'w', encoding='utf-8') as f:
    json.dump(node_type_docs, f, indent=2, ensure_ascii=False)

print(f"✓ 节点类型 JSON 已保存: {json_doc_file}")

print()
print("=" * 80)
print("✓ 完成！")
print("=" * 80)
print(f"输出目录: {output_dir}")
print()
print("生成的文件:")
print(f"  1. 主文档: HDA_Complete_Documentation.md")
print(f"  2. VEX 代码文档: VEX_Code_Documentation.md")
print(f"  3. 节点类型文档: Node_Types_Documentation.md")
print(f"  4. 节点类型 JSON: node_types_documentation.json")
if vex_docs:
    print(f"  5. VEX 代码 JSON: vex_documentation.json")
print()
