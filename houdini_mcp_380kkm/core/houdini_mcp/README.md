# Houdini MCP 核心模块

Houdini MCP 通信层，通过 RPyC 与 Houdini 进行远程通信。

## 功能

- **RPyC 连接管理** - 连接到 Houdini Python 环境
- **19 个工具模块** - 覆盖节点、参数、几何、渲染等
- **MCP 服务器** - 标准 MCP 协议实现

## 工具模块

### 渲染相关
- `rendering.py` - 视口渲染、ROP 管理
- `pane_screenshot.py` - 窗格截图 (30 种类型)

### 节点操作
- `nodes.py` - 创建、删除、查询节点
- `wiring.py` - 节点连接
- `layout.py` - 节点布局

### 参数管理
- `parameters.py` - 读写参数
- `code.py` - 执行 Python 代码

### 几何操作
- `geometry.py` - 几何数据读写
- `scene.py` - 场景信息

### 其他
- `materials.py` - 材质管理
- `cache.py` - 缓存管理
- `errors.py` - 错误处理
- `help.py` - 帮助信息
- `hscript.py` - HScript 命令
- `summarization.py` - 场景总结

## 使用

### Python API
```python
from core.houdini_mcp import tools

# 渲染视口
result = tools.render_viewport(
    resolution=[1024, 768],
    renderer="opengl"
)

# 截图窗格
result = tools.capture_pane_screenshot(
    pane_types=['SceneViewer']
)

# 创建节点
result = tools.create_node(
    parent_path="/obj",
    node_type="geo",
    node_name="terrain"
)
```

### 启动 MCP 服务器
```bash
python -m core.houdini_mcp.server
```

## 连接要求

- Houdini 需要运行 RPyC 服务器 (端口 18811)
- 在 Houdini Python Shell 中运行：
```python
import rpyc
from rpyc.utils.server import ThreadedServer
server = ThreadedServer(rpyc.SlaveService, port=18811)
server.start()
```

