"""分批构建索引 - 避免内存问题"""
from indexer import DocumentIndexer
import yaml
import json

print('=' * 60)
print('分批构建 Houdini 文档索引')
print('=' * 60)

# 加载配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 加载所有文档
print('\n加载文档列表...')
with open('data/raw/houdini_docs.json', 'r', encoding='utf-8') as f:
    all_docs = json.load(f)

print(f'总文档数: {len(all_docs)}')

# 分批处理
batch_size = 1000
total_batches = (len(all_docs) + batch_size - 1) // batch_size

print(f'将分 {total_batches} 批处理，每批 {batch_size} 个文档\n')

indexer = DocumentIndexer(config)

for i in range(total_batches):
    start_idx = i * batch_size
    end_idx = min((i + 1) * batch_size, len(all_docs))
    batch = all_docs[start_idx:end_idx]

    print(f'批次 {i+1}/{total_batches}: 处理文档 {start_idx+1}-{end_idx}')

    # 保存临时批次
    temp_file = f'data/raw/batch_{i}.json'
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False)

    # 加载并构建索引
    documents = indexer.load_documents(temp_file)
    print(f'  加载了 {len(documents)} 个文档')

    if i == 0:
        # 第一批：创建新索引
        print(f'  创建向量索引...')
        indexer.build_index(documents)
    else:
        # 后续批次：追加到现有索引
        print(f'  追加到现有索引...')
        vectorstore = indexer.load_index()

        # 分割文档
        chunks = indexer.text_splitter.split_documents(documents)
        print(f'  生成了 {len(chunks)} 个文本块')

        # 添加到向量库
        vectorstore.add_documents(chunks)
        print(f'  ✓ 已添加')

    print()

print('=' * 60)
print('✓ 索引构建完成！')
print('=' * 60)
