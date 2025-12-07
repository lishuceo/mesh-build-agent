"""
变形节点组测试脚本
单独测试每个变形节点组的效果

使用方法：
blender assets/node_library.blend --python tests/test_deformations.py
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

from gnodes_builder import GNodesBuilder


def clear_scene():
    for obj in list(bpy.data.objects):
        if obj.type == 'MESH' and obj.name != "Camera":
            bpy.data.objects.remove(obj, do_unlink=True)


def test_taper():
    """测试 G_Taper"""
    print("\n🧪 测试 G_Taper...")
    
    builder = GNodesBuilder("Test_Taper")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (0.5, 0.5, 2.0)})
    builder.add_node_group("G_Taper", inputs={"Factor": 0.5})
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    obj = builder.get_object()
    obj.location = (0, 0, 0)
    print("   预期：立方体顶部收窄50%")


def test_shear():
    """测试 G_Shear"""
    print("\n🧪 测试 G_Shear...")
    
    builder = GNodesBuilder("Test_Shear")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (0.5, 0.5, 2.0)})
    builder.add_node_group("G_Shear", inputs={"Amount": 0.5})
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    obj = builder.get_object()
    obj.location = (1.5, 0, 0)
    print("   预期：立方体向前倾斜")


def test_smooth():
    """测试 G_Smooth"""
    print("\n🧪 测试 G_Smooth...")
    
    builder = GNodesBuilder("Test_Smooth")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (0.5, 0.5, 0.5)})
    builder.add_node_group("G_Smooth", inputs={"Level": 2})
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    obj = builder.get_object()
    obj.location = (3, 0, 0)
    print("   预期：立方体变圆润")


def test_bend():
    """测试 G_Bend"""
    print("\n🧪 测试 G_Bend...")
    
    builder = GNodesBuilder("Test_Bend")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (0.3, 0.3, 3.0)})
    builder.add_node_group("G_Bend", inputs={"Angle": math.pi / 2})  # 90度
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    obj = builder.get_object()
    obj.location = (0, 2, 0)
    print("   预期：长条向前弯曲成90度弧")


def test_twist():
    """测试 G_Twist"""
    print("\n🧪 测试 G_Twist...")
    
    builder = GNodesBuilder("Test_Twist")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (0.5, 0.5, 2.0)})
    builder.add_node_group("G_Twist", inputs={"Angle": math.pi})  # 180度
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    obj = builder.get_object()
    obj.location = (1.5, 2, 0)
    print("   预期：立方体扭曲180度")


def test_pipe():
    """测试 G_Pipe"""
    print("\n🧪 测试 G_Pipe...")
    
    builder = GNodesBuilder("Test_Pipe")
    builder.add_node_group("G_Pipe", inputs={
        "Radius": 0.1,
        "Length": 2.0,
        "Resolution": 12
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    obj = builder.get_object()
    obj.location = (3, 2, 0)
    print("   预期：圆柱管道")


def create_ground():
    """地面参考"""
    builder = GNodesBuilder("Ground")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (8, 6, 0.01)})
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    builder.get_object().location = (2, 1, 0)


def setup_camera():
    """设置相机"""
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
    else:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
    
    cam.location = (6, -6, 4)
    cam.rotation_euler = (1.1, 0, 0.7)
    bpy.context.scene.camera = cam


def setup_lighting():
    """灯光"""
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    sun = bpy.context.object
    sun.data.energy = 3


def main():
    print("\n" + "="*60)
    print("🧪 变形节点组测试")
    print("="*60)
    
    clear_scene()
    
    create_ground()
    
    # 测试每个变形节点组
    test_taper()
    test_shear()
    test_smooth()
    test_bend()
    test_twist()
    test_pipe()
    
    setup_camera()
    setup_lighting()
    
    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)
    print("\n布局（俯视图）：")
    print("  前排：Taper  Shear  Smooth")
    print("  后排：Bend   Twist  Pipe")
    print("\n请在Blender中检查每个物体的形状是否正确")
    
    if bpy.app.background:
        out = os.path.join(project_root, "assets", "test_deformations.blend")
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print(f"\n💾 保存: {out}")


if __name__ == "__main__":
    main()

