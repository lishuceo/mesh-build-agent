"""
演示测试脚本
在 Blender 中运行，生成多个示例模型并保存

使用方法：
blender assets/node_library.blend --python examples/demo_test.py
"""

import bpy
import sys
import os

# 添加 src 目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from gnodes_builder import GNodesBuilder


def demo_wall():
    """示例1：简单墙体"""
    print("\n📦 创建示例1: 简单墙体")
    builder = GNodesBuilder("Wall_01")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (4.0, 0.3, 2.5)})
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    # 移动位置便于查看
    builder.get_object().location = (-5, 0, 0)


def demo_pillar():
    """示例2：破损石柱"""
    print("\n📦 创建示例2: 破损石柱")
    builder = GNodesBuilder("Ancient_Pillar")
    builder.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.5, 
        "Height": 3.0, 
        "Resolution": 16
    })
    builder.add_node_group("G_Damage_Edges", inputs={
        "Amount": 0.6,
        "Scale": 2.0,
        "Seed": 123
    })
    builder.add_node_group("G_Scatter_Moss", inputs={
        "Density": 40.0, 
        "Seed": 456
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    builder.get_object().location = (0, 0, 0)


def demo_boulder():
    """示例3：长满苔藓的石头"""
    print("\n📦 创建示例3: 苔藓石头")
    builder = GNodesBuilder("Mossy_Boulder")
    builder.add_node_group("G_Base_Sphere", inputs={
        "Radius": 1.0,
        "Resolution": 12
    })
    builder.add_node_group("G_Damage_Edges", inputs={
        "Amount": 0.8,
        "Scale": 1.5
    })
    builder.add_node_group("G_Scatter_Moss", inputs={
        "Density": 60.0,
        "Seed": 789
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    builder.get_object().location = (5, 0, 0)


def demo_platform():
    """示例4：带顶部装饰的平台"""
    print("\n📦 创建示例4: 装饰平台")
    builder = GNodesBuilder("Decorated_Platform")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (3.0, 3.0, 0.5)
    })
    builder.add_node_group("G_Scatter_On_Top", inputs={
        "Density": 5.0,
        "Seed": 101
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    builder.get_object().location = (0, 5, 0)


def demo_voxel_cube():
    """示例5：体素化立方体"""
    print("\n📦 创建示例5: 体素化立方体")
    builder = GNodesBuilder("Voxel_Cube")
    builder.add_node_group("G_Base_Sphere", inputs={
        "Radius": 1.5,
        "Resolution": 16
    })
    builder.add_node_group("G_Voxel_Remesh", inputs={
        "Voxel_Size": 0.15
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    builder.get_object().location = (0, -5, 0)


def main():
    """运行所有演示"""
    print("\n" + "=" * 60)
    print("🎮 AI Geometry Nodes 演示")
    print("=" * 60)
    
    # 删除默认立方体
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
    
    # 运行所有演示
    demo_wall()
    demo_pillar()
    demo_boulder()
    demo_platform()
    demo_voxel_cube()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！共创建 5 个示例模型")
    print("=" * 60)
    
    # 调整视图
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    bpy.ops.view3d.view_all(override)
                    break
    
    # 如果是命令行模式，保存结果
    if bpy.app.background:
        output_path = os.path.join(project_root, "assets", "demo_output.blend")
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        print(f"\n💾 结果已保存到: {output_path}")


if __name__ == "__main__":
    main()

