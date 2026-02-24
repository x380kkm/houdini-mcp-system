#!/usr/bin/env python3
"""
HDA 节点列表提取器
简化版：只读取节点列表和基本信息，保存为 JSON
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'houdini_mcp_380kkm/core'))

from houdini_mcp.tools import execute_code

if len(sys.argv) < 2:
    print("用法: python extract_hda_nodes.py <HDA文件路径>")
    sys.exit(1)

hda_path = sys.argv[1]
HOUDINI_HOST = "localhost"
HOUDINI_PORT = 18811

print("=" * 80)
print("HDA 节点列表提取器")
print("=" * 80)
print(f"目标 HDA: {hda_path}")
print()

# 步骤 1: 导入并创建节点
print("步骤 1: 导入 HDA 并创建实例...")

setup_code = f"""
import json

hda_path = r"{hda_path}"
hou.hda.installFile(hda_path)

definitions = hou.hda.definitionsInFile(hda_path)
node_type_name = definitions[0].nodeTypeName()
node_category = definitions[0].nodeTypeCategory().name()

print("节点类型:", node_type_name)
print("节点类别:", node_category)

obj = hou.node('/obj')

if node_category == 'Sop':
    geo = obj.createNode('geo', 'hda_extract_temp')
    for child in geo.children():
        child.destroy()
    node = geo.createNode(node_type_name)
else:
    node = obj.createNode(node_type_name)

node_path = node.path()
print("节点路径:", node_path)
"""

result = execute_code(code=setup_code, host=HOUDINI_HOST, port=HOUDINI_PORT, timeout=30)
print(result.get('stdout', ''))

if result.get('status') != 'success':
    print(f"✗ 失败: {result.get('message', '')}")
    sys.exit(1)

# 提取节点路径
node_path = None
for line in result.get('stdout', '').split('\n'):
    if '节点路径:' in line:
        node_path = line.split(':', 1)[1].strip()
        break

if not node_path:
    print("✗ 未能获取节点路径")
    sys.exit(1)

print(f"✓ 节点已创建: {node_path}")
print()

# 步骤 2: 读取子节点列表（轻量级）
print("步骤 2: 读取子节点列表...")

extract_code = f"""
import json

def get_node_list(node, depth=0, max_depth=10):
    '''轻量级递归：只获取路径、名称、类型'''
    if depth > max_depth:
        return []

    nodes = []
    try:
        for child in node.children():
            nodes.append({{
                'path': child.path(),
                'name': child.name(),
                'type': child.type().name(),
                'depth': depth
            }})
            # 递归子节点
            nodes.extend(get_node_list(child, depth + 1, max_depth))
    except:
        pass

    return nodes

hda_node = hou.node(r"{node_path}")
all_nodes = get_node_list(hda_node)

print("找到", len(all_nodes), "个子节点")

# 统计节点类型
type_counts = {{}}
for n in all_nodes:
    t = n['type']
    type_counts[t] = type_counts.get(t, 0) + 1

print("\\n节点类型统计:")
for node_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {{node_type}}: {{count}} 个")

# 输出 JSON
print("\\nJSON_START")
print(json.dumps(all_nodes, indent=2, ensure_ascii=False))
print("JSON_END")
"""

result = execute_code(
    code=extract_code,
    host=HOUDINI_HOST,
    port=HOUDINI_PORT,
    timeout=60,
    max_stdout_size=1000000  # 1MB
)

stdout = result.get('stdout', '')

if result.get('status') != 'success':
    print(f"✗ 失败: {result.get('message', '')}")
    sys.exit(1)

# 解析 JSON
json_start = stdout.find('JSON_START')
json_end = stdout.find('JSON_END')

if json_start == -1 or json_end == -1:
    print("✗ 未找到 JSON 数据")
    # 打印部分输出用于调试
    print("输出前 500 字符:")
    print(stdout[:500])
    sys.exit(1)

json_str = stdout[json_start + len('JSON_START'):json_end].strip()

try:
    nodes_data = json.loads(json_str)
    print(f"✓ 成功解析 {len(nodes_data)} 个节点")
except Exception as e:
    print(f"✗ JSON 解析失败: {e}")
    sys.exit(1)

# 保存到文件
output_file = Path("hda_nodes_list.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(nodes_data, f, indent=2, ensure_ascii=False)

print(f"✓ 节点列表已保存到: {output_file}")
print()

# 显示统计信息
print("=" * 80)
print("统计信息")
print("=" * 80)
print(f"总节点数: {len(nodes_data)}")

type_counts = {}
for node in nodes_data:
    t = node['type']
    type_counts[t] = type_counts.get(t, 0) + 1

print(f"节点类型数: {len(type_counts)}")
print()
print("前 10 个最常用的节点类型:")
for node_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {node_type}: {count} 个")

print()
print("✓ 完成！")
