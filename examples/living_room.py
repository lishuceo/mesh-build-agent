"""
客厅场景生成脚本
生成一个 5m x 4m 的客厅，包含沙发、电视、茶几等家具

使用方法：
blender assets/node_library.blend --python examples/living_room.py

布局说明（俯视图）：
    ┌─────────────────────────────┐
    │           电视墙             │ (Y = 4m)
    │         ┌───────┐           │
    │         │ 电视柜 │           │
    │         │  电视  │           │
    │         └───────┘           │
    │                             │
    │          ┌─────┐            │
    │          │ 茶几 │            │
    │          └─────┘            │
    │                             │
    │    ┌─────────────────┐      │
    │    │      沙发       │      │ (Y = 0.5m)
    │    └─────────────────┘      │
    └─────────────────────────────┘
    (X = 0)                    (X = 5m)
"""

import bpy
import sys
import os

# 设置路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from gnodes_builder import GNodesBuilder

# ============ 房间尺寸 ============
ROOM_WIDTH = 5.0   # X 方向
ROOM_DEPTH = 4.0   # Y 方向
ROOM_HEIGHT = 2.8  # 层高


def create_floor():
    """创建地板"""
    print("\n🏠 创建地板...")
    builder = GNodesBuilder("Floor")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (ROOM_WIDTH, ROOM_DEPTH, 0.05)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    obj = builder.get_object()
    obj.location = (ROOM_WIDTH / 2, ROOM_DEPTH / 2, 0)
    return obj


def create_sofa():
    """
    创建沙发（3人座）
    尺寸：宽 2.2m，深 0.9m，高 0.85m
    """
    print("\n🛋️ 创建沙发...")
    
    # 沙发底座
    builder = GNodesBuilder("Sofa_Base")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (2.2, 0.9, 0.45)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    base = builder.get_object()
    base.location = (ROOM_WIDTH / 2, 0.6, 0)
    
    # 沙发靠背
    builder2 = GNodesBuilder("Sofa_Back")
    builder2.add_node_group("G_Base_Cube", inputs={
        "Size": (2.2, 0.15, 0.45)
    })
    builder2.add_node_group("G_Align_Ground")
    builder2.finalize()
    back = builder2.get_object()
    back.location = (ROOM_WIDTH / 2, 0.2, 0.45)
    
    # 左扶手
    builder3 = GNodesBuilder("Sofa_Arm_Left")
    builder3.add_node_group("G_Base_Cube", inputs={
        "Size": (0.15, 0.75, 0.3)
    })
    builder3.add_node_group("G_Align_Ground")
    builder3.finalize()
    arm_left = builder3.get_object()
    arm_left.location = (ROOM_WIDTH / 2 - 1.1 + 0.075, 0.525, 0.45)
    
    # 右扶手
    builder4 = GNodesBuilder("Sofa_Arm_Right")
    builder4.add_node_group("G_Base_Cube", inputs={
        "Size": (0.15, 0.75, 0.3)
    })
    builder4.add_node_group("G_Align_Ground")
    builder4.finalize()
    arm_right = builder4.get_object()
    arm_right.location = (ROOM_WIDTH / 2 + 1.1 - 0.075, 0.525, 0.45)
    
    return [base, back, arm_left, arm_right]


def create_coffee_table():
    """
    创建茶几
    尺寸：宽 1.2m，深 0.6m，高 0.45m
    """
    print("\n☕ 创建茶几...")
    
    # 桌面
    builder = GNodesBuilder("CoffeeTable_Top")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (1.2, 0.6, 0.05)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    top = builder.get_object()
    top.location = (ROOM_WIDTH / 2, ROOM_DEPTH / 2, 0.4)
    
    # 四条腿
    legs = []
    leg_positions = [
        (ROOM_WIDTH / 2 - 0.5, ROOM_DEPTH / 2 - 0.25),
        (ROOM_WIDTH / 2 + 0.5, ROOM_DEPTH / 2 - 0.25),
        (ROOM_WIDTH / 2 - 0.5, ROOM_DEPTH / 2 + 0.25),
        (ROOM_WIDTH / 2 + 0.5, ROOM_DEPTH / 2 + 0.25),
    ]
    
    for i, (x, y) in enumerate(leg_positions):
        builder = GNodesBuilder(f"CoffeeTable_Leg_{i+1}")
        builder.add_node_group("G_Base_Cylinder", inputs={
            "Radius": 0.03,
            "Height": 0.4,
            "Resolution": 8
        })
        builder.add_node_group("G_Align_Ground")
        builder.finalize()
        leg = builder.get_object()
        leg.location = (x, y, 0)
        legs.append(leg)
    
    return [top] + legs


def create_tv_stand():
    """
    创建电视柜
    尺寸：宽 1.8m，深 0.4m，高 0.5m
    """
    print("\n📺 创建电视柜...")
    
    builder = GNodesBuilder("TV_Stand")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (1.8, 0.4, 0.5)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    obj = builder.get_object()
    obj.location = (ROOM_WIDTH / 2, ROOM_DEPTH - 0.25, 0)
    return obj


def create_tv():
    """
    创建电视
    尺寸：55寸电视，约 1.22m x 0.05m x 0.71m
    """
    print("\n📺 创建电视...")
    
    builder = GNodesBuilder("TV")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (1.22, 0.05, 0.71)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    obj = builder.get_object()
    obj.location = (ROOM_WIDTH / 2, ROOM_DEPTH - 0.2, 0.55)
    return obj


def create_side_table():
    """
    创建边几（沙发旁边）
    尺寸：0.5m x 0.5m x 0.55m
    """
    print("\n🪑 创建边几...")
    
    # 桌面
    builder = GNodesBuilder("SideTable_Top")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (0.5, 0.5, 0.04)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    top = builder.get_object()
    top.location = (ROOM_WIDTH / 2 + 1.5, 0.6, 0.51)
    
    # 腿
    builder2 = GNodesBuilder("SideTable_Leg")
    builder2.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.15,
        "Height": 0.5,
        "Resolution": 12
    })
    builder2.add_node_group("G_Align_Ground")
    builder2.finalize()
    leg = builder2.get_object()
    leg.location = (ROOM_WIDTH / 2 + 1.5, 0.6, 0)
    
    return [top, leg]


def create_plant():
    """
    创建装饰植物（简化为球体）
    放在角落
    """
    print("\n🌿 创建装饰植物...")
    
    # 花盆
    builder = GNodesBuilder("Plant_Pot")
    builder.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.15,
        "Height": 0.25,
        "Resolution": 12
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    pot = builder.get_object()
    pot.location = (0.3, ROOM_DEPTH - 0.3, 0)
    
    # 植物（用球体代表）
    builder2 = GNodesBuilder("Plant_Foliage")
    builder2.add_node_group("G_Base_Sphere", inputs={
        "Radius": 0.25,
        "Resolution": 12
    })
    builder2.add_node_group("G_Scatter_On_Top", inputs={
        "Density": 3.0,
        "Seed": 42
    })
    builder2.add_node_group("G_Align_Ground")
    builder2.finalize()
    foliage = builder2.get_object()
    foliage.location = (0.3, ROOM_DEPTH - 0.3, 0.35)
    
    return [pot, foliage]


def create_rug():
    """
    创建地毯
    尺寸：2.5m x 1.8m
    """
    print("\n🟫 创建地毯...")
    
    builder = GNodesBuilder("Rug")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (2.5, 1.8, 0.02)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    obj = builder.get_object()
    obj.location = (ROOM_WIDTH / 2, ROOM_DEPTH / 2 - 0.2, 0.05)
    return obj


def setup_camera():
    """设置相机位置"""
    print("\n📷 设置相机...")
    
    # 检查是否存在相机
    if "Camera" not in bpy.data.objects:
        bpy.ops.object.camera_add()
        camera = bpy.context.object
    else:
        camera = bpy.data.objects["Camera"]
    
    # 设置相机位置（从角落俯视）
    camera.location = (7, -2, 4)
    camera.rotation_euler = (1.1, 0, 0.9)
    
    return camera


def setup_lighting():
    """设置灯光"""
    print("\n💡 设置灯光...")
    
    # 删除默认灯光
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # 添加主光源（模拟窗户光）
    bpy.ops.object.light_add(type='AREA', location=(ROOM_WIDTH / 2, -1, 2.5))
    main_light = bpy.context.object
    main_light.name = "Main_Light"
    main_light.data.energy = 500
    main_light.data.size = 3
    main_light.rotation_euler = (0.8, 0, 0)
    
    # 添加补光
    bpy.ops.object.light_add(type='AREA', location=(ROOM_WIDTH / 2, ROOM_DEPTH + 1, 2))
    fill_light = bpy.context.object
    fill_light.name = "Fill_Light"
    fill_light.data.energy = 200
    fill_light.data.size = 2
    fill_light.rotation_euler = (-0.5, 0, 0)
    
    return [main_light, fill_light]


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🏠 开始生成客厅场景")
    print(f"   尺寸: {ROOM_WIDTH}m x {ROOM_DEPTH}m")
    print("=" * 60)
    
    # 清理默认物体
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
    
    # 创建场景元素
    objects = []
    
    # 地板和地毯
    objects.append(create_floor())
    objects.append(create_rug())
    
    # 沙发区域
    objects.extend(create_sofa())
    objects.extend(create_side_table())
    
    # 茶几
    objects.extend(create_coffee_table())
    
    # 电视区域
    objects.append(create_tv_stand())
    objects.append(create_tv())
    
    # 装饰
    objects.extend(create_plant())
    
    # 设置相机和灯光
    setup_camera()
    setup_lighting()
    
    # 统计
    total_objects = len([o for o in objects if o is not None])
    
    print("\n" + "=" * 60)
    print(f"✅ 客厅场景生成完成！")
    print(f"   共创建 {total_objects} 个物体")
    print("=" * 60)
    
    # 保存结果
    if bpy.app.background:
        output_path = os.path.join(project_root, "assets", "living_room.blend")
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        print(f"\n💾 已保存到: {output_path}")


if __name__ == "__main__":
    main()

