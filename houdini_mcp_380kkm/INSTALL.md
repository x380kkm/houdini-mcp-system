# 安装指南

## 系统要求

- Python 3.11+
- Houdini 19.5+ (或其他支持 Python 3 的版本)
- Windows / Linux / macOS

## 安装步骤

### 1. 克隆/下载项目
```bash
cd /path/to/your/projects
git clone <repo-url> houdini_mcp_380kkm
cd houdini_mcp_380kkm
```

### 2. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

主要依赖：
- `rpyc` - 远程 Python 调用
- `mcp` - Model Context Protocol
- `pyyaml` - 配置管理
- `requests` - API 调用
- `Pillow` - 图片处理

### 3. 配置 Houdini

#### 方法 1: 手动启动 RPyC 服务器
在 Houdini Python Shell 中运行：
```python
import rpyc
from rpyc.utils.server import ThreadedServer
server = ThreadedServer(rpyc.SlaveService, port=18811)
print("RPyC server started on port 18811")
server.start()
```

#### 方法 2: 使用 Houdini 插件 (推荐)
```bash
# 复制插件到 Houdini
cp -r sandbox_test/houdini-mcp/houdini_plugin $HOUDINI_USER_PREF_DIR/scripts/python/
```

然后在 Houdini 中：
1. Windows → Python Shell
2. 运行: `import houdini_mcp_server; houdini_mcp_server.start()`

### 4. 配置评估 API
```bash
cd core/evaluator
cp config.yaml.template config.yaml
# 编辑 config.yaml，填入你的 Gemini API key
```

### 5. 测试安装

#### 测试 Houdini 连接
```bash
python -c "from core.houdini_mcp import tools; print(tools.get_scene_info())"
```

应该看到 Houdini 场景信息。

#### 测试评估系统
```bash
cd core/evaluator
python test_api_basic.py
```

应该看到 API 连接成功。

#### 测试完整流程
```bash
cd core/evaluator
python test_full_pipeline.py
```

应该看到渲染和评估结果。

## 配置 Claude Desktop (可选)

如果要在 Claude Desktop 中使用：

```bash
# 编辑 Claude Desktop 配置
# Windows: %APPDATA%\Claude\claude_desktop_config.json
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Linux: ~/.config/Claude/claude_desktop_config.json
```

添加：
```json
{
  "mcpServers": {
    "houdini": {
      "command": "python",
      "args": ["-m", "core.houdini_mcp.server"],
      "cwd": "/path/to/houdini_mcp_380kkm"
    }
  }
}
```

## 故障排除

### RPyC 连接失败
- 确认 Houdini 中 RPyC 服务器已启动
- 检查端口 18811 是否被占用
- 尝试重启 Houdini

### API 调用失败
- 检查 `core/evaluator/config.yaml` 中的 API key
- 确认网络连接正常
- 查看 `core/evaluator/image_evaluator.log`

### 导入错误
- 确认已安装所有依赖: `pip install -r requirements.txt`
- 检查 Python 版本: `python --version` (需要 3.11+)

## 下一步

安装完成后，查看：
- `README.md` - 项目总览
- `TOOLS.md` - 工具索引
- `core/evaluator/README.md` - 评估系统使用
- `examples/mountain_terrain.py` - 完整示例
