# HDA 教程生成工作流程

## 概述

本项目提供了一套完整的工具链，用于从 Houdini Digital Asset (HDA) 文件自动生成详细的教程文档。

## 工作流程

### 1. 连接 Houdini MCP

**前置条件**：
- Houdini 已启动
- hrpyc 服务器已运行

**启动 hrpyc 服务器**：
```python
# 在 Houdini Python Shell 中执行
import hrpyc
hrpyc.start_server(port=18811)
```

### 2. 提取节点数据

**命令**：
```bash
python extract_hda_nodes.py <HDA文件路径> [深度]
```

**参数说明**：
- `HDA文件路径`：HDA 文件的完整路径
- `深度`（可选）：
  - `0`：只提取表层节点（默认）
  - `1`：提取第一层子节点
  - `-1`：提取所有层级

**输出**：
- `hda_nodes_list.json`：节点结构、参数、VEX 代码
- `hda_vex_codes.json`：单独的 VEX 代码文件（如果有）

**示例**：
```bash
# 提取表层节点
python extract_hda_nodes.py "E:\path\to\your.hda" 0

# 提取所有层级
python extract_hda_nodes.py "E:\path\to\your.hda" -1
```

### 3. 生成完整文档

**命令**：
```bash
python generate_hda_doc.py hda_nodes_list.json
```

**处理流程**：
- **节点类型**：通过 RAG 系统查询 Houdini 官方文档
- **VEX 代码**：直接调用 LLM 进行解释
- **参数信息**：从提取的数据中读取

**输出**：
- `hda_docs/YYYYMMDD_HHMMSS/`：带时间戳的文档目录
  - `HDA_Complete_Documentation.md`：完整文档
  - `VEX_Code_Documentation.md`：VEX 代码说明
  - `Node_Types_Documentation.md`：节点类型说明
  - `*.json`：原始数据

### 4. 生成教程章节

**方式 1：使用自动化脚本**
```bash
python generate_hda_tutorial.py <HDA文件路径> [选项]
```

**选项**：
- `--depth <N>`：提取深度（默认 0）
- `--output <DIR>`：输出目录（默认 blog_YYYYMMDD_HHMMSS）
- `--host <HOST>`：Houdini 主机（默认 localhost）
- `--port <PORT>`：Houdini 端口（默认 18811）

**方式 2：使用 Claude Code**

1. 打开 Claude Code
2. 提供以下输入：
   - `hda_nodes_list.json`：节点数据
   - `hda_docs/YYYYMMDD_HHMMSS/HDA_Complete_Documentation.md`：完整文档
3. 要求生成教程章节

**输出结构**：
```
blog_YYYYMMDD_HHMMSS/
├── README.md                    # 教程总览
├── 01_基础几何体准备.md
├── 02_自动斜角系统.md
├── 03_对象合并与条件切换.md
├── 04_循环处理系统.md
├── 05_几何体清理.md
├── 06_纹理映射.md
├── 07_UV处理.md
├── 08_材质属性.md
├── 09_核心算法.md
├── 10_边缘处理.md
└── 11_比例控制.md
```

## 教程章节格式

每个章节包含：

1. **功能目标**：要实现什么
2. **算法思路**：核心逻辑和数学原理
3. **数据流图**：ASCII 图表展示节点连接
4. **参数配置**：实际参数值（来自提取的数据）
5. **测试验证**：Python 测试代码
6. **常见问题**：FAQ
7. **优化建议**：性能和质量优化
8. **节点详解**：技术参考

## 文件组织

### 工程文件（提交到 Git）
```
mcp_project/
├── extract_hda_nodes.py          # 节点提取脚本
├── generate_hda_doc.py           # 文档生成脚本（串行）
├── generate_hda_doc_parallel.py  # 文档生成脚本（并行）
├── generate_hda_tutorial.py      # 教程生成脚本
├── CLAUDE.md                     # 项目指南
├── README.md                     # 项目说明
├── .gitignore                    # Git 忽略配置
├── houdini_mcp_380kkm/           # MCP 核心
└── houdini_rag/                  # RAG 系统
```

### 非工程文件（不提交）
```
mcp_project/
├── blog/                         # 教程章节（示例）
├── blog_*/                       # 生成的教程（带时间戳）
├── hda_docs/                     # 生成的文档
├── hda_nodes_list.json           # 提取的节点数据
├── hda_vex_codes.json            # 提取的 VEX 代码
├── TODO.md                       # 临时任务列表
└── blog.md                       # 临时笔记
```

## 完整示例

### 示例 1：快速生成教程

```bash
# 1. 启动 Houdini 并运行 hrpyc
# （在 Houdini Python Shell 中）
import hrpyc
hrpyc.start_server(port=18811)

# 2. 使用自动化脚本
python generate_hda_tutorial.py "E:\素材\GameJamStarterKit\otls\HE_TrimT_Tool.hda" --depth 0

# 3. 查看输出
# blog_20260225_143022/TASK.md
```

### 示例 2：手动分步执行

```bash
# 1. 提取节点（表层）
python extract_hda_nodes.py "E:\素材\GameJamStarterKit\otls\HE_TrimT_Tool.hda" 0

# 2. 生成完整文档
python generate_hda_doc.py hda_nodes_list.json

# 3. 使用 Claude Code 生成教程
# 打开 Claude Code，提供：
# - hda_nodes_list.json
# - hda_docs/20260225_130422/HDA_Complete_Documentation.md
# 要求：生成教程章节到 blog_20260225_143022/
```

### 示例 3：并行生成（更快）

```bash
# 使用并行版本（6-8x 更快）
python generate_hda_doc_parallel.py hda_nodes_list.json 10
```

## 技术细节

### 节点提取

**核心功能**：
- 递归遍历 HDA 内部节点
- 提取节点类型、路径、深度
- 提取非默认参数值
- 提取 VEX 代码（wrangle 节点）
- 跳过不可序列化的参数（如 Ramp）

**关键代码**：
```python
def get_node_list(node, depth=0, max_depth=10, target_depth=-1):
    # 递归获取节点信息
    # target_depth: -1=所有层, 0=只顶层, 1=第一层子节点
    ...
```

### 文档生成

**RAG 查询**（节点类型）：
```python
# 查询 Houdini 官方文档
answer = rag.query(f"What is the {node_type} node in Houdini?")
```

**LLM 直接调用**（VEX 代码）：
```python
# 直接调用 LLM 解释 VEX
explanation = rag.llm.invoke(prompt).content
```

### 教程生成

**数据来源**：
1. `hda_nodes_list.json`：实际参数值
2. `HDA_Complete_Documentation.md`：节点说明和 VEX 解释
3. 节点连接关系：从 HDA 结构推断

**生成策略**：
- 按功能模块分章节（不是按节点顺序）
- 逻辑和数学公式优先
- 节点详解放在最后
- 包含可测试的验证代码

## 性能优化

### 并行处理

使用 `generate_hda_doc_parallel.py`：
```bash
# 10 个线程
python generate_hda_doc_parallel.py hda_nodes_list.json 10
```

**性能对比**：
- 串行：~5-10 分钟（531 个节点）
- 并行（10 线程）：~1-2 分钟

### RAG 系统优化

**向量数据库**：
- 使用 ChromaDB
- 预先构建索引
- 缓存查询结果

**查询优化**：
- 批量查询节点类型
- 避免重复查询
- 使用合适的 top_k 值

## 故障排除

### 连接失败

**问题**：`Connection refused (port 18811)`

**解决**：
```python
# 在 Houdini 中检查
import hrpyc
hrpyc.start_server(port=18811)
```

### JSON 序列化错误

**问题**：`Object of type Ramp is not JSON serializable`

**解决**：已在 `extract_hda_nodes.py` 中处理，跳过 Ramp 类型参数

### RAG 查询失败

**问题**：向量数据库未构建

**解决**：
```bash
cd houdini_rag
python cli.py scrape --max-pages 500
python cli.py index
```

## 最佳实践

1. **提取深度选择**：
   - 表层（depth=0）：快速预览，适合大多数情况
   - 所有层（depth=-1）：完整分析，用于深入研究

2. **文档生成**：
   - 小型 HDA（<100 节点）：使用串行版本
   - 大型 HDA（>100 节点）：使用并行版本

3. **教程生成**：
   - 使用 Claude Code 生成更灵活
   - 可以根据需要调整章节结构
   - 结合实际参数值和文档说明

4. **版本控制**：
   - 只提交工程文件
   - 生成的文档和教程不提交
   - 使用 .gitignore 排除

## 相关文档

- [CLAUDE.md](./CLAUDE.md)：项目架构和命令
- [README.md](./README.md)：项目说明
- [houdini_rag/README.md](./houdini_rag/README.md)：RAG 系统说明

## 更新日志

- **2026-02-25**：创建工作流程文档
- **2026-02-25**：添加教程生成脚本
- **2026-02-25**：完成 11 章教程示例
