# Houdini RAG 查询技能

查询 Houdini 文档知识库，获取关于 Houdini 的详细信息和技术文档。

## 用法

```bash
houdini-rag <问题>
```

## 示例

```bash
# 基础问题
houdini-rag "What is Houdini?"

# 技术问题
houdini-rag "How do I create a heightfield terrain?"

# VEX编程
houdini-rag "What VEX functions are available for vector math?"

# 节点相关
houdini-rag "How does the Copy to Points node work?"

# 工作流程
houdini-rag "How do I set up a Pyro simulation?"
```

## 功能

- 基于向量检索的语义搜索
- 从10,009个Houdini官方文档中检索
- 提供详细回答和参考来源
- 支持中英文查询

## 覆盖范围

- 所有节点类型 (SOP, DOP, VOP, LOP, ROP, CHOP, COP, TOP)
- VEX编程语言
- Python API (HOM)
- 工具和工作流程
- 动力学模拟
- 渲染和材质
- 角色和动画

## 注意事项

- 需要先构建向量索引
- 需要配置API密钥（config.yaml）
- 当前使用100文档测试索引

## 相关文件

- 配置: `houdini_rag/config.yaml`
- 数据: `houdini_rag/data/raw/houdini_docs.json`
- 索引: `houdini_rag/data/chroma/`
