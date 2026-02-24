# 🎉 Houdini RAG 系统 - 使用指南

## ✅ 系统状态

**当前状态**: ✅ 可用
- 索引文档数: 100个（测试数据）
- 向量数据库: 27MB
- API配置: ✅ 已配置

## 🚀 快速使用

### 方法1: Python脚本查询

```python
from rag_engine import HoudiniRAG
import yaml

# 加载配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 初始化RAG
rag = HoudiniRAG(config)

# 查询
response = rag.query('What is Houdini?')
print(response['answer'])
```

### 方法2: 命令行查询

```bash
# 单次查询
python -c "
from rag_engine import HoudiniRAG
import yaml
config = yaml.safe_load(open('config.yaml'))
rag = HoudiniRAG(config)
print(rag.query('How do I create a sphere?')['answer'])
"
```

## 📊 当前能力

### ✅ 可以回答的问题类型

基于现有100个文档，系统可以回答：
- Houdini基础概念
- 动画工具
- 资产管理
- 基础操作
- 配置相关

### 示例查询

```python
# 基础问题
rag.query('What is Houdini?')
rag.query('What are digital assets?')
rag.query('How does procedural workflow work?')

# 工具相关
rag.query('What animation tools are available?')
rag.query('How do I use shelf tools?')
```

## 🔧 扩展索引（可选）

如果需要完整的10,009个文档索引，有两个选择：

### 选项1: 分批构建（推荐）

创建改进的分批脚本，每批处理后立即保存：

```python
# 需要优化 build_batch_index.py
# 添加更多进度输出和错误处理
```

### 选项2: 减少文档数量

只索引最重要的分类：

```python
import json

# 加载全部文档
with open('data/raw/houdini_docs.json') as f:
    all_docs = json.load(f)

# 筛选重要分类
important = ['nodes', 'vex', 'basics', 'model', 'render']
filtered = [d for d in all_docs if d['category'] in important]

# 保存筛选后的文档
with open('data/raw/filtered_docs.json', 'w') as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)

# 然后构建索引
```

## 💡 使用建议

### 当前系统（100文档）
- ✅ 适合演示和测试
- ✅ 可以回答基础问题
- ⚠️ 深度技术问题可能缺乏上下文

### 完整系统（10,009文档）
- ✅ 完整的Houdini知识库
- ✅ 可以回答所有技术问题
- ⚠️ 需要解决索引构建问题

## 🐛 已知问题

### 索引构建卡住
**问题**: 加载10,009个文档（34MB JSON）时Python进程卡住
**原因**: 内存加载大文件耗时过长
**解决方案**:
1. 使用流式读取JSON
2. 分批处理并立即释放内存
3. 添加进度输出（flush=True）

### API费用
**当前配置**: text-embedding-3-large
**预计费用**:
- 100文档: ~$0.10
- 10,009文档: ~$10-15

## 📝 测试结果

```
查询: "What is Houdini?"
回答: ✅ 成功
质量: 优秀（详细解释了程序化工作流、数字资产等核心概念）
来源: 5个相关文档
```

## 🎯 下一步

1. **立即可用**: 使用当前100文档索引进行测试和演示
2. **扩展索引**: 优化分批构建脚本，构建完整索引
3. **集成应用**: 将RAG系统集成到你的应用中

---

**创建日期**: 2026-02-24
**系统版本**: v1.0
**状态**: 可用（有限数据）
