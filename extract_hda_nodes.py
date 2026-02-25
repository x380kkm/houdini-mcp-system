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
    print("用法: python extract_hda_nodes.py <HDA文件路径> [目标深度]")
    print("  目标深度: 0=只获取顶层, 1=获取第一层子节点, -1=获取所有层（默认）")
    sys.exit(1)

hda_path = sys.argv[1]
target_depth = int(sys.argv[2]) if len(sys.argv) > 2 else -1  # -1 表示所有层
HOUDINI_HOST = "localhost"
HOUDINI_PORT = 18811

print("=" * 80)
print("HDA 节点列表提取器")
print("=" * 80)
print(f"目标 HDA: {hda_path}")
if target_depth == -1:
    print(f"提取深度: 所有层")
else:
    print(f"提取深度: 第 {target_depth} 层")
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

def get_node_list(node, depth=0, max_depth=10, target_depth=-1):
    '''递归获取节点信息，包括 VEX 代码和参数
    target_depth: -1=所有层, 0=只顶层, 1=第一层子节点, 等等
    '''
    if depth > max_depth:
        return []

    nodes = []
    try:
        for child in node.children():
            # 如果指定了目标深度，只收集该深度的节点
            should_collect = (target_depth == -1) or (depth == target_depth)

            if should_collect:
                node_info = {{
                    'path': child.path(),
                    'name': child.name(),
                    'type': child.type().name(),
                    'depth': depth,
                    'vex_code': None,
                    'parameters': {{}}
                }}

                # 检查是否有 VEX 代码（wrangle 节点）
                if child.type().name() in ['attribwrangle', 'volumewrangle', 'pointwrangle', 'primwrangle']:
                    try:
                        snippet_parm = child.parm('snippet')
                        if snippet_parm:
                            vex_code = snippet_parm.eval()
                            if vex_code and vex_code.strip():
                                node_info['vex_code'] = vex_code
                    except:
                        pass

                # 提取参数（只提取非默认值的参数）
                try:
                    for parm in child.parms():
                        parm_name = parm.name()

                        # 跳过内部参数
                        if parm_name.startswith('__'):
                            continue

                        try:
                            parm_template = parm.parmTemplate()
                            parm_type = parm_template.type()

                            # 跳过 Ramp 和其他复杂类型
                            if parm_type in [hou.parmTemplateType.Ramp]:
                                continue

                            value = parm.eval()

                            # 转换为 JSON 可序列化的类型
                            if hasattr(value, '__iter__') and not isinstance(value, str):
                                value = list(value)

                            # 获取默认值
                            default_value = parm_template.defaultValue()
                            if isinstance(default_value, (list, tuple)) and default_value:
                                default_value = default_value[0]

                            # 只保存非默认值或重要参数
                            if value != default_value or parm_name in ['snippet', 'group', 'class', 'switcher']:
                                node_info['parameters'][parm_name] = value
                        except:
                            pass
                except:
                    pass

                nodes.append(node_info)

            # 继续递归（即使不收集当前层，也要继续深入）
            if target_depth == -1 or depth < target_depth:
                nodes.extend(get_node_list(child, depth + 1, max_depth, target_depth))
    except:
        pass

    return nodes

hda_node = hou.node(r"{node_path}")
all_nodes = get_node_list(hda_node, target_depth={target_depth})

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
vex_nodes_count = 0
nodes_with_params = 0
for node in nodes_data:
    t = node['type']
    type_counts[t] = type_counts.get(t, 0) + 1
    if node.get('vex_code'):
        vex_nodes_count += 1
    if node.get('parameters'):
        nodes_with_params += 1

print(f"节点类型数: {len(type_counts)}")
print(f"包含 VEX 代码的节点数: {vex_nodes_count}")
print(f"有非默认参数的节点数: {nodes_with_params}")
print()
print("前 10 个最常用的节点类型:")
for node_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {node_type}: {count} 个")

# 单独保存 VEX 代码
vex_nodes = [node for node in nodes_data if node.get('vex_code')]
if vex_nodes:
    vex_output_file = Path("hda_vex_codes.json")
    with open(vex_output_file, 'w', encoding='utf-8') as f:
        json.dump(vex_nodes, f, indent=2, ensure_ascii=False)
    print(f"\n✓ VEX 代码已单独保存到: {vex_output_file}")

print()
print("✓ 完成！")
