# Houdini HDA Documentation System

自动为 Houdini Digital Assets (HDA) 生成完整技术文档的系统，集成了 Houdini MCP 远程控制和 RAG 文档检索。

## 🎯 功能特性

- 🔌 **远程控制** - 通过 MCP (Model Context Protocol) 远程操作 Houdini
- 📦 **节点提取** - 递归扫描 HDA 内部所有子节点结构
- 🤖 **智能文档** - 使用 RAG 系统自动查询官方文档
- 📝 **自动生成** - 生成结构化的 Markdown 技术文档
- 📊 **数据分析** - 统计节点类型、层级结构等信息

## 📋 系统要求

- Python 3.8+
- Houdini 18.0+ (任意版本)
- OpenAI 兼容 API (用于 RAG)

## 🚀 快速开始

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

```bash
# 步骤 1: 提取节点列表
python extract_hda_nodes.py "path/to/your.hda"

# 步骤 2: 生成文档
python generate_hda_doc.py hda_nodes_list.json
```

生成的文档位于 `hda_docs/YYYYMMDD_HHMMSS/` 目录。

## 📖 使用示例

查看 `examples/HE_pipe_example/` 目录，包含：
- `HDA_Complete_Documentation.md` - 完整的生成文档示例（1,187 行）
- `node_types_documentation.json` - RAG 查询结果
- `hda_nodes_list.json` - 节点列表数据

## 🏗️ 项目结构

```
.
├── extract_hda_nodes.py          # 节点提取脚本
├── generate_hda_doc.py            # 文档生成脚本
├── houdini_mcp_380kkm/            # Houdini MCP 模块
│   └── core/                      # 核心功能
│       └── houdini_mcp/
│           ├── connection.py      # 连接管理
│           └── tools/             # 工具集
├── houdini_rag/                   # RAG 系统
│   ├── config.example.yaml        # 配置模板
│   ├── scraper.py                 # 文档爬虫
│   ├── build_vectordb.py          # 向量数据库构建
│   └── rag_engine.py              # RAG 引擎
└── examples/                      # 示例输出
    └── HE_pipe_example/           # HE_pipe.hda 示例
```

## 🔧 工作流程

### 步骤 1: 节点提取

`extract_hda_nodes.py` 执行以下操作：
1. 通过 MCP 连接到 Houdini
2. 导入 HDA 文件
3. 创建节点实例
4. 递归扫描所有子节点
5. 导出为 JSON 格式

**输出**: `hda_nodes_list.json`

### 步骤 2: 文档生成

`generate_hda_doc.py` 执行以下操作：
1. 读取节点列表 JSON
2. 统计节点类型和使用频率
3. 对每种节点类型进行 RAG 查询
4. 生成结构化 Markdown 文档

**输出**:
- `HDA_Complete_Documentation.md` - 完整文档
- `node_types_documentation.json` - RAG 查询结果

## 📊 生成的文档内容

生成的文档包含：

1. **📋 目录** - 快速导航
2. **📊 概览** - 节点统计信息
3. **🌳 节点结构** - 层级树状图
4. **📚 节点类型说明** - 每种节点的详细说明（RAG 生成）
   - 功能描述
   - 主要参数
   - 使用示例
   - 官方文档链接
5. **📝 完整节点列表** - 所有节点的表格清单

## ⚙️ 配置说明

### Houdini MCP 配置

默认连接参数：
- Host: `localhost`
- Port: `18811`

可在脚本中修改：
```python
HOUDINI_HOST = "localhost"
HOUDINI_PORT = 18811
```

### RAG 系统配置

编辑 `houdini_rag/config.yaml`：

```yaml
# API 配置
api:
  base_url: "https://api.openai.com/v1"
  api_key: "your-api-key-here"
  model: "gpt-4"
  embedding_model: "text-embedding-3-large"

# 向量数据库配置
vectordb:
  persist_directory: "./data/chroma"
  collection_name: "houdini_docs"
  chunk_size: 1000
  chunk_overlap: 200

# RAG 配置
rag:
  top_k: 5  # 检索 top-k 个相关文档
  temperature: 0.7
  max_tokens: 8000
```

## 🎨 自定义

### 修改查询的节点类型数量

编辑 `generate_hda_doc.py`：
```python
# 只查询前 10 个最常用的节点类型
top_node_types = sorted(node_types.items(), key=lambda x: len(x[1]), reverse=True)[:10]
```

改为：
```python
# 查询所有节点类型
top_node_types = sorted(node_types.items(), key=lambda x: len(x[1]), reverse=True)
```

### 自定义文档模板

修改 `generate_hda_doc.py` 中的文档生成部分，自定义 Markdown 输出格式。

## 🐛 故障排除

### 问题 1: 无法连接到 Houdini

**错误**: `Failed to connect to Houdini at localhost:18811`

**解决方案**:
1. 确保 Houdini 正在运行
2. 在 Houdini Python Shell 中运行 `import hrpyc; hrpyc.start_server(port=18811)`
3. 检查防火墙设置

### 问题 2: API Key 错误

**错误**: `Invalid API key`

**解决方案**:
1. 检查 `config.yaml` 中的 API key 是否正确
2. 或设置环境变量 `export OPENAI_API_KEY="your-key"`

### 问题 3: 向量数据库未找到

**错误**: `Vector database not found`

**解决方案**:
```bash
cd houdini_rag
python build_vectordb.py
```

### 问题 4: Houdini 崩溃

**原因**: 一次性加载过多数据

**解决方案**:
- 使用两步式工作流程（先提取节点列表，再生成文档）
- 已在当前版本中实现

## 📈 性能指标

基于 HE_pipe.hda 测试（121 个节点，44 种类型）：

| 阶段 | 时间 |
|------|------|
| 节点提取 | ~10 秒 |
| RAG 初始化 | ~30 秒 |
| RAG 查询 (10 次) | ~50 秒 |
| 文档生成 | ~1 秒 |
| **总计** | **~2 分钟** |

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [Houdini](https://www.sidefx.com/) - 3D 动画和视觉效果软件
- [LangChain](https://www.langchain.com/) - LLM 应用框架
- [ChromaDB](https://www.trychroma.com/) - 向量数据库

## 📞 联系方式

如有问题或建议，请提交 Issue。

---

**注意**: 本项目仅用于学习和研究目的。请遵守 Houdini 和相关服务的使用条款。
