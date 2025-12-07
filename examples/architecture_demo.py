"""
建筑/关卡设计演示脚本
展示新增节点组的能力：曲线、变形、阵列

使用方法：
1. 先更新节点库：blender --background --python scripts/create_node_library.py
2. 运行演示：blender assets/node_library.blend --python examples/architecture_demo.py
"""

import bpy
import sys
import os
import math

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from gnodes_builder import GNodesBuilder, create_chair, create_table_with_chairs, create_fence, create_arch


def clear_scene():
    """清理默认物体"""
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)


def create_twisted_column():
    """创建扭曲柱子 - 展示 G_Twist"""
    print("\n🌀 创建扭曲柱子...")
    
    builder = GNodesBuilder("Twisted_Column")
    builder.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.2,
        "Height": 3.0,
        "Resolution": 16
    })
    builder.add_node_group("G_Twist", inputs={"Angle": math.pi * 1.5})  # 扭曲270度
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    obj = builder.get_object()
    obj.location = (-3, 0, 0)
    return obj


def create_arch_demo():
    """创建拱门 - 使用 create_arch 模板（内部用 G_Arch_Complete，顶点自动缝合）"""
    print("\n🏛️ 创建拱门（create_arch 模板，使用 G_Arch_Complete）...")

    objects = create_arch(
        name="MainArch",
        location=(0, 0, 0),
        width=2.0,
        height=2.0,
        thickness=0.25,
        depth=0.25
    )

    print("   ✓ 拱门：单个网格物体，柱子与拱顶顶点已缝合")
    return objects


def create_pipe_system():
    """创建管道系统 - 展示 G_Pipe"""
    print("\n🔧 创建管道...")
    objects = []
    
    # 竖直管道
    builder = GNodesBuilder("Pipe_Vertical")
    builder.add_node_group("G_Pipe", inputs={
        "Radius": 0.08,
        "Length": 2.0,
        "Resolution": 12
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    pipe_v = builder.get_object()
    pipe_v.location = (3, 0, 0)
    objects.append(pipe_v)
    
    # 水平管道（使用 Cylinder_Centered 旋转）
    builder2 = GNodesBuilder("Pipe_Horizontal")
    builder2.add_node_group("G_Base_Cylinder_Centered", inputs={
        "Radius": 0.08,
        "Height": 1.5,
        "Resolution": 12
    })
    builder2.finalize()
    pipe_h = builder2.get_object()
    pipe_h.location = (3.75, 0, 2.0)
    pipe_h.rotation_euler = (0, math.pi/2, 0)
    objects.append(pipe_h)
    
    return objects


def create_fence_demo():
    """创建栅栏 - 使用 create_fence 模板"""
    print("\n🚧 创建栅栏（使用 create_fence 模板）...")
    
    # 之前需要30+行代码，现在只需一行！
    # 自动计算柱子间距、横杆长度和角度
    objects = create_fence(
        name="Fence_01",
        start_pos=(-4, 3),
        end_pos=(0, 3),
        num_posts=8,
        post_height=1.0,
        rail_height=0.7
    )
    
    print(f"   ✓ 自动生成：8根柱子 + 1根横杆")
    print(f"   ✓ 长度和角度自动计算")
    return objects


def create_circular_table():
    """创建圆桌和椅子 - 使用组合模板"""
    print("\n🪑 创建圆桌场景（使用 create_table_with_chairs 模板）...")
    
    # 之前需要70+行代码，现在只需一行！
    # 空间关系全自动计算，不会出错
    objects = create_table_with_chairs(
        name="DiningSet",
        location=(0, -3, 0.7),
        table_radius=0.6,
        num_chairs=4,
        chair_distance=1.0
    )
    
    print(f"   ✓ 自动生成：1张桌子 + 4把椅子")
    print(f"   ✓ 空间关系自动计算，无需手动推理角度")
    return objects


def create_ruined_pillar():
    """创建废墟石柱 - 展示效果处理"""
    print("\n🏛️ 创建废墟石柱...")
    
    builder = GNodesBuilder("Ruined_Pillar")
    builder.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.3,
        "Height": 2.5,
        "Resolution": 12
    })
    builder.add_node_group("G_Damage_Edges", inputs={
        "Amount": 0.6,
        "Scale": 3.0,
        "Seed": 42
    })
    builder.add_node_group("G_Scatter_Moss", inputs={
        "Density": 30.0,
        "Seed": 123
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    obj = builder.get_object()
    obj.location = (5, 0, 0)
    return obj


def create_ground():
    """创建地面"""
    builder = GNodesBuilder("Ground")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (15, 12, 0.05)})
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    ground = builder.get_object()
    ground.location = (0, 0, 0)
    return ground


def setup_camera():
    """设置相机"""
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
    else:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
    
    cam.location = (8, -10, 6)
    cam.rotation_euler = (1.1, 0, 0.6)
    bpy.context.scene.camera = cam


def setup_lighting():
    """设置灯光"""
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    sun = bpy.context.object
    sun.data.energy = 3
    sun.rotation_euler = (0.8, 0.2, 0.5)


def main():
    print("\n" + "="*60)
    print("🏗️ 建筑/关卡设计演示")
    print("="*60)
    print("\n展示功能：")
    print("  • G_Bend   - 弯曲变形（自动细分+平滑着色）")
    print("  • G_Twist  - 扭曲变形（装饰柱）")
    print("  • G_Pipe   - 便捷管道")
    print("  • G_Taper  - 锥形变形（栅栏尖顶）")
    print("  • G_Damage_Edges - 破损效果")
    print("  • G_Scatter_Moss - 苔藓效果")
    print("  • G_Arch_Complete - 完整拱门（顶点缝合）")
    print("  • create_arch - 组合模板（拱门，单个物体）")
    print("  • create_table_with_chairs - 组合模板（桌椅）")
    print("  • create_fence - 组合模板（栅栏）")

    clear_scene()

    objects = []

    # 地面
    objects.append(create_ground())

    # 各种演示物体
    objects.extend(create_arch_demo())  # 拱门（使用 G_Arch_Complete，顶点缝合）
    objects.append(create_twisted_column())
    objects.extend(create_pipe_system())
    objects.extend(create_fence_demo())
    objects.extend(create_circular_table())
    objects.append(create_ruined_pillar())
    
    # 场景设置
    setup_camera()
    setup_lighting()
    
    total = len([o for o in objects if o])
    
    print("\n" + "="*60)
    print(f"✅ 演示完成！共 {total} 个物体")
    print("="*60)
    print("\n物体说明：")
    print("  • 中间：拱门 (create_arch 模板，G_Arch_Complete 顶点缝合)")
    print("  • 左侧：扭曲柱子 (G_Twist)")
    print("  • 右前：管道系统 (G_Pipe + Cylinder_Centered)")
    print("  • 后方：栅栏 (create_fence 模板)")
    print("  • 前方：圆桌椅子 (create_table_with_chairs 模板)")
    print("  • 右后：废墟石柱 (G_Damage_Edges + G_Scatter_Moss)")
    
    if bpy.app.background:
        out = os.path.join(project_root, "assets", "architecture_demo.blend")
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print(f"\n💾 保存: {out}")


if __name__ == "__main__":
    main()

