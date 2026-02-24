#!/usr/bin/env python3
"""
HDA 文档化技能 v2.0
完整流程：
1. 导入 HDA
2. 创建实例
3. 进入 HDA 内部，递归搜索所有子节点
4. 读取每个子节点的类型和属性
5. 整理所有用到的节点类型
6. 对每种节点类型进行 RAG 检索
7. 生成包含所有节点信息的完整文档
"""

import sys
import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../houdini_rag'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../houdini_mcp_380kkm/core'))

def print_section(title):
    """打印分节标题"""
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    print()

def print_step(step_num, title):
    """打印步骤标题"""
    print()
    print(f"步骤 {step_num}: {title}")
    print("-" * 80)

def main():
    if len(sys.argv) < 2:
        print("用法: hda-doc <HDA文件路径>")
        print()
        print("示例:")
        print('  hda-doc "E:\\path\\to\\your.hda"')
        sys.exit(1)

    hda_path = sys.argv[1]

    if not os.path.exists(hda_path):
        print(f"✗ 错误: HDA 文件不存在: {hda_path}")
        sys.exit(1)

    print_section("HDA 完整文档化系统 v2.0")
    print(f"目标 HDA: {hda_path}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 导入模块
    from houdini_mcp.tools import execute_code, get_node_info
    from rag_engine import HoudiniRAG

    HOUDINI_HOST = "localhost"
    HOUDINI_PORT = 18811

    # ========================================================================
    # 步骤 1: 导入 HDA
    # ========================================================================
    print_step(1, "导入 HDA 到 Houdini")

    import_code = f"""
hda_path = r"{hda_path}"
print("正在安装 HDA:", hda_path)

hou.hda.installFile(hda_path)
print("✓ HDA 已安装")

definitions = hou.hda.definitionsInFile(hda_path)
print("找到", len(definitions), "个资产定义:")

for definition in definitions:
    print("  -", definition.nodeTypeName())
    print("    类别:", definition.nodeTypeCategory().name())
    print("    标签:", definition.description())
"""

    try:
        result = execute_code(code=import_code, host=HOUDINI_HOST, port=HOUDINI_PORT, timeout=30)
        print(result.get('stdout', ''))

        if result.get('status') != 'success':
            print(f"✗ 导入失败: {result.get('message', 'Unknown error')}")
            sys.exit(1)

        print("✓ HDA 导入成功")

    except Exception as e:
        print(f"✗ 执行失败: {e}")
        sys.exit(1)

    # ========================================================================
    # 步骤 2: 创建节点实例
    # ========================================================================
    print_step(2, "创建 HDA 节点实例")

    create_code = f"""
obj = hou.node('/obj')

# 查找节点类型
node_type_name = None
node_category = None
hda_basename = '{os.path.basename(hda_path).replace('.hda', '').replace('.hdanc', '')}'

for definition_file in hou.hda.loadedFiles():
    for def_obj in hou.hda.definitionsInFile(definition_file):
        type_name = def_obj.nodeTypeName()
        if hda_basename.lower() in type_name.lower() or 'pipe' in type_name.lower():
            node_type_name = type_name
            node_category = def_obj.nodeTypeCategory().name()
            break
    if node_type_name:
        break

if not node_type_name:
    all_defs = []
    for definition_file in hou.hda.loadedFiles():
        for def_obj in hou.hda.definitionsInFile(definition_file):
            all_defs.append((def_obj.nodeTypeName(), def_obj.nodeTypeCategory().name()))
    if all_defs:
        node_type_name, node_category = all_defs[-1]

if not node_type_name:
    print("✗ 未找到节点类型")
else:
    print("找到节点类型:", node_type_name)
    print("节点类别:", node_category)

    # 根据类别创建节点
    if node_category == 'Sop':
        geo = obj.createNode('geo', 'hda_doc_container')
        for child in geo.children():
            child.destroy()
        node = geo.createNode(node_type_name)
        node_path = node.path()
        print("✓ 节点已创建:", node_path)
    elif node_category == 'Object':
        node = obj.createNode(node_type_name)
        node_path = node.path()
        print("✓ 节点已创建:", node_path)
    else:
        print("✗ 不支持的节点类别:", node_category)
        node_path = None

    if node_path:
        if node_category == 'Sop':
            geo.layoutChildren()
        else:
            obj.layoutChildren()
"""

    try:
        result = execute_code(code=create_code, host=HOUDINI_HOST, port=HOUDINI_PORT, timeout=30)
        stdout = result.get('stdout', '')
        print(stdout)

        if result.get('status') != 'success':
            print(f"✗ 创建失败: {result.get('message', '')}")
            sys.exit(1)

        # 提取节点路径
        node_path = None
        for line in stdout.split('\n'):
            if '✓ 节点已创建:' in line:
                node_path = line.split(':', 1)[1].strip()
                break

        if not node_path:
            print("✗ 未能获取节点路径")
            sys.exit(1)

        print(f"✓ 节点创建成功: {node_path}")

    except Exception as e:
        print(f"✗ 执行失败: {e}")
        sys.exit(1)

    # ========================================================================
    # 步骤 3: 递归搜索所有子节点
    # ========================================================================
    print_step(3, "递归搜索 HDA 内部所有子节点")

    search_code = f"""
def get_all_children_recursive(node, depth=0, max_depth=10):
    '''递归获取所有子节点'''
    if depth > max_depth:
        return []

    nodes_info = []

    try:
        children = node.children()
        for child in children:
            # 获取节点信息
            node_info = {{
                'path': child.path(),
                'name': child.name(),
                'type': child.type().name(),
                'type_category': child.type().category().name(),
                'depth': depth,
                'comment': child.comment() if hasattr(child, 'comment') else '',
            }}

            # 获取参数
            try:
                parms = []
                for parm in child.parms():
                    parm_info = {{
                        'name': parm.name(),
                        'label': parm.description(),
                        'type': str(parm.parmTemplate().type()),
                        'value': str(parm.eval())
                    }}
                    parms.append(parm_info)
                node_info['parameters'] = parms
            except:
                node_info['parameters'] = []

            nodes_info.append(node_info)

            # 递归获取子节点
            if child.children():
                nodes_info.extend(get_all_children_recursive(child, depth + 1, max_depth))

    except Exception as e:
        print(f"获取子节点时出错: {{e}}")

    return nodes_info

# 获取 HDA 节点
hda_node = hou.node(r"{node_path}")

if not hda_node:
    print("✗ 未找到节点:", r"{node_path}")
else:
    print("正在扫描节点:", hda_node.path())
    print("节点类型:", hda_node.type().name())

    # 获取所有子节点
    all_nodes = get_all_children_recursive(hda_node)

    print(f"✓ 找到 {{len(all_nodes)}} 个子节点")

    # 统计节点类型
    type_counts = {{}}
    for node_info in all_nodes:
        node_type = node_info['type']
        type_counts[node_type] = type_counts.get(node_type, 0) + 1

    print("\\n节点类型统计:")
    for node_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {{node_type}}: {{count}} 个")
"""

    try:
        result = execute_code(code=search_code, host=HOUDINI_HOST, port=HOUDINI_PORT, timeout=60)
        stdout = result.get('stdout', '')
        print(stdout)

        if result.get('status') != 'success':
            print(f"✗ 搜索失败: {result.get('message', '')}")
            sys.exit(1)

        print("✓ 子节点扫描完成")

    except Exception as e:
        print(f"✗ 执行失败: {e}")
        sys.exit(1)

    # ========================================================================
    # 步骤 4: 获取完整节点数据
    # ========================================================================
    print_step(4, "获取完整节点数据")

    get_data_code = f"""
import json

hda_node = hou.node(r"{node_path}")

def get_all_children_recursive(node, depth=0, max_depth=10):
    if depth > max_depth:
        return []

    nodes_info = []

    try:
        children = node.children()
        for child in children:
            node_info = {{
                'path': child.path(),
                'name': child.name(),
                'type': child.type().name(),
                'type_category': child.type().category().name(),
                'depth': depth,
                'comment': child.comment() if hasattr(child, 'comment') else '',
            }}

            try:
                parms = []
                for parm in child.parms():
                    parm_info = {{
                        'name': parm.name(),
                        'label': parm.description(),
                        'type': str(parm.parmTemplate().type()),
                        'value': str(parm.eval())
                    }}
                    parms.append(parm_info)
                node_info['parameters'] = parms
            except:
                node_info['parameters'] = []

            nodes_info.append(node_info)

            if child.children():
                nodes_info.extend(get_all_children_recursive(child, depth + 1, max_depth))

    except Exception as e:
        pass

    return nodes_info

all_nodes = get_all_children_recursive(hda_node)

# 输出 JSON
print("JSON_START")
print(json.dumps(all_nodes, indent=2, ensure_ascii=False))
print("JSON_END")
"""

    try:
        result = execute_code(
            code=get_data_code,
            host=HOUDINI_HOST,
            port=HOUDINI_PORT,
            timeout=60,
            max_stdout_size=500000  # 增加到 500KB
        )
        stdout = result.get('stdout', '')

        if result.get('status') != 'success':
            print(f"✗ 获取数据失败: {result.get('message', '')}")
            sys.exit(1)

        # 解析 JSON 数据
        json_start = stdout.find('JSON_START')
        json_end = stdout.find('JSON_END')

        if json_start == -1 or json_end == -1:
            print("✗ 未找到 JSON 数据")
            sys.exit(1)

        json_str = stdout[json_start + len('JSON_START'):json_end].strip()
        all_nodes_data = json.loads(json_str)

        print(f"✓ 成功获取 {len(all_nodes_data)} 个节点的完整数据")

    except Exception as e:
        print(f"✗ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ========================================================================
    # 步骤 5: 整理节点类型
    # ========================================================================
    print_step(5, "整理所有用到的节点类型")

    # 统计节点类型
    node_types = defaultdict(list)
    for node_data in all_nodes_data:
        node_type = node_data['type']
        node_types[node_type].append(node_data)

    print(f"共使用了 {len(node_types)} 种不同的节点类型:")
    for node_type, nodes in sorted(node_types.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {node_type}: {len(nodes)} 个实例")

    # ========================================================================
    # 步骤 6: RAG 查询每种节点类型
    # ========================================================================
    print_step(6, "使用 RAG 查询每种节点类型的文档")

    # 加载 RAG 配置
    config_path = Path(__file__).parent.parent.parent / 'houdini_rag' / 'config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    config['vectordb']['persist_directory'] = str(
        Path(__file__).parent.parent.parent / 'houdini_rag' / config['vectordb']['persist_directory'].lstrip('./')
    )

    print("初始化 RAG 系统...")
    rag = HoudiniRAG(config)
    print("✓ RAG 系统初始化成功")
    print()

    # 对每种节点类型进行查询
    node_type_docs = {}

    for idx, (node_type, nodes) in enumerate(sorted(node_types.items(), key=lambda x: len(x[1]), reverse=True), 1):
        print(f"查询 {idx}/{len(node_types)}: {node_type} 节点")
        print("-" * 40)

        query = f"What is the {node_type} node in Houdini? What does it do and what are its main parameters?"

        try:
            response = rag.query(query)
            node_type_docs[node_type] = {
                'answer': response['answer'],
                'sources': response['sources']
            }

            # 显示简短摘要
            answer_preview = response['answer'][:200] + "..." if len(response['answer']) > 200 else response['answer']
            print(answer_preview)
            print()

        except Exception as e:
            print(f"⚠ 查询失败: {e}")
            node_type_docs[node_type] = {
                'answer': f"无法获取 {node_type} 的文档信息",
                'sources': []
            }
            print()

    print("✓ RAG 查询完成")

    # ========================================================================
    # 步骤 7: 生成完整文档
    # ========================================================================
    print_step(7, "生成完整 Markdown 文档")

    # 创建输出目录
    output_dir = Path("hda_docs") / datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成文档
    hda_name = os.path.basename(hda_path).replace('.hda', '').replace('.hdanc', '')
    doc_content = f"""# {hda_name} - HDA 完整文档

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**HDA 文件**: `{hda_path}`
**HDA 节点路径**: `{node_path}`

---

## 📋 概览

| 属性 | 值 |
|------|-----|
| 总节点数 | {len(all_nodes_data)} |
| 节点类型数 | {len(node_types)} |
| 最大深度 | {max([n['depth'] for n in all_nodes_data]) if all_nodes_data else 0} |

---

## 🏗️ 节点结构

### 节点类型统计

"""

    for node_type, nodes in sorted(node_types.items(), key=lambda x: len(x[1]), reverse=True):
        doc_content += f"- **{node_type}**: {len(nodes)} 个实例\n"

    doc_content += "\n---\n\n## 📦 所有内部节点列表\n\n"

    # 按深度分组显示节点
    nodes_by_depth = defaultdict(list)
    for node_data in all_nodes_data:
        nodes_by_depth[node_data['depth']].append(node_data)

    for depth in sorted(nodes_by_depth.keys()):
        doc_content += f"\n### 深度 {depth}\n\n"

        for node_data in nodes_by_depth[depth]:
            indent = "  " * depth
            doc_content += f"{indent}- **{node_data['name']}** (`{node_data['type']}`)\n"
            doc_content += f"{indent}  - 路径: `{node_data['path']}`\n"

            if node_data.get('comment'):
                doc_content += f"{indent}  - 注释: {node_data['comment']}\n"

            if node_data.get('parameters'):
                doc_content += f"{indent}  - 参数数量: {len(node_data['parameters'])}\n"

    doc_content += "\n---\n\n## 📚 节点类型文档 (RAG 检索)\n\n"

    # 添加每种节点类型的文档
    for node_type, doc_info in node_type_docs.items():
        instances = node_types[node_type]
        doc_content += f"\n### {node_type}\n\n"
        doc_content += f"**使用次数**: {len(instances)}\n\n"
        doc_content += f"**实例列表**:\n"
        for inst in instances:
            doc_content += f"- `{inst['path']}`\n"

        doc_content += f"\n**功能说明**:\n\n{doc_info['answer']}\n\n"

        if doc_info['sources']:
            doc_content += "**参考文档**:\n"
            for src in doc_info['sources'][:3]:
                doc_content += f"- [{src['title']}]({src['url']})\n"

        doc_content += "\n---\n\n"

    doc_content += f"""
## 📝 生成信息

- **生成工具**: HDA 完整文档化系统 v2.0
- **RAG 模型**: {config['api']['model']}
- **Embedding 模型**: {config['api']['embedding_model']}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

*本文档由 Houdini MCP + RAG 系统自动生成*
"""

    # 保存文档
    doc_path = output_dir / f"{hda_name}_complete_documentation.md"
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(doc_content)

    # 保存 JSON 数据
    json_path = output_dir / f"{hda_name}_nodes_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'hda_path': hda_path,
            'node_path': node_path,
            'total_nodes': len(all_nodes_data),
            'node_types': {k: len(v) for k, v in node_types.items()},
            'all_nodes': all_nodes_data
        }, f, indent=2, ensure_ascii=False)

    print(f"✓ 文档已生成: {doc_path}")
    print(f"✓ 数据已保存: {json_path}")

    print_section("✓ 文档化完成！")
    print(f"输出目录: {output_dir}")
    print(f"文档文件: {doc_path.name}")
    print(f"数据文件: {json_path.name}")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
