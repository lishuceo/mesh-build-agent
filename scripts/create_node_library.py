"""
节点组库自动生成脚本
在 Blender 中运行此脚本，自动创建所有预定义的节点组并保存为库文件

使用方法：
1. 打开 Blender
2. 切换到 Scripting 工作区
3. 打开此脚本
4. 点击运行（或按 Alt+P）
5. 库文件将保存到脚本所在目录

或者通过命令行运行：
blender --background --python create_node_library.py
"""

import bpy
import os
from mathutils import Vector


class NodeGroupFactory:
    """节点组工厂类，用于创建各种预制节点组"""
    
    @staticmethod
    def clear_existing_groups(prefix: str = "G_"):
        """清除已存在的节点组（可选）"""
        groups_to_remove = [g for g in bpy.data.node_groups if g.name.startswith(prefix)]
        for group in groups_to_remove:
            bpy.data.node_groups.remove(group)
        print(f"✓ 已清除 {len(groups_to_remove)} 个旧节点组")
    
    @staticmethod
    def create_node_group(name: str) -> bpy.types.NodeTree:
        """创建基础节点组框架"""
        # 如果已存在，先删除
        if name in bpy.data.node_groups:
            bpy.data.node_groups.remove(bpy.data.node_groups[name])
        
        # 创建新节点组
        node_group = bpy.data.node_groups.new(name=name, type='GeometryNodeTree')
        node_group.use_fake_user = True  # 防止被清除
        
        # 创建输入输出节点
        nodes = node_group.nodes
        input_node = nodes.new('NodeGroupInput')
        output_node = nodes.new('NodeGroupOutput')
        input_node.location = (-400, 0)
        output_node.location = (600, 0)
        
        return node_group
    
    @staticmethod
    def add_geometry_interface(node_group: bpy.types.NodeTree, 
                               has_input: bool = True, 
                               has_output: bool = True):
        """添加几何体输入输出接口"""
        if has_input:
            node_group.interface.new_socket(
                name="Geometry", 
                in_out='INPUT', 
                socket_type='NodeSocketGeometry'
            )
        if has_output:
            node_group.interface.new_socket(
                name="Geometry", 
                in_out='OUTPUT', 
                socket_type='NodeSocketGeometry'
            )


# ========== 节点组创建函数 ==========

def create_g_base_cube() -> bpy.types.NodeTree:
    """
    创建 G_Base_Cube 节点组
    功能：生成标准倒角立方体，原点在底部中心
    """
    ng = NodeGroupFactory.create_node_group("G_Base_Cube")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    size_socket = ng.interface.new_socket(name="Size", in_out='INPUT', socket_type='NodeSocketVector')
    size_socket.default_value = (1.0, 1.0, 1.0)
    
    bevel_socket = ng.interface.new_socket(name="Bevel", in_out='INPUT', socket_type='NodeSocketFloat')
    bevel_socket.default_value = 0.0
    bevel_socket.min_value = 0.0
    bevel_socket.max_value = 1.0
    
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 创建 Mesh Cube 节点
    cube_node = nodes.new(type='GeometryNodeMeshCube')
    cube_node.location = (0, 0)
    cube_node.label = "Base Cube"
    
    # 创建 Bevel 节点（边缘倒角）
    # 注意：Geometry Nodes 中没有直接的 Bevel Edges，使用 Subdivision + smooth 替代
    # 或者使用 Dual Mesh 等方法，这里简化为直接输出
    # 实际生产环境可以添加更复杂的倒角逻辑
    
    # 创建 Transform 节点 - 用于将原点移到底部
    transform_node = nodes.new(type='GeometryNodeTransform')
    transform_node.location = (200, 0)
    transform_node.label = "Move to Bottom"
    
    # 创建数学节点 - 计算 Z 偏移 (Size.Z / 2)
    separate_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    separate_xyz.location = (-200, -200)
    
    math_div = nodes.new(type='ShaderNodeMath')
    math_div.operation = 'DIVIDE'
    math_div.location = (0, -200)
    math_div.inputs[1].default_value = 2.0
    
    combine_xyz = nodes.new(type='ShaderNodeCombineXYZ')
    combine_xyz.location = (200, -200)
    
    # 连接节点
    links.new(input_node.outputs['Size'], cube_node.inputs['Size'])
    links.new(cube_node.outputs['Mesh'], transform_node.inputs['Geometry'])
    
    # 计算底部偏移
    links.new(input_node.outputs['Size'], separate_xyz.inputs['Vector'])
    links.new(separate_xyz.outputs['Z'], math_div.inputs[0])
    links.new(math_div.outputs['Value'], combine_xyz.inputs['Z'])
    links.new(combine_xyz.outputs['Vector'], transform_node.inputs['Translation'])
    
    # 输出
    links.new(transform_node.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Base_Cube")
    return ng


def create_g_base_cylinder() -> bpy.types.NodeTree:
    """
    创建 G_Base_Cylinder 节点组
    功能：生成标准圆柱，原点在底部中心
    """
    ng = NodeGroupFactory.create_node_group("G_Base_Cylinder")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    radius_socket = ng.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    radius_socket.default_value = 0.5
    radius_socket.min_value = 0.01
    
    height_socket = ng.interface.new_socket(name="Height", in_out='INPUT', socket_type='NodeSocketFloat')
    height_socket.default_value = 2.0
    height_socket.min_value = 0.01
    
    res_socket = ng.interface.new_socket(name="Resolution", in_out='INPUT', socket_type='NodeSocketInt')
    res_socket.default_value = 16
    res_socket.min_value = 3
    res_socket.max_value = 64
    
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 创建 Mesh Cylinder 节点
    cylinder_node = nodes.new(type='GeometryNodeMeshCylinder')
    cylinder_node.location = (0, 0)
    cylinder_node.label = "Base Cylinder"
    
    # Transform 节点 - 移动到底部
    transform_node = nodes.new(type='GeometryNodeTransform')
    transform_node.location = (200, 0)
    
    # 计算偏移
    math_div = nodes.new(type='ShaderNodeMath')
    math_div.operation = 'DIVIDE'
    math_div.location = (0, -150)
    math_div.inputs[1].default_value = 2.0
    
    combine_xyz = nodes.new(type='ShaderNodeCombineXYZ')
    combine_xyz.location = (150, -150)
    
    # 连接
    links.new(input_node.outputs['Radius'], cylinder_node.inputs['Radius'])
    links.new(input_node.outputs['Height'], cylinder_node.inputs['Depth'])
    links.new(input_node.outputs['Resolution'], cylinder_node.inputs['Vertices'])
    
    links.new(cylinder_node.outputs['Mesh'], transform_node.inputs['Geometry'])
    
    links.new(input_node.outputs['Height'], math_div.inputs[0])
    links.new(math_div.outputs['Value'], combine_xyz.inputs['Z'])
    links.new(combine_xyz.outputs['Vector'], transform_node.inputs['Translation'])
    
    links.new(transform_node.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Base_Cylinder")
    return ng


def create_g_base_sphere() -> bpy.types.NodeTree:
    """
    创建 G_Base_Sphere 节点组
    功能：生成标准球体，原点在底部中心
    """
    ng = NodeGroupFactory.create_node_group("G_Base_Sphere")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    radius_socket = ng.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    radius_socket.default_value = 1.0
    radius_socket.min_value = 0.01
    
    res_socket = ng.interface.new_socket(name="Resolution", in_out='INPUT', socket_type='NodeSocketInt')
    res_socket.default_value = 16
    res_socket.min_value = 4
    res_socket.max_value = 64
    
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 创建 UV Sphere 节点
    sphere_node = nodes.new(type='GeometryNodeMeshUVSphere')
    sphere_node.location = (0, 0)
    
    # Transform - 移动到底部（向上移动 radius）
    transform_node = nodes.new(type='GeometryNodeTransform')
    transform_node.location = (200, 0)
    
    combine_xyz = nodes.new(type='ShaderNodeCombineXYZ')
    combine_xyz.location = (100, -150)
    
    # 连接
    links.new(input_node.outputs['Radius'], sphere_node.inputs['Radius'])
    links.new(input_node.outputs['Resolution'], sphere_node.inputs['Segments'])
    links.new(input_node.outputs['Resolution'], sphere_node.inputs['Rings'])
    
    links.new(sphere_node.outputs['Mesh'], transform_node.inputs['Geometry'])
    
    links.new(input_node.outputs['Radius'], combine_xyz.inputs['Z'])
    links.new(combine_xyz.outputs['Vector'], transform_node.inputs['Translation'])
    
    links.new(transform_node.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Base_Sphere")
    return ng


def create_g_damage_edges() -> bpy.types.NodeTree:
    """
    创建 G_Damage_Edges 节点组
    功能：边缘破损效果，使用噪声位移
    """
    ng = NodeGroupFactory.create_node_group("G_Damage_Edges")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    amount_socket = ng.interface.new_socket(name="Amount", in_out='INPUT', socket_type='NodeSocketFloat')
    amount_socket.default_value = 0.5
    amount_socket.min_value = 0.0
    amount_socket.max_value = 1.0
    
    scale_socket = ng.interface.new_socket(name="Scale", in_out='INPUT', socket_type='NodeSocketFloat')
    scale_socket.default_value = 2.0
    scale_socket.min_value = 0.1
    
    seed_socket = ng.interface.new_socket(name="Seed", in_out='INPUT', socket_type='NodeSocketInt')
    seed_socket.default_value = 0
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 获取位置
    position_node = nodes.new(type='GeometryNodeInputPosition')
    position_node.location = (-200, -100)
    
    # 噪声纹理
    noise_node = nodes.new(type='ShaderNodeTexNoise')
    noise_node.location = (0, -100)
    noise_node.noise_dimensions = '3D'
    
    # 数学节点 - 缩放噪声强度
    math_mult = nodes.new(type='ShaderNodeMath')
    math_mult.operation = 'MULTIPLY'
    math_mult.location = (200, -100)
    
    # 组合位移向量
    combine_xyz = nodes.new(type='ShaderNodeCombineXYZ')
    combine_xyz.location = (350, -100)
    
    # Set Position 节点
    set_position = nodes.new(type='GeometryNodeSetPosition')
    set_position.location = (200, 100)
    
    # 向量数学 - 缩放位移
    vector_math = nodes.new(type='ShaderNodeVectorMath')
    vector_math.operation = 'SCALE'
    vector_math.location = (400, 0)
    
    # 获取法线用于位移方向
    normal_node = nodes.new(type='GeometryNodeInputNormal')
    normal_node.location = (200, -200)
    
    # 最终位移
    vector_math2 = nodes.new(type='ShaderNodeVectorMath')
    vector_math2.operation = 'SCALE'
    vector_math2.location = (400, -150)
    
    # Set Position 应用位移
    set_pos_final = nodes.new(type='GeometryNodeSetPosition')
    set_pos_final.location = (550, 100)
    
    # 连接
    links.new(input_node.outputs['Geometry'], set_pos_final.inputs['Geometry'])
    links.new(position_node.outputs['Position'], noise_node.inputs['Vector'])
    links.new(input_node.outputs['Scale'], noise_node.inputs['Scale'])
    
    # 噪声值作为位移量
    links.new(noise_node.outputs['Fac'], math_mult.inputs[0])
    links.new(input_node.outputs['Amount'], math_mult.inputs[1])
    
    # 沿法线方向位移
    links.new(normal_node.outputs['Normal'], vector_math2.inputs[0])
    links.new(math_mult.outputs['Value'], vector_math2.inputs['Scale'])
    
    links.new(vector_math2.outputs['Vector'], set_pos_final.inputs['Offset'])
    links.new(set_pos_final.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Damage_Edges")
    return ng


def create_g_scatter_moss() -> bpy.types.NodeTree:
    """
    创建 G_Scatter_Moss 节点组
    功能：在表面散布苔藓（小球体代表）
    """
    ng = NodeGroupFactory.create_node_group("G_Scatter_Moss")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    density_socket = ng.interface.new_socket(name="Density", in_out='INPUT', socket_type='NodeSocketFloat')
    density_socket.default_value = 50.0
    density_socket.min_value = 0.0
    density_socket.max_value = 200.0
    
    seed_socket = ng.interface.new_socket(name="Seed", in_out='INPUT', socket_type='NodeSocketInt')
    seed_socket.default_value = 0
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 分布点
    distribute_points = nodes.new(type='GeometryNodeDistributePointsOnFaces')
    distribute_points.location = (0, 0)
    distribute_points.distribute_method = 'RANDOM'
    
    # 创建苔藓几何体（小球）
    moss_sphere = nodes.new(type='GeometryNodeMeshIcoSphere')
    moss_sphere.location = (0, -200)
    moss_sphere.inputs['Radius'].default_value = 0.02
    moss_sphere.inputs['Subdivisions'].default_value = 1
    
    # 实例化
    instance_on_points = nodes.new(type='GeometryNodeInstanceOnPoints')
    instance_on_points.location = (200, 0)
    
    # 实现为实例
    realize = nodes.new(type='GeometryNodeRealizeInstances')
    realize.location = (400, 0)
    
    # 合并几何体
    join_geo = nodes.new(type='GeometryNodeJoinGeometry')
    join_geo.location = (550, 100)
    
    # 连接
    links.new(input_node.outputs['Geometry'], distribute_points.inputs['Mesh'])
    links.new(input_node.outputs['Density'], distribute_points.inputs['Density'])
    links.new(input_node.outputs['Seed'], distribute_points.inputs['Seed'])
    
    links.new(distribute_points.outputs['Points'], instance_on_points.inputs['Points'])
    links.new(moss_sphere.outputs['Mesh'], instance_on_points.inputs['Instance'])
    
    links.new(instance_on_points.outputs['Instances'], realize.inputs['Geometry'])
    
    # 合并原始几何体和苔藓
    links.new(input_node.outputs['Geometry'], join_geo.inputs['Geometry'])
    links.new(realize.outputs['Geometry'], join_geo.inputs['Geometry'])
    
    links.new(join_geo.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Scatter_Moss")
    return ng


def create_g_scatter_on_top() -> bpy.types.NodeTree:
    """
    创建 G_Scatter_On_Top 节点组
    功能：只在物体顶部（朝上的面）散布东西
    """
    ng = NodeGroupFactory.create_node_group("G_Scatter_On_Top")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    density_socket = ng.interface.new_socket(name="Density", in_out='INPUT', socket_type='NodeSocketFloat')
    density_socket.default_value = 10.0
    
    seed_socket = ng.interface.new_socket(name="Seed", in_out='INPUT', socket_type='NodeSocketInt')
    seed_socket.default_value = 0
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 获取法线
    normal_node = nodes.new(type='GeometryNodeInputNormal')
    normal_node.location = (-200, -100)
    
    # 分离 Z 分量
    separate_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    separate_xyz.location = (-50, -100)
    
    # 比较 - 只选择朝上的面 (Z > 0.5)
    compare_node = nodes.new(type='FunctionNodeCompare')
    compare_node.location = (100, -100)
    compare_node.data_type = 'FLOAT'
    compare_node.operation = 'GREATER_THAN'
    compare_node.inputs[1].default_value = 0.5  # 阈值
    
    # 分布点（只在选中的面上）
    distribute_points = nodes.new(type='GeometryNodeDistributePointsOnFaces')
    distribute_points.location = (250, 0)
    distribute_points.distribute_method = 'RANDOM'
    
    # 创建实例几何体（小立方体代表草/石头）
    instance_geo = nodes.new(type='GeometryNodeMeshCube')
    instance_geo.location = (250, -200)
    instance_geo.inputs['Size'].default_value = (0.05, 0.05, 0.1)
    
    # 实例化
    instance_on_points = nodes.new(type='GeometryNodeInstanceOnPoints')
    instance_on_points.location = (450, 0)
    
    # 实现实例
    realize = nodes.new(type='GeometryNodeRealizeInstances')
    realize.location = (600, 0)
    
    # 合并
    join_geo = nodes.new(type='GeometryNodeJoinGeometry')
    join_geo.location = (750, 100)
    
    # 连接
    links.new(normal_node.outputs['Normal'], separate_xyz.inputs['Vector'])
    links.new(separate_xyz.outputs['Z'], compare_node.inputs[0])
    
    links.new(input_node.outputs['Geometry'], distribute_points.inputs['Mesh'])
    links.new(compare_node.outputs['Result'], distribute_points.inputs['Selection'])
    links.new(input_node.outputs['Density'], distribute_points.inputs['Density'])
    links.new(input_node.outputs['Seed'], distribute_points.inputs['Seed'])
    
    links.new(distribute_points.outputs['Points'], instance_on_points.inputs['Points'])
    links.new(instance_geo.outputs['Mesh'], instance_on_points.inputs['Instance'])
    
    links.new(instance_on_points.outputs['Instances'], realize.inputs['Geometry'])
    
    links.new(input_node.outputs['Geometry'], join_geo.inputs['Geometry'])
    links.new(realize.outputs['Geometry'], join_geo.inputs['Geometry'])
    
    links.new(join_geo.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Scatter_On_Top")
    return ng


def create_g_boolean_cut() -> bpy.types.NodeTree:
    """
    创建 G_Boolean_Cut 节点组
    功能：布尔切割操作
    """
    ng = NodeGroupFactory.create_node_group("G_Boolean_Cut")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口 - 两个几何体输入
    ng.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket(name="Cut_Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 布尔节点
    boolean_node = nodes.new(type='GeometryNodeMeshBoolean')
    boolean_node.location = (200, 0)
    boolean_node.operation = 'DIFFERENCE'
    
    # 连接
    links.new(input_node.outputs['Geometry'], boolean_node.inputs['Mesh 1'])
    links.new(input_node.outputs['Cut_Geometry'], boolean_node.inputs['Mesh 2'])
    links.new(boolean_node.outputs['Mesh'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Boolean_Cut")
    return ng


def create_g_voxel_remesh() -> bpy.types.NodeTree:
    """
    创建 G_Voxel_Remesh 节点组
    功能：体素重建，风格化处理
    
    注意：Geometry Nodes 中的 Volume to Mesh 可以实现类似效果
    这里使用 Mesh to Volume + Volume to Mesh 的组合
    """
    ng = NodeGroupFactory.create_node_group("G_Voxel_Remesh")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    voxel_socket = ng.interface.new_socket(name="Voxel_Size", in_out='INPUT', socket_type='NodeSocketFloat')
    voxel_socket.default_value = 0.1
    voxel_socket.min_value = 0.01
    voxel_socket.max_value = 1.0
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # Mesh to Volume
    mesh_to_volume = nodes.new(type='GeometryNodeMeshToVolume')
    mesh_to_volume.location = (0, 0)
    mesh_to_volume.resolution_mode = 'VOXEL_SIZE'
    
    # Volume to Mesh
    volume_to_mesh = nodes.new(type='GeometryNodeVolumeToMesh')
    volume_to_mesh.location = (250, 0)
    volume_to_mesh.resolution_mode = 'VOXEL_SIZE'
    
    # 连接
    links.new(input_node.outputs['Geometry'], mesh_to_volume.inputs['Mesh'])
    links.new(input_node.outputs['Voxel_Size'], mesh_to_volume.inputs['Voxel Size'])
    
    links.new(mesh_to_volume.outputs['Volume'], volume_to_mesh.inputs['Volume'])
    links.new(input_node.outputs['Voxel_Size'], volume_to_mesh.inputs['Voxel Size'])
    
    links.new(volume_to_mesh.outputs['Mesh'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Voxel_Remesh")
    return ng


def create_g_base_cube_centered() -> bpy.types.NodeTree:
    """
    创建 G_Base_Cube_Centered 节点组
    功能：生成标准立方体，原点在几何中心（适合旋转）
    """
    ng = NodeGroupFactory.create_node_group("G_Base_Cube_Centered")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    size_socket = ng.interface.new_socket(name="Size", in_out='INPUT', socket_type='NodeSocketVector')
    size_socket.default_value = (1.0, 1.0, 1.0)
    
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 创建 Mesh Cube 节点（原点默认在中心）
    cube_node = nodes.new(type='GeometryNodeMeshCube')
    cube_node.location = (0, 0)
    
    # 直接连接，不做偏移
    links.new(input_node.outputs['Size'], cube_node.inputs['Size'])
    links.new(cube_node.outputs['Mesh'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Base_Cube_Centered")
    return ng


def create_g_base_cylinder_centered() -> bpy.types.NodeTree:
    """
    创建 G_Base_Cylinder_Centered 节点组
    功能：生成标准圆柱，原点在几何中心（适合旋转）
    """
    ng = NodeGroupFactory.create_node_group("G_Base_Cylinder_Centered")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    radius_socket = ng.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    radius_socket.default_value = 0.5
    radius_socket.min_value = 0.01
    
    height_socket = ng.interface.new_socket(name="Height", in_out='INPUT', socket_type='NodeSocketFloat')
    height_socket.default_value = 2.0
    height_socket.min_value = 0.01
    
    res_socket = ng.interface.new_socket(name="Resolution", in_out='INPUT', socket_type='NodeSocketInt')
    res_socket.default_value = 16
    res_socket.min_value = 3
    res_socket.max_value = 64
    
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 创建 Mesh Cylinder 节点（原点默认在中心）
    cylinder_node = nodes.new(type='GeometryNodeMeshCylinder')
    cylinder_node.location = (0, 0)
    
    # 直接连接，不做偏移
    links.new(input_node.outputs['Radius'], cylinder_node.inputs['Radius'])
    links.new(input_node.outputs['Height'], cylinder_node.inputs['Depth'])
    links.new(input_node.outputs['Resolution'], cylinder_node.inputs['Vertices'])
    links.new(cylinder_node.outputs['Mesh'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Base_Cylinder_Centered")
    return ng


def create_g_base_sphere_centered() -> bpy.types.NodeTree:
    """
    创建 G_Base_Sphere_Centered 节点组
    功能：生成标准球体，原点在几何中心（适合旋转）
    """
    ng = NodeGroupFactory.create_node_group("G_Base_Sphere_Centered")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    radius_socket = ng.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    radius_socket.default_value = 1.0
    radius_socket.min_value = 0.01
    
    res_socket = ng.interface.new_socket(name="Resolution", in_out='INPUT', socket_type='NodeSocketInt')
    res_socket.default_value = 16
    res_socket.min_value = 4
    res_socket.max_value = 64
    
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 创建 UV Sphere 节点（原点默认在中心）
    sphere_node = nodes.new(type='GeometryNodeMeshUVSphere')
    sphere_node.location = (0, 0)
    
    # 直接连接，不做偏移
    links.new(input_node.outputs['Radius'], sphere_node.inputs['Radius'])
    links.new(input_node.outputs['Resolution'], sphere_node.inputs['Segments'])
    links.new(input_node.outputs['Resolution'], sphere_node.inputs['Rings'])
    links.new(sphere_node.outputs['Mesh'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Base_Sphere_Centered")
    return ng


def create_g_taper() -> bpy.types.NodeTree:
    """
    创建 G_Taper 节点组 ⚠️ 新增变形节点
    功能：锥形变形 - 让几何体一端变小
    
    用途：车头收窄、A柱倾斜、任何需要渐变尺寸的地方
    """
    ng = NodeGroupFactory.create_node_group("G_Taper")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    # Factor: 0 = 不变形, 1 = 顶部收缩到点
    factor_socket = ng.interface.new_socket(name="Factor", in_out='INPUT', socket_type='NodeSocketFloat')
    factor_socket.default_value = 0.5
    factor_socket.min_value = 0.0
    factor_socket.max_value = 1.0
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 获取边界框来确定高度范围
    bbox = nodes.new(type='GeometryNodeBoundBox')
    bbox.location = (-200, -200)
    
    # 获取当前位置
    position = nodes.new(type='GeometryNodeInputPosition')
    position.location = (-400, 0)
    
    # 分离 XYZ
    sep_pos = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_pos.location = (-200, 0)
    
    sep_min = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_min.location = (0, -300)
    
    sep_max = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_max.location = (0, -400)
    
    # 计算 Z 的归一化位置 (z - min) / (max - min)
    sub_z_min = nodes.new(type='ShaderNodeMath')
    sub_z_min.operation = 'SUBTRACT'
    sub_z_min.location = (150, -100)
    
    sub_max_min = nodes.new(type='ShaderNodeMath')
    sub_max_min.operation = 'SUBTRACT'
    sub_max_min.location = (150, -250)
    
    div_norm = nodes.new(type='ShaderNodeMath')
    div_norm.operation = 'DIVIDE'
    div_norm.location = (300, -150)
    
    # 计算缩放因子: 1 - factor * normalized_z
    mult_factor = nodes.new(type='ShaderNodeMath')
    mult_factor.operation = 'MULTIPLY'
    mult_factor.location = (450, -100)
    
    sub_scale = nodes.new(type='ShaderNodeMath')
    sub_scale.operation = 'SUBTRACT'
    sub_scale.location = (600, -100)
    sub_scale.inputs[0].default_value = 1.0
    
    # 缩放 X 和 Y
    mult_x = nodes.new(type='ShaderNodeMath')
    mult_x.operation = 'MULTIPLY'
    mult_x.location = (750, 50)
    
    mult_y = nodes.new(type='ShaderNodeMath')
    mult_y.operation = 'MULTIPLY'
    mult_y.location = (750, -50)
    
    # 组合新位置
    combine = nodes.new(type='ShaderNodeCombineXYZ')
    combine.location = (900, 0)
    
    # Set Position
    set_pos = nodes.new(type='GeometryNodeSetPosition')
    set_pos.location = (1050, 100)
    
    # 连接
    links.new(input_node.outputs['Geometry'], bbox.inputs['Geometry'])
    links.new(input_node.outputs['Geometry'], set_pos.inputs['Geometry'])
    links.new(position.outputs['Position'], sep_pos.inputs['Vector'])
    links.new(bbox.outputs['Min'], sep_min.inputs['Vector'])
    links.new(bbox.outputs['Max'], sep_max.inputs['Vector'])
    
    # 归一化 Z
    links.new(sep_pos.outputs['Z'], sub_z_min.inputs[0])
    links.new(sep_min.outputs['Z'], sub_z_min.inputs[1])
    links.new(sep_max.outputs['Z'], sub_max_min.inputs[0])
    links.new(sep_min.outputs['Z'], sub_max_min.inputs[1])
    links.new(sub_z_min.outputs['Value'], div_norm.inputs[0])
    links.new(sub_max_min.outputs['Value'], div_norm.inputs[1])
    
    # 计算缩放
    links.new(input_node.outputs['Factor'], mult_factor.inputs[0])
    links.new(div_norm.outputs['Value'], mult_factor.inputs[1])
    links.new(mult_factor.outputs['Value'], sub_scale.inputs[1])
    
    # 应用缩放
    links.new(sep_pos.outputs['X'], mult_x.inputs[0])
    links.new(sub_scale.outputs['Value'], mult_x.inputs[1])
    links.new(sep_pos.outputs['Y'], mult_y.inputs[0])
    links.new(sub_scale.outputs['Value'], mult_y.inputs[1])
    
    links.new(mult_x.outputs['Value'], combine.inputs['X'])
    links.new(mult_y.outputs['Value'], combine.inputs['Y'])
    links.new(sep_pos.outputs['Z'], combine.inputs['Z'])
    
    links.new(combine.outputs['Vector'], set_pos.inputs['Position'])
    links.new(set_pos.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Taper (变形)")
    return ng


def create_g_shear() -> bpy.types.NodeTree:
    """
    创建 G_Shear 节点组 ⚠️ 新增变形节点
    功能：剪切变形 - 让几何体倾斜
    
    用途：挡风玻璃倾斜、溜背造型
    """
    ng = NodeGroupFactory.create_node_group("G_Shear")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    # Amount: 剪切量（正值向前倾，负值向后倾）
    amount_socket = ng.interface.new_socket(name="Amount", in_out='INPUT', socket_type='NodeSocketFloat')
    amount_socket.default_value = 0.3
    amount_socket.min_value = -2.0
    amount_socket.max_value = 2.0
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 获取边界框
    bbox = nodes.new(type='GeometryNodeBoundBox')
    bbox.location = (-200, -200)
    
    # 获取位置
    position = nodes.new(type='GeometryNodeInputPosition')
    position.location = (-400, 0)
    
    # 分离 XYZ
    sep_pos = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_pos.location = (-200, 0)
    
    sep_min = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_min.location = (0, -300)
    
    sep_max = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_max.location = (0, -400)
    
    # 归一化 Z: (z - min) / (max - min)
    sub_z = nodes.new(type='ShaderNodeMath')
    sub_z.operation = 'SUBTRACT'
    sub_z.location = (150, -100)
    
    sub_range = nodes.new(type='ShaderNodeMath')
    sub_range.operation = 'SUBTRACT'
    sub_range.location = (150, -250)
    
    div_norm = nodes.new(type='ShaderNodeMath')
    div_norm.operation = 'DIVIDE'
    div_norm.location = (300, -150)
    
    # X 偏移 = Amount * normalized_z * (max_z - min_z)
    mult_amount = nodes.new(type='ShaderNodeMath')
    mult_amount.operation = 'MULTIPLY'
    mult_amount.location = (450, -50)
    
    mult_range = nodes.new(type='ShaderNodeMath')
    mult_range.operation = 'MULTIPLY'
    mult_range.location = (600, -50)
    
    # 新 X = 原 X + 偏移
    add_x = nodes.new(type='ShaderNodeMath')
    add_x.operation = 'ADD'
    add_x.location = (750, 0)
    
    # 组合
    combine = nodes.new(type='ShaderNodeCombineXYZ')
    combine.location = (900, 0)
    
    # Set Position
    set_pos = nodes.new(type='GeometryNodeSetPosition')
    set_pos.location = (1050, 100)
    
    # 连接
    links.new(input_node.outputs['Geometry'], bbox.inputs['Geometry'])
    links.new(input_node.outputs['Geometry'], set_pos.inputs['Geometry'])
    links.new(position.outputs['Position'], sep_pos.inputs['Vector'])
    links.new(bbox.outputs['Min'], sep_min.inputs['Vector'])
    links.new(bbox.outputs['Max'], sep_max.inputs['Vector'])
    
    # 归一化
    links.new(sep_pos.outputs['Z'], sub_z.inputs[0])
    links.new(sep_min.outputs['Z'], sub_z.inputs[1])
    links.new(sep_max.outputs['Z'], sub_range.inputs[0])
    links.new(sep_min.outputs['Z'], sub_range.inputs[1])
    links.new(sub_z.outputs['Value'], div_norm.inputs[0])
    links.new(sub_range.outputs['Value'], div_norm.inputs[1])
    
    # 计算偏移
    links.new(input_node.outputs['Amount'], mult_amount.inputs[0])
    links.new(div_norm.outputs['Value'], mult_amount.inputs[1])
    links.new(mult_amount.outputs['Value'], mult_range.inputs[0])
    links.new(sub_range.outputs['Value'], mult_range.inputs[1])
    
    # 应用
    links.new(sep_pos.outputs['X'], add_x.inputs[0])
    links.new(mult_range.outputs['Value'], add_x.inputs[1])
    
    links.new(add_x.outputs['Value'], combine.inputs['X'])
    links.new(sep_pos.outputs['Y'], combine.inputs['Y'])
    links.new(sep_pos.outputs['Z'], combine.inputs['Z'])
    
    links.new(combine.outputs['Vector'], set_pos.inputs['Position'])
    links.new(set_pos.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Shear (变形)")
    return ng


def create_g_smooth() -> bpy.types.NodeTree:
    """
    创建 G_Smooth 节点组 ⚠️ 新增变形节点
    功能：细分平滑 - 让方块变圆润
    
    用途：圆润的车身、平滑过渡
    """
    ng = NodeGroupFactory.create_node_group("G_Smooth")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    level_socket = ng.interface.new_socket(name="Level", in_out='INPUT', socket_type='NodeSocketInt')
    level_socket.default_value = 2
    level_socket.min_value = 1
    level_socket.max_value = 4
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # Subdivision Surface 节点
    subdiv = nodes.new(type='GeometryNodeSubdivisionSurface')
    subdiv.location = (200, 0)
    
    # 连接
    links.new(input_node.outputs['Geometry'], subdiv.inputs['Mesh'])
    links.new(input_node.outputs['Level'], subdiv.inputs['Level'])
    links.new(subdiv.outputs['Mesh'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Smooth (变形)")
    return ng


def create_g_base_wedge() -> bpy.types.NodeTree:
    """
    创建 G_Base_Wedge 节点组 ⚠️ 新增基础几何体
    功能：楔形体（三角柱）- 原点在底部中心
    
    用途：挡风玻璃、斜面部件、车头造型
    """
    ng = NodeGroupFactory.create_node_group("G_Base_Wedge")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    size_socket = ng.interface.new_socket(name="Size", in_out='INPUT', socket_type='NodeSocketVector')
    size_socket.default_value = (1.0, 1.0, 1.0)
    
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 创建立方体
    cube = nodes.new(type='GeometryNodeMeshCube')
    cube.location = (0, 0)
    
    # 分离尺寸
    sep_size = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_size.location = (-200, -150)
    
    # 创建用于切割的立方体（倾斜切割）
    cut_cube = nodes.new(type='GeometryNodeMeshCube')
    cut_cube.location = (0, -200)
    
    # 缩放切割立方体
    scale_cut = nodes.new(type='ShaderNodeVectorMath')
    scale_cut.operation = 'SCALE'
    scale_cut.location = (-100, -200)
    scale_cut.inputs['Scale'].default_value = 2.0
    
    # 变换切割立方体 - 旋转45度并移动
    transform_cut = nodes.new(type='GeometryNodeTransform')
    transform_cut.location = (200, -200)
    transform_cut.inputs['Rotation'].default_value = (0.785398, 0, 0)  # 45度
    
    # 计算切割立方体位置（向上向后移动）
    combine_offset = nodes.new(type='ShaderNodeCombineXYZ')
    combine_offset.location = (100, -350)
    
    # Z 偏移 = Size.Z
    # X 偏移 = Size.X / 2
    div_x = nodes.new(type='ShaderNodeMath')
    div_x.operation = 'DIVIDE'
    div_x.location = (-50, -350)
    div_x.inputs[1].default_value = 2.0
    
    # 布尔切割
    boolean = nodes.new(type='GeometryNodeMeshBoolean')
    boolean.location = (400, 0)
    boolean.operation = 'DIFFERENCE'
    
    # 移动到底部中心
    sep_size2 = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_size2.location = (400, -200)
    
    div_z = nodes.new(type='ShaderNodeMath')
    div_z.operation = 'DIVIDE'
    div_z.location = (550, -200)
    div_z.inputs[1].default_value = 2.0
    
    combine_trans = nodes.new(type='ShaderNodeCombineXYZ')
    combine_trans.location = (700, -200)
    
    transform_final = nodes.new(type='GeometryNodeTransform')
    transform_final.location = (600, 0)
    
    # 连接尺寸
    links.new(input_node.outputs['Size'], cube.inputs['Size'])
    links.new(input_node.outputs['Size'], sep_size.inputs['Vector'])
    links.new(input_node.outputs['Size'], scale_cut.inputs['Vector'])
    links.new(scale_cut.outputs['Vector'], cut_cube.inputs['Size'])
    
    # 切割立方体位置
    links.new(sep_size.outputs['X'], div_x.inputs[0])
    links.new(div_x.outputs['Value'], combine_offset.inputs['X'])
    links.new(sep_size.outputs['Z'], combine_offset.inputs['Z'])
    links.new(combine_offset.outputs['Vector'], transform_cut.inputs['Translation'])
    
    links.new(cut_cube.outputs['Mesh'], transform_cut.inputs['Geometry'])
    
    # 布尔
    links.new(cube.outputs['Mesh'], boolean.inputs['Mesh 1'])
    links.new(transform_cut.outputs['Geometry'], boolean.inputs['Mesh 2'])
    
    # 移动到底部
    links.new(input_node.outputs['Size'], sep_size2.inputs['Vector'])
    links.new(sep_size2.outputs['Z'], div_z.inputs[0])
    links.new(div_z.outputs['Value'], combine_trans.inputs['Z'])
    
    links.new(boolean.outputs['Mesh'], transform_final.inputs['Geometry'])
    links.new(combine_trans.outputs['Vector'], transform_final.inputs['Translation'])
    
    links.new(transform_final.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Base_Wedge (基础几何体)")
    return ng


def create_g_align_ground() -> bpy.types.NodeTree:
    """
    创建 G_Align_Ground 节点组 ⚠️ 核心节点组
    功能：强制对齐地面，将 Min Z 归零
    
    这是最重要的节点组，确保模型不会"插进地里"
    """
    ng = NodeGroupFactory.create_node_group("G_Align_Ground")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    # 获取输入输出节点
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # Bounding Box - 获取边界框
    bbox_node = nodes.new(type='GeometryNodeBoundBox')
    bbox_node.location = (0, -100)
    
    # 分离 Min 的 Z 值
    separate_min = nodes.new(type='ShaderNodeSeparateXYZ')
    separate_min.location = (200, -100)
    separate_min.label = "Get Min Z"
    
    # 取负值（用于向上移动）
    math_negate = nodes.new(type='ShaderNodeMath')
    math_negate.operation = 'MULTIPLY'
    math_negate.location = (350, -100)
    math_negate.inputs[1].default_value = -1.0
    math_negate.label = "Negate"
    
    # 组合偏移向量 (0, 0, -MinZ)
    combine_offset = nodes.new(type='ShaderNodeCombineXYZ')
    combine_offset.location = (500, -100)
    combine_offset.label = "Offset Vector"
    
    # Transform - 应用偏移
    transform_node = nodes.new(type='GeometryNodeTransform')
    transform_node.location = (350, 100)
    transform_node.label = "Apply Ground Align"
    
    # 连接
    links.new(input_node.outputs['Geometry'], bbox_node.inputs['Geometry'])
    links.new(input_node.outputs['Geometry'], transform_node.inputs['Geometry'])
    
    links.new(bbox_node.outputs['Min'], separate_min.inputs['Vector'])
    links.new(separate_min.outputs['Z'], math_negate.inputs[0])
    links.new(math_negate.outputs['Value'], combine_offset.inputs['Z'])
    links.new(combine_offset.outputs['Vector'], transform_node.inputs['Translation'])
    
    links.new(transform_node.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Align_Ground (核心)")
    return ng


# ========== Phase 1: 曲线能力 ==========

def create_g_curve_circle() -> bpy.types.NodeTree:
    """
    创建 G_Curve_Circle 节点组
    功能：生成圆形曲线（用作挤出截面）
    """
    ng = NodeGroupFactory.create_node_group("G_Curve_Circle")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    radius_socket = ng.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    radius_socket.default_value = 0.1
    radius_socket.min_value = 0.001
    
    res_socket = ng.interface.new_socket(name="Resolution", in_out='INPUT', socket_type='NodeSocketInt')
    res_socket.default_value = 12
    res_socket.min_value = 3
    res_socket.max_value = 64
    
    ng.interface.new_socket(name="Curve", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 创建圆形曲线
    circle = nodes.new(type='GeometryNodeCurvePrimitiveCircle')
    circle.location = (0, 0)
    circle.mode = 'RADIUS'
    
    links.new(input_node.outputs['Radius'], circle.inputs['Radius'])
    links.new(input_node.outputs['Resolution'], circle.inputs['Resolution'])
    links.new(circle.outputs['Curve'], output_node.inputs['Curve'])
    
    print("✓ 创建节点组: G_Curve_Circle")
    return ng


def create_g_curve_line() -> bpy.types.NodeTree:
    """
    创建 G_Curve_Line 节点组
    功能：生成直线曲线（用作路径）
    """
    ng = NodeGroupFactory.create_node_group("G_Curve_Line")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    start_socket = ng.interface.new_socket(name="Start", in_out='INPUT', socket_type='NodeSocketVector')
    start_socket.default_value = (0.0, 0.0, 0.0)
    
    end_socket = ng.interface.new_socket(name="End", in_out='INPUT', socket_type='NodeSocketVector')
    end_socket.default_value = (0.0, 0.0, 1.0)
    
    ng.interface.new_socket(name="Curve", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 创建直线曲线
    line = nodes.new(type='GeometryNodeCurvePrimitiveLine')
    line.location = (0, 0)
    line.mode = 'POINTS'
    
    links.new(input_node.outputs['Start'], line.inputs['Start'])
    links.new(input_node.outputs['End'], line.inputs['End'])
    links.new(line.outputs['Curve'], output_node.inputs['Curve'])
    
    print("✓ 创建节点组: G_Curve_Line")
    return ng


def create_g_curve_arc() -> bpy.types.NodeTree:
    """
    创建 G_Curve_Arc 节点组
    功能：生成圆弧曲线（用作拱门路径）
    参数：Radius（半径）、Sweep（扫掠角度，默认π=半圆）、Resolution
    """
    ng = NodeGroupFactory.create_node_group("G_Curve_Arc")
    nodes = ng.nodes
    links = ng.links

    # 添加接口
    radius_socket = ng.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    radius_socket.default_value = 1.0
    radius_socket.min_value = 0.01

    sweep_socket = ng.interface.new_socket(name="Sweep", in_out='INPUT', socket_type='NodeSocketFloat')
    sweep_socket.default_value = 3.14159  # π = 半圆
    sweep_socket.min_value = 0.1
    sweep_socket.max_value = 6.28318  # 2π

    res_socket = ng.interface.new_socket(name="Resolution", in_out='INPUT', socket_type='NodeSocketInt')
    res_socket.default_value = 16
    res_socket.min_value = 3
    res_socket.max_value = 64

    ng.interface.new_socket(name="Curve", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')

    # 创建圆弧曲线
    arc = nodes.new(type='GeometryNodeCurveArc')
    arc.location = (0, 0)
    arc.mode = 'RADIUS'

    # 连接参数
    links.new(input_node.outputs['Radius'], arc.inputs['Radius'])
    links.new(input_node.outputs['Sweep'], arc.inputs['Sweep Angle'])
    links.new(input_node.outputs['Resolution'], arc.inputs['Resolution'])
    links.new(arc.outputs['Curve'], output_node.inputs['Curve'])

    print("✓ 创建节点组: G_Curve_Arc")
    return ng


def create_g_curve_rectangle() -> bpy.types.NodeTree:
    """
    创建 G_Curve_Rectangle 节点组
    功能：生成矩形曲线（用作挤出截面）
    参数：Width（宽度）、Height（高度）
    """
    ng = NodeGroupFactory.create_node_group("G_Curve_Rectangle")
    nodes = ng.nodes
    links = ng.links

    # 添加接口
    width_socket = ng.interface.new_socket(name="Width", in_out='INPUT', socket_type='NodeSocketFloat')
    width_socket.default_value = 0.25
    width_socket.min_value = 0.01

    height_socket = ng.interface.new_socket(name="Height", in_out='INPUT', socket_type='NodeSocketFloat')
    height_socket.default_value = 0.25
    height_socket.min_value = 0.01

    ng.interface.new_socket(name="Curve", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')

    # 创建矩形曲线
    rect = nodes.new(type='GeometryNodeCurvePrimitiveQuadrilateral')
    rect.location = (0, 0)
    rect.mode = 'RECTANGLE'

    links.new(input_node.outputs['Width'], rect.inputs['Width'])
    links.new(input_node.outputs['Height'], rect.inputs['Height'])
    links.new(rect.outputs['Curve'], output_node.inputs['Curve'])

    print("✓ 创建节点组: G_Curve_Rectangle")
    return ng


def create_g_arch() -> bpy.types.NodeTree:
    """
    创建 G_Arch 节点组
    功能：生成均匀截面的拱顶（使用曲线挤出，避免 G_Bend 的截面变形问题）
    参数：
        - Span: 拱门跨度（两端点间距离）
        - Thickness: 截面宽度（X方向）
        - Depth: 截面深度（Y方向）
        - Resolution: 圆弧分辨率

    输出：原点在拱顶起点（左下角），拱顶向右延伸
    """
    ng = NodeGroupFactory.create_node_group("G_Arch")
    nodes = ng.nodes
    links = ng.links

    # 添加接口
    span_socket = ng.interface.new_socket(name="Span", in_out='INPUT', socket_type='NodeSocketFloat')
    span_socket.default_value = 2.0
    span_socket.min_value = 0.1

    thick_socket = ng.interface.new_socket(name="Thickness", in_out='INPUT', socket_type='NodeSocketFloat')
    thick_socket.default_value = 0.25
    thick_socket.min_value = 0.01

    depth_socket = ng.interface.new_socket(name="Depth", in_out='INPUT', socket_type='NodeSocketFloat')
    depth_socket.default_value = 0.25
    depth_socket.min_value = 0.01

    res_socket = ng.interface.new_socket(name="Resolution", in_out='INPUT', socket_type='NodeSocketInt')
    res_socket.default_value = 16
    res_socket.min_value = 4
    res_socket.max_value = 64

    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')

    # 1. 计算半径：Span = 2 * Radius，所以 Radius = Span / 2
    divide = nodes.new(type='ShaderNodeMath')
    divide.location = (-400, 100)
    divide.operation = 'DIVIDE'
    divide.inputs[1].default_value = 2.0
    links.new(input_node.outputs['Span'], divide.inputs[0])

    # 2. 创建圆弧路径（半圆）
    arc = nodes.new(type='GeometryNodeCurveArc')
    arc.location = (-200, 100)
    arc.mode = 'RADIUS'
    arc.inputs['Sweep Angle'].default_value = 3.14159  # π = 180°
    arc.inputs['Start Angle'].default_value = 0.0
    links.new(divide.outputs['Value'], arc.inputs['Radius'])
    links.new(input_node.outputs['Resolution'], arc.inputs['Resolution'])

    # 3. 创建矩形截面
    rect = nodes.new(type='GeometryNodeCurvePrimitiveQuadrilateral')
    rect.location = (-200, -100)
    rect.mode = 'RECTANGLE'
    links.new(input_node.outputs['Thickness'], rect.inputs['Width'])
    links.new(input_node.outputs['Depth'], rect.inputs['Height'])

    # 4. 曲线转网格（沿圆弧路径挤出矩形截面）
    curve_to_mesh = nodes.new(type='GeometryNodeCurveToMesh')
    curve_to_mesh.location = (0, 0)
    curve_to_mesh.inputs['Fill Caps'].default_value = True
    links.new(arc.outputs['Curve'], curve_to_mesh.inputs['Curve'])
    links.new(rect.outputs['Curve'], curve_to_mesh.inputs['Profile Curve'])

    # 5. 旋转使拱顶朝上（圆弧默认在XY平面，需要旋转到XZ平面）
    transform = nodes.new(type='GeometryNodeTransform')
    transform.location = (200, 0)
    # 绕X轴旋转90度，让圆弧从XY平面转到XZ平面（向上凸起）
    transform.inputs['Rotation'].default_value = (1.5708, 0.0, 0.0)  # π/2
    links.new(curve_to_mesh.outputs['Mesh'], transform.inputs['Geometry'])

    # 6. 平滑着色
    shade_smooth = nodes.new(type='GeometryNodeSetShadeSmooth')
    shade_smooth.location = (400, 0)
    shade_smooth.inputs['Shade Smooth'].default_value = True
    links.new(transform.outputs['Geometry'], shade_smooth.inputs['Geometry'])

    links.new(shade_smooth.outputs['Geometry'], output_node.inputs['Geometry'])

    print("✓ 创建节点组: G_Arch")
    return ng


def create_g_arch_complete() -> bpy.types.NodeTree:
    """
    创建 G_Arch_Complete 节点组
    功能：生成完整的拱门（柱子 + 拱顶，物理重叠无缝）

    原理：柱子立方体和拱顶曲线挤出，通过物理重叠实现视觉无缝

    参数：
        - Width: 拱门内宽（两柱内侧间距）
        - Height: 柱子高度（拱顶起点高度）
        - Thickness: 柱子/拱顶厚度（X方向）
        - Depth: 柱子/拱顶深度（Y方向）
        - Resolution: 圆弧分辨率

    输出：原点在拱门中心底部
    """
    ng = NodeGroupFactory.create_node_group("G_Arch_Complete")
    nodes = ng.nodes
    links = ng.links

    # ========== 添加接口 ==========
    width_socket = ng.interface.new_socket(name="Width", in_out='INPUT', socket_type='NodeSocketFloat')
    width_socket.default_value = 2.0
    width_socket.min_value = 0.1

    height_socket = ng.interface.new_socket(name="Height", in_out='INPUT', socket_type='NodeSocketFloat')
    height_socket.default_value = 2.0
    height_socket.min_value = 0.1

    thick_socket = ng.interface.new_socket(name="Thickness", in_out='INPUT', socket_type='NodeSocketFloat')
    thick_socket.default_value = 0.25
    thick_socket.min_value = 0.01

    depth_socket = ng.interface.new_socket(name="Depth", in_out='INPUT', socket_type='NodeSocketFloat')
    depth_socket.default_value = 0.25
    depth_socket.min_value = 0.01

    res_socket = ng.interface.new_socket(name="Resolution", in_out='INPUT', socket_type='NodeSocketInt')
    res_socket.default_value = 16
    res_socket.min_value = 4
    res_socket.max_value = 64

    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')

    # ========== 计算关键尺寸 ==========
    # 柱子X位置 = ±(Width/2 + Thickness/2)
    half_width = nodes.new(type='ShaderNodeMath')
    half_width.location = (-800, 200)
    half_width.operation = 'DIVIDE'
    half_width.inputs[1].default_value = 2.0
    links.new(input_node.outputs['Width'], half_width.inputs[0])

    half_thick = nodes.new(type='ShaderNodeMath')
    half_thick.location = (-800, 100)
    half_thick.operation = 'DIVIDE'
    half_thick.inputs[1].default_value = 2.0
    links.new(input_node.outputs['Thickness'], half_thick.inputs[0])

    pillar_x = nodes.new(type='ShaderNodeMath')
    pillar_x.location = (-600, 150)
    pillar_x.operation = 'ADD'
    links.new(half_width.outputs['Value'], pillar_x.inputs[0])
    links.new(half_thick.outputs['Value'], pillar_x.inputs[1])

    pillar_x_neg = nodes.new(type='ShaderNodeMath')
    pillar_x_neg.location = (-400, 150)
    pillar_x_neg.operation = 'MULTIPLY'
    pillar_x_neg.inputs[1].default_value = -1.0
    links.new(pillar_x.outputs['Value'], pillar_x_neg.inputs[0])

    # 柱子高度（延伸一点进入拱顶）
    pillar_height = nodes.new(type='ShaderNodeMath')
    pillar_height.location = (-600, 0)
    pillar_height.operation = 'ADD'
    links.new(input_node.outputs['Height'], pillar_height.inputs[0])
    links.new(half_thick.outputs['Value'], pillar_height.inputs[1])

    # 柱子Z位置（中心在半高处）
    pillar_z = nodes.new(type='ShaderNodeMath')
    pillar_z.location = (-400, 0)
    pillar_z.operation = 'DIVIDE'
    pillar_z.inputs[1].default_value = 2.0
    links.new(pillar_height.outputs['Value'], pillar_z.inputs[0])

    # ========== 左柱 ==========
    left_size = nodes.new(type='ShaderNodeCombineXYZ')
    left_size.location = (-200, 300)
    links.new(input_node.outputs['Thickness'], left_size.inputs['X'])
    links.new(input_node.outputs['Depth'], left_size.inputs['Y'])
    links.new(pillar_height.outputs['Value'], left_size.inputs['Z'])

    left_cube = nodes.new(type='GeometryNodeMeshCube')
    left_cube.location = (0, 300)
    links.new(left_size.outputs['Vector'], left_cube.inputs['Size'])

    left_pos = nodes.new(type='ShaderNodeCombineXYZ')
    left_pos.location = (-200, 200)
    links.new(pillar_x_neg.outputs['Value'], left_pos.inputs['X'])
    left_pos.inputs['Y'].default_value = 0.0
    links.new(pillar_z.outputs['Value'], left_pos.inputs['Z'])

    left_transform = nodes.new(type='GeometryNodeTransform')
    left_transform.location = (200, 300)
    links.new(left_cube.outputs['Mesh'], left_transform.inputs['Geometry'])
    links.new(left_pos.outputs['Vector'], left_transform.inputs['Translation'])

    # ========== 右柱 ==========
    right_cube = nodes.new(type='GeometryNodeMeshCube')
    right_cube.location = (0, 100)
    links.new(left_size.outputs['Vector'], right_cube.inputs['Size'])

    right_pos = nodes.new(type='ShaderNodeCombineXYZ')
    right_pos.location = (-200, 0)
    links.new(pillar_x.outputs['Value'], right_pos.inputs['X'])
    right_pos.inputs['Y'].default_value = 0.0
    links.new(pillar_z.outputs['Value'], right_pos.inputs['Z'])

    right_transform = nodes.new(type='GeometryNodeTransform')
    right_transform.location = (200, 100)
    links.new(right_cube.outputs['Mesh'], right_transform.inputs['Geometry'])
    links.new(right_pos.outputs['Vector'], right_transform.inputs['Translation'])

    # ========== 拱顶 ==========
    # 拱顶跨度 = Width + Thickness
    arch_span = nodes.new(type='ShaderNodeMath')
    arch_span.location = (-200, -100)
    arch_span.operation = 'ADD'
    links.new(input_node.outputs['Width'], arch_span.inputs[0])
    links.new(input_node.outputs['Thickness'], arch_span.inputs[1])

    # 拱顶半径 = Span / 2
    arch_radius = nodes.new(type='ShaderNodeMath')
    arch_radius.location = (0, -100)
    arch_radius.operation = 'DIVIDE'
    arch_radius.inputs[1].default_value = 2.0
    links.new(arch_span.outputs['Value'], arch_radius.inputs[0])

    # 创建圆弧
    arc = nodes.new(type='GeometryNodeCurveArc')
    arc.location = (200, -100)
    arc.mode = 'RADIUS'
    arc.inputs['Sweep Angle'].default_value = 3.14159
    arc.inputs['Start Angle'].default_value = 0.0
    links.new(arch_radius.outputs['Value'], arc.inputs['Radius'])
    links.new(input_node.outputs['Resolution'], arc.inputs['Resolution'])

    # 旋转到XZ平面
    arc_rotate = nodes.new(type='GeometryNodeTransform')
    arc_rotate.location = (400, -100)
    arc_rotate.inputs['Rotation'].default_value = (1.5708, 0.0, 0.0)
    links.new(arc.outputs['Curve'], arc_rotate.inputs['Geometry'])

    # 平移到正确高度
    arc_pos = nodes.new(type='ShaderNodeCombineXYZ')
    arc_pos.location = (400, -250)
    arc_pos.inputs['X'].default_value = 0.0
    arc_pos.inputs['Y'].default_value = 0.0
    links.new(input_node.outputs['Height'], arc_pos.inputs['Z'])

    arc_translate = nodes.new(type='GeometryNodeTransform')
    arc_translate.location = (600, -100)
    links.new(arc_rotate.outputs['Geometry'], arc_translate.inputs['Geometry'])
    links.new(arc_pos.outputs['Vector'], arc_translate.inputs['Translation'])

    # 矩形截面
    rect = nodes.new(type='GeometryNodeCurvePrimitiveQuadrilateral')
    rect.location = (400, -350)
    rect.mode = 'RECTANGLE'
    links.new(input_node.outputs['Thickness'], rect.inputs['Width'])
    links.new(input_node.outputs['Depth'], rect.inputs['Height'])

    # 曲线转网格
    curve_to_mesh = nodes.new(type='GeometryNodeCurveToMesh')
    curve_to_mesh.location = (800, -100)
    curve_to_mesh.inputs['Fill Caps'].default_value = False  # 不填充端面，让它和柱子重叠
    links.new(arc_translate.outputs['Geometry'], curve_to_mesh.inputs['Curve'])
    links.new(rect.outputs['Curve'], curve_to_mesh.inputs['Profile Curve'])

    # ========== 合并所有几何体 ==========
    join_all = nodes.new(type='GeometryNodeJoinGeometry')
    join_all.location = (1000, 100)
    links.new(left_transform.outputs['Geometry'], join_all.inputs['Geometry'])
    links.new(right_transform.outputs['Geometry'], join_all.inputs['Geometry'])
    links.new(curve_to_mesh.outputs['Mesh'], join_all.inputs['Geometry'])

    # ========== 平滑着色 ==========
    shade_smooth = nodes.new(type='GeometryNodeSetShadeSmooth')
    shade_smooth.location = (1200, 100)
    shade_smooth.inputs['Shade Smooth'].default_value = True
    links.new(join_all.outputs['Geometry'], shade_smooth.inputs['Geometry'])

    links.new(shade_smooth.outputs['Geometry'], output_node.inputs['Geometry'])

    print("✓ 创建节点组: G_Arch_Complete")
    return ng


def create_g_curve_to_mesh() -> bpy.types.NodeTree:
    """
    创建 G_Curve_To_Mesh 节点组
    功能：将曲线转换为网格（沿路径挤出截面）
    用途：管道、栏杆、扶手、电线
    """
    ng = NodeGroupFactory.create_node_group("G_Curve_To_Mesh")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口 - 两个曲线输入（路径和截面）
    ng.interface.new_socket(name="Curve", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket(name="Profile", in_out='INPUT', socket_type='NodeSocketGeometry')
    
    fill_socket = ng.interface.new_socket(name="Fill_Caps", in_out='INPUT', socket_type='NodeSocketBool')
    fill_socket.default_value = True
    
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # Curve to Mesh 节点
    curve_to_mesh = nodes.new(type='GeometryNodeCurveToMesh')
    curve_to_mesh.location = (200, 0)
    
    links.new(input_node.outputs['Curve'], curve_to_mesh.inputs['Curve'])
    links.new(input_node.outputs['Profile'], curve_to_mesh.inputs['Profile Curve'])
    links.new(input_node.outputs['Fill_Caps'], curve_to_mesh.inputs['Fill Caps'])
    links.new(curve_to_mesh.outputs['Mesh'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Curve_To_Mesh")
    return ng


def create_g_pipe() -> bpy.types.NodeTree:
    """
    创建 G_Pipe 节点组
    功能：便捷地创建管道（圆形截面沿直线挤出）
    用途：简单管道、栏杆
    """
    ng = NodeGroupFactory.create_node_group("G_Pipe")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    radius_socket = ng.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    radius_socket.default_value = 0.05
    radius_socket.min_value = 0.001
    
    length_socket = ng.interface.new_socket(name="Length", in_out='INPUT', socket_type='NodeSocketFloat')
    length_socket.default_value = 2.0
    length_socket.min_value = 0.01
    
    res_socket = ng.interface.new_socket(name="Resolution", in_out='INPUT', socket_type='NodeSocketInt')
    res_socket.default_value = 12
    res_socket.min_value = 3
    
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 创建圆形截面
    circle = nodes.new(type='GeometryNodeCurvePrimitiveCircle')
    circle.location = (0, -150)
    circle.mode = 'RADIUS'
    
    # 创建路径（竖直线段）
    line = nodes.new(type='GeometryNodeCurvePrimitiveLine')
    line.location = (0, 0)
    line.mode = 'POINTS'
    line.inputs['Start'].default_value = (0, 0, 0)
    
    # 组合终点
    combine_end = nodes.new(type='ShaderNodeCombineXYZ')
    combine_end.location = (-150, 50)
    
    # Curve to Mesh
    curve_to_mesh = nodes.new(type='GeometryNodeCurveToMesh')
    curve_to_mesh.location = (200, 0)
    curve_to_mesh.inputs['Fill Caps'].default_value = True
    
    # 连接
    links.new(input_node.outputs['Radius'], circle.inputs['Radius'])
    links.new(input_node.outputs['Resolution'], circle.inputs['Resolution'])
    links.new(input_node.outputs['Length'], combine_end.inputs['Z'])
    links.new(combine_end.outputs['Vector'], line.inputs['End'])
    
    links.new(line.outputs['Curve'], curve_to_mesh.inputs['Curve'])
    links.new(circle.outputs['Curve'], curve_to_mesh.inputs['Profile Curve'])
    links.new(curve_to_mesh.outputs['Mesh'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Pipe (便捷管道)")
    return ng


# ========== Phase 2: 更多变形 ==========

def create_g_bend() -> bpy.types.NodeTree:
    """
    创建 G_Bend 节点组
    功能：弯曲变形 - 让几何体沿 Z 轴弯曲成圆弧

    特性：
    - 自动细分几何体（解决低顶点数问题）
    - 支持任意角度弯曲

    数学原理：
    - 将 Z 方向的长度映射到圆弧上
    - 圆弧半径 R = height / angle
    - 对于归一化高度 t (0到1)：
      - theta = angle * t
      - new_x = x * cos(theta) + (R + x) * sin(theta)
      - new_z = z_min + (R + x) * (1 - cos(theta))
    """
    ng = NodeGroupFactory.create_node_group("G_Bend")
    nodes = ng.nodes
    links = ng.links

    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)

    angle_socket = ng.interface.new_socket(name="Angle", in_out='INPUT', socket_type='NodeSocketFloat')
    angle_socket.default_value = 1.57  # π/2 = 90度
    angle_socket.min_value = 0.0
    angle_socket.max_value = 6.28  # 最大 360度

    subdiv_socket = ng.interface.new_socket(name="Subdivisions", in_out='INPUT', socket_type='NodeSocketInt')
    subdiv_socket.default_value = 3  # 默认细分3级（面数×64，平滑且不过多）
    subdiv_socket.min_value = 0
    subdiv_socket.max_value = 5

    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')

    # ===== 第一步：细分几何体 =====
    subdivide = nodes.new(type='GeometryNodeSubdivideMesh')
    subdivide.location = (-500, 100)

    # 获取边界框（从细分后的几何体）
    bbox = nodes.new(type='GeometryNodeBoundBox')
    bbox.location = (-300, -300)
    
    # 分离边界框
    sep_min = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_min.location = (-100, -350)
    
    sep_max = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_max.location = (-100, -450)
    
    # 获取位置
    position = nodes.new(type='GeometryNodeInputPosition')
    position.location = (-300, 0)
    
    sep_pos = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_pos.location = (-100, 0)
    
    # 计算归一化Z: t = (z - z_min) / (z_max - z_min)
    sub_z_min = nodes.new(type='ShaderNodeMath')
    sub_z_min.operation = 'SUBTRACT'
    sub_z_min.location = (100, 0)
    
    sub_height = nodes.new(type='ShaderNodeMath')
    sub_height.operation = 'SUBTRACT'
    sub_height.location = (100, -150)
    
    div_t = nodes.new(type='ShaderNodeMath')
    div_t.operation = 'DIVIDE'
    div_t.location = (250, -50)
    
    # theta = angle * t
    mult_theta = nodes.new(type='ShaderNodeMath')
    mult_theta.operation = 'MULTIPLY'
    mult_theta.location = (400, -50)
    
    # R = height / angle（基准半径，中心线的半径）
    div_radius = nodes.new(type='ShaderNodeMath')
    div_radius.operation = 'DIVIDE'
    div_radius.location = (250, -200)
    
    # effective_radius = R + original_x  ⚠️ 关键修复
    # 不同X位置的顶点在不同半径的圆弧上
    add_effective_r = nodes.new(type='ShaderNodeMath')
    add_effective_r.operation = 'ADD'
    add_effective_r.location = (400, -200)
    
    # ===== 正确的弯曲公式 =====
    # new_x = x * cos(theta) + (R + x) * sin(theta)
    # new_z = z_min + (R + x) * (1 - cos(theta))

    # cos(theta) 和 sin(theta)
    cos_theta = nodes.new(type='ShaderNodeMath')
    cos_theta.operation = 'COSINE'
    cos_theta.location = (550, 50)

    sin_theta = nodes.new(type='ShaderNodeMath')
    sin_theta.operation = 'SINE'
    sin_theta.location = (550, -50)

    # x * cos(theta)
    x_cos = nodes.new(type='ShaderNodeMath')
    x_cos.operation = 'MULTIPLY'
    x_cos.location = (700, 100)

    # (R + x) * sin(theta)
    r_plus_x_sin = nodes.new(type='ShaderNodeMath')
    r_plus_x_sin.operation = 'MULTIPLY'
    r_plus_x_sin.location = (700, 0)

    # new_x = x * cos(theta) + (R + x) * sin(theta)
    new_x = nodes.new(type='ShaderNodeMath')
    new_x.operation = 'ADD'
    new_x.location = (850, 50)

    # 1 - cos(theta)
    one_minus_cos = nodes.new(type='ShaderNodeMath')
    one_minus_cos.operation = 'SUBTRACT'
    one_minus_cos.location = (700, -150)
    one_minus_cos.inputs[0].default_value = 1.0

    # (R + x) * (1 - cos(theta))
    r_plus_x_1_minus_cos = nodes.new(type='ShaderNodeMath')
    r_plus_x_1_minus_cos.operation = 'MULTIPLY'
    r_plus_x_1_minus_cos.location = (850, -150)

    # new_z = z_min + (R + x) * (1 - cos(theta))
    new_z = nodes.new(type='ShaderNodeMath')
    new_z.operation = 'ADD'
    new_z.location = (1000, -150)

    combine = nodes.new(type='ShaderNodeCombineXYZ')
    combine.location = (1150, 0)

    # Set Position
    set_pos = nodes.new(type='GeometryNodeSetPosition')
    set_pos.location = (1300, 100)

    # Set Shade Smooth（平滑着色）
    shade_smooth = nodes.new(type='GeometryNodeSetShadeSmooth')
    shade_smooth.location = (1500, 100)

    # ===== 连接 =====

    # 细分几何体
    links.new(input_node.outputs['Geometry'], subdivide.inputs['Mesh'])
    links.new(input_node.outputs['Subdivisions'], subdivide.inputs['Level'])

    # 细分后的几何体 → bbox 和 set_pos
    links.new(subdivide.outputs['Mesh'], bbox.inputs['Geometry'])
    links.new(subdivide.outputs['Mesh'], set_pos.inputs['Geometry'])

    # 边界框
    links.new(bbox.outputs['Min'], sep_min.inputs['Vector'])
    links.new(bbox.outputs['Max'], sep_max.inputs['Vector'])

    # 位置
    links.new(position.outputs['Position'], sep_pos.inputs['Vector'])

    # 归一化 t = (z - z_min) / height
    links.new(sep_pos.outputs['Z'], sub_z_min.inputs[0])
    links.new(sep_min.outputs['Z'], sub_z_min.inputs[1])
    links.new(sep_max.outputs['Z'], sub_height.inputs[0])
    links.new(sep_min.outputs['Z'], sub_height.inputs[1])
    links.new(sub_z_min.outputs['Value'], div_t.inputs[0])
    links.new(sub_height.outputs['Value'], div_t.inputs[1])

    # theta = angle * t
    links.new(input_node.outputs['Angle'], mult_theta.inputs[0])
    links.new(div_t.outputs['Value'], mult_theta.inputs[1])

    # R = height / angle
    links.new(sub_height.outputs['Value'], div_radius.inputs[0])
    links.new(input_node.outputs['Angle'], div_radius.inputs[1])

    # effective_radius = R + x
    links.new(div_radius.outputs['Value'], add_effective_r.inputs[0])
    links.new(sep_pos.outputs['X'], add_effective_r.inputs[1])

    # 三角函数
    links.new(mult_theta.outputs['Value'], cos_theta.inputs[0])
    links.new(mult_theta.outputs['Value'], sin_theta.inputs[0])

    # x * cos(theta)
    links.new(sep_pos.outputs['X'], x_cos.inputs[0])
    links.new(cos_theta.outputs['Value'], x_cos.inputs[1])

    # (R + x) * sin(theta)
    links.new(add_effective_r.outputs['Value'], r_plus_x_sin.inputs[0])
    links.new(sin_theta.outputs['Value'], r_plus_x_sin.inputs[1])

    # new_x = x * cos(theta) + (R + x) * sin(theta)
    links.new(x_cos.outputs['Value'], new_x.inputs[0])
    links.new(r_plus_x_sin.outputs['Value'], new_x.inputs[1])

    # 1 - cos(theta)
    links.new(cos_theta.outputs['Value'], one_minus_cos.inputs[1])

    # (R + x) * (1 - cos(theta))
    links.new(add_effective_r.outputs['Value'], r_plus_x_1_minus_cos.inputs[0])
    links.new(one_minus_cos.outputs['Value'], r_plus_x_1_minus_cos.inputs[1])

    # new_z = z_min + (R + x) * (1 - cos(theta))
    links.new(sep_min.outputs['Z'], new_z.inputs[0])
    links.new(r_plus_x_1_minus_cos.outputs['Value'], new_z.inputs[1])

    # 组合最终位置
    links.new(new_x.outputs['Value'], combine.inputs['X'])
    links.new(sep_pos.outputs['Y'], combine.inputs['Y'])
    links.new(new_z.outputs['Value'], combine.inputs['Z'])

    links.new(combine.outputs['Vector'], set_pos.inputs['Position'])

    # 平滑着色
    links.new(set_pos.outputs['Geometry'], shade_smooth.inputs['Geometry'])
    links.new(shade_smooth.outputs['Geometry'], output_node.inputs['Geometry'])

    print("✓ 创建节点组: G_Bend (自动细分+正确公式+平滑着色)")
    return ng


def create_g_twist() -> bpy.types.NodeTree:
    """
    创建 G_Twist 节点组
    功能：扭曲变形 - 让几何体绕 Z 轴扭曲
    用途：螺旋柱、麻花造型
    """
    ng = NodeGroupFactory.create_node_group("G_Twist")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    angle_socket = ng.interface.new_socket(name="Angle", in_out='INPUT', socket_type='NodeSocketFloat')
    angle_socket.default_value = 1.57  # 90度（弧度）
    angle_socket.min_value = -6.28
    angle_socket.max_value = 6.28
    
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 获取边界框
    bbox = nodes.new(type='GeometryNodeBoundBox')
    bbox.location = (-200, -200)
    
    # 获取位置
    position = nodes.new(type='GeometryNodeInputPosition')
    position.location = (-400, 0)
    
    sep_pos = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_pos.location = (-200, 0)
    
    sep_min = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_min.location = (0, -300)
    
    sep_max = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_max.location = (0, -400)
    
    # 归一化 Z
    sub_z = nodes.new(type='ShaderNodeMath')
    sub_z.operation = 'SUBTRACT'
    sub_z.location = (150, -100)
    
    sub_range = nodes.new(type='ShaderNodeMath')
    sub_range.operation = 'SUBTRACT'
    sub_range.location = (150, -250)
    
    div_norm = nodes.new(type='ShaderNodeMath')
    div_norm.operation = 'DIVIDE'
    div_norm.location = (300, -150)
    
    # 计算旋转角度 = angle * normalized_z
    mult_angle = nodes.new(type='ShaderNodeMath')
    mult_angle.operation = 'MULTIPLY'
    mult_angle.location = (450, -100)
    
    # 旋转 XY 坐标
    # new_x = x * cos(theta) - y * sin(theta)
    # new_y = x * sin(theta) + y * cos(theta)
    cos_node = nodes.new(type='ShaderNodeMath')
    cos_node.operation = 'COSINE'
    cos_node.location = (600, -50)
    
    sin_node = nodes.new(type='ShaderNodeMath')
    sin_node.operation = 'SINE'
    sin_node.location = (600, -150)
    
    # x * cos
    mult_x_cos = nodes.new(type='ShaderNodeMath')
    mult_x_cos.operation = 'MULTIPLY'
    mult_x_cos.location = (750, 50)
    
    # y * sin
    mult_y_sin = nodes.new(type='ShaderNodeMath')
    mult_y_sin.operation = 'MULTIPLY'
    mult_y_sin.location = (750, -50)
    
    # x * sin
    mult_x_sin = nodes.new(type='ShaderNodeMath')
    mult_x_sin.operation = 'MULTIPLY'
    mult_x_sin.location = (750, -150)
    
    # y * cos
    mult_y_cos = nodes.new(type='ShaderNodeMath')
    mult_y_cos.operation = 'MULTIPLY'
    mult_y_cos.location = (750, -250)
    
    # new_x = x*cos - y*sin
    sub_new_x = nodes.new(type='ShaderNodeMath')
    sub_new_x.operation = 'SUBTRACT'
    sub_new_x.location = (900, 0)
    
    # new_y = x*sin + y*cos
    add_new_y = nodes.new(type='ShaderNodeMath')
    add_new_y.operation = 'ADD'
    add_new_y.location = (900, -200)
    
    # 组合
    combine = nodes.new(type='ShaderNodeCombineXYZ')
    combine.location = (1050, 0)
    
    # Set Position
    set_pos = nodes.new(type='GeometryNodeSetPosition')
    set_pos.location = (1200, 100)
    
    # 连接
    links.new(input_node.outputs['Geometry'], bbox.inputs['Geometry'])
    links.new(input_node.outputs['Geometry'], set_pos.inputs['Geometry'])
    links.new(position.outputs['Position'], sep_pos.inputs['Vector'])
    links.new(bbox.outputs['Min'], sep_min.inputs['Vector'])
    links.new(bbox.outputs['Max'], sep_max.inputs['Vector'])
    
    # 归一化
    links.new(sep_pos.outputs['Z'], sub_z.inputs[0])
    links.new(sep_min.outputs['Z'], sub_z.inputs[1])
    links.new(sep_max.outputs['Z'], sub_range.inputs[0])
    links.new(sep_min.outputs['Z'], sub_range.inputs[1])
    links.new(sub_z.outputs['Value'], div_norm.inputs[0])
    links.new(sub_range.outputs['Value'], div_norm.inputs[1])
    
    # 角度
    links.new(input_node.outputs['Angle'], mult_angle.inputs[0])
    links.new(div_norm.outputs['Value'], mult_angle.inputs[1])
    links.new(mult_angle.outputs['Value'], cos_node.inputs[0])
    links.new(mult_angle.outputs['Value'], sin_node.inputs[0])
    
    # 旋转计算
    links.new(sep_pos.outputs['X'], mult_x_cos.inputs[0])
    links.new(cos_node.outputs['Value'], mult_x_cos.inputs[1])
    links.new(sep_pos.outputs['Y'], mult_y_sin.inputs[0])
    links.new(sin_node.outputs['Value'], mult_y_sin.inputs[1])
    links.new(sep_pos.outputs['X'], mult_x_sin.inputs[0])
    links.new(sin_node.outputs['Value'], mult_x_sin.inputs[1])
    links.new(sep_pos.outputs['Y'], mult_y_cos.inputs[0])
    links.new(cos_node.outputs['Value'], mult_y_cos.inputs[1])
    
    links.new(mult_x_cos.outputs['Value'], sub_new_x.inputs[0])
    links.new(mult_y_sin.outputs['Value'], sub_new_x.inputs[1])
    links.new(mult_x_sin.outputs['Value'], add_new_y.inputs[0])
    links.new(mult_y_cos.outputs['Value'], add_new_y.inputs[1])
    
    links.new(sub_new_x.outputs['Value'], combine.inputs['X'])
    links.new(add_new_y.outputs['Value'], combine.inputs['Y'])
    links.new(sep_pos.outputs['Z'], combine.inputs['Z'])
    
    links.new(combine.outputs['Vector'], set_pos.inputs['Position'])
    links.new(set_pos.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Twist (扭曲)")
    return ng


# ========== Phase 3: 阵列能力 ==========

def create_g_array_linear() -> bpy.types.NodeTree:
    """
    创建 G_Array_Linear 节点组
    功能：线性阵列 - 沿指定方向复制几何体
    用途：栅栏、楼梯、重复结构
    """
    ng = NodeGroupFactory.create_node_group("G_Array_Linear")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    count_socket = ng.interface.new_socket(name="Count", in_out='INPUT', socket_type='NodeSocketInt')
    count_socket.default_value = 5
    count_socket.min_value = 1
    count_socket.max_value = 100
    
    offset_socket = ng.interface.new_socket(name="Offset", in_out='INPUT', socket_type='NodeSocketVector')
    offset_socket.default_value = (1.0, 0.0, 0.0)
    
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 创建线性点分布
    line = nodes.new(type='GeometryNodeCurvePrimitiveLine')
    line.location = (0, -150)
    line.mode = 'POINTS'
    line.inputs['Start'].default_value = (0, 0, 0)
    
    # 计算终点 = offset * (count - 1)
    sub_one = nodes.new(type='ShaderNodeMath')
    sub_one.operation = 'SUBTRACT'
    sub_one.location = (-200, -200)
    sub_one.inputs[1].default_value = 1.0
    
    # 转换 int 到 float
    int_to_float = nodes.new(type='ShaderNodeMath')
    int_to_float.operation = 'ADD'
    int_to_float.location = (-350, -200)
    int_to_float.inputs[1].default_value = 0.0
    
    scale_offset = nodes.new(type='ShaderNodeVectorMath')
    scale_offset.operation = 'SCALE'
    scale_offset.location = (-50, -200)
    
    # 重采样曲线得到点
    resample = nodes.new(type='GeometryNodeResampleCurve')
    resample.location = (200, -150)
    resample.mode = 'COUNT'
    
    # Instance on Points
    instance = nodes.new(type='GeometryNodeInstanceOnPoints')
    instance.location = (400, 0)
    
    # Realize Instances
    realize = nodes.new(type='GeometryNodeRealizeInstances')
    realize.location = (600, 0)
    
    # 连接
    links.new(input_node.outputs['Count'], int_to_float.inputs[0])
    links.new(int_to_float.outputs['Value'], sub_one.inputs[0])
    links.new(input_node.outputs['Offset'], scale_offset.inputs[0])
    links.new(sub_one.outputs['Value'], scale_offset.inputs['Scale'])
    links.new(scale_offset.outputs['Vector'], line.inputs['End'])
    
    links.new(line.outputs['Curve'], resample.inputs['Curve'])
    links.new(input_node.outputs['Count'], resample.inputs['Count'])
    
    links.new(resample.outputs['Curve'], instance.inputs['Points'])
    links.new(input_node.outputs['Geometry'], instance.inputs['Instance'])
    
    links.new(instance.outputs['Instances'], realize.inputs['Geometry'])
    links.new(realize.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Array_Linear (线性阵列)")
    return ng


def create_g_array_circular() -> bpy.types.NodeTree:
    """
    创建 G_Array_Circular 节点组
    功能：环形阵列 - 围绕 Z 轴复制几何体
    用途：圆桌椅子、吊灯、车轮辐条
    """
    ng = NodeGroupFactory.create_node_group("G_Array_Circular")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    count_socket = ng.interface.new_socket(name="Count", in_out='INPUT', socket_type='NodeSocketInt')
    count_socket.default_value = 6
    count_socket.min_value = 1
    count_socket.max_value = 64
    
    radius_socket = ng.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    radius_socket.default_value = 1.0
    radius_socket.min_value = 0.0
    
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 创建圆形曲线
    circle = nodes.new(type='GeometryNodeCurvePrimitiveCircle')
    circle.location = (0, -150)
    circle.mode = 'RADIUS'
    
    # 重采样得到点
    resample = nodes.new(type='GeometryNodeResampleCurve')
    resample.location = (200, -150)
    resample.mode = 'COUNT'
    
    # Instance on Points (带旋转)
    instance = nodes.new(type='GeometryNodeInstanceOnPoints')
    instance.location = (400, 0)
    
    # 获取切线用于旋转
    curve_tangent = nodes.new(type='GeometryNodeInputTangent')
    curve_tangent.location = (200, -300)
    
    # Align Euler to Vector
    align_euler = nodes.new(type='FunctionNodeAlignEulerToVector')
    align_euler.location = (350, -300)
    align_euler.axis = 'X'
    
    # Realize Instances
    realize = nodes.new(type='GeometryNodeRealizeInstances')
    realize.location = (600, 0)
    
    # 连接
    links.new(input_node.outputs['Radius'], circle.inputs['Radius'])
    links.new(circle.outputs['Curve'], resample.inputs['Curve'])
    links.new(input_node.outputs['Count'], resample.inputs['Count'])
    
    links.new(resample.outputs['Curve'], instance.inputs['Points'])
    links.new(input_node.outputs['Geometry'], instance.inputs['Instance'])
    
    # 旋转使实例朝向圆心
    links.new(curve_tangent.outputs['Tangent'], align_euler.inputs['Vector'])
    links.new(align_euler.outputs['Rotation'], instance.inputs['Rotation'])
    
    links.new(instance.outputs['Instances'], realize.inputs['Geometry'])
    links.new(realize.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Array_Circular (环形阵列)")
    return ng


# ========== Phase 4: 多流构建支持 ==========

def create_g_instance_on_points() -> bpy.types.NodeTree:
    """
    创建 G_Instance_On_Points 节点组
    功能：在输入几何体的顶点/面上实例化另一个几何体
    
    这是复杂度的核心来源：
    - 生成 1 个精细的螺丝，在复杂表面实例化 1000 次
    - 模型瞬间变得极其复杂，但计算量很小
    
    用途：铆钉、螺丝、装饰细节、重复性结构
    """
    ng = NodeGroupFactory.create_node_group("G_Instance_On_Points")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口 - 两个几何体输入
    ng.interface.new_socket(name="Points", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket(name="Instance", in_out='INPUT', socket_type='NodeSocketGeometry')
    
    scale_socket = ng.interface.new_socket(name="Scale", in_out='INPUT', socket_type='NodeSocketFloat')
    scale_socket.default_value = 1.0
    scale_socket.min_value = 0.01
    
    align_socket = ng.interface.new_socket(name="Align_To_Normal", in_out='INPUT', socket_type='NodeSocketBool')
    align_socket.default_value = True
    
    seed_socket = ng.interface.new_socket(name="Seed", in_out='INPUT', socket_type='NodeSocketInt')
    seed_socket.default_value = 0
    
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # Mesh to Points（将顶点转为点云）
    mesh_to_points = nodes.new(type='GeometryNodeMeshToPoints')
    mesh_to_points.location = (0, 100)
    mesh_to_points.mode = 'VERTICES'
    
    # Instance on Points
    instance_on_points = nodes.new(type='GeometryNodeInstanceOnPoints')
    instance_on_points.location = (200, 100)
    
    # 获取法线用于对齐
    normal_node = nodes.new(type='GeometryNodeInputNormal')
    normal_node.location = (0, -100)
    
    # Align Euler to Vector（对齐到法线）
    align_euler = nodes.new(type='FunctionNodeAlignEulerToVector')
    align_euler.location = (100, -100)
    align_euler.axis = 'Z'
    
    # 缩放
    combine_scale = nodes.new(type='ShaderNodeCombineXYZ')
    combine_scale.location = (0, -200)
    
    # Realize Instances
    realize = nodes.new(type='GeometryNodeRealizeInstances')
    realize.location = (400, 100)
    
    # 连接
    links.new(input_node.outputs['Points'], mesh_to_points.inputs['Mesh'])
    links.new(mesh_to_points.outputs['Points'], instance_on_points.inputs['Points'])
    links.new(input_node.outputs['Instance'], instance_on_points.inputs['Instance'])
    
    # 缩放
    links.new(input_node.outputs['Scale'], combine_scale.inputs['X'])
    links.new(input_node.outputs['Scale'], combine_scale.inputs['Y'])
    links.new(input_node.outputs['Scale'], combine_scale.inputs['Z'])
    links.new(combine_scale.outputs['Vector'], instance_on_points.inputs['Scale'])
    
    # 对齐法线
    links.new(normal_node.outputs['Normal'], align_euler.inputs['Vector'])
    links.new(align_euler.outputs['Rotation'], instance_on_points.inputs['Rotation'])
    
    links.new(instance_on_points.outputs['Instances'], realize.inputs['Geometry'])
    links.new(realize.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Instance_On_Points (通用点实例化)")
    return ng


def create_g_panel_grid() -> bpy.types.NodeTree:
    """
    创建 G_Panel_Grid 节点组
    功能：在表面生成面板网格（如玻璃幕墙）
    
    用途：建筑幕墙、科幻面板、太阳能板阵列
    """
    ng = NodeGroupFactory.create_node_group("G_Panel_Grid")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    rows_socket = ng.interface.new_socket(name="Rows", in_out='INPUT', socket_type='NodeSocketInt')
    rows_socket.default_value = 4
    rows_socket.min_value = 1
    rows_socket.max_value = 50
    
    cols_socket = ng.interface.new_socket(name="Columns", in_out='INPUT', socket_type='NodeSocketInt')
    cols_socket.default_value = 4
    cols_socket.min_value = 1
    cols_socket.max_value = 50
    
    gap_socket = ng.interface.new_socket(name="Gap", in_out='INPUT', socket_type='NodeSocketFloat')
    gap_socket.default_value = 0.02
    gap_socket.min_value = 0.0
    gap_socket.max_value = 0.5
    
    inset_socket = ng.interface.new_socket(name="Inset", in_out='INPUT', socket_type='NodeSocketFloat')
    inset_socket.default_value = 0.01
    inset_socket.min_value = 0.0
    inset_socket.max_value = 0.2
    
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # Subdivide Mesh（细分以创建网格）
    subdivide = nodes.new(type='GeometryNodeSubdivideMesh')
    subdivide.location = (0, 0)
    
    # 细分级别 = log2(rows * cols) 大约
    # 简化：直接使用行数作为细分级别
    math_sub = nodes.new(type='ShaderNodeMath')
    math_sub.operation = 'SUBTRACT'
    math_sub.location = (-150, -100)
    math_sub.inputs[1].default_value = 1
    
    # Extrude Mesh（挤出创建深度）
    extrude = nodes.new(type='GeometryNodeExtrudeMesh')
    extrude.location = (200, 0)
    extrude.mode = 'FACES'
    
    # 缩放面（创建间隙）
    scale_elements = nodes.new(type='GeometryNodeScaleElements')
    scale_elements.location = (400, 0)
    
    # 计算缩放比例 = 1 - gap
    math_scale = nodes.new(type='ShaderNodeMath')
    math_scale.operation = 'SUBTRACT'
    math_scale.location = (250, -150)
    math_scale.inputs[0].default_value = 1.0
    
    # 连接
    links.new(input_node.outputs['Geometry'], subdivide.inputs['Mesh'])
    links.new(input_node.outputs['Rows'], math_sub.inputs[0])
    links.new(math_sub.outputs['Value'], subdivide.inputs['Level'])
    
    links.new(subdivide.outputs['Mesh'], extrude.inputs['Mesh'])
    links.new(input_node.outputs['Inset'], extrude.inputs['Offset'])
    
    links.new(extrude.outputs['Mesh'], scale_elements.inputs['Geometry'])
    links.new(extrude.outputs['Top'], scale_elements.inputs['Selection'])
    links.new(input_node.outputs['Gap'], math_scale.inputs[1])
    links.new(math_scale.outputs['Value'], scale_elements.inputs['Scale'])
    
    links.new(scale_elements.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Panel_Grid (面板网格)")
    return ng


def create_g_boolean_random_cut() -> bpy.types.NodeTree:
    """
    创建 G_Boolean_Random_Cut 节点组
    功能：随机布尔切割 - 在物体表面"啃"出缺口
    
    原理："减法"往往比"加法"更容易产生复杂形状
    
    用途：机械零件、战损效果、科幻凹槽
    """
    ng = NodeGroupFactory.create_node_group("G_Boolean_Random_Cut")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    count_socket = ng.interface.new_socket(name="Count", in_out='INPUT', socket_type='NodeSocketInt')
    count_socket.default_value = 5
    count_socket.min_value = 1
    count_socket.max_value = 20
    
    size_socket = ng.interface.new_socket(name="Cut_Size", in_out='INPUT', socket_type='NodeSocketFloat')
    size_socket.default_value = 0.3
    size_socket.min_value = 0.01
    
    depth_socket = ng.interface.new_socket(name="Depth", in_out='INPUT', socket_type='NodeSocketFloat')
    depth_socket.default_value = 0.2
    depth_socket.min_value = 0.01
    
    seed_socket = ng.interface.new_socket(name="Seed", in_out='INPUT', socket_type='NodeSocketInt')
    seed_socket.default_value = 0
    
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # 获取边界框用于定位切割
    bbox = nodes.new(type='GeometryNodeBoundBox')
    bbox.location = (-200, -100)
    
    # 在表面分布点
    distribute = nodes.new(type='GeometryNodeDistributePointsOnFaces')
    distribute.location = (0, -200)
    distribute.distribute_method = 'RANDOM'
    
    # 创建切割立方体
    cut_cube = nodes.new(type='GeometryNodeMeshCube')
    cut_cube.location = (0, -400)
    
    # 组合尺寸
    combine_size = nodes.new(type='ShaderNodeCombineXYZ')
    combine_size.location = (-150, -400)
    
    # Instance on Points（在分布点上放置切割体）
    instance = nodes.new(type='GeometryNodeInstanceOnPoints')
    instance.location = (200, -200)
    
    # 获取法线用于对齐
    normal = nodes.new(type='GeometryNodeInputNormal')
    normal.location = (0, -300)
    
    # Align to normal
    align = nodes.new(type='FunctionNodeAlignEulerToVector')
    align.location = (100, -300)
    align.axis = 'Z'
    
    # Realize
    realize = nodes.new(type='GeometryNodeRealizeInstances')
    realize.location = (400, -200)
    
    # Boolean 切割
    boolean = nodes.new(type='GeometryNodeMeshBoolean')
    boolean.location = (600, 0)
    boolean.operation = 'DIFFERENCE'
    
    # 连接
    links.new(input_node.outputs['Geometry'], bbox.inputs['Geometry'])
    links.new(input_node.outputs['Geometry'], distribute.inputs['Mesh'])
    links.new(input_node.outputs['Count'], distribute.inputs['Density'])  # 用 count 作为密度
    links.new(input_node.outputs['Seed'], distribute.inputs['Seed'])
    
    # 切割体尺寸
    links.new(input_node.outputs['Cut_Size'], combine_size.inputs['X'])
    links.new(input_node.outputs['Cut_Size'], combine_size.inputs['Y'])
    links.new(input_node.outputs['Depth'], combine_size.inputs['Z'])
    links.new(combine_size.outputs['Vector'], cut_cube.inputs['Size'])
    
    # 实例化
    links.new(distribute.outputs['Points'], instance.inputs['Points'])
    links.new(cut_cube.outputs['Mesh'], instance.inputs['Instance'])
    links.new(normal.outputs['Normal'], align.inputs['Vector'])
    links.new(align.outputs['Rotation'], instance.inputs['Rotation'])
    
    links.new(instance.outputs['Instances'], realize.inputs['Geometry'])
    
    # 布尔切割
    links.new(input_node.outputs['Geometry'], boolean.inputs['Mesh 1'])
    links.new(realize.outputs['Geometry'], boolean.inputs['Mesh 2'])
    
    links.new(boolean.outputs['Mesh'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Boolean_Random_Cut (随机布尔雕刻)")
    return ng


def create_g_edge_detail() -> bpy.types.NodeTree:
    """
    创建 G_Edge_Detail 节点组
    功能：沿边缘添加细节（如霓虹灯带、金属条）
    
    用途：建筑边缘灯带、科幻装饰线
    """
    ng = NodeGroupFactory.create_node_group("G_Edge_Detail")
    nodes = ng.nodes
    links = ng.links
    
    # 添加接口
    NodeGroupFactory.add_geometry_interface(ng, has_input=True, has_output=True)
    
    radius_socket = ng.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    radius_socket.default_value = 0.02
    radius_socket.min_value = 0.001
    
    res_socket = ng.interface.new_socket(name="Resolution", in_out='INPUT', socket_type='NodeSocketInt')
    res_socket.default_value = 8
    res_socket.min_value = 3
    
    input_node = nodes.get('Group Input')
    output_node = nodes.get('Group Output')
    
    # Mesh to Curve（提取边缘为曲线）
    mesh_to_curve = nodes.new(type='GeometryNodeMeshToCurve')
    mesh_to_curve.location = (0, 0)
    
    # 创建圆形截面
    circle = nodes.new(type='GeometryNodeCurvePrimitiveCircle')
    circle.location = (0, -150)
    circle.mode = 'RADIUS'
    
    # Curve to Mesh（曲线转网格）
    curve_to_mesh = nodes.new(type='GeometryNodeCurveToMesh')
    curve_to_mesh.location = (200, 0)
    
    # Join with original
    join = nodes.new(type='GeometryNodeJoinGeometry')
    join.location = (400, 50)
    
    # 连接
    links.new(input_node.outputs['Geometry'], mesh_to_curve.inputs['Mesh'])
    links.new(input_node.outputs['Radius'], circle.inputs['Radius'])
    links.new(input_node.outputs['Resolution'], circle.inputs['Resolution'])
    
    links.new(mesh_to_curve.outputs['Curve'], curve_to_mesh.inputs['Curve'])
    links.new(circle.outputs['Curve'], curve_to_mesh.inputs['Profile Curve'])
    
    links.new(input_node.outputs['Geometry'], join.inputs['Geometry'])
    links.new(curve_to_mesh.outputs['Mesh'], join.inputs['Geometry'])
    
    links.new(join.outputs['Geometry'], output_node.inputs['Geometry'])
    
    print("✓ 创建节点组: G_Edge_Detail (边缘细节)")
    return ng


# ========== 主函数 ==========

def create_all_node_groups():
    """创建所有节点组"""
    print("\n" + "=" * 60)
    print("开始创建节点组库...")
    print("=" * 60 + "\n")
    
    # 创建所有节点组
    groups = [
        # 基础几何体（原点在底部中心，适合放置在地面）
        create_g_base_cube,
        create_g_base_cylinder, 
        create_g_base_sphere,
        create_g_base_wedge,
        # 基础几何体（原点在几何中心，适合旋转）
        create_g_base_cube_centered,
        create_g_base_cylinder_centered,
        create_g_base_sphere_centered,
        # 变形节点组
        create_g_taper,
        create_g_shear,
        create_g_smooth,
        create_g_bend,                # Phase 2: 弯曲
        create_g_twist,               # Phase 2: 扭曲
        # 曲线节点组 (Phase 1)
        create_g_curve_circle,
        create_g_curve_line,
        create_g_curve_arc,           # 圆弧曲线（用于拱门）
        create_g_curve_rectangle,     # 矩形曲线（用于截面）
        create_g_curve_to_mesh,
        create_g_pipe,                # 便捷管道
        create_g_arch,                # 均匀截面拱顶（曲线挤出）
        create_g_arch_complete,       # 完整拱门（柱+拱，顶点缝合）
        # 阵列节点组 (Phase 3)
        create_g_array_linear,
        create_g_array_circular,
        # 多流构建支持 (Phase 4) - 复杂度倍增器
        create_g_instance_on_points,  # 通用点实例化 ⭐ 复杂度神器
        create_g_panel_grid,          # 面板网格（玻璃幕墙）
        create_g_boolean_random_cut,  # 随机布尔雕刻 ⭐ 细节神器
        create_g_edge_detail,         # 边缘细节（霓虹灯带）
        # 效果处理
        create_g_damage_edges,
        create_g_scatter_moss,
        create_g_scatter_on_top,
        create_g_boolean_cut,
        create_g_voxel_remesh,
        # 后处理
        create_g_align_ground,
    ]
    
    created = []
    for create_func in groups:
        try:
            ng = create_func()
            created.append(ng.name)
        except Exception as e:
            print(f"✗ 创建失败: {create_func.__name__} - {e}")
    
    print("\n" + "=" * 60)
    print(f"完成！共创建 {len(created)} 个节点组:")
    for name in created:
        print(f"  - {name}")
    print("=" * 60 + "\n")
    
    return created


def save_library(filepath: str = None):
    """
    保存节点组库
    
    Args:
        filepath: 保存路径，默认为 assets/node_library.blend
    """
    if filepath is None:
        # 获取项目根目录（脚本在 scripts/ 下）
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        assets_dir = os.path.join(project_root, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        filepath = os.path.join(assets_dir, "node_library.blend")

    # 删除已存在的文件（避免 Blender 重命名为 node_library1.blend）
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"✓ 已删除旧文件: {filepath}")

    # 保存文件
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"✓ 库文件已保存到: {filepath}")
    return filepath


def main():
    """主入口函数"""
    import sys
    
    # 解析命令行参数
    output_path = None
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1:]
        for i, arg in enumerate(argv):
            if arg in ("--output", "-o") and i + 1 < len(argv):
                output_path = argv[i + 1]
    
    # 创建所有节点组
    create_all_node_groups()
    
    # 保存库文件
    if bpy.app.background:
        # 命令行模式：自动保存
        save_library(output_path)
    else:
        print("\n💡 提示：在 Blender 中手动保存文件，或调用 save_library() 函数")
        print("   示例: save_library('C:/path/to/node_library.blend')")


# 运行
if __name__ == "__main__":
    main()

