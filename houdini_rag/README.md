# Houdini RAG 系统

轻量化的 RAG (Retrieval-Augmented Generation) 系统，用于分析和查询 Houdini 官方文档。

## 功能特性

- 🕷️ **文档爬取** - 自动爬取 Houdini 官方文档
- 📚 **向量索引** - 使用 ChromaDB 构建轻量化向量数据库
- 🤖 **智能问答** - 基于 OpenAI 兼容 API 的 RAG 查询
- 🔍 **相似度搜索** - 快速查找相关文档
- 💬 **交互模式** - 命令行交互式问答

## 安装

```bash
cd houdini_rag
pip install -r requirements.txt
```

## 配置

编辑 `config.yaml` 文件：

```yaml
api:
  base_url: "https://api.openai.com/v1"  # 你的API地址
  api_key: "your-api-key-here"           # 你的API密钥
  model: "gpt-3.5-turbo"
  embedding_model: "text-embedding-ada-002"
```

## 使用流程

### 1. 爬取文档

```bash
python cli.py scrape --max-pages 50
```

这将爬取 Houdini 官方文档并保存到 `./data/raw/houdini_docs.json`

### 2. 构建索引

```bash
python cli.py index
```

这将创建向量索引并保存到 `./data/chroma/`

### 3. 查询

**单次查询:**
```bash
python cli.py query "How do I create a mountain in Houdini?"
```

**交互模式:**
```bash
python cli.py query -i
```

**相似度搜索:**
```bash
python cli.py search "heightfield terrain" --top-k 5
```

## 项目结构

```
houdini_rag/
├── config.yaml          # 配置文件
├── requirements.txt     # 依赖
├── scraper.py          # 文档爬虫
├── indexer.py          # 索引构建
├── rag_engine.py       # RAG 引擎
├── cli.py              # 命令行界面
├── README.md           # 说明文档
└── data/               # 数据目录
    ├── raw/            # 原始文档
    └── chroma/         # 向量数据库
```

## API 兼容性

支持任何 OpenAI 兼容的 API，包括：
- OpenAI 官方 API
- Azure OpenAI
- 本地部署的模型 (如 LocalAI, Ollama)
- 其他兼容服务

## 示例

```python
from rag_engine import HoudiniRAG
import yaml

# 加载配置
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 初始化 RAG
rag = HoudiniRAG(config)

# 查询
result = rag.query("How do I use the HeightField node?")
print(result['answer'])

# 相似度搜索
docs = rag.search_similar("terrain generation", k=5)
for doc in docs:
    print(doc['title'], doc['url'])
```

## 注意事项

- 首次运行需要先爬取文档和构建索引
- 爬取时请遵守网站的 robots.txt 和使用条款
- 建议设置合理的爬取延迟避免对服务器造成压力
- 向量索引会占用一定磁盘空间

## 许可

MIT License
