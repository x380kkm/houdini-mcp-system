#!/usr/bin/env python3
"""
Houdini RAG 查询技能
查询Houdini文档知识库
"""
import sys
import os
import yaml

# 添加houdini_rag到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../houdini_rag'))

from rag_engine import HoudiniRAG


def main():
    # 解析参数
    if len(sys.argv) < 2:
        print("用法: houdini-rag <问题>")
        print("\n示例:")
        print("  houdini-rag 'What is Houdini?'")
        print("  houdini-rag 'How do I create a sphere?'")
        print("  houdini-rag 'What are VEX functions?'")
        sys.exit(1)

    question = ' '.join(sys.argv[1:])

    # 加载配置
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(script_dir, '../..'))
    config_path = os.path.join(project_dir, 'houdini_rag/config.yaml')

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 修正相对路径为绝对路径
    config['vectordb']['persist_directory'] = os.path.join(
        project_dir,
        'houdini_rag',
        config['vectordb']['persist_directory'].lstrip('./')
    )

    # 初始化RAG
    try:
        rag = HoudiniRAG(config)
    except Exception as e:
        print(f"错误: 无法初始化RAG系统")
        print(f"详情: {e}")
        print("\n提示: 请确保向量索引已构建")
        sys.exit(1)

    # 查询
    print(f"查询: {question}\n")
    print("=" * 60)

    try:
        response = rag.query(question)

        # 输出回答
        print("\n回答:")
        print(response['answer'])

        # 输出来源
        print("\n" + "=" * 60)
        print("参考文档:")
        for i, src in enumerate(response['sources'], 1):
            print(f"\n{i}. {src['title']}")
            print(f"   {src['url']}")
            print(f"   {src['content'][:150]}...")

    except Exception as e:
        print(f"查询失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
