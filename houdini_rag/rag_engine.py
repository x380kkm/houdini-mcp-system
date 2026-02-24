"""RAG 查询引擎"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class HoudiniRAG:
    def __init__(self, config):
        self.config = config

        # 初始化 LLM
        self.llm = ChatOpenAI(
            openai_api_key=config['api']['api_key'],
            openai_api_base=config['api']['base_url'],
            model_name=config['api']['model'],
            temperature=config['rag']['temperature'],
            max_tokens=config['rag']['max_tokens']
        )

        # 初始化 Embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=config['api']['api_key'],
            openai_api_base=config['api']['base_url'],
            model=config['api']['embedding_model']
        )

        # 加载向量数据库
        self.vectorstore = Chroma(
            persist_directory=config['vectordb']['persist_directory'],
            embedding_function=self.embeddings,
            collection_name=config['vectordb']['collection_name']
        )

        # 创建检索器
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": config['rag']['top_k']}
        )

        # 自定义提示模板
        template = """你是一个Houdini专家助手。基于以下文档内容回答用户问题。

相关文档:
{context}

问题: {question}

请提供准确、完整的回答。使用清晰的结构（如分类列表），确保回答完整不被截断。

回答:"""

        self.prompt = PromptTemplate.from_template(template)

    def query(self, question):
        """查询"""
        # 检索相关文档
        docs = self.retriever.invoke(question)

        # 构建上下文
        context = "\n\n".join([doc.page_content for doc in docs])

        # 生成回答
        chain = self.prompt | self.llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})

        return {
            'answer': answer,
            'sources': [
                {
                    'title': doc.metadata.get('title', ''),
                    'url': doc.metadata.get('url', ''),
                    'content': doc.page_content[:200] + '...'
                }
                for doc in docs
            ]
        }

    def search_similar(self, query, k=5):
        """相似度搜索"""
        docs = self.vectorstore.similarity_search(query, k=k)
        return [
            {
                'title': doc.metadata.get('title', ''),
                'url': doc.metadata.get('url', ''),
                'content': doc.page_content[:300] + '...'
            }
            for doc in docs
        ]


if __name__ == "__main__":
    import yaml

    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    rag = HoudiniRAG(config)

    # 测试查询
    question = "How do I create a mountain in Houdini?"
    result = rag.query(question)

    print(f"问题: {question}\n")
    print(f"回答: {result['answer']}\n")
    print("相关文档:")
    for i, source in enumerate(result['sources'], 1):
        print(f"{i}. {source['title']}")
        print(f"   {source['url']}")
