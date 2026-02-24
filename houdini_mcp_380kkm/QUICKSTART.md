# Quick Start - Houdini MCP 380kkm

快速开始使用 Houdini 自动化地形生成系统。

## 1. 启动 Houdini RPyC 服务器

在 Houdini Python Shell 中运行：

```python
import rpyc
from rpyc.utils.server import ThreadedServer
server = ThreadedServer(rpyc.SlaveService, port=18811)
print("RPyC server started on port 18811")
server.start()
```

## 2. 配置评估 API

```bash
cd core/tools/evaluator
cp config.yaml.template config.yaml
# 编辑 config.yaml 填入 Gemini API key
```

## 3. 测试连接

```bash
# 测试 Houdini 连接
python -c "from core.houdini_mcp.connection import connect; conn = connect(); print('Connected:', conn)"

# 测试评估 API
cd core/tools/evaluator
python test_api_basic.py
```

## 4. 运行示例

```bash
# 生成山脉地形
python examples/mountain_terrain.py
```

## 完整工作流

```
用户描述任务 (自然语言)
    ↓
任务拆解 (流程规划)
    ↓
逐节点实现 (Houdini MCP)
    ↓
效果评估 (Gemini Vision)
    ↓
参数调整 (迭代优化)
    ↓
归档记录 (archives/)
```

## 核心模块

- `core/houdini_mcp/` - Houdini 通信层 (19 个工具)
- `core/tools/evaluator/` - AI 评估系统
- `core/tools/renderer/` - 渲染封装

## 文档索引

- `README.md` - 项目总览
- `INSTALL.md` - 详细安装指南
- `TOOLS.md` - 完整工具索引
- `core/houdini_mcp/README.md` - MCP 工具说明
- `core/tools/evaluator/README.md` - 评估工具说明
- `core/tools/renderer/README.md` - 渲染工具说明

## 常用命令

```bash
# 创建节点
from core.houdini_mcp import tools
tools.create_node("/obj", "geo", "terrain")

# 渲染视口
tools.render_viewport(resolution=[1920, 1080])

# 评估地形
from core.tools.evaluator.evaluator import ImageEvaluator
evaluator = ImageEvaluator()
result = evaluator.evaluate_stage("render.png", "main_mountain", {...})
```

## 故障排除

- **连接失败**: 确认 Houdini RPyC 服务器已启动 (端口 18811)
- **API 错误**: 检查 `core/tools/evaluator/config.yaml` 中的 API key
- **导入错误**: 确认已安装依赖 `pip install -r requirements.txt`
