"""
三轮车生成脚本
生成一个载货三轮车模型

使用方法：
blender assets/node_library.blend --python examples/tricycle.py

三轮车结构（侧视图）：
                 ┌──┐
                 │把│
                 └┬┘
          座椅    │
         ┌───┐   │
         │   │   │      ┌─────────┐
         └───┘   │      │ 后车厢  │
           ╲    ╱       │         │
            车架        └────┬────┘
           ╱    ╲           │
         ○       ○         ○ ○
        前轮              后轮(2个)

俯视图：
              ┌───┐
              │把 │
              └─┬─┘
           ┌───┴───┐
           │  座椅  │
           └───┬───┘
        ○     │
       前轮   车架
              │
         ┌────┴────┐
         │ 后车厢  │
         │         │
         └────┬────┘
           ○   ○
          后轮(2个)
"""

import bpy
import sys
import os
import math

# 设置路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from gnodes_builder import GNodesBuilder


# ============ 三轮车尺寸参数 ============
WHEEL_RADIUS = 0.3          # 车轮半径
WHEEL_WIDTH = 0.08          # 车轮宽度
FRAME_HEIGHT = 0.5          # 车架高度
TOTAL_LENGTH = 2.0          # 总长度
REAR_WIDTH = 0.9            # 后轮间距


def create_wheel(name: str, location: tuple, rotation_y: float = 0):
    """
    创建车轮
    
    Args:
        name: 物体名称
        location: 位置 (x, y, z) - 车轮中心位置
        rotation_y: Y轴旋转角度（弧度）
    """
    # 轮胎 - 使用 bpy 直接创建，避免原点偏移
    bpy.ops.mesh.primitive_cylinder_add(
        radius=WHEEL_RADIUS,
        depth=WHEEL_WIDTH,
        vertices=24,
        location=location,
        rotation=(math.pi / 2, rotation_y, 0)
    )
    tire = bpy.context.object
    tire.name = f"{name}_Tire"
    
    # 轮毂
    bpy.ops.mesh.primitive_cylinder_add(
        radius=WHEEL_RADIUS * 0.4,
        depth=WHEEL_WIDTH + 0.02,
        vertices=16,
        location=location,
        rotation=(math.pi / 2, rotation_y, 0)
    )
    hub = bpy.context.object
    hub.name = f"{name}_Hub"
    
    return [tire, hub]


def create_front_wheel():
    """创建前轮"""
    print("\n🔵 创建前轮...")
    return create_wheel("FrontWheel", (0, 0, WHEEL_RADIUS))


def create_rear_wheels():
    """创建后轮（两个）"""
    print("\n🔵 创建后轮...")
    
    left_wheel = create_wheel(
        "RearWheel_Left", 
        (TOTAL_LENGTH - 0.3, -REAR_WIDTH / 2, WHEEL_RADIUS)
    )
    right_wheel = create_wheel(
        "RearWheel_Right", 
        (TOTAL_LENGTH - 0.3, REAR_WIDTH / 2, WHEEL_RADIUS)
    )
    
    return left_wheel + right_wheel


def create_frame():
    """创建车架"""
    print("\n🔧 创建车架...")
    
    objects = []
    
    # 主梁（从前轮到后轮）
    builder = GNodesBuilder("Frame_Main")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (TOTAL_LENGTH - 0.5, 0.08, 0.08)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    main_beam = builder.get_object()
    main_beam.location = (TOTAL_LENGTH / 2 - 0.1, 0, FRAME_HEIGHT)
    objects.append(main_beam)
    
    # 前叉（连接前轮）
    builder2 = GNodesBuilder("Frame_FrontFork")
    builder2.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.025,
        "Height": FRAME_HEIGHT - WHEEL_RADIUS + 0.1,
        "Resolution": 8
    })
    builder2.add_node_group("G_Align_Ground")
    builder2.finalize()
    front_fork = builder2.get_object()
    front_fork.location = (0.1, 0, WHEEL_RADIUS)
    objects.append(front_fork)
    
    # 后架横梁
    builder3 = GNodesBuilder("Frame_RearCross")
    builder3.add_node_group("G_Base_Cube", inputs={
        "Size": (0.08, REAR_WIDTH + 0.1, 0.08)
    })
    builder3.add_node_group("G_Align_Ground")
    builder3.finalize()
    rear_cross = builder3.get_object()
    rear_cross.location = (TOTAL_LENGTH - 0.3, 0, FRAME_HEIGHT)
    objects.append(rear_cross)
    
    # 后架支撑（左）
    builder4 = GNodesBuilder("Frame_RearSupport_Left")
    builder4.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.02,
        "Height": FRAME_HEIGHT - WHEEL_RADIUS + 0.05,
        "Resolution": 8
    })
    builder4.add_node_group("G_Align_Ground")
    builder4.finalize()
    left_support = builder4.get_object()
    left_support.location = (TOTAL_LENGTH - 0.3, -REAR_WIDTH / 2, WHEEL_RADIUS)
    objects.append(left_support)
    
    # 后架支撑（右）
    builder5 = GNodesBuilder("Frame_RearSupport_Right")
    builder5.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.02,
        "Height": FRAME_HEIGHT - WHEEL_RADIUS + 0.05,
        "Resolution": 8
    })
    builder5.add_node_group("G_Align_Ground")
    builder5.finalize()
    right_support = builder5.get_object()
    right_support.location = (TOTAL_LENGTH - 0.3, REAR_WIDTH / 2, WHEEL_RADIUS)
    objects.append(right_support)
    
    return objects


def create_horizontal_cylinder(name: str, radius: float, length: float, 
                                location: tuple, resolution: int = 8):
    """
    创建水平放置的圆柱（沿 Y 轴方向）
    圆柱中心在指定位置
    
    问题：G_Base_Cylinder 的原点在底部中心，旋转后位置会偏移
    解决：计算补偿值，让圆柱中心在指定位置
    """
    builder = GNodesBuilder(name)
    builder.add_node_group("G_Base_Cylinder", inputs={
        "Radius": radius,
        "Height": length,
        "Resolution": resolution
    })
    builder.finalize()
    
    obj = builder.get_object()
    
    # G_Base_Cylinder 的原点在底部中心
    # 绕 X 轴旋转 90 度后，原来的 Z 轴（高度方向）变成 -Y 方向
    # 几何中心相对于原点偏移了 (0, -length/2, 0)
    # 为了让几何中心在 location，需要补偿这个偏移
    
    x, y, z = location
    # 旋转后补偿：原点需要在 (x, y + length/2, z)
    obj.location = (x, y, z)
    obj.rotation_euler = (math.pi / 2, 0, 0)
    
    # 应用补偿：让圆柱中心在指定位置
    # 旋转后，原来的"底部"变成了 Y+ 方向的端点
    # 所以需要向 Y- 方向移动 length/2
    obj.location = (x, y, z)
    
    return obj


def create_cylinder_along_y(name: str, radius: float, length: float,
                            center_location: tuple, resolution: int = 8):
    """
    创建沿 Y 轴方向的圆柱，中心在指定位置
    
    这是更精确的版本，直接使用 Blender 原生圆柱避免偏移问题
    """
    # 直接使用 bpy 创建圆柱，不经过节点组
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=length,
        vertices=resolution,
        location=center_location,
        rotation=(math.pi / 2, 0, 0)  # 沿 Y 轴
    )
    obj = bpy.context.object
    obj.name = name
    return obj


def create_handlebar():
    """创建车把"""
    print("\n🎯 创建车把...")
    
    objects = []
    
    # 车把立管（竖直的，可以用 G_Align_Ground）
    builder = GNodesBuilder("Handlebar_Stem")
    builder.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.02,
        "Height": 0.5,
        "Resolution": 8
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    stem = builder.get_object()
    stem.location = (0.1, 0, FRAME_HEIGHT + 0.05)
    objects.append(stem)
    
    # 车把横杆（水平的，使用 bpy 直接创建避免偏移）
    bar = create_cylinder_along_y(
        "Handlebar_Bar",
        radius=0.015,
        length=0.6,
        center_location=(0.1, 0, FRAME_HEIGHT + 0.55),
        resolution=8
    )
    objects.append(bar)
    
    # 左把手
    grip_left = create_cylinder_along_y(
        "Handlebar_Grip_Left",
        radius=0.02,
        length=0.12,
        center_location=(0.1, -0.35, FRAME_HEIGHT + 0.55),
        resolution=8
    )
    objects.append(grip_left)
    
    # 右把手
    grip_right = create_cylinder_along_y(
        "Handlebar_Grip_Right",
        radius=0.02,
        length=0.12,
        center_location=(0.1, 0.35, FRAME_HEIGHT + 0.55),
        resolution=8
    )
    objects.append(grip_right)
    
    return objects


def create_seat():
    """创建座椅"""
    print("\n💺 创建座椅...")
    
    objects = []
    
    # 座垫
    builder = GNodesBuilder("Seat_Cushion")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (0.3, 0.25, 0.08)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    cushion = builder.get_object()
    cushion.location = (0.4, 0, FRAME_HEIGHT + 0.1)
    objects.append(cushion)
    
    # 座杆
    builder2 = GNodesBuilder("Seat_Post")
    builder2.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.02,
        "Height": 0.15,
        "Resolution": 8
    })
    builder2.add_node_group("G_Align_Ground")
    builder2.finalize()
    post = builder2.get_object()
    post.location = (0.4, 0, FRAME_HEIGHT - 0.05)
    objects.append(post)
    
    return objects


def create_cargo_box():
    """创建后车厢"""
    print("\n📦 创建后车厢...")
    
    objects = []
    
    BOX_LENGTH = 0.8
    BOX_WIDTH = REAR_WIDTH - 0.1
    BOX_HEIGHT = 0.35
    BOX_X = TOTAL_LENGTH - 0.3
    
    # 底板
    builder = GNodesBuilder("Cargo_Bottom")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (BOX_LENGTH, BOX_WIDTH, 0.03)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    bottom = builder.get_object()
    bottom.location = (BOX_X, 0, FRAME_HEIGHT + 0.05)
    objects.append(bottom)
    
    # 前板
    builder2 = GNodesBuilder("Cargo_Front")
    builder2.add_node_group("G_Base_Cube", inputs={
        "Size": (0.03, BOX_WIDTH, BOX_HEIGHT)
    })
    builder2.add_node_group("G_Align_Ground")
    builder2.finalize()
    front = builder2.get_object()
    front.location = (BOX_X - BOX_LENGTH / 2 + 0.015, 0, FRAME_HEIGHT + 0.08)
    objects.append(front)
    
    # 后板
    builder3 = GNodesBuilder("Cargo_Back")
    builder3.add_node_group("G_Base_Cube", inputs={
        "Size": (0.03, BOX_WIDTH, BOX_HEIGHT)
    })
    builder3.add_node_group("G_Align_Ground")
    builder3.finalize()
    back = builder3.get_object()
    back.location = (BOX_X + BOX_LENGTH / 2 - 0.015, 0, FRAME_HEIGHT + 0.08)
    objects.append(back)
    
    # 左侧板
    builder4 = GNodesBuilder("Cargo_Left")
    builder4.add_node_group("G_Base_Cube", inputs={
        "Size": (BOX_LENGTH, 0.03, BOX_HEIGHT)
    })
    builder4.add_node_group("G_Align_Ground")
    builder4.finalize()
    left = builder4.get_object()
    left.location = (BOX_X, -BOX_WIDTH / 2 + 0.015, FRAME_HEIGHT + 0.08)
    objects.append(left)
    
    # 右侧板
    builder5 = GNodesBuilder("Cargo_Right")
    builder5.add_node_group("G_Base_Cube", inputs={
        "Size": (BOX_LENGTH, 0.03, BOX_HEIGHT)
    })
    builder5.add_node_group("G_Align_Ground")
    builder5.finalize()
    right = builder5.get_object()
    right.location = (BOX_X, BOX_WIDTH / 2 - 0.015, FRAME_HEIGHT + 0.08)
    objects.append(right)
    
    return objects


def create_pedals():
    """创建脚踏板"""
    print("\n🦶 创建脚踏板...")
    
    objects = []
    
    # 曲柄（水平圆柱，使用 bpy 直接创建）
    crank = create_cylinder_along_y(
        "Pedal_Crank",
        radius=0.015,
        length=0.35,
        center_location=(0.25, 0, FRAME_HEIGHT - 0.1),
        resolution=8
    )
    objects.append(crank)
    
    # 左踏板
    builder2 = GNodesBuilder("Pedal_Left")
    builder2.add_node_group("G_Base_Cube", inputs={
        "Size": (0.1, 0.06, 0.02)
    })
    builder2.add_node_group("G_Align_Ground")
    builder2.finalize()
    pedal_left = builder2.get_object()
    pedal_left.location = (0.25, -0.2, FRAME_HEIGHT - 0.1)
    objects.append(pedal_left)
    
    # 右踏板
    builder3 = GNodesBuilder("Pedal_Right")
    builder3.add_node_group("G_Base_Cube", inputs={
        "Size": (0.1, 0.06, 0.02)
    })
    builder3.add_node_group("G_Align_Ground")
    builder3.finalize()
    pedal_right = builder3.get_object()
    pedal_right.location = (0.25, 0.2, FRAME_HEIGHT - 0.1)
    objects.append(pedal_right)
    
    return objects


def setup_camera():
    """设置相机"""
    print("\n📷 设置相机...")
    
    if "Camera" not in bpy.data.objects:
        bpy.ops.object.camera_add()
        camera = bpy.context.object
    else:
        camera = bpy.data.objects["Camera"]
    
    camera.location = (0.5, -3.5, 1.5)
    camera.rotation_euler = (1.2, 0, 0.1)
    
    return camera


def setup_lighting():
    """设置灯光"""
    print("\n💡 设置灯光...")
    
    # 清除现有灯光
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # 主光源
    bpy.ops.object.light_add(type='SUN', location=(2, -2, 5))
    sun = bpy.context.object
    sun.name = "Sun"
    sun.data.energy = 3
    sun.rotation_euler = (0.8, 0.2, 0.5)
    
    return sun


def create_ground():
    """创建地面"""
    print("\n🟫 创建地面...")
    
    builder = GNodesBuilder("Ground")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (5, 5, 0.05)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    ground = builder.get_object()
    ground.location = (1, 0, 0)
    return ground


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚲 开始生成三轮车模型")
    print("=" * 60)
    
    # 清理默认物体
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
    
    # 创建各部件
    objects = []
    
    # 地面
    objects.append(create_ground())
    
    # 车轮
    objects.extend(create_front_wheel())
    objects.extend(create_rear_wheels())
    
    # 车架
    objects.extend(create_frame())
    
    # 车把
    objects.extend(create_handlebar())
    
    # 座椅
    objects.extend(create_seat())
    
    # 脚踏板
    objects.extend(create_pedals())
    
    # 后车厢
    objects.extend(create_cargo_box())
    
    # 设置相机和灯光
    setup_camera()
    setup_lighting()
    
    # 统计
    total_objects = len([o for o in objects if o is not None])
    
    print("\n" + "=" * 60)
    print(f"✅ 三轮车模型生成完成！")
    print(f"   共创建 {total_objects} 个部件")
    print("=" * 60)
    
    # 保存结果
    if bpy.app.background:
        output_path = os.path.join(project_root, "assets", "tricycle.blend")
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        print(f"\n💾 已保存到: {output_path}")


if __name__ == "__main__":
    main()

