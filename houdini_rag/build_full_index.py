"""构建完整索引 - 带进度显示"""
from indexer import DocumentIndexer
import yaml

print('=' * 60)
print('构建完整 Houdini 文档索引')
print('=' * 60)

print('\n加载配置...')
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

print('初始化索引器...')
indexer = DocumentIndexer(config)

print('加载全部文档（10,009个）...')
print('这可能需要1-2分钟...')
documents = indexer.load_documents('data/raw/houdini_docs.json')
print(f'✓ 成功加载 {len(documents)} 个文档')

print('\n开始构建向量索引...')
print('预计时间: 15-30分钟')
print('请耐心等待...\n')

indexer.build_index(documents)

print('\n' + '=' * 60)
print('✓ 索引构建完成！')
print('=' * 60)
print('现在可以使用 RAG 系统进行查询了')
