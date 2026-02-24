"""
Houdini 地形渲染工具
通过节点流程自动渲染地形预览图
"""

import sys
import time
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.houdini_mcp import tools


def render_heightfield_preview(
    heightfield_node_path: str,
    output_path: str,
    resolution: tuple = (1280, 720),
    camera_distance: float = 1500.0,
    camera_height: float = 600.0,
    camera_angle: float = -25.0
):
    """
    渲染高度场预览图

    Args:
        heightfield_node_path: 高度场节点路径（如 '/obj/mountain_terrain/base_mountains'）
        output_path: 输出图片路径
        resolution: 分辨率 (width, height)
        camera_distance: 相机距离
        camera_height: 相机高度
        camera_angle: 相机俯仰角
    """

    code = f'''
import hou
import os

# 获取高度场节点
hf_node = hou.node('{heightfield_node_path}')
if not hf_node:
    raise ValueError(f"节点不存在: {heightfield_node_path}")

# 获取父对象
obj = hou.node('/obj')

# 创建临时相机
cam = obj.createNode('cam', 'temp_render_cam')
cam.parm('resx').set({resolution[0]})
cam.parm('resy').set({resolution[1]})

# 计算地形中心和尺寸
geo = hf_node.geometry()
bbox = geo.boundingBox()
center = bbox.center()
size = bbox.sizevec()

# 设置相机位置（从侧面斜上方看）
cam.parm('tx').set(center.x() + {camera_distance})
cam.parm('ty').set(center.y() + {camera_distance})
cam.parm('tz').set(center.z() + {camera_height})

# 设置相机朝向（看向地形中心）
cam.parm('rx').set({camera_angle})
cam.parm('ry').set(45.0)

# 创建 OpenGL ROP 节点
rop = obj.createNode('opengl', 'temp_render_rop')
rop.parm('camera').set(cam.path())
rop.parm('picture').set(r'{output_path}')
rop.parm('tres').set(2)  # 1280x720

# 设置渲染选项
rop.parm('soho_outputmode').set(1)  # Render to disk

# 只渲染指定的对象
parent_geo = hf_node.parent().parent()
rop.parm('objects').set(parent_geo.path())

print(f'开始渲染: {{hf_node.path()}}')
print(f'输出: {output_path}')
print(f'分辨率: {resolution[0]}x{resolution[1]}')

# 执行渲染
rop.render(frame_range=(1, 1))

# 检查文件是否生成
if os.path.exists(r'{output_path}'):
    print('✅ 渲染完成')
else:
    print('❌ 渲染失败：文件未生成')

# 清理临时节点
cam.destroy()
rop.destroy()
'''

    print(f"正在渲染: {heightfield_node_path}")
    result = tools.execute_code(code, host='localhost', port=18811, timeout=60)

    if result['stdout']:
        print(result['stdout'])
    if result['stderr']:
        print(f"错误: {result['stderr']}")

    # 等待文件生成
    max_wait = 10
    for i in range(max_wait):
        if os.path.exists(output_path):
            print(f"✅ 渲染文件已生成: {output_path}")
            return True
        time.sleep(1)

    print(f"❌ 渲染超时：文件未生成")
    return False


def render_with_mantra(
    heightfield_node_path: str,
    output_path: str,
    resolution: tuple = (1280, 720),
    samples: int = 1
):
    """
    使用 Mantra 渲染高质量预览

    Args:
        heightfield_node_path: 高度场节点路径
        output_path: 输出图片路径
        resolution: 分辨率
        samples: 采样数（1=快速预览，4+=高质量）
    """

    code = f'''
import hou
import os

# 获取高度场节点
hf_node = hou.node('{heightfield_node_path}')
if not hf_node:
    raise ValueError(f"节点不存在: {heightfield_node_path}")

obj = hou.node('/obj')

# 创建相机
cam = obj.createNode('cam', 'temp_mantra_cam')
cam.parm('resx').set({resolution[0]})
cam.parm('resy').set({resolution[1]})

# 计算地形中心
geo = hf_node.geometry()
bbox = geo.boundingBox()
center = bbox.center()

# 设置相机位置
cam.parm('tx').set(center.x() + 1500.0)
cam.parm('ty').set(center.y() + 1500.0)
cam.parm('tz').set(center.z() + 600.0)
cam.parm('rx').set(-25.0)
cam.parm('ry').set(45.0)

# 创建 Mantra ROP
rop = obj.createNode('ifd', 'temp_mantra_rop')
rop.parm('camera').set(cam.path())
rop.parm('vm_picture').set(r'{output_path}')

# 快速渲染设置
rop.parm('vm_renderengine').set('pbrraytrace')
rop.parm('vm_samples').set({samples})
rop.parm('vm_samplesx').set({samples})
rop.parm('vm_samplesy').set({samples})

# 设置分辨率
rop.parm('override_camerares').set(1)
rop.parm('res_fraction').set('specific')
rop.parm('res_overridex').set({resolution[0]})
rop.parm('res_overridey').set({resolution[1]})

print(f'开始 Mantra 渲染: {{hf_node.path()}}')
print(f'输出: {output_path}')

# 执行渲染
rop.render(frame_range=(1, 1))

# 检查文件
if os.path.exists(r'{output_path}'):
    print('✅ Mantra 渲染完成')
else:
    print('❌ Mantra 渲染失败')

# 清理
cam.destroy()
rop.destroy()
'''

    print(f"正在使用 Mantra 渲染: {heightfield_node_path}")
    result = tools.execute_code(code, host='localhost', port=18811, timeout=120)

    if result['stdout']:
        print(result['stdout'])
    if result['stderr']:
        print(f"错误: {result['stderr']}")

    # 等待文件生成
    max_wait = 30
    for i in range(max_wait):
        if os.path.exists(output_path):
            print(f"✅ 渲染文件已生成: {output_path}")
            return True
        time.sleep(1)

    print(f"❌ 渲染超时")
    return False


if __name__ == '__main__':
    # 测试
    import argparse

    parser = argparse.ArgumentParser(description='渲染 Houdini 地形预览')
    parser.add_argument('node', help='高度场节点路径')
    parser.add_argument('output', help='输出图片路径')
    parser.add_argument('--method', choices=['opengl', 'mantra'], default='opengl', help='渲染方法')
    parser.add_argument('--resolution', default='1280x720', help='分辨率 (WxH)')

    args = parser.parse_args()

    # 解析分辨率
    w, h = map(int, args.resolution.split('x'))

    # 渲染
    if args.method == 'opengl':
        success = render_heightfield_preview(args.node, args.output, (w, h))
    else:
        success = render_with_mantra(args.node, args.output, (w, h))

    sys.exit(0 if success else 1)
