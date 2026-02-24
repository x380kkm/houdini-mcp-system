"""优化的全量索引构建脚本"""
import json
import yaml
import sys
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# 强制刷新输出
def print_flush(msg):
    print(msg, flush=True)


def build_full_index():
    """构建完整索引"""
    print_flush('=' * 60)
    print_flush('构建完整 Houdini 文档索引')
    print_flush('=' * 60)

    # 加载配置
    print_flush('\n1. 加载配置...')
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 初始化embeddings
    print_flush('2. 初始化 Embeddings...')
    embeddings = OpenAIEmbeddings(
        openai_api_key=config['api']['api_key'],
        openai_api_base=config['api']['base_url'],
        model=config['api']['embedding_model']
    )

    # 初始化文本分割器
    print_flush('3. 初始化文本分割器...')
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config['vectordb']['chunk_size'],
        chunk_overlap=config['vectordb']['chunk_overlap'],
        separators=["\n\n", "\n", "。", ".", " ", ""]
    )

    # 清空现有索引
    print_flush('4. 清空现有索引...')
    import shutil
    chroma_dir = Path(config['vectordb']['persist_directory'])
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)
        print_flush('   ✓ 已删除旧索引')

    # 分批处理
    batch_size = 500  # 每批500个文档
    json_file = 'data/raw/houdini_docs.json'

    print_flush(f'5. 加载文档列表...')
    with open(json_file, 'r', encoding='utf-8') as f:
        all_docs = json.load(f)

    total_docs = len(all_docs)
    total_batches = (total_docs + batch_size - 1) // batch_size

    print_flush(f'   总文档数: {total_docs}')
    print_flush(f'   批次大小: {batch_size}')
    print_flush(f'   总批次数: {total_batches}')

    print_flush(f'\n6. 开始分批处理...\n')

    vectorstore = None
    total_chunks = 0

    for batch_idx in range(total_batches):
        start_idx = batch_idx * batch_size
        end_idx = min((batch_idx + 1) * batch_size, total_docs)
        batch_docs = all_docs[start_idx:end_idx]

        print_flush(f'批次 {batch_idx + 1}/{total_batches}: 文档 {start_idx + 1}-{end_idx}')

        # 转换为Document对象
        documents = []
        for item in batch_docs:
            doc = Document(
                page_content=item['content'],
                metadata={
                    'title': item['title'],
                    'url': item['url'],
                    'category': item.get('category', ''),
                    'file': item.get('file', '')
                }
            )
            documents.append(doc)

        # 分割文档
        chunks = text_splitter.split_documents(documents)
        print_flush(f'   生成了 {len(chunks)} 个文本块')

        # 第一批：创建新索引
        if batch_idx == 0:
            print_flush(f'   创建向量索引...')
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=config['vectordb']['persist_directory'],
                collection_name=config['vectordb']['collection_name']
            )
        else:
            # 后续批次：追加到现有索引
            print_flush(f'   追加到现有索引...')
            vectorstore.add_documents(chunks)

        total_chunks += len(chunks)
        print_flush(f'   ✓ 完成 (累计: {total_chunks} 个文本块)\n')

        # 每5批保存一次（防止意外中断）
        if (batch_idx + 1) % 5 == 0:
            print_flush(f'   💾 保存检查点...\n')
            sys.stdout.flush()

    # 最终统计
    print_flush('=' * 60)
    print_flush('✓ 索引构建完成！')
    print_flush('=' * 60)
    print_flush(f'总文档数: {total_docs}')
    print_flush(f'总文本块: {total_chunks}')
    print_flush(f'平均每文档: {total_chunks / total_docs:.1f} 个文本块')
    print_flush(f'保存位置: {config["vectordb"]["persist_directory"]}')

    # 验证索引
    print_flush('\n验证索引...')
    collection = vectorstore._collection
    count = collection.count()
    print_flush(f'向量库中的文档数: {count}')

    if count == total_chunks:
        print_flush('✓ 验证通过！')
    else:
        print_flush(f'⚠️  警告: 预期 {total_chunks} 个，实际 {count} 个')

    return vectorstore


if __name__ == '__main__':
    try:
        build_full_index()
    except KeyboardInterrupt:
        print_flush('\n\n⚠️  用户中断')
        sys.exit(1)
    except Exception as e:
        print_flush(f'\n\n❌ 错误: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
