"""
金门大桥 1:1 比例生成脚本
Golden Gate Bridge - 1:1 Scale Model

使用方法：
blender assets/node_library.blend --python examples/golden_gate_bridge.py

金门大桥关键尺寸（真实数据）：
- 总长度：2,737 米
- 主跨长度：1,280 米
- 桥塔高度：227 米（水面以上）
- 桥面宽度：27.4 米
- 桥面距水面高度：67 米
- 主缆直径：0.927 米
- 边跨长度：各约 343 米

结构示意图（侧视图）：
           ┌─┐                           ┌─┐
           │ │ 塔高 227m                 │ │
           │ │ ╲                        ╱│ │
      主缆 │ │  ╲──────────────────────╱ │ │ 主缆
          ╱│ │   ╲      主跨 1280m   ╱   │ │╲
         ╱ │ │    ╲                 ╱    │ │ ╲
        ╱  └┬┘     ╲               ╱     └┬┘  ╲
       ╱    │       ╲             ╱       │    ╲
 锚碇●─────┼────────┼─桥面 67m──┼────────┼─────●锚碇
           │       |||           |||      │
          塔       吊索          吊索     塔
      ◄───343m───►◄─────1280m────►◄───343m───►
                    总长 2737m
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


# ============ 金门大桥尺寸参数（1:1 真实比例，单位：米）============

# 总体尺寸
TOTAL_LENGTH = 2737.0          # 总长度
MAIN_SPAN = 1280.0             # 主跨长度（两塔之间）
SIDE_SPAN = 343.0              # 边跨长度（塔到锚碇）
APPROACH_LENGTH = (TOTAL_LENGTH - MAIN_SPAN - 2 * SIDE_SPAN) / 2  # 引桥长度

# 桥塔尺寸
TOWER_HEIGHT = 227.0           # 塔高（水面以上）
TOWER_BASE_WIDTH = 10.0        # 塔基宽度
TOWER_TOP_WIDTH = 6.0          # 塔顶宽度
TOWER_DEPTH = 10.0             # 塔深度（沿桥方向）
TOWER_CROSS_BEAM_HEIGHT = 30.0 # 横梁高度

# 桥面尺寸
DECK_WIDTH = 27.4              # 桥面宽度
DECK_HEIGHT = 67.0             # 桥面距水面高度
DECK_THICKNESS = 7.6           # 桥面厚度（钢桁架结构）
DECK_TRUSS_HEIGHT = 7.6        # 桁架高度

# 缆索尺寸
MAIN_CABLE_DIAMETER = 0.927    # 主缆直径
MAIN_CABLE_SAG = 143.0         # 主缆最低点下垂（抛物线）
SUSPENDER_DIAMETER = 0.08      # 吊索直径
SUSPENDER_SPACING = 15.24      # 吊索间距（约50英尺）

# 锚碇尺寸
ANCHORAGE_WIDTH = 40.0         # 锚碇宽度
ANCHORAGE_HEIGHT = 70.0        # 锚碇高度
ANCHORAGE_DEPTH = 60.0         # 锚碇深度

# 塔的位置（以桥中心为原点）
TOWER_SOUTH_X = -MAIN_SPAN / 2  # 南塔 X 位置
TOWER_NORTH_X = MAIN_SPAN / 2   # 北塔 X 位置


def create_tower_leg(name: str, location: tuple, height: float,
                     base_width: float, top_width: float, depth: float):
    """
    创建单个塔腿（带锥形收缩）
    
    金门大桥的塔腿是梯形截面，底部宽，顶部窄
    使用多段立方体模拟锥形效果
    """
    objects = []
    segments = 8  # 分段数
    segment_height = height / segments
    
    for i in range(segments):
        # 计算当前段的宽度（线性插值）
        t = i / segments
        current_width = base_width * (1 - t) + top_width * t
        next_width = base_width * (1 - (t + 1/segments)) + top_width * (t + 1/segments)
        avg_width = (current_width + next_width) / 2
        
        segment_name = f"{name}_Segment_{i}"
        builder = GNodesBuilder(segment_name)
        builder.add_node_group("G_Base_Cube", inputs={
            "Size": (depth, avg_width, segment_height)
        })
        builder.add_node_group("G_Align_Ground")
        builder.finalize()
        
        segment = builder.get_object()
        x, y, z = location
        segment.location = (x, y, z + i * segment_height)
        objects.append(segment)
    
    return objects


def create_tower(name: str, x_position: float):
    """
    创建完整的桥塔
    
    金门大桥的塔有两根塔腿，由多层横梁连接
    
    俯视图：
    ┌───┐   ┌───┐
    │ 腿 │   │ 腿 │
    └─┬─┘   └─┬─┘
      │       │
      └───────┘ 横梁
    """
    print(f"\n🏗️ 创建桥塔: {name}...")
    objects = []
    
    # 两根塔腿的 Y 位置
    leg_spacing = DECK_WIDTH / 2 + TOWER_BASE_WIDTH / 2
    
    # 左塔腿
    left_leg = create_tower_leg(
        f"{name}_Leg_Left",
        (x_position, -leg_spacing / 2 - TOWER_BASE_WIDTH / 4, DECK_HEIGHT),
        TOWER_HEIGHT - DECK_HEIGHT,
        TOWER_BASE_WIDTH,
        TOWER_TOP_WIDTH,
        TOWER_DEPTH
    )
    objects.extend(left_leg)
    
    # 右塔腿
    right_leg = create_tower_leg(
        f"{name}_Leg_Right",
        (x_position, leg_spacing / 2 + TOWER_BASE_WIDTH / 4, DECK_HEIGHT),
        TOWER_HEIGHT - DECK_HEIGHT,
        TOWER_BASE_WIDTH,
        TOWER_TOP_WIDTH,
        TOWER_DEPTH
    )
    objects.extend(right_leg)
    
    # 横梁（连接两根塔腿）
    beam_heights = [DECK_HEIGHT + 20, DECK_HEIGHT + 80, DECK_HEIGHT + 140, TOWER_HEIGHT - 10]
    for i, beam_z in enumerate(beam_heights):
        beam_name = f"{name}_CrossBeam_{i}"
        builder = GNodesBuilder(beam_name)
        builder.add_node_group("G_Base_Cube", inputs={
            "Size": (TOWER_DEPTH * 0.8, leg_spacing + TOWER_BASE_WIDTH, 8.0)
        })
        builder.add_node_group("G_Align_Ground")
        builder.finalize()
        beam = builder.get_object()
        beam.location = (x_position, 0, beam_z)
        objects.append(beam)
    
    # 塔顶装饰（鞍座，用于支撑主缆）
    for y_offset in [-leg_spacing / 2 - TOWER_BASE_WIDTH / 4, leg_spacing / 2 + TOWER_BASE_WIDTH / 4]:
        saddle_name = f"{name}_Saddle_{'Left' if y_offset < 0 else 'Right'}"
        builder = GNodesBuilder(saddle_name)
        builder.add_node_group("G_Base_Cylinder", inputs={
            "Radius": MAIN_CABLE_DIAMETER * 2,
            "Height": 5.0,
            "Resolution": 16
        })
        builder.add_node_group("G_Align_Ground")
        builder.finalize()
        saddle = builder.get_object()
        saddle.location = (x_position, y_offset, TOWER_HEIGHT)
        objects.append(saddle)
    
    return objects


def create_deck_section(name: str, x_start: float, length: float):
    """
    创建桥面段
    
    桥面结构包括：
    - 主桁架（钢结构）
    - 行车道
    - 人行道
    """
    objects = []
    
    # 主桥面板
    builder = GNodesBuilder(f"{name}_Deck")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (length, DECK_WIDTH, DECK_THICKNESS)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    deck = builder.get_object()
    deck.location = (x_start + length / 2, 0, DECK_HEIGHT - DECK_THICKNESS)
    objects.append(deck)
    
    # 桥面护栏（两侧）
    for y_sign in [-1, 1]:
        rail_name = f"{name}_Rail_{'Left' if y_sign < 0 else 'Right'}"
        builder = GNodesBuilder(rail_name)
        builder.add_node_group("G_Base_Cube", inputs={
            "Size": (length, 0.5, 1.5)
        })
        builder.add_node_group("G_Align_Ground")
        builder.finalize()
        rail = builder.get_object()
        rail.location = (x_start + length / 2, y_sign * (DECK_WIDTH / 2 - 0.25), DECK_HEIGHT)
        objects.append(rail)
    
    return objects


def create_bridge_deck():
    """
    创建完整的桥面
    
    桥面分为几个部分：
    - 南引桥
    - 南边跨（南塔到南锚碇）
    - 主跨（两塔之间）
    - 北边跨（北塔到北锚碇）
    - 北引桥
    """
    print("\n🛤️ 创建桥面...")
    objects = []
    
    # 计算各段起点
    total_start = -TOTAL_LENGTH / 2
    
    # 简化：将桥面分成 20 段，便于管理
    num_segments = 20
    segment_length = TOTAL_LENGTH / num_segments
    
    for i in range(num_segments):
        x_start = total_start + i * segment_length
        segment = create_deck_section(f"Deck_Segment_{i}", x_start, segment_length)
        objects.extend(segment)
    
    return objects


def calculate_cable_height(x: float, tower_x: float, is_main_span: bool):
    """
    计算主缆在给定 X 位置的高度
    
    主缆呈抛物线形状：
    - 在塔顶最高
    - 在跨中最低（下垂 MAIN_CABLE_SAG）
    
    使用抛物线公式：y = a * x^2 + b
    """
    if is_main_span:
        # 主跨：两塔之间
        span = MAIN_SPAN
        center_x = 0  # 主跨中心
    else:
        # 边跨：塔到锚碇
        span = SIDE_SPAN
        if tower_x < 0:  # 南塔
            center_x = tower_x - SIDE_SPAN / 2
        else:  # 北塔
            center_x = tower_x + SIDE_SPAN / 2
    
    # 抛物线参数
    # 在塔顶（x=tower_x）高度为 TOWER_HEIGHT
    # 在跨中（x=center_x）高度为 TOWER_HEIGHT - sag
    sag = MAIN_CABLE_SAG if is_main_span else MAIN_CABLE_SAG * 0.4
    
    # 计算相对位置
    if is_main_span:
        rel_x = x / (MAIN_SPAN / 2)  # 归一化到 [-1, 1]
    else:
        if tower_x < 0:
            rel_x = (x - (tower_x - SIDE_SPAN / 2)) / (SIDE_SPAN / 2)
        else:
            rel_x = (x - (tower_x + SIDE_SPAN / 2)) / (SIDE_SPAN / 2)
    
    # 抛物线：最低点在中心
    height = TOWER_HEIGHT - sag * (1 - rel_x ** 2)
    
    return height


def create_main_cable_segment(name: str, x_start: float, x_end: float, 
                               y_offset: float, is_main_span: bool):
    """
    创建主缆的一段（使用多段圆柱模拟曲线）
    """
    objects = []
    
    # 计算这段缆索的起点和终点高度
    tower_x = TOWER_SOUTH_X if x_start < 0 else TOWER_NORTH_X
    
    z_start = calculate_cable_height(x_start, tower_x, is_main_span)
    z_end = calculate_cable_height(x_end, tower_x, is_main_span)
    
    # 计算长度和角度
    dx = x_end - x_start
    dz = z_end - z_start
    length = math.sqrt(dx ** 2 + dz ** 2)
    angle = math.atan2(dz, dx)
    
    # 创建圆柱
    bpy.ops.mesh.primitive_cylinder_add(
        radius=MAIN_CABLE_DIAMETER / 2,
        depth=length,
        vertices=12,
        location=((x_start + x_end) / 2, y_offset, (z_start + z_end) / 2),
        rotation=(0, -angle + math.pi / 2, 0)
    )
    cable = bpy.context.object
    cable.name = name
    objects.append(cable)
    
    return objects


def create_main_cables():
    """
    创建主缆（两条，桥的两侧各一条）
    
    主缆从南锚碇 → 南塔 → 北塔 → 北锚碇
    """
    print("\n🔗 创建主缆...")
    objects = []
    
    # 缆索 Y 位置（桥面两侧外）
    cable_y_offsets = [-DECK_WIDTH / 2 - 2, DECK_WIDTH / 2 + 2]
    
    for cable_idx, y_offset in enumerate(cable_y_offsets):
        cable_side = "Left" if y_offset < 0 else "Right"
        
        # 主跨（南塔到北塔）
        num_segments = 40
        for i in range(num_segments):
            x_start = TOWER_SOUTH_X + i * (MAIN_SPAN / num_segments)
            x_end = TOWER_SOUTH_X + (i + 1) * (MAIN_SPAN / num_segments)
            
            segment = create_main_cable_segment(
                f"MainCable_{cable_side}_Main_{i}",
                x_start, x_end, y_offset, is_main_span=True
            )
            objects.extend(segment)
        
        # 南边跨（南锚碇到南塔）
        for i in range(10):
            x_start = TOWER_SOUTH_X - SIDE_SPAN + i * (SIDE_SPAN / 10)
            x_end = TOWER_SOUTH_X - SIDE_SPAN + (i + 1) * (SIDE_SPAN / 10)
            
            segment = create_main_cable_segment(
                f"MainCable_{cable_side}_SouthSide_{i}",
                x_start, x_end, y_offset, is_main_span=False
            )
            objects.extend(segment)
        
        # 北边跨（北塔到北锚碇）
        for i in range(10):
            x_start = TOWER_NORTH_X + i * (SIDE_SPAN / 10)
            x_end = TOWER_NORTH_X + (i + 1) * (SIDE_SPAN / 10)
            
            segment = create_main_cable_segment(
                f"MainCable_{cable_side}_NorthSide_{i}",
                x_start, x_end, y_offset, is_main_span=False
            )
            objects.extend(segment)
    
    return objects


def create_suspender(name: str, x: float, y: float, cable_height: float):
    """
    创建单根吊索（连接主缆和桥面）
    """
    length = cable_height - DECK_HEIGHT
    if length <= 0:
        return []
    
    builder = GNodesBuilder(name)
    builder.add_node_group("G_Base_Cylinder", inputs={
        "Radius": SUSPENDER_DIAMETER / 2,
        "Height": length,
        "Resolution": 8
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    suspender = builder.get_object()
    suspender.location = (x, y, DECK_HEIGHT)
    
    return [suspender]


def create_suspenders():
    """
    创建所有吊索
    
    吊索垂直连接主缆和桥面，间距约 15.24 米
    """
    print("\n⛓️ 创建吊索...")
    objects = []
    
    cable_y_offsets = [-DECK_WIDTH / 2 - 2, DECK_WIDTH / 2 + 2]
    
    # 主跨吊索
    num_suspenders_main = int(MAIN_SPAN / SUSPENDER_SPACING)
    for i in range(num_suspenders_main):
        x = TOWER_SOUTH_X + (i + 0.5) * SUSPENDER_SPACING
        if abs(x - TOWER_SOUTH_X) < TOWER_DEPTH or abs(x - TOWER_NORTH_X) < TOWER_DEPTH:
            continue  # 跳过塔附近的吊索
        
        cable_height = calculate_cable_height(x, TOWER_SOUTH_X if x < 0 else TOWER_NORTH_X, True)
        
        for y_offset in cable_y_offsets:
            side = "Left" if y_offset < 0 else "Right"
            suspender = create_suspender(
                f"Suspender_Main_{i}_{side}",
                x, y_offset, cable_height
            )
            objects.extend(suspender)
    
    # 边跨吊索（南侧）
    num_suspenders_side = int(SIDE_SPAN / SUSPENDER_SPACING)
    for i in range(num_suspenders_side):
        x = TOWER_SOUTH_X - SIDE_SPAN + (i + 0.5) * SUSPENDER_SPACING
        cable_height = calculate_cable_height(x, TOWER_SOUTH_X, False)
        
        for y_offset in cable_y_offsets:
            side = "Left" if y_offset < 0 else "Right"
            suspender = create_suspender(
                f"Suspender_South_{i}_{side}",
                x, y_offset, cable_height
            )
            objects.extend(suspender)
    
    # 边跨吊索（北侧）
    for i in range(num_suspenders_side):
        x = TOWER_NORTH_X + (i + 0.5) * SUSPENDER_SPACING
        cable_height = calculate_cable_height(x, TOWER_NORTH_X, False)
        
        for y_offset in cable_y_offsets:
            side = "Left" if y_offset < 0 else "Right"
            suspender = create_suspender(
                f"Suspender_North_{i}_{side}",
                x, y_offset, cable_height
            )
            objects.extend(suspender)
    
    return objects


def create_anchorage(name: str, x_position: float):
    """
    创建锚碇（固定主缆的巨大混凝土结构）
    """
    print(f"\n⚓ 创建锚碇: {name}...")
    objects = []
    
    # 主体
    builder = GNodesBuilder(f"{name}_Main")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (ANCHORAGE_DEPTH, ANCHORAGE_WIDTH, ANCHORAGE_HEIGHT)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    main = builder.get_object()
    main.location = (x_position, 0, 0)
    objects.append(main)
    
    return objects


def create_water_surface():
    """
    创建水面
    """
    print("\n🌊 创建水面...")
    
    builder = GNodesBuilder("Water_Surface")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (TOTAL_LENGTH * 1.5, TOTAL_LENGTH, 0.5)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    water = builder.get_object()
    water.location = (0, 0, -0.5)
    
    return [water]


def setup_camera():
    """设置相机（适合观看整座桥）"""
    print("\n📷 设置相机...")
    
    if "Camera" not in bpy.data.objects:
        bpy.ops.object.camera_add()
        camera = bpy.context.object
    else:
        camera = bpy.data.objects["Camera"]
    
    # 从侧面斜上方观看整座桥
    camera.location = (-500, -1500, 500)
    camera.rotation_euler = (math.radians(60), 0, math.radians(-20))
    camera.data.clip_end = 10000  # 增加远裁剪距离
    
    return camera


def setup_lighting():
    """设置灯光"""
    print("\n☀️ 设置灯光...")
    
    # 清除现有灯光
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # 太阳光
    bpy.ops.object.light_add(type='SUN', location=(500, -500, 1000))
    sun = bpy.context.object
    sun.name = "Sun"
    sun.data.energy = 5
    sun.rotation_euler = (math.radians(45), math.radians(15), math.radians(30))
    
    return sun


def print_bridge_info():
    """打印金门大桥信息"""
    print("\n" + "=" * 70)
    print("🌉 金门大桥 (Golden Gate Bridge) - 1:1 比例模型")
    print("=" * 70)
    print(f"""
    📐 尺寸参数：
    ├── 总长度:       {TOTAL_LENGTH:,.0f} 米
    ├── 主跨长度:     {MAIN_SPAN:,.0f} 米
    ├── 边跨长度:     {SIDE_SPAN:,.0f} 米 × 2
    ├── 桥塔高度:     {TOWER_HEIGHT:,.0f} 米
    ├── 桥面宽度:     {DECK_WIDTH:,.1f} 米
    ├── 桥面高度:     {DECK_HEIGHT:,.0f} 米（距水面）
    ├── 主缆直径:     {MAIN_CABLE_DIAMETER:.3f} 米
    └── 吊索间距:     {SUSPENDER_SPACING:.2f} 米
    
    🏗️ 结构组成：
    ├── 2 座主塔
    ├── 2 条主缆
    ├── ~{int((MAIN_SPAN + 2 * SIDE_SPAN) / SUSPENDER_SPACING * 4)} 根吊索
    └── 2 个锚碇
    """)


def main():
    """主函数"""
    print_bridge_info()
    
    # 清理默认物体
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
    
    # 创建各组件
    all_objects = []
    
    # 1. 水面
    all_objects.extend(create_water_surface())
    
    # 2. 锚碇
    south_anchorage_x = TOWER_SOUTH_X - SIDE_SPAN - ANCHORAGE_DEPTH / 2
    north_anchorage_x = TOWER_NORTH_X + SIDE_SPAN + ANCHORAGE_DEPTH / 2
    all_objects.extend(create_anchorage("Anchorage_South", south_anchorage_x))
    all_objects.extend(create_anchorage("Anchorage_North", north_anchorage_x))
    
    # 3. 桥塔
    all_objects.extend(create_tower("Tower_South", TOWER_SOUTH_X))
    all_objects.extend(create_tower("Tower_North", TOWER_NORTH_X))
    
    # 4. 桥面
    all_objects.extend(create_bridge_deck())
    
    # 5. 主缆
    all_objects.extend(create_main_cables())
    
    # 6. 吊索
    all_objects.extend(create_suspenders())
    
    # 设置场景
    setup_camera()
    setup_lighting()
    
    # 设置视图裁剪距离
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.clip_end = 10000
    
    # 统计
    total_objects = len([o for o in all_objects if o is not None])
    
    print("\n" + "=" * 70)
    print(f"✅ 金门大桥模型生成完成！")
    print(f"   共创建 {total_objects} 个部件")
    print(f"   模型尺寸: {TOTAL_LENGTH:,.0f} 米 × {DECK_WIDTH:,.1f} 米 × {TOWER_HEIGHT:,.0f} 米")
    print("=" * 70)
    
    # 保存结果
    if bpy.app.background:
        output_path = os.path.join(project_root, "assets", "golden_gate_bridge.blend")
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        print(f"\n💾 已保存到: {output_path}")


if __name__ == "__main__":
    main()

