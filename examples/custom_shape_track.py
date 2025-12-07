"""
自定义形状赛道示例
==================

根据用户提供的图片生成类似飞机/恐龙轮廓的复杂赛道。

特点：
- 复杂的不规则闭环形状
- 多个突起和弯道
- 平滑的曲线过渡

使用方法：
blender assets/node_library.blend --python examples/custom_shape_track.py

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

from gnodes_builder import create_custom_track, generate_custom_path, create_track_from_path


# ============ 配置参数 ============
TRACK_WIDTH = 6.0           # 赛道宽度
TRACK_THICKNESS = 0.3       # 路面厚度
BARRIER_HEIGHT = 0.6        # 护栏高度


# ============ 核心：自定义赛道形状 ============
def build_custom_shape_track():
    """
    构建自定义形状的赛道
    
    根据图片分析，赛道形状类似一个飞机/恐龙的轮廓：
    - 左边有一个"头部"状的大突起
    - 上方有两个"翅膀"状的突起  
    - 右边延伸向下有波浪形的"尾巴"
    - 下方有"腿"状的突起
    """
    
    # 定义控制点（按顺时针方向）
    # 坐标单位为米，整体尺寸约 120m x 80m
    waypoints = [
        # 左边起点（身体左侧中部）
        (-50, 0),
        
        # 向左上方延伸（头部区域）
        (-55, 10),
        (-45, 20),
        (-35, 25),
        
        # 上方第一个突起（左翅膀）
        (-25, 20),
        (-15, 35),
        (-5, 30),
        
        # 上方第二个突起（右翅膀）
        (5, 25),
        (20, 40),
        (35, 35),
        (40, 25),
        
        # 右上方小突起
        (45, 20),
        (55, 25),
        (60, 15),
        
        # 右边向下延伸（尾巴开始）
        (55, 5),
        (50, -5),
        
        # 下方波浪形区域（尾巴主体）
        (40, -8),
        (30, -15),
        (25, -10),
        (15, -20),
        (5, -15),
        
        # 下方突起（后腿）
        (-5, -25),
        (-15, -35),
        (-25, -30),
        
        # 左下方突起（前腿）
        (-35, -25),
        (-45, -35),
        (-55, -25),
        
        # 回到起点方向
        (-55, -10),
    ]
    
    print("🏎️ 开始构建自定义形状赛道...")
    print(f"   控制点数量: {len(waypoints)}")
    
    # 使用 create_custom_track 一行创建完整赛道
    track_objects = create_custom_track(
        name="CustomShape",
        waypoints=waypoints,
        location=(0, 0, 0),
        track_width=TRACK_WIDTH,
        track_thickness=TRACK_THICKNESS,
        barrier_height=BARRIER_HEIGHT,
        include_barriers=True,
        segments_per_section=16  # 每段细分16个点，保证平滑
    )
    
    print(f"✅ 赛道构建完成！共 {len(track_objects)} 个部件")
    print(f"   赛道宽度: {TRACK_WIDTH}m")
    print(f"   预估尺寸: 约 120m x 80m")
    
    return track_objects


def build_refined_track():
    """
    更精确地还原图片中的赛道形状
    
    通过更多的控制点来模拟图片中的曲线细节
    """
    
    # 更详细的控制点，尝试更准确地还原图片形状
    waypoints = [
        # 左边"脖子"区域（从下往上）
        (-55, -5),
        (-58, 5),
        (-55, 15),
        
        # "头部"突起
        (-48, 22),
        (-38, 28),
        (-28, 25),
        
        # 上方"背部"向右延伸
        (-20, 20),
        (-10, 18),
        
        # 第一个"翅膀"突起
        (-5, 25),
        (5, 32),
        (15, 28),
        
        # 第二个大"翅膀"突起
        (22, 22),
        (30, 35),
        (40, 32),
        (48, 22),
        
        # 右上方小突起
        (52, 18),
        (58, 22),
        (62, 15),
        (58, 8),
        
        # 右边"尾巴"向下延伸
        (52, 0),
        (48, -8),
        
        # 下方波浪形"尾巴"（多个弯曲）
        (42, -5),
        (35, -12),
        (28, -8),
        (22, -15),
        (15, -10),
        (8, -18),
        (0, -12),
        
        # 下方"后腿"突起
        (-8, -20),
        (-15, -30),
        (-22, -28),
        (-28, -20),
        
        # 下方"前腿"突起
        (-35, -22),
        (-42, -32),
        (-50, -28),
        (-55, -20),
        
        # 回到起点区域
        (-58, -12),
    ]
    
    print("🏎️ 开始构建精细版自定义赛道...")
    print(f"   控制点数量: {len(waypoints)}")
    
    # 创建赛道
    track_objects = create_custom_track(
        name="RefinedTrack",
        waypoints=waypoints,
        location=(0, 0, 0),
        track_width=TRACK_WIDTH,
        track_thickness=TRACK_THICKNESS,
        barrier_height=BARRIER_HEIGHT,
        include_barriers=True,
        segments_per_section=12
    )
    
    print(f"✅ 精细版赛道构建完成！共 {len(track_objects)} 个部件")
    
    return track_objects


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
    
    # 俯瞰整个赛道
    cam.location = (0, -80, 100)
    cam.rotation_euler = (0.7, 0, 0)
    bpy.context.scene.camera = cam


def setup_lighting():
    """设置灯光"""
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    bpy.ops.object.light_add(type='SUN', location=(20, -20, 50))
    sun = bpy.context.object
    sun.data.energy = 3
    sun.rotation_euler = (0.6, 0.2, 0.3)


# ============ 主函数 ============
def main():
    print("\n" + "=" * 60)
    print("🏎️ 自定义形状赛道")
    print("=" * 60)
    print("\n特点：")
    print("  • 根据用户图片生成的复杂闭环赛道")
    print("  • 类似飞机/恐龙轮廓的不规则形状")
    print("  • 使用 Catmull-Rom 样条插值实现平滑曲线")
    print()
    
    clear_scene()
    
    # 可以选择使用哪个版本的赛道
    # build_custom_shape_track()  # 简化版
    build_refined_track()  # 精细版
    
    setup_camera()
    setup_lighting()
    
    print("\n" + "=" * 60)
    print("✅ 赛道构建完成！")
    print("=" * 60)
    
    if bpy.app.background:
        out = os.path.join(project_root, "assets", "custom_shape_track.blend")
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print(f"\n💾 保存到: {out}")


if __name__ == "__main__":
    main()

