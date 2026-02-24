"""
简单山脉生成示例

测试基本的 Houdini 节点创建和参数设置
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.houdini_mcp.connection import connect


def create_simple_mountain():
    """创建简单的山脉地形"""

    print("连接 Houdini...")
    conn, hou = connect()
    print("✅ 已连接\n")

    # 获取 /obj 节点
    obj = hou.node("/obj")

    # 清理旧节点
    if obj.node("simple_mountain"):
        obj.node("simple_mountain").destroy()
        print("清理旧节点\n")

    # 创建 geo 容器
    print("步骤 1: 创建 geo 容器")
    geo = obj.createNode("geo", "simple_mountain")
    print(f"✅ 创建: {geo.path()}\n")

    # 创建 heightfield
    print("步骤 2: 创建基础 heightfield")
    hf = geo.createNode("heightfield", "base")
    hf.parm("gridspacing").set(2.0)
    hf.parm("gridsamples").set(512)
    hf.parm("sizex").set(1000.0)
    hf.parm("sizey").set(1000.0)
    hf.setDisplayFlag(True)
    print(f"✅ 创建: {hf.path()}")
    print(f"   分辨率: 512x512, 尺寸: 1000x1000\n")

    # 布局
    geo.layoutChildren()

    # 添加噪声
    print("步骤 3: 添加主山脉噪声")
    noise = geo.createNode("heightfield_noise", "main_mountain")
    noise.setInput(0, hf)
    noise.parm("amp").set(100.0)
    noise.parm("elementsize").set(50.0)
    noise.parm("rough").set(0.5)
    noise.parm("oct").set(8)
    noise.setDisplayFlag(True)
    print(f"✅ 创建: {noise.path()}")
    print(f"   振幅: 100, 元素大小: 50, 粗糙度: 0.5\n")

    # 布局
    geo.layoutChildren()

    # 添加细节
    print("步骤 4: 添加细节层")
    detail = geo.createNode("heightfield_noise", "detail")
    detail.setInput(0, noise)
    detail.parm("amp").set(20.0)
    detail.parm("elementsize").set(10.0)
    detail.parm("rough").set(0.8)
    detail.parm("offsetx").set(123.0)  # 不同种子
    detail.setDisplayFlag(True)
    print(f"✅ 创建: {detail.path()}")
    print(f"   振幅: 20, 元素大小: 10\n")

    # 布局
    geo.layoutChildren()

    # 转换为网格
    print("步骤 5: 转换为多边形网格")
    output = geo.createNode("heightfield_output", "mesh")
    output.setInput(0, detail)
    output.setDisplayFlag(True)
    output.setRenderFlag(True)
    print(f"✅ 创建: {output.path()}\n")

    # 最终布局
    geo.layoutChildren(horizontal_spacing=2.0, vertical_spacing=1.5)

    print("="*60)
    print("✅ 山脉地形创建完成！")
    print("="*60)
    print(f"节点路径: {geo.path()}")
    print(f"节点数量: {len(geo.children())}")
    print("\n在 Houdini 中查看效果")


if __name__ == "__main__":
    create_simple_mountain()
