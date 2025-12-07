"""
最简单的 G_Bend 测试
只创建一个弯曲的长条，看看效果
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


# 清理场景
if "Cube" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)

# 测试1：不弯曲（angle=0）
print("\n测试1：angle=0（不弯曲）")
builder1 = GNodesBuilder("NoBend")
builder1.add_node_group("G_Base_Cube", inputs={"Size": (0.2, 0.2, 2.0)})
builder1.add_node_group("G_Bend", inputs={"Angle": 0.0})
builder1.add_node_group("G_Align_Ground")
builder1.finalize()
obj1 = builder1.get_object()
obj1.location = (-2, 0, 0)

# 测试2：小角度弯曲（30度）
print("\n测试2：angle=π/6（30度弯曲）")
builder2 = GNodesBuilder("SmallBend")
builder2.add_node_group("G_Base_Cube", inputs={"Size": (0.2, 0.2, 2.0)})
builder2.add_node_group("G_Bend", inputs={"Angle": math.pi / 6})
builder2.add_node_group("G_Align_Ground")
builder2.finalize()
obj2 = builder2.get_object()
obj2.location = (0, 0, 0)

# 测试3：90度弯曲
print("\n测试3：angle=π/2（90度弯曲）")
builder3 = GNodesBuilder("BigBend")
builder3.add_node_group("G_Base_Cube", inputs={"Size": (0.2, 0.2, 2.0)})
builder3.add_node_group("G_Bend", inputs={"Angle": math.pi / 2})
builder3.add_node_group("G_Align_Ground")
builder3.finalize()
obj3 = builder3.get_object()
obj3.location = (2, 0, 0)

# 设置相机
if "Camera" not in bpy.data.objects:
    bpy.ops.object.camera_add()
cam = bpy.data.objects["Camera"]
cam.location = (0, -5, 2)
cam.rotation_euler = (1.3, 0, 0)

# 灯光
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)
bpy.ops.object.light_add(type='SUN')
sun = bpy.context.object
sun.data.energy = 3

print("\n✅ 创建完成")
print("从左到右：0度、30度、90度")
print("预期：直杆 → 微弯 → 90度圆弧")

if bpy.app.background:
    out = os.path.join(project_root, "assets", "test_bend_simple.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out)
    print(f"保存: {out}")

