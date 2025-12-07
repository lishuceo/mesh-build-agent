"""
8字形复杂赛道示例
==================

一个带立交桥的8字形（∞形）赛道，展示如何创建复杂路径的赛道。

特点：
- 8字形路径（两个圆相交）
- 中间有立交桥（一段抬高）
- 平滑的高度过渡
- 完整的护栏

使用方法：
blender assets/node_library.blend --python examples/figure8_track.py

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

from gnodes_builder import GNodesBuilder


# ============ 配置参数 ============
TRACK_WIDTH = 6.0           # 赛道宽度
TRACK_THICKNESS = 0.3       # 路面厚度
BARRIER_HEIGHT = 0.6        # 护栏高度
BARRIER_WIDTH = 0.12        # 护栏宽度

LOOP_RADIUS = 20.0          # 每个圆环的半径
LOOP_SEPARATION = 15.0      # 两个圆心之间的距离
BRIDGE_HEIGHT = 4.0         # 立交桥高度
SEGMENTS_PER_LOOP = 48      # 每个圆环的分段数


# ============ 核心：沿路径创建赛道 ============
def create_track_along_path(name, path_points, width, thickness, segments_per_section=4):
    """
    沿任意路径创建赛道网格
    
    Args:
        name: 网格名称
        path_points: 路径点列表 [(x, y, z), ...]，必须是闭合的
        width: 赛道宽度
        thickness: 赛道厚度
        segments_per_section: 每段之间的细分数
    
    Returns:
        创建的网格对象
    """
    import bmesh
    
    n = len(path_points)
    if n < 3:
        raise ValueError("路径至少需要3个点")
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # 计算每个点的切线方向和法线
    def get_tangent(i):
        """获取点i处的切线方向"""
        prev_i = (i - 1) % n
        next_i = (i + 1) % n
        
        p_prev = path_points[prev_i]
        p_next = path_points[next_i]
        
        # 切线 = 下一点 - 上一点
        tx = p_next[0] - p_prev[0]
        ty = p_next[1] - p_prev[1]
        tz = p_next[2] - p_prev[2]
        
        # 归一化
        length = math.sqrt(tx*tx + ty*ty + tz*tz)
        if length > 0.001:
            tx /= length
            ty /= length
            tz /= length
        
        return (tx, ty, tz)
    
    def get_perpendicular(tangent):
        """获取水平面上垂直于切线的方向（用于赛道宽度方向）"""
        tx, ty, tz = tangent
        
        # 在XY平面上，垂直于(tx, ty)的方向是(-ty, tx)
        px = -ty
        py = tx
        pz = 0
        
        # 归一化
        length = math.sqrt(px*px + py*py)
        if length > 0.001:
            px /= length
            py /= length
        else:
            px, py = 1, 0
        
        return (px, py, pz)
    
    # 创建所有横截面的顶点
    all_sections = []  # 每个section是4个顶点: [外上, 内上, 内下, 外下]
    
    half_width = width / 2
    
    for i, point in enumerate(path_points):
        x, y, z = point
        tangent = get_tangent(i)
        perp = get_perpendicular(tangent)
        
        px, py, pz = perp
        
        # 4个角的顶点
        # 外上
        outer_top = bm.verts.new((
            x + px * half_width,
            y + py * half_width,
            z + thickness
        ))
        # 内上
        inner_top = bm.verts.new((
            x - px * half_width,
            y - py * half_width,
            z + thickness
        ))
        # 内下
        inner_bottom = bm.verts.new((
            x - px * half_width,
            y - py * half_width,
            z
        ))
        # 外下
        outer_bottom = bm.verts.new((
            x + px * half_width,
            y + py * half_width,
            z
        ))
        
        all_sections.append([outer_top, inner_top, inner_bottom, outer_bottom])
    
    bm.verts.ensure_lookup_table()
    
    # 连接相邻截面形成面
    for i in range(n):
        j = (i + 1) % n
        
        s1 = all_sections[i]  # [外上, 内上, 内下, 外下]
        s2 = all_sections[j]
        
        # 顶面
        bm.faces.new([s1[0], s2[0], s2[1], s1[1]])
        # 底面
        bm.faces.new([s1[3], s1[2], s2[2], s2[3]])
        # 外侧面
        bm.faces.new([s1[3], s2[3], s2[0], s1[0]])
        # 内侧面
        bm.faces.new([s1[1], s2[1], s2[2], s1[2]])
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    return obj


def create_barrier_along_path(name, path_points, offset, width, height):
    """
    沿路径创建护栏
    
    Args:
        name: 名称
        path_points: 路径点列表
        offset: 相对于路径中心线的偏移（正=外侧，负=内侧）
        width: 护栏宽度
        height: 护栏高度
    """
    import bmesh
    
    n = len(path_points)
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    def get_tangent(i):
        prev_i = (i - 1) % n
        next_i = (i + 1) % n
        p_prev = path_points[prev_i]
        p_next = path_points[next_i]
        tx = p_next[0] - p_prev[0]
        ty = p_next[1] - p_prev[1]
        length = math.sqrt(tx*tx + ty*ty)
        if length > 0.001:
            tx /= length
            ty /= length
        return (tx, ty)
    
    def get_perpendicular(tangent):
        tx, ty = tangent
        return (-ty, tx)
    
    all_sections = []
    half_width = width / 2
    
    for i, point in enumerate(path_points):
        x, y, z = point
        tangent = get_tangent(i)
        perp = get_perpendicular(tangent)
        px, py = perp
        
        # 护栏中心位置
        cx = x + px * offset
        cy = y + py * offset
        cz = z + TRACK_THICKNESS
        
        # 4个角
        outer_top = bm.verts.new((cx + px * half_width, cy + py * half_width, cz + height))
        inner_top = bm.verts.new((cx - px * half_width, cy - py * half_width, cz + height))
        inner_bottom = bm.verts.new((cx - px * half_width, cy - py * half_width, cz))
        outer_bottom = bm.verts.new((cx + px * half_width, cy + py * half_width, cz))
        
        all_sections.append([outer_top, inner_top, inner_bottom, outer_bottom])
    
    bm.verts.ensure_lookup_table()
    
    for i in range(n):
        j = (i + 1) % n
        s1 = all_sections[i]
        s2 = all_sections[j]
        
        bm.faces.new([s1[0], s2[0], s2[1], s1[1]])  # 顶
        bm.faces.new([s1[3], s1[2], s2[2], s2[3]])  # 底
        bm.faces.new([s1[3], s2[3], s2[0], s1[0]])  # 外
        bm.faces.new([s1[1], s2[1], s2[2], s1[2]])  # 内
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    return obj


# ============ 8字形路径生成 ============
def generate_figure8_path():
    """
    生成8字形路径点
    
    8字形由两个圆组成，在中间交叉处有立交桥。
    一个圆在上层，一个圆在下层。
    """
    points = []
    
    # 左圆圆心
    left_cx = -LOOP_SEPARATION / 2
    left_cy = 0
    
    # 右圆圆心
    right_cx = LOOP_SEPARATION / 2
    right_cy = 0
    
    # 计算交叉点的角度
    # 两圆相交时，交点相对于各自圆心的角度
    # 对于左圆，交点在右侧；对于右圆，交点在左侧
    
    # 第一部分：左圆的上半部分（从交点上方到交点下方，逆时针）
    # 角度从 -30° 到 210°（逆时针走上半圈）
    for i in range(SEGMENTS_PER_LOOP):
        t = i / SEGMENTS_PER_LOOP
        angle = math.radians(-30 + t * 240)  # -30° 到 210°
        
        x = left_cx + LOOP_RADIUS * math.cos(angle)
        y = left_cy + LOOP_RADIUS * math.sin(angle)
        
        # 高度：在交叉区域抬高（这部分在上层）
        # 交叉区域大约在 angle 接近 0° 或 180° 时
        cross_factor = abs(math.cos(angle))  # 在0°和180°时最大
        if cross_factor > 0.8:  # 接近交叉点
            z = BRIDGE_HEIGHT * smooth_step((cross_factor - 0.8) / 0.2)
        else:
            z = 0
        
        points.append((x, y, z))
    
    # 第二部分：右圆的完整圆（从交点进入，绕一圈）
    # 这部分在底层
    for i in range(SEGMENTS_PER_LOOP):
        t = i / SEGMENTS_PER_LOOP
        angle = math.radians(210 - t * 360)  # 210° 到 -150°（顺时针）
        
        x = right_cx + LOOP_RADIUS * math.cos(angle)
        y = right_cy + LOOP_RADIUS * math.sin(angle)
        z = 0  # 底层
        
        points.append((x, y, z))
    
    # 第三部分：左圆的下半部分
    for i in range(SEGMENTS_PER_LOOP):
        t = i / SEGMENTS_PER_LOOP
        angle = math.radians(210 + t * 120)  # 210° 到 330°
        
        x = left_cx + LOOP_RADIUS * math.cos(angle)
        y = left_cy + LOOP_RADIUS * math.sin(angle)
        z = 0
        
        points.append((x, y, z))
    
    return points


def smooth_step(t):
    """平滑插值函数"""
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


def generate_simple_figure8_path():
    """
    生成简化的8字形路径（平面版，无立交）
    两个圆平滑连接
    """
    points = []
    
    # 使用 Lemniscate of Bernoulli（伯努利双纽线）的参数方程
    # x = a * cos(t) / (1 + sin²(t))
    # y = a * sin(t) * cos(t) / (1 + sin²(t))
    
    # 或者更简单：两个圆平滑连接
    total_segments = SEGMENTS_PER_LOOP * 2
    
    # 8字形的参数方程（改进版）
    a = LOOP_RADIUS * 1.5  # 整体大小
    
    for i in range(total_segments):
        t = 2 * math.pi * i / total_segments
        
        # 8字形参数方程
        x = a * math.sin(t)
        y = a * math.sin(t) * math.cos(t)
        
        # 在交叉点添加高度差（立交桥效果）
        # 交叉点在 t = 0, π 时
        cross_factor = abs(math.sin(2 * t))  # 在交叉点附近变化
        
        # 上半圈抬高，下半圈保持
        if math.pi/4 < t < 3*math.pi/4 or 5*math.pi/4 < t < 7*math.pi/4:
            # 这些区间在上方
            bridge_t = 0
        else:
            # 判断是否在交叉区域
            dist_to_cross = min(abs(t), abs(t - math.pi), abs(t - 2*math.pi))
            if dist_to_cross < math.pi/6:
                # 根据行进方向决定高度
                if t < math.pi:
                    bridge_t = smooth_step(1 - dist_to_cross / (math.pi/6))
                else:
                    bridge_t = 0
            else:
                bridge_t = 0
        
        z = bridge_t * BRIDGE_HEIGHT
        
        points.append((x, y, z))
    
    return points


def generate_lemniscate_path_with_bridge():
    """
    生成带立交桥的双纽线（∞形）路径
    使用参数方程，在交叉点处一段抬高形成立交桥
    """
    points = []
    
    total_segments = SEGMENTS_PER_LOOP * 3  # 更多段数保证平滑
    a = LOOP_RADIUS * 1.8  # 大小参数
    
    # 第一遍：计算基础坐标
    raw_points = []
    for i in range(total_segments):
        t = 2 * math.pi * i / total_segments
        
        # 双纽线参数方程
        denom = 1 + math.sin(t) ** 2
        x = a * math.cos(t) / denom
        y = a * math.sin(t) * math.cos(t) / denom
        
        raw_points.append((x, y, t))
    
    # 第二遍：计算高度（立交桥）
    cross_zone = a * 0.4  # 交叉区域的x范围
    ramp_zone = a * 0.3   # 坡道区域
    
    for i, (x, y, t) in enumerate(raw_points):
        # 判断是否在交叉区域及其坡道
        dist_from_center = abs(x)
        
        if dist_from_center < cross_zone + ramp_zone:
            # 在交叉区域或坡道区域
            
            # 计算高度因子
            if dist_from_center < cross_zone:
                # 在交叉区域中心，高度最大
                height_factor = 1.0
            else:
                # 在坡道区域，逐渐降低
                ramp_progress = (dist_from_center - cross_zone) / ramp_zone
                height_factor = 1.0 - smooth_step(ramp_progress)
            
            # 根据行进方向决定是上层还是下层
            # t ∈ [0, π): 从右向左穿过中心 → 上层
            # t ∈ [π, 2π): 从左向右穿过中心 → 下层
            if t < math.pi:
                z = BRIDGE_HEIGHT * height_factor
            else:
                z = 0
        else:
            z = 0
        
        points.append((x, y, z))
    
    # 平滑处理
    smoothed_points = smooth_height_transitions(points, window=8)
    
    return smoothed_points


def smooth_height_transitions(points, window=5):
    """平滑高度过渡"""
    n = len(points)
    smoothed = []
    
    for i in range(n):
        # 取周围点的平均高度
        z_sum = 0
        count = 0
        for j in range(-window, window + 1):
            idx = (i + j) % n
            z_sum += points[idx][2]
            count += 1
        
        avg_z = z_sum / count
        
        # 混合原始高度和平滑高度
        orig_z = points[i][2]
        new_z = 0.7 * orig_z + 0.3 * avg_z
        
        smoothed.append((points[i][0], points[i][1], new_z))
    
    return smoothed


# ============ 主构建函数 ============
def build_figure8_track():
    """构建8字形赛道"""
    objects = []
    
    print("🏎️ 开始构建8字形赛道...")
    
    # 1. 生成路径点
    print("  📐 生成8字形路径...")
    path_points = generate_lemniscate_path_with_bridge()
    
    # 2. 创建赛道路面
    print("  🛣️ 创建赛道路面...")
    track_surface = create_track_along_path(
        "Figure8_Track_Surface",
        path_points,
        TRACK_WIDTH,
        TRACK_THICKNESS
    )
    objects.append(track_surface)
    
    # 3. 创建外护栏
    print("  🚧 创建外护栏...")
    outer_barrier = create_barrier_along_path(
        "Figure8_Outer_Barrier",
        path_points,
        TRACK_WIDTH / 2 + BARRIER_WIDTH / 2,
        BARRIER_WIDTH,
        BARRIER_HEIGHT
    )
    objects.append(outer_barrier)
    
    # 4. 创建内护栏
    print("  🚧 创建内护栏...")
    inner_barrier = create_barrier_along_path(
        "Figure8_Inner_Barrier",
        path_points,
        -(TRACK_WIDTH / 2 + BARRIER_WIDTH / 2),
        BARRIER_WIDTH,
        BARRIER_HEIGHT
    )
    objects.append(inner_barrier)
    
    print(f"✅ 8字形赛道构建完成！")
    print(f"   路径点数: {len(path_points)}")
    print(f"   赛道宽度: {TRACK_WIDTH}m")
    print(f"   立交桥高度: {BRIDGE_HEIGHT}m")
    
    return objects


# ============ 场景设置 ============
def clear_scene():
    """清理默认物体"""
    for obj in list(bpy.data.objects):
        if obj.type in ('MESH', 'CURVE'):
            bpy.data.objects.remove(obj, do_unlink=True)


def setup_camera():
    """设置相机"""
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
    else:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
    
    cam.location = (0, -60, 50)
    cam.rotation_euler = (0.8, 0, 0)
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
    print("🏎️ 8字形复杂赛道")
    print("=" * 60)
    print("\n特点：")
    print("  • 双纽线（∞形）路径")
    print("  • 中间立交桥结构")
    print("  • 平滑的高度过渡")
    print("  • 完整护栏")
    print()
    
    clear_scene()
    build_figure8_track()
    setup_camera()
    setup_lighting()
    
    print("\n" + "=" * 60)
    print("✅ 赛道构建完成！")
    print("=" * 60)
    
    if bpy.app.background:
        out = os.path.join(project_root, "assets", "figure8_track_demo.blend")
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print(f"\n💾 保存到: {out}")


if __name__ == "__main__":
    main()

