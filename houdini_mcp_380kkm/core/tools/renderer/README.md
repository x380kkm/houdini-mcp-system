# Renderer - 渲染工具

简化的 Houdini 渲染接口。

## 使用

```python
from core.tools.renderer.houdini_render import render_heightfield_preview

render_heightfield_preview(
    heightfield_node_path="/obj/terrain/base_mountains",
    output_path="render.png",
    resolution=(1280, 720)
)
```

## 渲染方法

- `opengl` - 快速预览
- `mantra` - 高质量渲染
