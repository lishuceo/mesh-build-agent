"""
变形节点组验证脚本
通过检查边界框和顶点位置，验证变形是否正确

使用方法：
blender assets/node_library.blend --python scripts/verify_deformations.py
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


def get_bbox_info(obj):
    """获取物体的边界框信息"""
    # 应用修改器获取实际几何体
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()
    
    if len(mesh.vertices) == 0:
        return None
    
    # 计算边界框
    verts = [obj.matrix_world @ v.co for v in mesh.vertices]
    xs = [v.x for v in verts]
    ys = [v.y for v in verts]
    zs = [v.z for v in verts]
    
    obj_eval.to_mesh_clear()
    
    return {
        "min": (min(xs), min(ys), min(zs)),
        "max": (max(xs), max(ys), max(zs)),
        "size": (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)),
        "num_verts": len(verts)
    }


def verify_taper():
    """验证 G_Taper"""
    print("\n" + "="*60)
    print("测试 G_Taper（锥形变形）")
    print("="*60)
    
    # 创建标准立方体
    builder1 = GNodesBuilder("Ref_Cube")
    builder1.add_node_group("G_Base_Cube", inputs={"Size": (1.0, 1.0, 2.0)})
    builder1.add_node_group("G_Align_Ground")
    builder1.finalize()
    ref = builder1.get_object()
    ref_info = get_bbox_info(ref)
    
    # 创建带Taper的立方体
    builder2 = GNodesBuilder("Taper_Cube")
    builder2.add_node_group("G_Base_Cube", inputs={"Size": (1.0, 1.0, 2.0)})
    builder2.add_node_group("G_Taper", inputs={"Factor": 0.5})  # 顶部收窄50%
    builder2.add_node_group("G_Align_Ground")
    builder2.finalize()
    taper = builder2.get_object()
    taper.location = (2, 0, 0)
    taper_info = get_bbox_info(taper)
    
    print(f"参考立方体：{ref_info['size']}")
    print(f"Taper立方体：{taper_info['size']}")
    print(f"顶部尺寸应该 ≈ 底部 * (1-Factor)")
    
    # 检查：底部应该是1.0，顶部应该是0.5
    if taper_info['size'][0] < ref_info['size'][0]:
        print("✅ Taper效果正确：顶部确实比底部小")
    else:
        print("❌ Taper效果错误：顶部没有收窄")
    
    # 清理
    bpy.data.objects.remove(ref, do_unlink=True)
    bpy.data.objects.remove(taper, do_unlink=True)


def verify_shear():
    """验证 G_Shear"""
    print("\n" + "="*60)
    print("测试 G_Shear（剪切变形）")
    print("="*60)
    
    builder = GNodesBuilder("Shear_Cube")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (0.5, 0.5, 2.0)})
    builder.add_node_group("G_Shear", inputs={"Amount": 0.5})
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    shear = builder.get_object()
    info = get_bbox_info(shear)
    
    print(f"尺寸：{info['size']}")
    print(f"最小Z：{info['min'][2]:.3f}")
    print(f"最大Z：{info['max'][2]:.3f}")
    
    # 剪切后，顶部应该向X正方向偏移
    # 检查最大X是否大于原始尺寸
    if info['size'][0] > 1.0:  # 原始宽度0.5，剪切后X方向应该扩大
        print("✅ Shear效果正确：顶部向前偏移")
    else:
        print("⚠️ Shear效果可能不明显或有问题")
    
    bpy.data.objects.remove(shear, do_unlink=True)


def verify_bend():
    """验证 G_Bend - 重点检查"""
    print("\n" + "="*60)
    print("测试 G_Bend（弯曲变形）")
    print("="*60)
    
    builder = GNodesBuilder("Bend_Test")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (0.2, 0.2, 2.0)})
    builder.add_node_group("G_Bend", inputs={"Angle": math.pi / 2})  # 90度
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    bend = builder.get_object()
    info = get_bbox_info(bend)
    
    print(f"原始尺寸应该：(0.2, 0.2, 2.0)")
    print(f"弯曲后边界框：{info['size']}")
    print(f"Min: {info['min']}")
    print(f"Max: {info['max']}")
    
    # 弯曲90度后，应该：
    # - 底部在原点
    # - 顶部向X正方向偏移
    # - X方向扩展
    
    print("\n预期检查：")
    print(f"1. Min Z应该 ≈ 0: {info['min'][2]:.3f} {'✅' if abs(info['min'][2]) < 0.01 else '❌'}")
    print(f"2. X方向应该扩大: {info['size'][0]:.3f} {'✅' if info['size'][0] > 0.5 else '❌'}")
    print(f"3. Z方向应该变小: {info['size'][2]:.3f} {'✅' if info['size'][2] < 2.0 else '❌'}")
    
    # 计算弯曲半径 (理论上 radius = height / angle = 2.0 / (π/2) ≈ 1.27)
    expected_radius = 2.0 / (math.pi / 2)
    print(f"\n理论弯曲半径: {expected_radius:.3f}m")
    print(f"实际X扩展: {info['max'][0]:.3f}m")
    
    if abs(info['max'][0] - expected_radius) < 0.3:
        print("✅ G_Bend 实现基本正确")
    else:
        print("❌ G_Bend 实现有问题")
    
    bpy.data.objects.remove(bend, do_unlink=True)


def verify_twist():
    """验证 G_Twist"""
    print("\n" + "="*60)
    print("测试 G_Twist（扭曲变形）")
    print("="*60)
    
    builder = GNodesBuilder("Twist_Test")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (0.5, 0.5, 2.0)})
    builder.add_node_group("G_Twist", inputs={"Angle": math.pi})  # 180度
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    twist = builder.get_object()
    info = get_bbox_info(twist)
    
    print(f"尺寸：{info['size']}")
    
    # 扭曲后，底面和顶面旋转180度
    # XY方向的边界框应该扩大
    if info['size'][0] > 0.6 or info['size'][1] > 0.6:
        print("✅ Twist效果正确：XY方向扩大（顶点旋转）")
    else:
        print("❌ Twist效果可能有问题")
    
    bpy.data.objects.remove(twist, do_unlink=True)


def main():
    print("\n" + "="*60)
    print("🔍 变形节点组验证测试")
    print("="*60)
    
    verify_taper()
    verify_shear()
    verify_bend()
    verify_twist()
    
    print("\n" + "="*60)
    print("✅ 验证完成")
    print("="*60)


if __name__ == "__main__":
    main()

