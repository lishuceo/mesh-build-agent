"""
新API演示 - 语义化空间API和组合模板

展示如何用新的API避免空间推理错误

使用方法：
blender assets/node_library.blend --python examples/new_api_demo.py
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

from gnodes_builder import (
    GNodesBuilder, 
    create_chair,
    create_table_with_chairs,
    create_fence,
    create_door_frame
)


def clear_scene():
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)


def demo_face_towards():
    """演示：face_towards API"""
    print("\n👀 演示 face_towards() - 让物体朝向目标")
    
    # 创建一个箭头形状（用细长的立方体表示）
    builder = GNodesBuilder("Arrow_01")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (1.0, 0.1, 0.1),  # 细长形，X轴是"箭头"方向
        "Bevel": 0.02
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    # 放在某个位置
    builder.set_location(-2, 2, 0.5)
    
    # 让它朝向原点 - 一行搞定，不用算角度！
    builder.face_towards(0, 0)
    
    print("   ✓ 箭头自动朝向 (0, 0)")
    return builder.get_object()


def demo_face_away_from():
    """演示：face_away_from API"""
    print("\n🔙 演示 face_away_from() - 让物体背对目标")
    
    # 创建一个"椅子"（简化版，只有靠背）
    builder = GNodesBuilder("Chair_Simple")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (0.4, 0.4, 0.05),  # 座面
        "Bevel": 0.02
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    builder.set_location(2, 2, 0.4)
    
    # 背对原点（人坐下后面向原点）- 一行搞定！
    builder.face_away_from(0, 0)
    
    print("   ✓ 椅子背对 (0, 0)，人坐下后面向 (0, 0)")
    return builder.get_object()


def demo_align_tangent():
    """演示：align_tangent_to_circle API"""
    print("\n🔄 演示 align_tangent_to_circle() - 对齐到圆的切线")
    
    # 在圆周上放置一个长条，让它沿切线方向
    radius = 1.5
    angle = math.pi / 4  # 45度
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    
    builder = GNodesBuilder("Tangent_Bar")
    builder.add_node_group("G_Base_Cube", inputs={
        "Size": (0.5, 0.05, 0.05),
        "Bevel": 0.01
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    builder.set_location(x, y, 0.5)
    
    # 自动对齐到切线方向 - 完美！
    builder.align_tangent_to_circle(0, 0)
    
    print(f"   ✓ 长条自动对齐到圆心 (0, 0) 的切线方向")
    return builder.get_object()


def demo_combined_template_chair():
    """演示：create_chair 组合模板"""
    print("\n🪑 演示 create_chair() 模板")
    
    # 之前：需要手动创建座面、靠背，手动计算位置和角度
    # 现在：一行代码搞定！
    
    objects = create_chair(
        name="Chair_Demo",
        location=(-2, -2, 0),
        face_direction=math.pi / 4,  # 朝向东北方向
        seat_size=(0.4, 0.4),
        back_height=0.5
    )
    
    print(f"   ✓ 创建了 {len(objects)} 个部件（座面+靠背）")
    print(f"   ✓ 空间关系由模板自动处理")
    return objects


def demo_combined_template_table():
    """演示：create_table_with_chairs 组合模板"""
    print("\n🍽️ 演示 create_table_with_chairs() 模板")
    
    # 一行代码创建整套餐桌！
    objects = create_table_with_chairs(
        name="DiningSet",
        location=(2, -2, 0.7),
        table_radius=0.5,
        num_chairs=3,
        chair_distance=0.9
    )
    
    print(f"   ✓ 创建了 {len(objects)} 个部件")
    print(f"   ✓ 1张桌子 + 3把椅子，环形排列自动处理")
    return objects


def demo_combined_template_fence():
    """演示：create_fence 组合模板"""
    print("\n🚧 演示 create_fence() 模板")
    
    # 创建一段斜向的栅栏
    objects = create_fence(
        name="Fence_Diagonal",
        start_pos=(3, 1),
        end_pos=(5, 3),
        num_posts=6
    )
    
    print(f"   ✓ 创建了 {len(objects)} 个部件")
    print(f"   ✓ 栅栏角度自动计算")
    return objects


def demo_combined_template_door():
    """演示：create_door_frame 组合模板"""
    print("\n🚪 演示 create_door_frame() 模板")
    
    objects = create_door_frame(
        name="MainDoor",
        location=(0, 3, 0),
        width=1.0,
        height=2.1
    )
    
    print(f"   ✓ 创建了 {len(objects)} 个部件（左柱+右柱+门楣）")
    return objects


def create_ground():
    """地面"""
    builder = GNodesBuilder("Ground")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (12, 10, 0.01)})
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    g = builder.get_object()
    g.location = (0, 0, 0)
    return g


def setup_scene():
    """相机和灯光"""
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
    else:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
    
    cam.location = (8, -8, 6)
    cam.rotation_euler = (1.0, 0, 0.8)
    bpy.context.scene.camera = cam
    
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    sun = bpy.context.object
    sun.data.energy = 3


def main():
    print("\n" + "="*70)
    print("🎯 新API演示 - 语义化空间API + 组合模板")
    print("="*70)
    print("\n目标：消除空间推理错误，让代码更易读")
    
    clear_scene()
    
    objects = []
    
    objects.append(create_ground())
    
    # 语义化API演示
    objects.append(demo_face_towards())
    objects.append(demo_face_away_from())
    objects.append(demo_align_tangent())
    
    # 组合模板演示
    objects.extend(demo_combined_template_chair())
    objects.extend(demo_combined_template_table())
    objects.extend(demo_combined_template_fence())
    objects.extend(demo_combined_template_door())
    
    setup_scene()
    
    total = len([o for o in objects if o])
    
    print("\n" + "="*70)
    print(f"✅ 演示完成！共 {total} 个物体")
    print("="*70)
    print("\n改进总结：")
    print("  1. face_towards()        - 自动朝向目标，无需算角度")
    print("  2. face_away_from()      - 自动背对目标（椅子场景）")
    print("  3. align_tangent_to_circle() - 自动对齐切线")
    print("  4. create_chair()        - 椅子组合，2部件自动组装")
    print("  5. create_table_with_chairs() - 整套餐桌，环形阵列自动")
    print("  6. create_fence()        - 栅栏组合，角度自动")
    print("  7. create_door_frame()   - 门框组合，3部件自动")
    
    if bpy.app.background:
        out = os.path.join(project_root, "assets", "new_api_demo.blend")
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print(f"\n💾 保存: {out}")


if __name__ == "__main__":
    main()

