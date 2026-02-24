# Houdini MCP 380kkm

个人 Houdini 自动化工具集，基于 Houdini MCP 和 AI 评估系统。

## 核心功能

- **Houdini MCP** - 通过 RPyC 与 Houdini 通信，自动化操作
- **自动评估** - 使用 Gemini API 评估地形质量
- **自动渲染** - 多角度渲染和截图
- **智能建议** - AI 提供参数调整建议
- **归档管理** - 项目-节点层级归档系统
- **缓存系统** - TTL 缓存提升性能，减少 RPyC 调用
- **在线文档** - 从 SideFX 官网实时获取 Houdini 文档
- **布局工具** - 节点着色、自动布局、Network Box 分组

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动 Houdini MCP 服务器
```bash
# 在 Houdini 中运行 Python Shell
import rpyc
from rpyc.utils.server import ThreadedServer
server = ThreadedServer(rpyc.SlaveService, port=18811)
server.start()
```

### 3. 配置评估 API
```bash
cd core/evaluator
cp config.yaml.template config.yaml
# 编辑 config.yaml 填入 API key
```

### 4. 测试
```bash
# 测试 Houdini 连接
python -c "from core.houdini_mcp import tools; print(tools.get_scene_info())"

# 测试评估系统
cd core/evaluator
python test_api_basic.py
python test_full_pipeline.py
```

## 项目结构

```
houdini_mcp_380kkm/
├── core/                          # 核心模块
│   ├── houdini_mcp/               # Houdini MCP 通信层
│   │   ├── server.py              # MCP 服务器
│   │   ├── connection.py          # RPyC 连接管理
│   │   └── tools/                 # 工具集 (渲染/节点/参数等)
│   ├── evaluator/                 # 图片评估系统
│   └── renderer/                  # 渲染封装
├── examples/                      # 示例代码
├── docs/                          # 文档
├── config/                        # 配置文件
└── archives/                      # 归档数据
```

详见 `TOOLS.md` 获取完整工具索引。

## 三层架构

### 1. Houdini MCP 层 (`core/houdini_mcp/`)
- **通信**: RPyC 连接 Houdini (localhost:18811)
- **工具集**: 19 个工具模块
  - `rendering.py` - 渲染和视口截图
  - `pane_screenshot.py` - 窗格截图
  - `nodes.py` - 节点操作
  - `parameters.py` - 参数管理
  - `geometry.py` - 几何操作
  - 等等...

### 2. 渲染封装层 (`core/renderer/`)
- 封装 Houdini MCP 的渲染功能
- 提供简化的 API
- 支持多角度渲染

### 3. 评估层 (`core/evaluator/`)
- 使用 Gemini API 评估质量
- 8 个地形生成阶段
- 参数调整建议
- 归档管理

## 工具索引

### Houdini MCP 工具
- **rendering** - 视口渲染和 ROP 管理
- **pane_screenshot** - 窗格截图 (30 种窗格类型)
- **nodes** - 节点创建/删除/查询
- **parameters** - 参数读写
- **geometry** - 几何数据操作
- **cache** - 缓存系统（节点类型、参数模式）
- **help** - 在线文档获取
- **layout** - 节点布局、着色、分组

### 评估工具
- **image_evaluator** - 自动评估地形质量
- **archive_manager** - 管理评估历史

### 渲染工具
- **houdini_render** - 简化的渲染接口

### 示例
- **simple_mountain** - 简单山脉生成
- **colored_mountain** - 带颜色标记的地形生成

详细说明见 `TOOLS.md`

## 项目来源

本项目基于以下来源：
- **官方参考**: `../temp/` - 官方 houdini-mcp 项目（参考实现）
- **迁移尝试**: `../sandbox_test/` - 本项目的早期迁移尝试
- **当前项目**: `houdini_mcp_380kkm/` - 重组后的正式版本

## 版本

- **版本**: 1.0.0
- **创建日期**: 2026-02-19
- **作者**: 380kkm
