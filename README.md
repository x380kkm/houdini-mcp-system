# Houdini HDA Documentation System (暂命名)

自动为 Houdini Digital Assets (HDA) 生成完整技术文档的系统，集成了 Houdini MCP 远程控制和 RAG 文档检索。

### 1. 安装依赖

```bash
# 安装 Houdini MCP
cd houdini_mcp_380kkm/core
pip install -e .

# 安装 RAG 系统
cd ../../houdini_rag
pip install -r requirements.txt
```

### 2. 配置 API Key

复制配置文件模板：
```bash
cd houdini_rag
cp config.example.yaml config.yaml
```

编辑 `config.yaml`，填入你的 API key：
```yaml
api:
  base_url: "https://api.openai.com/v1"  # 或其他兼容服务
  api_key: "your-api-key-here"  # 填入你的 API key
  model: "gpt-4"  # 或 gpt-3.5-turbo
  embedding_model: "text-embedding-3-large"
```

**推荐方式**：使用环境变量
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. 启动 Houdini MCP 服务器

在 Houdini 中打开 Python Shell (Windows → Python Shell)，运行：
```python
import hrpyc
hrpyc.start_server(port=18811)
```

### 4. 构建向量数据库（首次使用）

```bash
cd houdini_rag
python build_vectordb.py
```

这将爬取 Houdini 官方文档并构建向量数据库（约需 10-30 分钟）。

### 5. 生成 HDA 文档


操作请使用Claudecode进行桥接
目前仍在开发中

