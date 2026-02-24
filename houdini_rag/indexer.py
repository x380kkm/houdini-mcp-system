"""向量数据库索引构建"""
import json
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


class DocumentIndexer:
    def __init__(self, config):
        self.config = config
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=config['api']['api_key'],
            openai_api_base=config['api']['base_url'],
            model=config['api']['embedding_model']
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config['vectordb']['chunk_size'],
            chunk_overlap=config['vectordb']['chunk_overlap'],
            separators=["\n\n", "\n", "。", ".", " ", ""]
        )

    def load_documents(self, json_file):
        """加载JSON文档"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        documents = []
        for item in data:
            doc = Document(
                page_content=item['content'],
                metadata={
                    'title': item['title'],
                    'url': item['url']
                }
            )
            documents.append(doc)

        return documents

    def build_index(self, documents):
        """构建向量索引"""
        print(f"分割文档...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"生成了 {len(chunks)} 个文本块")

        print("创建向量索引...")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.config['vectordb']['persist_directory'],
            collection_name=self.config['vectordb']['collection_name']
        )

        print("索引构建完成!")
        return vectorstore

    def load_index(self):
        """加载已有索引"""
        vectorstore = Chroma(
            persist_directory=self.config['vectordb']['persist_directory'],
            embedding_function=self.embeddings,
            collection_name=self.config['vectordb']['collection_name']
        )
        return vectorstore


if __name__ == "__main__":
    import yaml

    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    indexer = DocumentIndexer(config)
    docs = indexer.load_documents('./data/raw/houdini_docs.json')
    indexer.build_index(docs)
