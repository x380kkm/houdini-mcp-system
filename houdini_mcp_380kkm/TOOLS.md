# 工具索引 (TOOLS.md)

AI 友好的工具索引，快速定位和使用项目中的各种工具。

---

## 📊 评估工具

### image_evaluator
**自动评估 Houdini 地形质量**

- **路径**: `core/evaluator/`
- **主文件**: `evaluator.py`, `cli.py`
- **配置**: `config.yaml`, `prompts.yaml`
- **文档**: `core/evaluator/README.md`

**命令行使用**:
```bash
cd core/evaluator
python cli.py image.png --stage main_mountain --params '{"amplitude": 500, ...}'
python cli.py --list-stages
```

**Python API**:
```python
from core.evaluator.evaluator import ImageEvaluator
evaluator = ImageEvaluator()
result = evaluator.evaluate_stage("image.png", "main_mountain", {...})
```

**支持的阶段** (8 个):
1. `base_heightfield` - 基础高度场
2. `main_mountain` - 主山脉结构
3. `mid_detail` - 中等细节
4. `fine_detail` - 精细细节
5. `erosion` - 侵蚀效果
6. `terrain_masks` - 地形遮罩
7. `material_shading` - 材质着色
8. `final_mesh` - 最终网格

**输出格式**:
```json
{
  "quality_score": 8,
  "status": "success",
  "metrics": {...},
  "feedback": "...",
  "parameter_adjustments": {...}
}
```

---

### archive_manager
**管理评估历史归档**

- **路径**: `core/evaluator/archive_manager.py`
- **归档目录**: `archives/`

**命令**:
```bash
# 创建项目
python archive_manager.py create-project terrain_001

# 添加评估记录
python archive_manager.py add-evaluation \
    --project terrain_001 \
    --node "/obj/mountain_terrain/base_mountains" \
    --image "render.png"

# 清理旧记录 (交互式)
python archive_manager.py cleanup --days 30

# 列出项目
python archive_manager.py list-projects

# 列出节点
python archive_manager.py list-nodes terrain_001
```

**归档结构**:
```
archives/
└── project_terrain_001/
    └── base_mountains_001/
        ├── metadata.json
        └── 20260219_183115/
            ├── render.png
            ├── evaluation.json
            └── parameters.json
```

---

## 🎨 渲染工具

### houdini_render
**通过 Houdini MCP 自动渲染地形**

- **路径**: `core/renderer/houdini_render.py`
- **依赖**: Houdini MCP (rpyc 连接)

**函数**:
```python
# OpenGL 快速渲染
render_heightfield_preview(
    heightfield_node_path="/obj/terrain/base_mountains",
    output_path="render.png",
    resolution=(1280, 720),
    camera_distance=1500.0,
    camera_height=600.0,
    camera_angle=-25.0
)

# Mantra 高质量渲染
render_with_mantra(
    heightfield_node_path="/obj/terrain/base_mountains",
    output_path="render.png",
    resolution=(1920, 1080),
    samples=4
)
```

**命令行使用**:
```bash
python houdini_render.py \
    /obj/terrain/base_mountains \
    output.png \
    --method opengl \
    --resolution 1280x720
```

**支持的角度**:
- `front` - 正面视图 [0, 0, 0]
- `top` - 俯视图 [-90, 0, 0]
- `side` - 侧面视图 [0, 90, 0]
- `isometric` - 等轴测 [-30, 45, 0]

---

## 📚 示例代码

### mountain_terrain
**完整地形生成流程示例**

- **路径**: `examples/mountain_terrain.py`
- **功能**: 9 步地形生成流程

**步骤**:
1. 创建基础高度场
2. 添加主山脉噪声
3. 添加细节层
4. 应用侵蚀效果
5. 创建地形遮罩
6. 应用材质系统
7. 散布植被
8. 转换为网格
9. 设置渲染

**使用**:
```python
from examples.mountain_terrain import MountainTerrainGenerator, TerrainConfig

config = TerrainConfig(
    resolution=1024,
    size=1000.0,
    base_height=100.0
)

generator = MountainTerrainGenerator()
generator.connect()
generator.create_full_terrain(config)
```

---

## 🧪 测试工具

### test_api_basic
**测试 API 连接**
```bash
cd core/evaluator
python test_api_basic.py
```

### test_houdini_render
**测试 Houdini 渲染功能**
```bash
cd core/evaluator
python test_houdini_render.py
```

### test_full_pipeline
**测试完整流程 (渲染→评估)**
```bash
cd core/evaluator
python test_full_pipeline.py
```

---

## 📖 文档索引

### 核心文档
- `README.md` - 项目总览
- `TOOLS.md` - 本文档
- `core/evaluator/README.md` - 评估系统快速开始
- `core/evaluator/PROMPT_ENGINEERING.md` - Prompt 工程详细说明
- `core/evaluator/PROJECT_STRUCTURE.md` - 项目结构说明
- `core/evaluator/COMPLETION.md` - 完成总结

### 参考文档
- `docs/archive/` - 历史文档归档
- `docs/progress/` - 开发进度记录

---

## 🔧 配置文件

### API 配置
**文件**: `core/evaluator/config.yaml`
```yaml
api:
  base_url: "https://llmxapi.com/v1"
  api_key: "your-api-key"
  model: "gemini-3-pro-preview"
  max_tokens: 4000
```

### Claude Desktop 配置
**文件**: `config/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "houdini": {
      "command": "python",
      "args": ["-m", "houdini_mcp.server"]
    }
  }
}
```

---

## 🚀 常用工作流

### 工作流 1: 评估现有地形
```bash
# 1. 渲染地形
cd core/renderer
python houdini_render.py /obj/terrain/base_mountains render.png

# 2. 评估
cd ../evaluator
python cli.py render.png --stage main_mountain --params params.json

# 3. 归档
python archive_manager.py add-evaluation \
    --project terrain_001 \
    --node "/obj/terrain/base_mountains" \
    --image render.png
```

### 工作流 2: 自动化迭代优化
```bash
# 运行完整流程测试 (包含多角度评估)
cd core/evaluator
python test_full_pipeline.py

# 根据 AI 建议调整参数，重新生成地形
# 重复直到质量达标 (8/10+)
```

---

## 🔧 系统工具

### 缓存系统
**提升性能的内存缓存**

- **路径**: `core/houdini_mcp/tools/cache.py`
- **功能**: TTL 缓存、线程安全、统计监控

**使用**:
```python
from core.houdini_mcp.tools import get_cache_stats, invalidate_all_caches

# 获取缓存统计
stats = get_cache_stats()
print(f"命中率: {stats['node_types']['hit_rate']}")

# 失效所有缓存（场景切换时自动调用）
invalidate_all_caches()
```

**缓存类型**:
- `node_type_cache` - 节点类型缓存（TTL: 1小时）
- `parameter_schema_cache` - 参数模式缓存（TTL: 1小时）

**自动失效**:
- `load_scene()` - 加载场景时
- `new_scene()` - 新建场景时

---

### 在线文档获取
**从 SideFX 官网获取 Houdini 文档**

- **路径**: `core/houdini_mcp/tools/help.py`
- **功能**: 无需 Houdini 连接，实时获取最新文档

**使用**:
```python
from core.houdini_mcp.tools import get_houdini_help

# 获取节点文档
doc = get_houdini_help("sop", "heightfield_noise")
print(doc['description'])
print(doc['parameters'])

# 获取 VEX 函数文档
doc = get_houdini_help("vex_function", "noise")
```

**支持类型**:
- `sop`, `obj`, `dop`, `cop2`, `chop`, `vop`, `lop`, `top`, `rop`
- `vex_function` - VEX 函数
- `python_hou` - HOM API

---

### 布局工具
**节点组织和可视化**

- **路径**: `core/houdini_mcp/tools/layout.py`
- **功能**: 自动布局、着色、定位、分组

**使用**:
```python
from core.houdini_mcp.tools import (
    layout_children,
    set_node_color,
    create_network_box
)

# 自动布局
layout_children("/obj/geo1", horizontal_spacing=2.5)

# 设置节点颜色
set_node_color("/obj/geo1/noise1", [0.3, 0.5, 1.0])  # 蓝色

# 创建 Network Box
create_network_box(
    parent_path="/obj/geo1",
    node_paths=["/obj/geo1/box1", "/obj/geo1/noise1"],
    label="Terrain Generation",
    color=[0.2, 0.4, 0.8]
)
```

**颜色方案示例**:
- 蓝色 `[0.3, 0.5, 1.0]` - Macro（大尺度）
- 绿色 `[0.3, 0.8, 0.3]` - Meso（中等细节）
- 黄色 `[1.0, 0.8, 0.2]` - Micro（精细细节）

---

## 📦 依赖

### Python 包
```bash
pip install -r core/evaluator/requirements.txt
```
- `pyyaml` - 配置管理
- `requests` - API 调用
- `Pillow` - 图片处理

### 外部依赖
- **Houdini** - 3D 软件
- **Houdini MCP** - Houdini 自动化接口
- **Gemini API** - 视觉评估服务

---

## 💡 提示

### 对于 AI 助手
- 使用 `python -m core.evaluator.cli --list-stages` 查看可用阶段
- 评估结果是结构化 JSON，可直接解析
- 归档系统使用 UUID 映射，避免重命名冲突
- 所有工具都有 `--help` 参数

### 对于开发者
- 测试脚本在 `core/evaluator/test_*.py`
- Prompt 模板在 `core/evaluator/prompts.yaml`
- 临时文件在 `test_images/` 和 `evaluation_history/`
- 正式归档在 `archives/`

---

**版本**: 1.0.0
**更新日期**: 2026-02-19
