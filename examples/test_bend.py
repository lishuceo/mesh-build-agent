"""
测试 G_Bend 节点组 - 最简单的弯曲测试
运行方式：blender assets/node_library.blend --python examples/test_bend.py
"""

import bpy
import sys
import os
import math

# 添加 src 到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def clear_scene():
    """清理场景"""
    for obj in list(bpy.data.objects):
        if obj.type == 'MESH':
            bpy.data.objects.remove(obj, do_unlink=True)


def test_bend_with_subdivided_cube():
    """测试1：用细分过的立方体测试弯曲"""
    print("\n" + "="*60)
    print("测试1：细分立方体 + G_Bend")
    print("="*60)

    # 创建立方体
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.name = "Test_Bend_Cube"
    obj.scale = (0.25, 0.25, 3.0)  # 细长的立方体
    bpy.ops.object.transform_apply(scale=True)

    # 细分（关键！）- 沿 Z 轴增加顶点
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=20)  # 20次细分
    bpy.ops.object.mode_set(mode='OBJECT')

    print(f"  顶点数: {len(obj.data.vertices)}")

    # 添加几何节点修改器
    mod = obj.modifiers.new(name="GNodes", type='NODES')

    # 创建节点树
    node_tree = bpy.data.node_groups.new(name="Test_Bend_Tree", type='GeometryNodeTree')
    mod.node_group = node_tree

    nodes = node_tree.nodes
    links = node_tree.links

    # 输入输出
    input_node = nodes.new('NodeGroupInput')
    output_node = nodes.new('NodeGroupOutput')
    input_node.location = (-400, 0)
    output_node.location = (400, 0)

    # 添加接口
    node_tree.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    node_tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # 添加 G_Bend 节点组
    if "G_Bend" not in bpy.data.node_groups:
        print("  ❌ 错误：G_Bend 节点组不存在！")
        print("  请先运行：blender --background --python scripts/create_node_library.py")
        return None

    bend_node = nodes.new(type='GeometryNodeGroup')
    bend_node.node_tree = bpy.data.node_groups["G_Bend"]
    bend_node.location = (0, 0)
    bend_node.inputs["Angle"].default_value = math.pi / 2  # 90度弯曲

    # 连接
    links.new(input_node.outputs['Geometry'], bend_node.inputs['Geometry'])
    links.new(bend_node.outputs['Geometry'], output_node.inputs['Geometry'])

    obj.location = (-2, 0, 0)
    print(f"  ✓ 创建完成，位置：(-2, 0, 0)")
    print(f"  预期效果：应该弯曲成 90° 圆弧")

    return obj


def test_bend_with_cylinder():
    """测试2：用高分辨率圆柱测试弯曲"""
    print("\n" + "="*60)
    print("测试2：高分辨率圆柱 + G_Bend")
    print("="*60)

    # 创建圆柱（沿 Z 轴有很多段）
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.15,
        depth=3.0,
        vertices=16,
        end_fill_type='NGON'
    )
    obj = bpy.context.object
    obj.name = "Test_Bend_Cylinder"

    # 细分
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=30)
    bpy.ops.object.mode_set(mode='OBJECT')

    print(f"  顶点数: {len(obj.data.vertices)}")

    # 添加几何节点修改器
    mod = obj.modifiers.new(name="GNodes", type='NODES')

    # 创建节点树
    node_tree = bpy.data.node_groups.new(name="Test_Bend_Cylinder_Tree", type='GeometryNodeTree')
    mod.node_group = node_tree

    nodes = node_tree.nodes
    links = node_tree.links

    input_node = nodes.new('NodeGroupInput')
    output_node = nodes.new('NodeGroupOutput')
    input_node.location = (-400, 0)
    output_node.location = (400, 0)

    node_tree.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    node_tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    bend_node = nodes.new(type='GeometryNodeGroup')
    bend_node.node_tree = bpy.data.node_groups["G_Bend"]
    bend_node.location = (0, 0)
    bend_node.inputs["Angle"].default_value = math.pi / 2  # 90度

    links.new(input_node.outputs['Geometry'], bend_node.inputs['Geometry'])
    links.new(bend_node.outputs['Geometry'], output_node.inputs['Geometry'])

    obj.location = (2, 0, 0)
    print(f"  ✓ 创建完成，位置：(2, 0, 0)")

    return obj


def test_no_bend_reference():
    """测试3：参考物体（不弯曲）"""
    print("\n" + "="*60)
    print("测试3：参考物体（无弯曲，用于对比）")
    print("="*60)

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.15,
        depth=3.0,
        vertices=16
    )
    obj = bpy.context.object
    obj.name = "Reference_No_Bend"
    obj.location = (0, 3, 1.5)  # 放在后面作为参考

    print(f"  ✓ 参考物体，位置：(0, 3, 1.5)")
    return obj


def setup_camera():
    """设置相机"""
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
    else:
        bpy.ops.object.camera_add()
        cam = bpy.context.object

    cam.location = (0, -8, 4)
    cam.rotation_euler = (1.1, 0, 0)
    bpy.context.scene.camera = cam


def main():
    print("\n" + "="*60)
    print("🧪 G_Bend 弯曲测试")
    print("="*60)

    clear_scene()

    # 检查 G_Bend 是否存在
    if "G_Bend" not in bpy.data.node_groups:
        print("\n❌ 错误：G_Bend 节点组不存在！")
        print("请先运行：")
        print("  blender --background --python scripts/create_node_library.py")
        return

    print(f"\n✓ 找到 G_Bend 节点组")

    # 运行测试
    test_bend_with_subdivided_cube()
    test_bend_with_cylinder()
    test_no_bend_reference()

    setup_camera()

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n观察结果：")
    print("  • 左边 (-2,0,0)：细分立方体，应该弯曲成弧形")
    print("  • 右边 (2,0,0)：细分圆柱，应该弯曲成弧形")
    print("  • 后面 (0,3,1.5)：参考直立圆柱（对比用）")
    print("\n如果左右两个物体还是直的，说明 G_Bend 节点组有 bug")


if __name__ == "__main__":
    main()
