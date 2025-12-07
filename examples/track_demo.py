"""
赛道 API 演示
==============

展示三种赛道生成方式，每种只需一行代码！

使用方法：
blender assets/node_library.blend --python examples/track_demo.py

作者: AI Agent
"""

import bpy
import sys
import os

# 添加项目路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from gnodes_builder import create_oval_track, create_figure8_track, create_custom_track


def clear_scene():
    for obj in list(bpy.data.objects):
        if obj.type in ('MESH', 'CURVE'):
            bpy.data.objects.remove(obj, do_unlink=True)


def setup_camera():
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
    else:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
    cam.location = (0, -120, 80)
    cam.rotation_euler = (0.9, 0, 0)
    bpy.context.scene.camera = cam


def main():
    print("\n" + "=" * 60)
    print("🏎️ 赛道 API 演示 - 三种赛道，每种一行代码！")
    print("=" * 60)
    
    clear_scene()
    
    # ============ 赛道1：椭圆形 ============
    print("\n📍 创建椭圆形赛道...")
    create_oval_track("Oval", location=(-60, 0, 0),
        outer_radius_x=20, outer_radius_y=12, track_width=5)
    
    # ============ 赛道2：8字形 ============
    print("📍 创建8字形赛道（带立交桥）...")
    create_figure8_track("Figure8", location=(60, 0, 0),
        size=15, bridge_height=3)
    
    # ============ 赛道3：自定义形状 ============
    print("📍 创建自定义形状赛道...")
    waypoints = [
        (0, 30), (15, 35), (25, 25), (30, 10),
        (25, -5), (10, -10), (-10, -5), (-15, 10),
        (-10, 25)
    ]
    heights = [0, 1, 2, 3, 2, 1, 0, 0, 0]  # 有高度起伏
    create_custom_track("Custom", waypoints, location=(0, -60, 0),
        height_profile=heights, track_width=5)
    
    setup_camera()
    
    print("\n" + "=" * 60)
    print("✅ 三种赛道创建完成！")
    print("=" * 60)
    print("\n核心代码：")
    print("  create_oval_track('Oval', ...)")
    print("  create_figure8_track('Figure8', ...)")
    print("  create_custom_track('Custom', waypoints, ...)")
    
    if bpy.app.background:
        out = os.path.join(project_root, "assets", "track_demo.blend")
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print(f"\n💾 保存到: {out}")


if __name__ == "__main__":
    main()

