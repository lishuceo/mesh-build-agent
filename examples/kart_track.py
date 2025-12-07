"""
卡丁车赛道示例（使用新版 API）
================================

展示 create_oval_track() 模板函数的使用方法。
一行代码生成完整的椭圆形赛道！

使用方法：
blender assets/node_library.blend --python examples/kart_track.py

作者: AI Agent
"""

import bpy
import sys
import os
import math

# 添加项目路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from gnodes_builder import GNodesBuilder, merge_objects, create_oval_track


# ============ 配置参数 ============
TRACK_OUTER_RADIUS_X = 25.0  # 赛道外圈X半径（椭圆长轴）
TRACK_OUTER_RADIUS_Y = 15.0  # 赛道外圈Y半径（椭圆短轴）
TRACK_WIDTH = 6.0            # 赛道宽度
TRACK_THICKNESS = 0.3        # 路面厚度
BARRIER_HEIGHT = 0.8         # 护栏高度

TIRE_RADIUS = 0.35           # 轮胎半径


# ============ 装饰物构建 ============
def build_tire_wall(center_x, center_y, angle, num_tires=6):
    """在弯道外侧构建轮胎墙"""
    objects = []
    
    layers = 3
    tire_spacing = TIRE_RADIUS * 2.1
    
    for i in range(num_tires):
        for j in range(layers):
            builder = GNodesBuilder(f"Tire_{int(center_x)}_{int(center_y)}_{i}_{j}")
            builder.add_node_group("G_Base_Cylinder_Centered", inputs={
                "Radius": TIRE_RADIUS,
                "Height": TIRE_RADIUS * 0.8,
                "Resolution": 12
            })
            builder.finalize()
            
            obj = builder.get_object()
            
            # 沿切线方向排列
            tangent_x = math.cos(angle + math.pi/2)
            tangent_y = math.sin(angle + math.pi/2)
            
            offset_along = (i - (num_tires - 1) / 2) * tire_spacing
            stagger = (j % 2) * (tire_spacing / 2)
            
            pos_x = center_x + (offset_along + stagger) * tangent_x
            pos_y = center_y + (offset_along + stagger) * tangent_y
            pos_z = TRACK_THICKNESS + j * (TIRE_RADIUS * 1.8) + TIRE_RADIUS
            
            obj.location = (pos_x, pos_y, pos_z)
            builder.set_rotation(math.pi/2, 0, angle)
            
            objects.append(obj)
    
    return objects


def build_start_gate():
    """构建起跑拱门"""
    objects = []
    
    # 起跑门位置：赛道右侧中点
    # 在这个位置，赛道沿Y轴延伸，赛道宽度沿X轴
    start_y = 0
    
    # 内侧柱（靠近赛道内边缘）
    inner_x = TRACK_OUTER_RADIUS_X - TRACK_WIDTH - 0.5
    builder = GNodesBuilder("Start_Gate_Inner")
    builder.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.15, "Height": 4.0, "Resolution": 12
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    inner_pillar = builder.get_object()
    inner_pillar.location = (inner_x, start_y, TRACK_THICKNESS)
    objects.append(inner_pillar)
    
    # 外侧柱（靠近赛道外边缘）
    outer_x = TRACK_OUTER_RADIUS_X + 0.5
    builder = GNodesBuilder("Start_Gate_Outer")
    builder.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.15, "Height": 4.0, "Resolution": 12
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    outer_pillar = builder.get_object()
    outer_pillar.location = (outer_x, start_y, TRACK_THICKNESS)
    objects.append(outer_pillar)
    
    # 横梁：跨越赛道宽度（沿X方向）
    beam_center_x = TRACK_OUTER_RADIUS_X - TRACK_WIDTH / 2
    builder = GNodesBuilder("Start_Gate_Beam")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (TRACK_WIDTH + 1.5, 0.3, 0.5)  # X=宽度, Y=厚度, Z=高度
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    beam = builder.get_object()
    beam.location = (beam_center_x, start_y, TRACK_THICKNESS + 4.0)
    objects.append(beam)
    
    return objects


def build_grandstand():
    """构建简易看台"""
    objects = []
    
    stand_x = 0
    stand_y = -TRACK_OUTER_RADIUS_Y - 8
    
    rows = 4
    seats_per_row = 12
    
    for row in range(rows):
        for seat in range(seats_per_row):
            builder = GNodesBuilder(f"Seat_{row}_{seat}")
            builder.add_node_group("G_Base_Cube", inputs={
                "Size": (0.8, 0.8, 0.5 + row * 0.3)
            })
            builder.add_node_group("G_Align_Ground")
            builder.finalize()
            
            obj = builder.get_object()
            obj.location = (
                stand_x + (seat - seats_per_row/2) * 1.0,
                stand_y - row * 1.2,
                0
            )
            objects.append(obj)
    
    return objects


# ============ 主构建函数 ============
def build_kart_track():
    """构建完整的卡丁车赛道"""
    all_objects = []
    
    print("🏎️ 开始构建卡丁车赛道...")
    
    # 1. 核心赛道（一行搞定！）
    print("  📍 构建赛道路面和护栏...")
    track_objects = create_oval_track(
        "KartTrack",
        location=(0, 0, 0),
        outer_radius_x=TRACK_OUTER_RADIUS_X,
        outer_radius_y=TRACK_OUTER_RADIUS_Y,
        track_width=TRACK_WIDTH,
        track_thickness=TRACK_THICKNESS,
        barrier_height=BARRIER_HEIGHT,
        include_barriers=True,
        segments=64
    )
    all_objects.extend(track_objects)
    
    # 2. 轮胎墙（弯道装饰）
    print("  🛞 构建轮胎墙...")
    tire_offset = 0.5
    tire_walls = []
    tire_walls.extend(build_tire_wall(TRACK_OUTER_RADIUS_X + tire_offset + 1, 0, 0, num_tires=8))
    tire_walls.extend(build_tire_wall(-TRACK_OUTER_RADIUS_X - tire_offset - 1, 0, math.pi, num_tires=8))
    all_objects.extend(tire_walls)
    
    # 3. 起跑门
    print("  🏁 构建起跑门...")
    start_gate = build_start_gate()
    all_objects.extend(start_gate)
    
    # 4. 看台
    print("  🏟️ 构建看台...")
    grandstand = build_grandstand()
    all_objects.extend(grandstand)
    
    print(f"✅ 卡丁车赛道构建完成！共 {len(all_objects)} 个部件")
    print(f"   赛道尺寸: {TRACK_OUTER_RADIUS_X * 2}m x {TRACK_OUTER_RADIUS_Y * 2}m")
    print(f"   赛道宽度: {TRACK_WIDTH}m")
    
    return all_objects


# ============ 场景设置 ============
def clear_scene():
    """清理默认物体"""
    for obj in list(bpy.data.objects):
        if obj.type in ('MESH', 'CURVE'):
            bpy.data.objects.remove(obj, do_unlink=True)


def setup_camera():
    """设置相机 - 俯瞰视角"""
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
    else:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
    
    cam.location = (0, -50, 40)
    cam.rotation_euler = (0.9, 0, 0)
    bpy.context.scene.camera = cam


def setup_lighting():
    """设置灯光"""
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    bpy.ops.object.light_add(type='SUN', location=(10, -10, 30))
    sun = bpy.context.object
    sun.data.energy = 3
    sun.rotation_euler = (0.6, 0.2, 0.3)


# ============ 主函数 ============
def main():
    print("\n" + "=" * 60)
    print("🏎️ 卡丁车赛道 - 新版 API 演示")
    print("=" * 60)
    print("\n核心代码只需一行：")
    print("  track = create_oval_track('KartTrack', (0, 0, 0))")
    print()
    
    clear_scene()
    build_kart_track()
    setup_camera()
    setup_lighting()
    
    print("\n" + "=" * 60)
    print("✅ 赛道构建完成！")
    print("=" * 60)
    
    if bpy.app.background:
        out = os.path.join(project_root, "assets", "kart_track_demo.blend")
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print(f"\n💾 保存到: {out}")


if __name__ == "__main__":
    main()
