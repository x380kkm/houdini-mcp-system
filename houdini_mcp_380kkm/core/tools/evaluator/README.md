# Evaluator - 地形评估工具

使用 Gemini Vision API 自动评估 Houdini 地形质量并提供参数建议。

## 使用

```python
from core.tools.evaluator.evaluator import ImageEvaluator

evaluator = ImageEvaluator()
result = evaluator.evaluate_stage(
    image_path="render.png",
    stage="main_mountain",
    current_params={"amplitude": 500, "roughness": 0.5}
)

print(f"评分: {result['score']}/10")
print(f"建议: {result['suggestions']}")
```

## 配置

```bash
cd core/tools/evaluator
cp config.yaml.template config.yaml
# 编辑填入 Gemini API key
```

## 评估阶段

8 个地形生成阶段：
- `base_heightfield` - 基础高度场
- `main_mountain` - 主山脉
- `mid_detail` - 中等细节
- `fine_detail` - 精细细节
- `erosion` - 侵蚀效果
- `terrain_masks` - 地形遮罩
- `material_shading` - 材质着色
- `final_mesh` - 最终网格

## 归档

评估结果自动归档到 `archives/项目名_序号/节点名_序号/时间戳/`
