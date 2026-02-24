# Houdini RAG 系统 - 快速开始指南

## 🎯 项目概述

轻量化的RAG系统，用于分析和查询Houdini官方文档。已完成核心功能开发和测试。

## ✅ 已完成的工作

1. ✅ 文档爬虫 - 成功爬取10个测试页面
2. ✅ 数据存储 - JSON格式，32KB数据
3. ✅ 单元测试 - 4个测试全部通过
4. ✅ 向量索引模块 - 代码完成
5. ✅ RAG查询引擎 - 代码完成
6. ✅ 命令行工具 - 完整实现

## 📦 安装

```bash
cd houdini_rag
pip install -r requirements.txt
```

## ⚙️ 配置

**编辑 `config.yaml`**:

```yaml
api:
  base_url: "https://api.openai.com/v1"  # 你的API地址
  api_key: "sk-..."                      # 填入你的API密钥
  model: "gpt-3.5-turbo"
  embedding_model: "text-embedding-ada-002"
```

## 🚀 使用流程

### 方案A: 快速测试 (推荐)

使用已爬取的10个页面进行测试:

```bash
# 1. 配置API密钥 (编辑config.yaml)

# 2. 构建索引
python cli.py index

# 3. 开始查询
python cli.py query -i
```

### 方案B: 完整流程

爬取更多文档:

```bash
# 1. 爬取100个页面 (约3-4分钟)
python cli.py scrape --max-pages 100

# 2. 构建索引
python cli.py index

# 3. 查询
python cli.py query "How do I create terrain?"
```

## 📝 命令参考

### 爬取文档
```bash
python cli.py scrape --max-pages 50
```

### 构建索引
```bash
python cli.py index
```

### 查询
```bash
# 交互模式
python cli.py query -i

# 单次查询
python cli.py query "What is Houdini?"

# 相似度搜索
python cli.py search "heightfield" --top-k 5
```

### 测试
```bash
# 单元测试
python test_units.py -v

# 快速爬虫测试
python test_quick.py

# 完整集成测试 (需要API密钥)
python test_integration.py
```

## 📊 当前数据

- ✅ 已爬取: 10个页面
- ✅ 数据文件: `data/raw/houdini_docs.json` (32KB)
- ✅ 包含内容:
  - Houdini 21.0 概述
  - 新特性
  - 安装指南
  - 基础教程
  - 工具和参数

## 🔧 API配置选项

### OpenAI官方
```yaml
api:
  base_url: "https://api.openai.com/v1"
  api_key: "sk-..."
  model: "gpt-3.5-turbo"
```

### Azure OpenAI
```yaml
api:
  base_url: "https://your-resource.openai.azure.com"
  api_key: "your-azure-key"
  model: "gpt-35-turbo"
```

### 本地模型 (Ollama)
```yaml
api:
  base_url: "http://localhost:11434/v1"
  api_key: "ollama"
  model: "llama2"
  embedding_model: "nomic-embed-text"
```

## 📈 性能

- 爬虫速度: ~2秒/页
- 索引构建: ~10秒 (10页)
- 查询响应: ~2-3秒

## 🎓 示例查询

```python
from rag_engine import HoudiniRAG
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

rag = HoudiniRAG(config)

# 查询
result = rag.query("How do I create a mountain?")
print(result['answer'])

# 相似度搜索
docs = rag.search_similar("terrain", k=3)
for doc in docs:
    print(doc['title'])
```

## 📚 项目结构

```
houdini_rag/
├── config.yaml              # 配置文件 (需要填API密钥)
├── scraper.py              # 文档爬虫 ✅
├── indexer.py              # 向量索引 ✅
├── rag_engine.py           # RAG引擎 ✅
├── cli.py                  # 命令行工具 ✅
├── requirements.txt        # 依赖包 ✅
├── README.md               # 完整文档
├── QUICKSTART.md           # 本文件
├── TEST_REPORT.md          # 测试报告
└── data/
    ├── raw/
    │   └── houdini_docs.json  # 已爬取数据 ✅
    └── chroma/                # 向量数据库 (待生成)
```

## ⚠️ 注意事项

1. **API密钥**: 必须配置才能使用索引和查询功能
2. **爬虫礼仪**: 已设置1秒延迟，请勿修改过小
3. **数据大小**: 100页约300KB，建议从小规模开始

## 🐛 故障排除

### 问题: 导入错误
```bash
pip install -r requirements.txt --upgrade
```

### 问题: API连接失败
检查 `config.yaml` 中的 `base_url` 和 `api_key`

### 问题: 爬虫超时
增加 `config.yaml` 中的 `delay` 值

## 📞 下一步

1. **配置API密钥** - 编辑 `config.yaml`
2. **构建索引** - `python cli.py index`
3. **开始使用** - `python cli.py query -i`

---

**状态**: 核心功能完成，等待API配置
**版本**: 1.0.0
**日期**: 2026-02-24
