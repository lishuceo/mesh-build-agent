"""
组合物体模板 - 常用的复合结构便捷函数

这些函数封装了多个部件的组合逻辑，避免手动计算复杂的空间关系。
"""

import bpy
import math
from typing import List, Tuple
from .builder import GNodesBuilder


def create_chair(name: str, 
                 location: Tuple[float, float, float],
                 face_direction: float,
                 seat_size: Tuple[float, float] = (0.35, 0.35),
                 seat_height: float = 0.4,
                 back_height: float = 0.4) -> List[bpy.types.Object]:
    """
    创建完整的椅子（座面 + 靠背）
    
    Args:
        name: 椅子名称前缀
        location: 椅子座面中心位置 (x, y, z)
        face_direction: 椅子朝向角度（弧度），人坐下后面向的方向
        seat_size: 座面尺寸 (宽, 深)，默认 (0.35, 0.35)
        seat_height: 座面高度，默认 0.4
        back_height: 靠背高度，默认 0.4
    
    Returns:
        包含座面和靠背的物体列表
        
    Example:
        # 创建朝向北方的椅子
        objects = create_chair("Chair_01", (0, 0, 0), math.pi/2)
        
        # 创建环形排列的椅子
        for i in range(4):
            angle = i * (2 * math.pi / 4)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            # 面向圆心
            face_angle = angle + math.pi
            create_chair(f"Chair_{i}", (x, y, 0.4), face_angle)
    """
    objects = []
    x, y, z = location
    
    # 座面
    builder_seat = GNodesBuilder(f"{name}_Seat")
    builder_seat.add_node_group("G_Base_Cube", inputs={
        "Size": (seat_size[0], seat_size[1], 0.05),
        "Bevel": 0.02
    })
    builder_seat.add_node_group("G_Align_Ground")
    builder_seat.finalize()
    seat = builder_seat.get_object()
    seat.location = (x, y, z)
    seat.rotation_euler = (0, 0, face_direction)
    objects.append(seat)
    
    # 靠背（在座面后方）
    # 靠背尺寸：(宽, 厚, 高) = (seat_size[0], 0.05, back_height)
    # 默认状态：宽边沿X轴，厚边沿Y轴
    # 目标：宽边与人的背平行（垂直于face_direction）
    #      厚边沿face_direction方向
    
    back_offset = seat_size[1] / 2 + 0.025  # 座面深度的一半 + 靠背厚度的一半
    back_x = x - back_offset * math.cos(face_direction)
    back_y = y - back_offset * math.sin(face_direction)
    
    builder_back = GNodesBuilder(f"{name}_Back")
    builder_back.add_node_group("G_Base_Cube", inputs={
        "Size": (seat_size[0], 0.05, back_height),
        "Bevel": 0.02
    })
    # 不用 G_Shear（会变平行四边形），改用物体旋转实现后倾
    builder_back.add_node_group("G_Align_Ground")
    builder_back.finalize()
    back = builder_back.get_object()
    back.location = (back_x, back_y, z + 0.05)
    # 靠背旋转：
    # - 绕Z轴旋转：让宽边垂直于face_direction (+ π/2)
    # - 绕X轴旋转：让靠背后倾 (-0.1弧度 约-5.7度)
    back.rotation_euler = (
        -0.1,  # X轴：后倾
        0,     # Y轴：不旋转
        face_direction + math.pi / 2  # Z轴：朝向正确
    )
    objects.append(back)
    
    return objects


def create_table_with_chairs(name: str,
                             location: Tuple[float, float, float],
                             table_radius: float = 0.6,
                             num_chairs: int = 4,
                             chair_distance: float = 1.0) -> List[bpy.types.Object]:
    """
    创建圆桌和椅子组合
    
    Args:
        name: 名称前缀
        location: 桌子中心位置 (x, y, z)
        table_radius: 桌面半径，默认 0.6
        num_chairs: 椅子数量，默认 4
        chair_distance: 椅子距离桌子中心的距离，默认 1.0
    
    Returns:
        包含桌子和所有椅子的物体列表
        
    Example:
        # 创建4人圆桌
        objects = create_table_with_chairs("Dining", (0, 0, 0))
        
        # 创建6人大圆桌
        objects = create_table_with_chairs("Conference", (5, 5, 0), 
                                          table_radius=1.0, num_chairs=6)
    """
    objects = []
    cx, cy, cz = location
    
    # 桌面
    builder_top = GNodesBuilder(f"{name}_TableTop")
    builder_top.add_node_group("G_Base_Cylinder", inputs={
        "Radius": table_radius,
        "Height": 0.05,
        "Resolution": 24
    })
    builder_top.add_node_group("G_Align_Ground")
    builder_top.finalize()
    table_top = builder_top.get_object()
    table_top.location = location
    objects.append(table_top)
    
    # 桌腿
    builder_leg = GNodesBuilder(f"{name}_TableLeg")
    builder_leg.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.05,
        "Height": cz,
        "Resolution": 8
    })
    builder_leg.add_node_group("G_Align_Ground")
    builder_leg.finalize()
    leg = builder_leg.get_object()
    leg.location = (cx, cy, 0)
    objects.append(leg)
    
    # 环形排列椅子
    for i in range(num_chairs):
        angle = i * (2 * math.pi / num_chairs)
        chair_x = cx + chair_distance * math.cos(angle)
        chair_y = cy + chair_distance * math.sin(angle)
        # 椅子面向桌子中心
        face_angle = angle + math.pi
        
        chair_objects = create_chair(
            f"{name}_Chair_{i}",
            (chair_x, chair_y, 0.4),
            face_angle
        )
        objects.extend(chair_objects)
    
    return objects


def create_fence(name: str,
                start_pos: Tuple[float, float],
                end_pos: Tuple[float, float],
                num_posts: int = 8,
                post_height: float = 1.0,
                rail_height: float = 0.7) -> List[bpy.types.Object]:
    """
    创建栅栏（柱子 + 横杆）
    
    Args:
        name: 名称前缀
        start_pos: 起点 (x, y)
        end_pos: 终点 (x, y)
        num_posts: 柱子数量，默认 8
        post_height: 柱子高度，默认 1.0
        rail_height: 横杆高度，默认 0.7
    
    Returns:
        包含所有柱子和横杆的物体列表
        
    Example:
        # 创建一段栅栏
        objects = create_fence("Fence_01", (-4, 3), (0, 3), num_posts=8)
    """
    objects = []
    sx, sy = start_pos
    ex, ey = end_pos
    
    # 栅栏柱子
    for i in range(num_posts):
        t = i / (num_posts - 1) if num_posts > 1 else 0
        x = sx + (ex - sx) * t
        y = sy + (ey - sy) * t
        
        builder = GNodesBuilder(f"{name}_Post_{i}")
        builder.add_node_group("G_Base_Cube", inputs={
            "Size": (0.06, 0.06, post_height),
            "Bevel": 0.01
        })
        builder.add_node_group("G_Taper", inputs={"Factor": 0.2})
        builder.add_node_group("G_Align_Ground")
        builder.finalize()
        post = builder.get_object()
        post.location = (x, y, 0)
        objects.append(post)
    
    # 横杆
    fence_length = math.sqrt((ex - sx)**2 + (ey - sy)**2)
    fence_angle = math.atan2(ey - sy, ex - sx)
    mid_x = (sx + ex) / 2
    mid_y = (sy + ey) / 2
    
    builder_rail = GNodesBuilder(f"{name}_Rail")
    builder_rail.add_node_group("G_Base_Cube", inputs={
        "Size": (fence_length, 0.04, 0.04),
        "Bevel": 0.005
    })
    builder_rail.add_node_group("G_Align_Ground")
    builder_rail.finalize()
    rail = builder_rail.get_object()
    rail.location = (mid_x, mid_y, rail_height)
    rail.rotation_euler = (0, 0, fence_angle)
    objects.append(rail)
    
    return objects


def create_arch(name: str,
               location: Tuple[float, float, float],
               width: float = 2.0,
               height: float = 2.0,
               thickness: float = 0.25,
               depth: float = 0.25) -> List[bpy.types.Object]:
    """
    创建拱门（左柱 + 右柱 + 均匀截面拱顶，顶点已缝合）

    使用 G_Arch_Complete 节点组生成完整拱门，内部自动合并顶点。

    Args:
        name: 名称前缀
        location: 拱门中心底部位置 (x, y, z)
        width: 拱门内宽（两柱内侧间距），默认 2.0
        height: 柱子高度（拱顶起点），默认 2.0
        thickness: 柱子/拱顶厚度，默认 0.25
        depth: 柱子/拱顶深度，默认 0.25

    Returns:
        包含单个完整拱门物体的列表（顶点已缝合）

    Example:
        # 创建标准拱门
        objects = create_arch("Arch_01", (0, 0, 0))

        # 创建宽拱门
        objects = create_arch("WideArch", (0, 0, 0), width=3.0, height=2.5)
    """
    builder = GNodesBuilder(name)
    builder.add_node_group("G_Arch_Complete", inputs={
        "Width": width,
        "Height": height,
        "Thickness": thickness,
        "Depth": depth,
        "Resolution": 16
    })
    builder.finalize()

    arch = builder.get_object()
    arch.location = location

    return [arch]


def create_door_frame(name: str,
                     location: Tuple[float, float, float],
                     width: float = 1.0,
                     height: float = 2.1,
                     thickness: float = 0.15) -> List[bpy.types.Object]:
    """
    创建门框（左柱 + 右柱 + 门楣）
    
    Args:
        name: 名称前缀
        location: 门框中心位置 (x, y, z)
        width: 门宽，默认 1.0
        height: 门高，默认 2.1
        thickness: 柱子厚度，默认 0.15
    
    Returns:
        包含左柱、右柱、门楣的物体列表
        
    Example:
        # 创建标准门框
        objects = create_door_frame("Door_01", (0, 0, 0))
    """
    objects = []
    x, y, z = location
    
    # 左柱
    builder_left = GNodesBuilder(f"{name}_Left")
    builder_left.add_node_group("G_Base_Cube", inputs={
        "Size": (thickness, thickness, height)
    })
    builder_left.add_node_group("G_Align_Ground")
    builder_left.finalize()
    left = builder_left.get_object()
    left.location = (x - width/2 - thickness/2, y, z)
    objects.append(left)
    
    # 右柱
    builder_right = GNodesBuilder(f"{name}_Right")
    builder_right.add_node_group("G_Base_Cube", inputs={
        "Size": (thickness, thickness, height)
    })
    builder_right.add_node_group("G_Align_Ground")
    builder_right.finalize()
    right = builder_right.get_object()
    right.location = (x + width/2 + thickness/2, y, z)
    objects.append(right)
    
    # 门楣
    builder_top = GNodesBuilder(f"{name}_Top")
    builder_top.add_node_group("G_Base_Cube", inputs={
        "Size": (width + 2 * thickness, thickness, thickness)
    })
    builder_top.add_node_group("G_Align_Ground")
    builder_top.finalize()
    top = builder_top.get_object()
    top.location = (x, y, z + height)
    objects.append(top)
    
    return objects


# ============ 赛道/道路系统 ============
# 
# 架构设计：
#   层次1 (底层): _create_track_along_path(), _create_barrier_along_path()
#   层次2 (路径): generate_stadium_path(), generate_figure8_path(), generate_custom_path()
#   层次3 (高层): create_oval_track(), create_figure8_track(), create_custom_track()
#
# AI Agent 只需调用层次3的函数，一行代码生成完整赛道！
#

def _smooth_step(t: float) -> float:
    """平滑插值函数 (Hermite)"""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _smooth_height_transitions(points: List[Tuple[float, float, float]], 
                                window: int = 5) -> List[Tuple[float, float, float]]:
    """平滑高度过渡"""
    n = len(points)
    smoothed = []
    
    for i in range(n):
        z_sum = 0
        count = 0
        for j in range(-window, window + 1):
            idx = (i + j) % n
            z_sum += points[idx][2]
            count += 1
        
        avg_z = z_sum / count
        orig_z = points[i][2]
        new_z = 0.7 * orig_z + 0.3 * avg_z
        
        smoothed.append((points[i][0], points[i][1], new_z))
    
    return smoothed


# ========== 层次1：底层网格生成函数 ==========

def _compute_curvature_radius(path_points: List[Tuple[float, float, float]], 
                               index: int) -> float:
    """
    计算路径点处的曲率半径（使用三点外接圆）
    
    Args:
        path_points: 路径点列表
        index: 当前点的索引
    
    Returns:
        曲率半径（越小表示弯曲越急，直线返回 inf）
    """
    n = len(path_points)
    if n < 3:
        return float('inf')
    
    # 获取前后点
    prev_i = (index - 1) % n
    next_i = (index + 1) % n
    
    p0 = path_points[prev_i]
    p1 = path_points[index]
    p2 = path_points[next_i]
    
    # 计算三边长度
    a = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)  # p1-p2
    b = math.sqrt((p0[0] - p2[0])**2 + (p0[1] - p2[1])**2)  # p0-p2
    c = math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)  # p0-p1
    
    # 使用海伦公式计算面积
    s = (a + b + c) / 2
    area_sq = s * (s - a) * (s - b) * (s - c)
    
    if area_sq <= 0:
        # 三点共线
        return float('inf')
    
    area = math.sqrt(area_sq)
    
    # 外接圆半径 R = abc / (4 * area)
    if area < 0.0001:
        return float('inf')
    
    radius = (a * b * c) / (4 * area)
    
    return radius


def _compute_curvature_radii(path_points: List[Tuple[float, float, float]], 
                              smoothing_window: int = 2) -> List[float]:
    """
    计算所有路径点的平滑曲率半径
    
    Args:
        path_points: 路径点列表
        smoothing_window: 平滑窗口大小
    
    Returns:
        每个点的曲率半径列表
    """
    n = len(path_points)
    raw_radii = []
    
    # 计算原始曲率半径
    for i in range(n):
        r = _compute_curvature_radius(path_points, i)
        raw_radii.append(r)
    
    # 平滑处理（取局部最小值，保守处理急弯）
    smoothed_radii = []
    for i in range(n):
        min_r = raw_radii[i]
        for offset in range(-smoothing_window, smoothing_window + 1):
            idx = (i + offset) % n
            min_r = min(min_r, raw_radii[idx])
        smoothed_radii.append(min_r)
    
    return smoothed_radii


def _get_adaptive_offsets(curvature_radius: float, half_width: float, 
                          turn_direction: float) -> Tuple[float, float]:
    """
    根据曲率半径计算内外侧的自适应偏移距离
    
    Args:
        curvature_radius: 曲率半径
        half_width: 赛道半宽
        turn_direction: 转弯方向（正=左转，负=右转，用于确定哪侧是内侧）
    
    Returns:
        (left_offset, right_offset): 左右两侧的偏移距离
    """
    # 如果曲率半径很大（接近直线），正常偏移
    if curvature_radius > half_width * 3:
        return half_width, half_width
    
    # 内侧的安全偏移：不能超过曲率半径
    # 留一些余量，避免刚好在边界
    safe_inner_offset = max(0.1, min(half_width, curvature_radius * 0.85 - 0.1))
    
    # 根据转弯方向决定哪侧是内侧
    # turn_direction > 0 表示左转，左侧是内侧
    # turn_direction < 0 表示右转，右侧是内侧
    if turn_direction > 0.001:
        # 左转：左侧是内侧，需要收缩
        left_offset = safe_inner_offset
        right_offset = half_width
    elif turn_direction < -0.001:
        # 右转：右侧是内侧，需要收缩
        left_offset = half_width
        right_offset = safe_inner_offset
    else:
        # 直行
        left_offset = half_width
        right_offset = half_width
    
    return left_offset, right_offset


def _compute_turn_directions(path_points: List[Tuple[float, float, float]], 
                              tangents: List[Tuple[float, float]]) -> List[float]:
    """
    计算每个点的转弯方向（使用叉积）
    
    Args:
        path_points: 路径点列表
        tangents: 切线方向列表
    
    Returns:
        转弯方向列表（正=左转，负=右转）
    """
    n = len(path_points)
    directions = []
    
    for i in range(n):
        prev_i = (i - 1) % n
        next_i = (i + 1) % n
        
        # 入射方向
        dx1 = path_points[i][0] - path_points[prev_i][0]
        dy1 = path_points[i][1] - path_points[prev_i][1]
        
        # 出射方向
        dx2 = path_points[next_i][0] - path_points[i][0]
        dy2 = path_points[next_i][1] - path_points[i][1]
        
        # 叉积确定转弯方向
        cross = dx1 * dy2 - dy1 * dx2
        directions.append(cross)
    
    return directions


def _compute_smooth_tangents(path_points: List[Tuple[float, float, float]], 
                              smoothing_window: int = 3) -> List[Tuple[float, float]]:
    """
    计算平滑的切线方向（使用更大窗口避免急弯处突变）
    
    Args:
        path_points: 路径点列表
        smoothing_window: 平滑窗口大小（每侧的点数）
    
    Returns:
        每个点的切线方向列表 [(tx, ty), ...]
    """
    n = len(path_points)
    raw_tangents = []
    
    # 第一遍：计算原始切线（使用更大的窗口）
    for i in range(n):
        # 使用前后多个点来计算切线方向
        tx_sum, ty_sum = 0.0, 0.0
        weight_sum = 0.0
        
        for offset in range(1, smoothing_window + 1):
            prev_i = (i - offset) % n
            next_i = (i + offset) % n
            
            p_prev = path_points[prev_i]
            p_next = path_points[next_i]
            
            dx = p_next[0] - p_prev[0]
            dy = p_next[1] - p_prev[1]
            
            # 权重：距离越近权重越大
            weight = 1.0 / offset
            tx_sum += dx * weight
            ty_sum += dy * weight
            weight_sum += weight
        
        if weight_sum > 0:
            tx_sum /= weight_sum
            ty_sum /= weight_sum
        
        # 归一化
        length = math.sqrt(tx_sum * tx_sum + ty_sum * ty_sum)
        if length > 0.001:
            tx_sum /= length
            ty_sum /= length
        else:
            tx_sum, ty_sum = 1.0, 0.0
        
        raw_tangents.append((tx_sum, ty_sum))
    
    # 第二遍：进一步平滑切线方向（角度平滑）
    smoothed_tangents = []
    smooth_radius = 2  # 平滑半径
    
    for i in range(n):
        # 收集周围的切线角度
        angles = []
        weights = []
        
        for offset in range(-smooth_radius, smooth_radius + 1):
            idx = (i + offset) % n
            tx, ty = raw_tangents[idx]
            angle = math.atan2(ty, tx)
            weight = 1.0 / (1 + abs(offset))
            angles.append(angle)
            weights.append(weight)
        
        # 处理角度跨越 ±π 的情况
        base_angle = angles[smooth_radius]  # 当前点的角度
        adjusted_angles = []
        for angle in angles:
            diff = angle - base_angle
            # 将差值调整到 [-π, π] 范围
            while diff > math.pi:
                diff -= 2 * math.pi
            while diff < -math.pi:
                diff += 2 * math.pi
            adjusted_angles.append(base_angle + diff)
        
        # 加权平均
        avg_angle = sum(a * w for a, w in zip(adjusted_angles, weights)) / sum(weights)
        
        tx = math.cos(avg_angle)
        ty = math.sin(avg_angle)
        smoothed_tangents.append((tx, ty))
    
    return smoothed_tangents


def _create_track_along_path(name: str, 
                              path_points: List[Tuple[float, float, float]],
                              width: float, 
                              thickness: float,
                              adaptive_width: bool = True) -> bpy.types.Object:
    """
    沿任意路径创建赛道网格（核心底层函数）
    
    使用自适应内侧偏移：在急弯处自动收缩内侧边界，防止交叉。
    
    Args:
        name: 网格名称
        path_points: 闭合路径点列表 [(x, y, z), ...]
        width: 赛道宽度
        thickness: 赛道厚度
        adaptive_width: 是否启用自适应宽度（防止急弯处交叉）
    
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
    
    # 预计算平滑切线
    smoothing_window = max(3, n // 20)
    tangents = _compute_smooth_tangents(path_points, smoothing_window)
    
    half_width = width / 2
    
    # 如果启用自适应宽度，计算曲率和转弯方向
    if adaptive_width:
        curvature_radii = _compute_curvature_radii(path_points)
        turn_directions = _compute_turn_directions(path_points, tangents)
    
    all_sections = []
    
    for i, point in enumerate(path_points):
        x, y, z = point
        tx, ty = tangents[i]
        
        # 垂直方向（左侧为正方向）
        # px, py 指向赛道左侧
        px, py = -ty, tx
        
        if adaptive_width:
            # 自适应偏移：根据曲率调整内侧宽度
            left_offset, right_offset = _get_adaptive_offsets(
                curvature_radii[i], half_width, turn_directions[i]
            )
        else:
            left_offset = half_width
            right_offset = half_width
        
        # 左侧（正方向）和右侧（负方向）
        left_top = bm.verts.new((x + px*left_offset, y + py*left_offset, z + thickness))
        right_top = bm.verts.new((x - px*right_offset, y - py*right_offset, z + thickness))
        right_bottom = bm.verts.new((x - px*right_offset, y - py*right_offset, z))
        left_bottom = bm.verts.new((x + px*left_offset, y + py*left_offset, z))
        
        # 注意顺序：[left_top, right_top, right_bottom, left_bottom]
        # 对应原来的 [outer_top, inner_top, inner_bottom, outer_bottom]
        all_sections.append([left_top, right_top, right_bottom, left_bottom])
    
    bm.verts.ensure_lookup_table()
    
    for i in range(n):
        j = (i + 1) % n
        s1, s2 = all_sections[i], all_sections[j]
        
        bm.faces.new([s1[0], s2[0], s2[1], s1[1]])  # 顶
        bm.faces.new([s1[3], s1[2], s2[2], s2[3]])  # 底
        bm.faces.new([s1[3], s2[3], s2[0], s1[0]])  # 左侧（外）
        bm.faces.new([s1[1], s2[1], s2[2], s1[2]])  # 右侧（内）
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    return obj


def _create_barrier_along_path(name: str,
                                path_points: List[Tuple[float, float, float]],
                                offset: float,
                                width: float,
                                height: float,
                                base_height: float = 0,
                                track_half_width: float = None,
                                adaptive_offset: bool = True) -> bpy.types.Object:
    """
    沿路径创建护栏（核心底层函数）
    
    使用自适应偏移：在急弯处根据内侧收缩调整护栏位置。
    
    Args:
        name: 名称
        path_points: 路径点列表
        offset: 相对于路径中心线的偏移（正=左侧，负=右侧）
        width: 护栏宽度
        height: 护栏高度
        base_height: 护栏底部相对于路径的高度偏移
        track_half_width: 赛道半宽（用于自适应偏移计算）
        adaptive_offset: 是否启用自适应偏移
    """
    import bmesh
    
    n = len(path_points)
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # 使用平滑切线计算
    smoothing_window = max(3, n // 20)
    tangents = _compute_smooth_tangents(path_points, smoothing_window)
    
    # 如果启用自适应偏移，计算曲率和转弯方向
    if adaptive_offset and track_half_width is not None:
        curvature_radii = _compute_curvature_radii(path_points)
        turn_directions = _compute_turn_directions(path_points, tangents)
    else:
        adaptive_offset = False
    
    all_sections = []
    half_width = width / 2
    
    for i, point in enumerate(path_points):
        x, y, z = point
        tx, ty = tangents[i]
        px, py = -ty, tx  # 垂直方向（左侧为正）
        
        # 计算护栏中心线的偏移
        if adaptive_offset:
            # 根据曲率调整偏移
            left_track_offset, right_track_offset = _get_adaptive_offsets(
                curvature_radii[i], track_half_width, turn_directions[i]
            )
            
            if offset > 0:
                # 左侧护栏
                actual_offset = left_track_offset + half_width
            else:
                # 右侧护栏
                actual_offset = -(right_track_offset + half_width)
        else:
            actual_offset = offset
        
        cx = x + px * actual_offset
        cy = y + py * actual_offset
        cz = z + base_height
        
        outer_top = bm.verts.new((cx + px*half_width, cy + py*half_width, cz + height))
        inner_top = bm.verts.new((cx - px*half_width, cy - py*half_width, cz + height))
        inner_bottom = bm.verts.new((cx - px*half_width, cy - py*half_width, cz))
        outer_bottom = bm.verts.new((cx + px*half_width, cy + py*half_width, cz))
        
        all_sections.append([outer_top, inner_top, inner_bottom, outer_bottom])
    
    bm.verts.ensure_lookup_table()
    
    for i in range(n):
        j = (i + 1) % n
        s1, s2 = all_sections[i], all_sections[j]
        
        bm.faces.new([s1[0], s2[0], s2[1], s1[1]])
        bm.faces.new([s1[3], s1[2], s2[2], s2[3]])
        bm.faces.new([s1[3], s2[3], s2[0], s1[0]])
        bm.faces.new([s1[1], s2[1], s2[2], s1[2]])
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    return obj


# ========== 层次2：路径生成函数 ==========

# ========== 公开的路径生成函数（AI Agent 可调用）==========

def generate_stadium_path(length: float, radius: float, 
                          segments_per_curve: int = 16) -> List[Tuple[float, float, float]]:
    """
    生成操场形路径（两端半圆 + 中间直线）⭐ 最常用
    
    这是现实中最常见的赛道形状！
    
    Args:
        length: 直线段长度（两个半圆圆心之间的距离）
        radius: 半圆半径（也是赛道的宽度方向尺寸）
        segments_per_curve: 每个半圆的分段数
    
    Returns:
        闭合路径点列表
    
    Example:
        path = generate_stadium_path(length=40, radius=15)
        track = create_track_from_path("Stadium", path, track_width=6)
    """
    points = []
    half_length = length / 2
    
    # 右半圆（从上到下）
    for i in range(segments_per_curve):
        angle = math.pi/2 - math.pi * i / segments_per_curve
        x = half_length + radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append((x, y, 0))
    
    # 下直线（从右到左）
    segments_straight = max(4, int(length / 5))
    for i in range(segments_straight):
        t = i / segments_straight
        x = half_length - length * t
        y = -radius
        points.append((x, y, 0))
    
    # 左半圆（从下到上）
    for i in range(segments_per_curve):
        angle = -math.pi/2 - math.pi * i / segments_per_curve
        x = -half_length + radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append((x, y, 0))
    
    # 上直线（从左到右）
    for i in range(segments_straight):
        t = i / segments_straight
        x = -half_length + length * t
        y = radius
        points.append((x, y, 0))
    
    return points


def generate_oval_path(radius_x: float, radius_y: float, 
                       segments: int = 64) -> List[Tuple[float, float, float]]:
    """
    生成椭圆形路径
    
    Args:
        radius_x: X方向半径
        radius_y: Y方向半径
        segments: 分段数
    
    Returns:
        闭合路径点列表
    """
    points = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = radius_x * math.cos(angle)
        y = radius_y * math.sin(angle)
        points.append((x, y, 0))
    return points


def generate_circle_path(radius: float, 
                         segments: int = 32) -> List[Tuple[float, float, float]]:
    """
    生成圆形路径
    
    Args:
        radius: 半径
        segments: 分段数
    """
    return generate_oval_path(radius, radius, segments)


def generate_figure8_path(size: float, 
                          bridge_height: float = 4.0,
                          segments: int = 96) -> List[Tuple[float, float, float]]:
    """
    生成带立交桥的8字形（∞形）路径
    
    Args:
        size: 整体大小（半径）
        bridge_height: 立交桥高度（0=平面8字形）
        segments: 分段数
    
    Returns:
        闭合路径点列表（包含高度信息）
    
    Example:
        path = generate_figure8_path(size=20, bridge_height=4)
        track = create_track_from_path("Figure8", path, track_width=6)
    """
    points = []
    a = size * 1.8
    
    # 第一遍：计算基础坐标
    raw_points = []
    for i in range(segments):
        t = 2 * math.pi * i / segments
        denom = 1 + math.sin(t) ** 2
        x = a * math.cos(t) / denom
        y = a * math.sin(t) * math.cos(t) / denom
        raw_points.append((x, y, t))
    
    # 第二遍：计算立交桥高度
    cross_zone = a * 0.4
    ramp_zone = a * 0.3
    
    for x, y, t in raw_points:
        dist_from_center = abs(x)
        
        if dist_from_center < cross_zone + ramp_zone:
            if dist_from_center < cross_zone:
                height_factor = 1.0
            else:
                ramp_progress = (dist_from_center - cross_zone) / ramp_zone
                height_factor = 1.0 - _smooth_step(ramp_progress)
            
            z = bridge_height * height_factor if t < math.pi else 0
        else:
            z = 0
        
        points.append((x, y, z))
    
    return _smooth_height_transitions(points, window=8)


def _estimate_section_curvature(p0, p1, p2, p3) -> float:
    """
    估算一段曲线的曲率（用于自适应细分）
    
    通过计算控制点形成的角度变化来估算曲率
    """
    # 计算入射方向和出射方向
    dx1 = p1[0] - p0[0]
    dy1 = p1[1] - p0[1]
    dx2 = p2[0] - p1[0]
    dy2 = p2[1] - p1[1]
    dx3 = p3[0] - p2[0]
    dy3 = p3[1] - p2[1]
    
    # 计算角度变化
    def angle_diff(dx1, dy1, dx2, dy2):
        len1 = math.sqrt(dx1*dx1 + dy1*dy1)
        len2 = math.sqrt(dx2*dx2 + dy2*dy2)
        if len1 < 0.001 or len2 < 0.001:
            return 0
        # 归一化
        dx1, dy1 = dx1/len1, dy1/len1
        dx2, dy2 = dx2/len2, dy2/len2
        # 叉积的绝对值 = sin(角度差)
        cross = abs(dx1*dy2 - dy1*dx2)
        return cross
    
    # 取两次方向变化的最大值
    curvature = max(
        angle_diff(dx1, dy1, dx2, dy2),
        angle_diff(dx2, dy2, dx3, dy3)
    )
    
    return curvature


def generate_custom_path(waypoints: List[Tuple[float, float]],
                         height_profile: List[float] = None,
                         segments_per_section: int = 16,
                         adaptive_subdivision: bool = True) -> List[Tuple[float, float, float]]:
    """
    通过控制点生成平滑闭合路径（Catmull-Rom 样条插值）
    
    ⭐ 新增自适应细分功能：在曲率大的弯道处自动增加更多的点
    
    Args:
        waypoints: 控制点列表 [(x, y), ...]，至少3个点
        height_profile: 每个控制点的高度（可选）
        segments_per_section: 每段的基础细分数
        adaptive_subdivision: 是否启用自适应细分（默认True）
    
    Returns:
        平滑的闭合路径点列表
    
    Example:
        waypoints = [(0, 0), (30, 15), (50, 0), (30, -15)]
        path = generate_custom_path(waypoints)
        track = create_track_from_path("Custom", path, track_width=6)
        
        # 带高度起伏
        heights = [0, 3, 5, 2]
        path = generate_custom_path(waypoints, height_profile=heights)
    """
    n = len(waypoints)
    if n < 3:
        raise ValueError("至少需要3个控制点")
    
    if height_profile is None:
        height_profile = [0.0] * n
    
    points = []
    
    def catmull_rom(p0, p1, p2, p3, t):
        """Catmull-Rom 样条插值"""
        t2 = t * t
        t3 = t2 * t
        
        return 0.5 * (
            (2 * p1) +
            (-p0 + p2) * t +
            (2*p0 - 5*p1 + 4*p2 - p3) * t2 +
            (-p0 + 3*p1 - 3*p2 + p3) * t3
        )
    
    for i in range(n):
        # 获取4个控制点（循环）
        p0 = waypoints[(i - 1) % n]
        p1 = waypoints[i]
        p2 = waypoints[(i + 1) % n]
        p3 = waypoints[(i + 2) % n]
        
        h0 = height_profile[(i - 1) % n]
        h1 = height_profile[i]
        h2 = height_profile[(i + 1) % n]
        h3 = height_profile[(i + 2) % n]
        
        # 自适应细分：根据曲率调整该段的细分数
        if adaptive_subdivision:
            curvature = _estimate_section_curvature(p0, p1, p2, p3)
            # 曲率越大，细分越多（最多3倍）
            curvature_multiplier = 1.0 + curvature * 2.0
            actual_segments = int(segments_per_section * min(3.0, curvature_multiplier))
        else:
            actual_segments = segments_per_section
        
        for j in range(actual_segments):
            t = j / actual_segments
            
            x = catmull_rom(p0[0], p1[0], p2[0], p3[0], t)
            y = catmull_rom(p0[1], p1[1], p2[1], p3[1], t)
            z = catmull_rom(h0, h1, h2, h3, t)
            
            points.append((x, y, z))
    
    return points


# ========== 层次3：高级模板函数（AI Agent 调用）==========

def _limit_path_curvature(path: List[Tuple[float, float, float]],
                          track_width: float,
                          max_iterations: int = 50) -> List[Tuple[float, float, float]]:
    """
    限制路径的最大转弯角度，从源头上防止边缘交叉
    
    核心原理：如果转弯角度过大，内侧边缘会交叉。
    通过迭代平滑，将所有超过安全阈值的转弯角度降低。
    
    安全角度计算：
    - 假设点间距为 d，赛道半宽为 w
    - 内侧边缘点间距约为 d - 2*w*sin(θ/2)
    - 要保证内侧不交叉，需要 d > 2*w*sin(θ/2)
    - 即 θ < 2*arcsin(d/(2*w))
    
    Args:
        path: 原始路径点
        track_width: 赛道宽度（用于计算安全转弯角度）
        max_iterations: 最大迭代次数
    
    Returns:
        处理后的路径点（转弯角度受限）
    """
    n = len(path)
    if n < 4:
        return path
    
    # 转换为可修改的列表
    points = [list(p) for p in path]
    half_width = track_width / 2
    
    def get_turn_angle(i):
        """计算点 i 处的转弯角度"""
        prev_i = (i - 1) % n
        next_i = (i + 1) % n
        
        # 入射方向
        dx1 = points[i][0] - points[prev_i][0]
        dy1 = points[i][1] - points[prev_i][1]
        len1 = math.sqrt(dx1*dx1 + dy1*dy1)
        
        # 出射方向
        dx2 = points[next_i][0] - points[i][0]
        dy2 = points[next_i][1] - points[i][1]
        len2 = math.sqrt(dx2*dx2 + dy2*dy2)
        
        if len1 < 0.001 or len2 < 0.001:
            return 0, 0, 0  # angle, segment_length, direction
        
        # 归一化
        dx1, dy1 = dx1/len1, dy1/len1
        dx2, dy2 = dx2/len2, dy2/len2
        
        # 计算角度（使用点积和叉积）
        dot = dx1*dx2 + dy1*dy2
        cross = dx1*dy2 - dy1*dx2
        
        # 限制 dot 在 [-1, 1] 范围内
        dot = max(-1.0, min(1.0, dot))
        angle = math.acos(dot)  # 转弯角度（0 = 直行，π = 180度转弯）
        
        # 平均段长度
        avg_len = (len1 + len2) / 2
        
        return angle, avg_len, cross  # cross 的符号表示转弯方向
    
    def get_safe_angle(segment_length):
        """根据段长度计算安全的最大转弯角度"""
        if segment_length < 0.001:
            return 0.1
        
        # 安全条件：内侧边缘点间距 > 0
        # d - 2*w*sin(θ/2) > 0
        # sin(θ/2) < d/(2*w)
        ratio = segment_length / (2 * half_width)
        
        if ratio >= 1.0:
            # 段长度足够长，允许较大转弯
            return math.pi * 0.4  # 最大约 72 度
        else:
            # 段长度较短，限制转弯角度
            # 留一些余量（乘以 0.8）
            safe_sin = ratio * 0.8
            safe_sin = max(0.05, min(0.99, safe_sin))
            return 2 * math.asin(safe_sin)
    
    # 迭代平滑
    for iteration in range(max_iterations):
        max_excess = 0  # 记录最大超标量
        
        for i in range(n):
            angle, seg_len, direction = get_turn_angle(i)
            safe_angle = get_safe_angle(seg_len)
            
            if angle > safe_angle:
                excess = angle - safe_angle
                max_excess = max(max_excess, excess)
                
                # 平滑：将该点向邻居的平均位置移动
                prev_i = (i - 1) % n
                next_i = (i + 1) % n
                
                # 计算邻居的平均位置
                avg_x = (points[prev_i][0] + points[next_i][0]) / 2
                avg_y = (points[prev_i][1] + points[next_i][1]) / 2
                avg_z = (points[prev_i][2] + points[next_i][2]) / 2
                
                # 平滑系数：超标越多，平滑越强
                # 但不要一次移动太多，避免振荡
                smooth_factor = min(0.3, excess / math.pi)
                
                points[i][0] += (avg_x - points[i][0]) * smooth_factor
                points[i][1] += (avg_y - points[i][1]) * smooth_factor
                points[i][2] += (avg_z - points[i][2]) * smooth_factor
        
        # 如果所有点都在安全范围内，提前退出
        if max_excess < 0.01:  # 约 0.5 度的容差
            break
    
    return [tuple(p) for p in points]


def _resample_path_uniform(path: List[Tuple[float, float, float]], 
                           target_spacing: float = None,
                           min_points: int = 100) -> List[Tuple[float, float, float]]:
    """
    对路径进行均匀重采样，确保相邻点之间的间距大致相等
    
    这可以避免某些地方点太密集而另一些地方太稀疏的问题。
    
    Args:
        path: 原始路径点
        target_spacing: 目标间距（如果为None，则根据路径长度自动计算）
        min_points: 最少点数
    
    Returns:
        重采样后的路径点
    """
    n = len(path)
    if n < 3:
        return path
    
    # 计算路径总长度
    total_length = 0.0
    segment_lengths = []
    
    for i in range(n):
        j = (i + 1) % n
        dx = path[j][0] - path[i][0]
        dy = path[j][1] - path[i][1]
        dz = path[j][2] - path[i][2]
        seg_len = math.sqrt(dx*dx + dy*dy + dz*dz)
        segment_lengths.append(seg_len)
        total_length += seg_len
    
    # 确定目标点数和间距
    if target_spacing is None:
        # 自动计算：确保有足够的点，但间距不要太小
        target_points = max(min_points, n, int(total_length / 2.0))  # 约每2米一个点
    else:
        target_points = max(min_points, int(total_length / target_spacing))
    
    target_spacing = total_length / target_points
    
    # 重采样
    resampled = []
    current_pos = 0.0
    current_segment = 0
    segment_progress = 0.0
    
    for _ in range(target_points):
        # 找到当前位置对应的段和位置
        while segment_progress >= segment_lengths[current_segment] and segment_lengths[current_segment] > 0.001:
            segment_progress -= segment_lengths[current_segment]
            current_segment = (current_segment + 1) % n
        
        # 在当前段内插值
        if segment_lengths[current_segment] > 0.001:
            t = segment_progress / segment_lengths[current_segment]
        else:
            t = 0
        
        i = current_segment
        j = (i + 1) % n
        
        x = path[i][0] + (path[j][0] - path[i][0]) * t
        y = path[i][1] + (path[j][1] - path[i][1]) * t
        z = path[i][2] + (path[j][2] - path[i][2]) * t
        
        resampled.append((x, y, z))
        
        # 移动到下一个采样位置
        segment_progress += target_spacing
    
    return resampled


def create_track_from_path(
    name: str,
    path: List[Tuple[float, float, float]],
    track_width: float = 6.0,
    track_thickness: float = 0.3,
    barrier_height: float = 0.6,
    barrier_width: float = 0.12,
    include_barriers: bool = True,
    location: Tuple[float, float, float] = (0, 0, 0),
    resample: bool = True
) -> List[bpy.types.Object]:
    """
    从路径创建赛道（核心函数）⭐
    
    这是创建赛道的统一入口！配合路径生成函数使用。
    
    ⭐ 新增自动重采样功能：确保路径点均匀分布，避免尖角问题
    
    Args:
        name: 赛道名称前缀
        path: 路径点列表（由 generate_xxx_path 函数生成）
        track_width: 赛道宽度，默认 6m
        track_thickness: 赛道厚度，默认 0.3m
        barrier_height: 护栏高度，默认 0.6m
        barrier_width: 护栏宽度，默认 0.12m
        include_barriers: 是否包含护栏，默认 True
        location: 整体偏移位置
        resample: 是否对路径进行均匀重采样（默认True，推荐开启）
    
    Returns:
        包含赛道和护栏的物体列表
    
    Example:
        # 操场形赛道（最常用）
        path = generate_stadium_path(length=40, radius=15)
        track = create_track_from_path("Stadium", path, track_width=6)
        
        # 8字形赛道
        path = generate_figure8_path(size=20, bridge_height=4)
        track = create_track_from_path("Figure8", path)
        
        # 自定义赛道
        waypoints = [(0, 0), (30, 15), (50, 0), (30, -15)]
        path = generate_custom_path(waypoints)
        track = create_track_from_path("Custom", path)
    """
    objects = []
    x, y, z = location
    
    # 可选的路径重采样（推荐开启，可显著改善急弯处的质量）
    if resample:
        # 根据赛道宽度计算合适的采样间距（约每半个赛道宽度一个点）
        path = _resample_path_uniform(path, target_spacing=track_width / 3, min_points=100)
    
    # ⭐ 关键改进：限制路径的最大转弯角度，从源头上防止边缘交叉
    path = _limit_path_curvature(path, track_width)
    
    # 偏移路径到指定位置
    offset_path = [(px + x, py + y, pz + z) for px, py, pz in path]
    
    # 创建赛道路面
    track_surface = _create_track_along_path(
        f"{name}_Surface",
        offset_path,
        track_width,
        track_thickness,
        adaptive_width=True
    )
    objects.append(track_surface)
    
    # 创建护栏
    if include_barriers:
        half_width = track_width / 2
        outer_barrier = _create_barrier_along_path(
            f"{name}_Outer_Barrier",
            offset_path,
            half_width + barrier_width / 2,
            barrier_width,
            barrier_height,
            track_thickness,
            track_half_width=half_width,
            adaptive_offset=True
        )
        objects.append(outer_barrier)
        
        inner_barrier = _create_barrier_along_path(
            f"{name}_Inner_Barrier",
            offset_path,
            -(half_width + barrier_width / 2),
            barrier_width,
            barrier_height,
            track_thickness,
            track_half_width=half_width,
            adaptive_offset=True
        )
        objects.append(inner_barrier)
    
    return objects


def _create_ellipse_ring_mesh(name: str, 
                               outer_radius_x: float, outer_radius_y: float,
                               inner_radius_x: float, inner_radius_y: float, 
                               height: float, segments: int = 64) -> bpy.types.Object:
    """
    内部函数：直接创建椭圆环形网格（无缝）
    
    使用 BMesh 直接构建几何体，确保数学上完美无缝。
    """
    import bmesh
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # 创建顶点：顶层外圈、顶层内圈、底层外圈、底层内圈
    top_outer = []
    top_inner = []
    bottom_outer = []
    bottom_inner = []
    
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        
        ox = outer_radius_x * math.cos(angle)
        oy = outer_radius_y * math.sin(angle)
        ix = inner_radius_x * math.cos(angle)
        iy = inner_radius_y * math.sin(angle)
        
        top_outer.append(bm.verts.new((ox, oy, height)))
        top_inner.append(bm.verts.new((ix, iy, height)))
        bottom_outer.append(bm.verts.new((ox, oy, 0)))
        bottom_inner.append(bm.verts.new((ix, iy, 0)))
    
    bm.verts.ensure_lookup_table()
    
    # 创建面
    for i in range(segments):
        j = (i + 1) % segments
        
        # 顶面
        bm.faces.new([top_outer[i], top_outer[j], top_inner[j], top_inner[i]])
        # 底面
        bm.faces.new([bottom_outer[i], bottom_inner[i], bottom_inner[j], bottom_outer[j]])
        # 外侧面
        bm.faces.new([bottom_outer[i], bottom_outer[j], top_outer[j], top_outer[i]])
        # 内侧面
        bm.faces.new([bottom_inner[i], top_inner[i], top_inner[j], bottom_inner[j]])
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    return obj


def create_oval_track(
    name: str,
    location: Tuple[float, float, float] = (0, 0, 0),
    outer_radius_x: float = 25.0,
    outer_radius_y: float = 15.0,
    track_width: float = 6.0,
    track_thickness: float = 0.3,
    barrier_height: float = 0.8,
    barrier_width: float = 0.15,
    include_barriers: bool = True,
    segments: int = 64
) -> List[bpy.types.Object]:
    """
    一行创建完整的椭圆形赛道
    
    包含：
    - 赛道路面（无缝椭圆环形）
    - 内外护栏（可选）
    
    Args:
        name: 赛道名称前缀
        location: 赛道中心位置 (x, y, z)
        outer_radius_x: 赛道外圈X半径（长轴），默认 25m
        outer_radius_y: 赛道外圈Y半径（短轴），默认 15m
        track_width: 赛道宽度，默认 6m
        track_thickness: 赛道厚度，默认 0.3m
        barrier_height: 护栏高度，默认 0.8m
        barrier_width: 护栏宽度，默认 0.15m
        include_barriers: 是否包含护栏，默认 True
        segments: 分段数（越多越平滑），默认 64
    
    Returns:
        包含赛道和护栏的物体列表
        
    Example:
        # 简单调用 - 一行创建完整赛道
        track = create_oval_track("KartTrack", (0, 0, 0))
        
        # 自定义尺寸
        track = create_oval_track("BigTrack", (0, 0, 0),
            outer_radius_x=50, outer_radius_y=30,
            track_width=8, barrier_height=1.0)
        
        # 只要赛道，不要护栏
        track = create_oval_track("SimpleTrack", (0, 0, 0),
            include_barriers=False)
    """
    objects = []
    x, y, z = location
    
    # 计算内圈半径
    inner_radius_x = outer_radius_x - track_width
    inner_radius_y = outer_radius_y - track_width
    
    # 1. 创建赛道路面
    track_surface = _create_ellipse_ring_mesh(
        f"{name}_Surface",
        outer_radius_x, outer_radius_y,
        inner_radius_x, inner_radius_y,
        track_thickness, segments
    )
    track_surface.location = (x, y, z)
    objects.append(track_surface)
    
    # 2. 创建护栏（如果需要）
    if include_barriers:
        # 外护栏：紧贴赛道外边缘
        outer_barrier = _create_ellipse_ring_mesh(
            f"{name}_Outer_Barrier",
            outer_radius_x + barrier_width,  # 护栏外边缘
            outer_radius_y + barrier_width,
            outer_radius_x,                   # 护栏内边缘 = 赛道外边缘
            outer_radius_y,
            barrier_height, segments
        )
        outer_barrier.location = (x, y, z + track_thickness)
        objects.append(outer_barrier)
        
        # 内护栏：紧贴赛道内边缘
        # 确保内护栏半径为正
        if inner_radius_x > barrier_width and inner_radius_y > barrier_width:
            inner_barrier = _create_ellipse_ring_mesh(
                f"{name}_Inner_Barrier",
                inner_radius_x,                   # 护栏外边缘 = 赛道内边缘
                inner_radius_y,
                inner_radius_x - barrier_width,   # 护栏内边缘
                inner_radius_y - barrier_width,
                barrier_height, segments
            )
            inner_barrier.location = (x, y, z + track_thickness)
            objects.append(inner_barrier)
    
    return objects


def create_figure8_track(
    name: str,
    location: Tuple[float, float, float] = (0, 0, 0),
    size: float = 20.0,
    track_width: float = 6.0,
    track_thickness: float = 0.3,
    bridge_height: float = 4.0,
    barrier_height: float = 0.6,
    barrier_width: float = 0.12,
    include_barriers: bool = True,
    segments: int = 96
) -> List[bpy.types.Object]:
    """
    一行创建8字形（∞形）赛道，带立交桥
    
    Args:
        name: 赛道名称前缀
        location: 赛道中心位置
        size: 整体大小（单圈半径），默认 20m
        track_width: 赛道宽度，默认 6m
        track_thickness: 赛道厚度，默认 0.3m
        bridge_height: 立交桥高度，默认 4m
        barrier_height: 护栏高度，默认 0.6m
        barrier_width: 护栏宽度，默认 0.12m
        include_barriers: 是否包含护栏，默认 True
        segments: 分段数，默认 96
    
    Returns:
        包含赛道和护栏的物体列表
    
    Example:
        # 简单调用
        track = create_figure8_track("Figure8", (0, 0, 0))
        
        # 大型赛道
        track = create_figure8_track("BigFigure8", (0, 0, 0),
            size=40, bridge_height=6)
    """
    objects = []
    x, y, z = location
    
    # 1. 生成8字形路径
    path_points = generate_figure8_path(size, bridge_height, segments)
    
    # 2. 均匀重采样
    path_points = _resample_path_uniform(path_points, target_spacing=track_width / 3, min_points=100)
    
    # 3. ⭐ 限制最大转弯角度，防止边缘交叉
    path_points = _limit_path_curvature(path_points, track_width)
    
    # 偏移到指定位置
    path_points = [(px + x, py + y, pz + z) for px, py, pz in path_points]
    
    # 4. 创建赛道路面
    track_surface = _create_track_along_path(
        f"{name}_Surface",
        path_points,
        track_width,
        track_thickness,
        adaptive_width=True
    )
    objects.append(track_surface)
    
    # 5. 创建护栏
    if include_barriers:
        half_width = track_width / 2
        outer_barrier = _create_barrier_along_path(
            f"{name}_Outer_Barrier",
            path_points,
            half_width + barrier_width / 2,
            barrier_width,
            barrier_height,
            track_thickness,
            track_half_width=half_width,
            adaptive_offset=True
        )
        objects.append(outer_barrier)
        
        inner_barrier = _create_barrier_along_path(
            f"{name}_Inner_Barrier",
            path_points,
            -(half_width + barrier_width / 2),
            barrier_width,
            barrier_height,
            track_thickness,
            track_half_width=half_width,
            adaptive_offset=True
        )
        objects.append(inner_barrier)
    
    return objects


def create_custom_track(
    name: str,
    waypoints: List[Tuple[float, float]],
    location: Tuple[float, float, float] = (0, 0, 0),
    height_profile: List[float] = None,
    track_width: float = 6.0,
    track_thickness: float = 0.3,
    barrier_height: float = 0.6,
    barrier_width: float = 0.12,
    include_barriers: bool = True,
    segments_per_section: int = 16
) -> List[bpy.types.Object]:
    """
    通过控制点创建自定义形状的赛道（Catmull-Rom 样条插值）
    
    Args:
        name: 赛道名称前缀
        waypoints: 控制点列表 [(x, y), ...]，至少3个点，会自动闭合
        location: 整体偏移位置
        height_profile: 每个控制点的高度（可选），用于创建起伏
        track_width: 赛道宽度，默认 6m
        track_thickness: 赛道厚度，默认 0.3m
        barrier_height: 护栏高度，默认 0.6m
        barrier_width: 护栏宽度，默认 0.12m
        include_barriers: 是否包含护栏，默认 True
        segments_per_section: 每段控制点之间的细分数，默认 16
    
    Returns:
        包含赛道和护栏的物体列表
    
    Example:
        # 简单三角形赛道
        waypoints = [(0, 0), (30, 20), (30, -20)]
        track = create_custom_track("Triangle", waypoints)
        
        # 复杂赛道，带高度变化
        waypoints = [(0, 0), (20, 10), (40, 0), (30, -15), (10, -10)]
        heights = [0, 2, 4, 2, 0]  # 中间抬高
        track = create_custom_track("HillTrack", waypoints, 
            height_profile=heights)
        
        # 大型赛道
        waypoints = [
            (0, 0), (30, 10), (50, 0), (60, -20),
            (40, -40), (10, -30), (-10, -10)
        ]
        track = create_custom_track("Circuit", waypoints, track_width=8)
    """
    objects = []
    x, y, z = location
    
    # 1. 生成平滑路径
    path_points = generate_custom_path(waypoints, height_profile, segments_per_section)
    
    # 2. 均匀重采样
    path_points = _resample_path_uniform(path_points, target_spacing=track_width / 3, min_points=100)
    
    # 3. ⭐ 关键：限制最大转弯角度，从源头上防止边缘交叉
    path_points = _limit_path_curvature(path_points, track_width)
    
    # 偏移到指定位置
    path_points = [(px + x, py + y, pz + z) for px, py, pz in path_points]
    
    # 4. 创建赛道路面
    track_surface = _create_track_along_path(
        f"{name}_Surface",
        path_points,
        track_width,
        track_thickness,
        adaptive_width=True
    )
    objects.append(track_surface)
    
    # 5. 创建护栏
    if include_barriers:
        half_width = track_width / 2
        outer_barrier = _create_barrier_along_path(
            f"{name}_Outer_Barrier",
            path_points,
            half_width + barrier_width / 2,
            barrier_width,
            barrier_height,
            track_thickness,
            track_half_width=half_width,
            adaptive_offset=True
        )
        objects.append(outer_barrier)
        
        inner_barrier = _create_barrier_along_path(
            f"{name}_Inner_Barrier",
            path_points,
            -(half_width + barrier_width / 2),
            barrier_width,
            barrier_height,
            track_thickness,
            track_half_width=half_width,
            adaptive_offset=True
        )
        objects.append(inner_barrier)
    
    return objects

