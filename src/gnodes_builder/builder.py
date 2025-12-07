"""
AI驱动的Blender几何节点构建器
通过"胶水代码"模式，将Blender Geometry Nodes封装成简单API供AI调用

核心哲学：
- 人类负责定义"原子级"规则（Node Groups）
- AI负责进行"分子级"组装
- 保证模型绝对工整，同时赋予AI创作自由
"""

import bpy
from mathutils import Vector
from typing import Dict, Any, Optional, List, Tuple


class GNodesBuilder:
    """
    给AI使用的简易封装器。
    隐藏了复杂的Socket连接和API细节。
    """
    
    def __init__(self, target_object_name: str = "AI_Generated_Model", 
                 library_path: Optional[str] = None):
        """
        初始化构建器
        
        Args:
            target_object_name: 生成物体的名称
            library_path: 节点组库.blend文件路径（可选）
        """
        # 加载节点组库（如果提供）
        if library_path:
            self._load_node_library(library_path)
        
        # 1. 创建或清空目标物体
        if target_object_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[target_object_name], do_unlink=True)
        
        bpy.ops.mesh.primitive_cube_add()
        self.obj = bpy.context.object
        self.obj.name = target_object_name
        
        # 2. 添加几何节点修改器
        self.mod = self.obj.modifiers.new(name="AI_GNodes", type='NODES')
        self.node_group = bpy.data.node_groups.new(name=f"AI_NodeTree_{target_object_name}", 
                                                   type='GeometryNodeTree')
        self.mod.node_group = self.node_group
        
        # 3. 创建输入输出节点
        self.nodes = self.node_group.nodes
        self.links = self.node_group.links
        self.input_node = self.nodes.new('NodeGroupInput')
        self.output_node = self.nodes.new('NodeGroupOutput')
        self.input_node.location = (-400, 0)
        self.output_node.location = (800, 0)
        
        # 4. 添加 Geometry 输出接口（Blender 4.x 必须）
        # 这样 NodeGroupOutput 节点才会有 Geometry 输入 socket
        self.node_group.interface.new_socket(
            name="Geometry",
            in_out='OUTPUT',
            socket_type='NodeSocketGeometry'
        )
        
        # 记录节点链，支持分支和合并
        self.node_chain: List[Any] = []
        self.last_node = self.input_node
        self._x_offset = 0  # 用于自动布局
        
    def _load_node_library(self, library_path: str):
        """
        从外部.blend文件加载节点组库
        
        Args:
            library_path: .blend文件路径
        """
        try:
            with bpy.data.libraries.load(library_path) as (data_from, data_to):
                # 只加载节点组
                data_to.node_groups = [name for name in data_from.node_groups 
                                      if name.startswith('G_')]
            print(f"✓ 已加载节点组库: {library_path}")
        except Exception as e:
            print(f"⚠ 警告: 无法加载节点组库 {library_path}: {e}")
            print("   将使用当前场景中已有的节点组")
    
    def _find_geometry_socket(self, node, is_input: bool = True) -> Optional[Any]:
        """
        智能查找几何体Socket
        
        Args:
            node: 节点对象
            is_input: True查找输入，False查找输出
            
        Returns:
            找到的Socket或None
        """
        sockets = node.inputs if is_input else node.outputs
        for socket in sockets:
            if socket.type == 'GEOMETRY':
                return socket
        return None
    
    def add_node_group(self, 
                      group_name: str, 
                      location_offset: Tuple[float, float] = (200, 0),
                      inputs: Optional[Dict[str, Any]] = None,
                      connect_to: Optional[Any] = None) -> 'GNodesBuilder':
        """
        核心方法：添加一个预制的节点组
        
        Args:
            group_name: 节点组名称（必须以G_开头）
            location_offset: 节点位置偏移量
            inputs: 输入参数字典
            connect_to: 连接到指定节点（默认连接到上一个节点）
            
        Returns:
            self，支持链式调用
        """
        # 检查节点组是否存在
        if group_name not in bpy.data.node_groups:
            available = [name for name in bpy.data.node_groups.keys() if name.startswith('G_')]
            raise ValueError(
                f"错误：节点组 '{group_name}' 不存在！\n"
                f"可用节点组: {available if available else '无'}\n"
                f"请检查库文件或先创建节点组。"
            )
        
        # 创建节点
        node = self.nodes.new(type='GeometryNodeGroup')
        node.node_tree = bpy.data.node_groups[group_name]
        node.label = group_name  # 便于在视图中识别
        
        # 自动排版
        if connect_to:
            last_loc = connect_to.location
        else:
            last_loc = self.last_node.location
        self._x_offset += location_offset[0]
        node.location = (last_loc[0] + location_offset[0], 
                        last_loc[1] + location_offset[1])
        
        # 设置输入参数
        if inputs:
            for key, value in inputs.items():
                # 尝试精确匹配
                if key in node.inputs:
                    socket = node.inputs[key]
                    # 类型转换和验证
                    if socket.type == 'VECTOR' and isinstance(value, (list, tuple)):
                        socket.default_value = Vector(value)
                    elif socket.type == 'INT' and isinstance(value, float):
                        socket.default_value = int(value)
                    elif socket.type == 'FLOAT' and isinstance(value, int):
                        socket.default_value = float(value)
                    else:
                        socket.default_value = value
                else:
                    # 模糊匹配（忽略大小写和空格）
                    matched = False
                    for socket in node.inputs:
                        if socket.name.lower().replace(' ', '_') == key.lower().replace(' ', '_'):
                            socket.default_value = value
                            matched = True
                            break
                    if not matched:
                        print(f"⚠ 警告: 节点组 '{group_name}' 没有输入 '{key}'")
        
        # 自动连接几何体
        source_node = connect_to if connect_to else self.last_node
        source_socket = self._find_geometry_socket(source_node, is_input=False)
        target_socket = self._find_geometry_socket(node, is_input=True)
        
        if source_socket and target_socket:
            try:
                self.links.new(source_socket, target_socket)
            except Exception as e:
                print(f"⚠ 警告: 无法连接节点: {e}")
        
        # 更新链
        self.node_chain.append(node)
        self.last_node = node
        
        return self
    
    def add_custom_node(self, 
                       node_type: str,
                       location_offset: Tuple[float, float] = (200, 0),
                       inputs: Optional[Dict[str, Any]] = None) -> 'GNodesBuilder':
        """
        添加自定义节点（非节点组）
        
        Args:
            node_type: 节点类型（如'GeometryNodeMeshCube'）
            location_offset: 位置偏移
            inputs: 输入参数
        """
        node = self.nodes.new(type=node_type)
        self._x_offset += location_offset[0]
        node.location = (self.last_node.location[0] + location_offset[0],
                        self.last_node.location[1] + location_offset[1])
        
        if inputs:
            for key, value in inputs.items():
                if key in node.inputs:
                    node.inputs[key].default_value = value
        
        # 自动连接
        source_socket = self._find_geometry_socket(self.last_node, is_input=False)
        target_socket = self._find_geometry_socket(node, is_input=True)
        if source_socket and target_socket:
            self.links.new(source_socket, target_socket)
        
        self.node_chain.append(node)
        self.last_node = node
        return self
    
    def branch(self) -> 'GNodesBuilder':
        """
        创建分支点，用于组合多个几何体
        
        Returns:
            新的构建器实例（共享同一个节点组）
        """
        # 返回一个标记，表示这是分支点
        self._branch_point = self.last_node
        return self
    
    def join_geometries(self, *branches: List[Any]) -> 'GNodesBuilder':
        """
        合并多个几何体分支（同一 builder 内的节点）
        
        Args:
            *branches: 多个节点列表（每个分支的最后一个节点）
        """
        # 添加Join Geometry节点
        join_node = self.nodes.new(type='GeometryNodeJoinGeometry')
        self._x_offset += 200
        join_node.location = (self._x_offset, 0)
        
        # 连接所有分支
        for i, branch_end in enumerate(branches):
            source_socket = self._find_geometry_socket(branch_end, is_input=False)
            if source_socket:
                # Join Geometry有多个Geometry输入
                if i < len(join_node.inputs):
                    self.links.new(source_socket, join_node.inputs[i])
        
        self.last_node = join_node
        self.node_chain.append(join_node)
        return self
    
    def get_last_node(self) -> Any:
        """
        获取当前几何体流的最后一个节点
        用于多流构建时传递给 join_geometries
        
        Returns:
            最后一个节点对象
        """
        return self.last_node
    
    def get_node_group(self) -> bpy.types.NodeTree:
        """
        获取底层节点树
        高级用法：用于跨 builder 操作
        
        Returns:
            节点树对象
        """
        return self.node_group
    
    def finalize(self) -> 'GNodesBuilder':
        """
        最后一步：连接到最终输出
        
        Returns:
            self
        """
        output_socket = self._find_geometry_socket(self.output_node, is_input=True)
        source_socket = self._find_geometry_socket(self.last_node, is_input=False)
        
        if source_socket and output_socket:
            self.links.new(source_socket, output_socket)
            print(f"✓ 模型 '{self.obj.name}' 生成完毕。")
        else:
            print(f"⚠ 警告: 无法连接到输出节点")
        
        return self
    
    def get_object(self):
        """获取生成的物体对象"""
        return self.obj
    
    def set_location(self, x: float, y: float, z: float) -> 'GNodesBuilder':
        """
        设置物体位置
        
        Args:
            x, y, z: 位置坐标
        """
        self.obj.location = (x, y, z)
        return self
    
    def set_rotation(self, rx: float, ry: float, rz: float) -> 'GNodesBuilder':
        """
        设置物体旋转（欧拉角，弧度）
        
        Args:
            rx, ry, rz: 旋转角度（弧度）
        """
        self.obj.rotation_euler = (rx, ry, rz)
        return self
    
    def set_rotation_degrees(self, rx: float, ry: float, rz: float) -> 'GNodesBuilder':
        """
        设置物体旋转（角度制）
        
        Args:
            rx, ry, rz: 旋转角度（度）
        """
        import math
        self.obj.rotation_euler = (
            math.radians(rx),
            math.radians(ry),
            math.radians(rz)
        )
        return self
    
    # ========== 语义化空间API ==========
    
    def face_towards(self, target_x: float, target_y: float) -> 'GNodesBuilder':
        """
        让物体朝向指定位置（仅XY平面，Z轴旋转）
        
        Args:
            target_x, target_y: 目标位置的X、Y坐标
            
        Example:
            # 让椅子面向桌子中心
            builder.set_location(2, 3, 0)
            builder.face_towards(0, 0)  # 朝向原点
        """
        import math
        dx = target_x - self.obj.location.x
        dy = target_y - self.obj.location.y
        angle = math.atan2(dy, dx)
        self.obj.rotation_euler = (0, 0, angle)
        return self
    
    def face_away_from(self, target_x: float, target_y: float) -> 'GNodesBuilder':
        """
        让物体背对指定位置（仅XY平面，Z轴旋转）
        
        Args:
            target_x, target_y: 目标位置的X、Y坐标
            
        Example:
            # 让椅子背对桌子中心（人坐下后面向桌子）
            builder.set_location(2, 3, 0)
            builder.face_away_from(0, 0)
        """
        import math
        dx = target_x - self.obj.location.x
        dy = target_y - self.obj.location.y
        angle = math.atan2(dy, dx) + math.pi
        self.obj.rotation_euler = (0, 0, angle)
        return self
    
    def rotate_around_z(self, angle_radians: float) -> 'GNodesBuilder':
        """
        在当前朝向基础上，绕Z轴额外旋转
        
        Args:
            angle_radians: 旋转角度（弧度）
            
        Example:
            # 先朝向某点，再额外旋转90度
            builder.face_towards(0, 0)
            builder.rotate_around_z(math.pi / 2)
        """
        current_z = self.obj.rotation_euler.z
        self.obj.rotation_euler = (0, 0, current_z + angle_radians)
        return self
    
    def align_tangent_to_circle(self, center_x: float, center_y: float) -> 'GNodesBuilder':
        """
        对齐到圆的切线方向（物体的X轴沿切线）
        
        Args:
            center_x, center_y: 圆心坐标
            
        Example:
            # 椅子靠背垂直于半径方向
            builder.set_location(x, y, z)
            builder.align_tangent_to_circle(0, 0)
        """
        import math
        dx = self.obj.location.x - center_x
        dy = self.obj.location.y - center_y
        radius_angle = math.atan2(dy, dx)
        # 切线方向 = 半径方向 + 90度
        tangent_angle = radius_angle + math.pi / 2
        self.obj.rotation_euler = (0, 0, tangent_angle)
        return self


# ========== 便捷工厂函数 ==========

def create_cube(name: str, size: tuple = (1, 1, 1), 
                location: tuple = (0, 0, 0),
                centered: bool = False) -> bpy.types.Object:
    """
    快速创建立方体
    
    Args:
        name: 物体名称
        size: 尺寸 (x, y, z)
        location: 位置
        centered: True=原点在中心，False=原点在底部
    
    Returns:
        创建的物体
    """
    group_name = "G_Base_Cube_Centered" if centered else "G_Base_Cube"
    builder = GNodesBuilder(name)
    builder.add_node_group(group_name, inputs={"Size": size})
    if not centered:
        builder.add_node_group("G_Align_Ground")
    builder.finalize()
    builder.set_location(*location)
    return builder.get_object()


def create_cylinder(name: str, radius: float = 0.5, height: float = 2.0,
                    resolution: int = 16, location: tuple = (0, 0, 0),
                    rotation: tuple = (0, 0, 0), centered: bool = False) -> bpy.types.Object:
    """
    快速创建圆柱
    
    Args:
        name: 物体名称
        radius: 半径
        height: 高度
        resolution: 分段数
        location: 位置
        rotation: 旋转（弧度）
        centered: True=原点在中心（适合旋转），False=原点在底部
    
    Returns:
        创建的物体
    """
    group_name = "G_Base_Cylinder_Centered" if centered else "G_Base_Cylinder"
    builder = GNodesBuilder(name)
    builder.add_node_group(group_name, inputs={
        "Radius": radius,
        "Height": height,
        "Resolution": resolution
    })
    if not centered:
        builder.add_node_group("G_Align_Ground")
    builder.finalize()
    builder.set_rotation(*rotation)
    builder.set_location(*location)
    return builder.get_object()


def create_sphere(name: str, radius: float = 1.0, resolution: int = 16,
                  location: tuple = (0, 0, 0), centered: bool = False) -> bpy.types.Object:
    """
    快速创建球体
    
    Args:
        name: 物体名称
        radius: 半径
        resolution: 分段数
        location: 位置
        centered: True=原点在中心，False=原点在底部
    
    Returns:
        创建的物体
    """
    group_name = "G_Base_Sphere_Centered" if centered else "G_Base_Sphere"
    builder = GNodesBuilder(name)
    builder.add_node_group(group_name, inputs={
        "Radius": radius,
        "Resolution": resolution
    })
    if not centered:
        builder.add_node_group("G_Align_Ground")
    builder.finalize()
    builder.set_location(*location)
    return builder.get_object()


def create_from_library(library_path: str, object_name: str = "AI_Generated_Model") -> GNodesBuilder:
    """
    从库文件创建构建器
    
    Args:
        library_path: .blend文件路径
        object_name: 物体名称
    """
    return GNodesBuilder(object_name, library_path)


# ========== 多流构建辅助函数 ==========

def apply_modifiers(obj: bpy.types.Object) -> bpy.types.Object:
    """
    应用物体上的所有修改器，将几何节点结果转换为真实网格
    
    这对于需要导出或进一步编辑几何节点生成的模型很有用。
    
    Args:
        obj: 要处理的物体
        
    Returns:
        处理后的物体（同一个物体）
        
    Example:
        builder = GNodesBuilder("MyModel")
        builder.add_node_group("G_Base_Cube", inputs={"Size": (1, 1, 1)})
        builder.finalize()
        
        obj = builder.get_object()
        apply_modifiers(obj)  # 现在 obj 包含真实的网格数据
    """
    # 取消选择所有
    bpy.ops.object.select_all(action='DESELECT')
    # 选择目标物体
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 应用所有修改器
    for modifier in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            print(f"✓ 已应用修改器: {modifier.name}")
        except Exception as e:
            print(f"⚠ 警告: 无法应用修改器 {modifier.name}: {e}")
    
    return obj


def merge_objects(*objects: bpy.types.Object, name: str = "Merged_Model") -> bpy.types.Object:
    """
    合并多个 Blender 物体为一个（用于跨 builder 合并）
    
    这是"多重构建流"的关键函数：
    1. 每个部件独立构建（使用独立的 GNodesBuilder）
    2. 最后使用此函数合并所有部件
    
    重要：此函数会自动应用几何节点修改器，将程序化生成的几何体
    转换为真实的网格数据，然后再合并。
    
    Args:
        *objects: 要合并的物体
        name: 合并后物体的名称
        
    Returns:
        合并后的物体
        
    Example:
        # === 多流构建模式 ===
        
        # 步骤1：独立构建各部件
        structure = build_tower_structure()    # 返回 bpy.types.Object
        antenna = build_radar_antenna()        # 返回 bpy.types.Object
        pipes = build_decoration_pipes()       # 返回 bpy.types.Object
        
        # 步骤2：合并所有部件
        final = merge_objects(structure, antenna, pipes, name="SciFi_Tower")
        
        # 步骤3：（可选）对合并后的模型进行统一处理
        # 比如：应用全局材质、添加细节等
    """
    if not objects:
        raise ValueError("至少需要一个物体来合并")
    
    # 过滤掉 None 值
    valid_objects = [obj for obj in objects if obj is not None]
    if not valid_objects:
        raise ValueError("没有有效的物体可以合并")
    
    # ⭐ 关键修复：先应用所有几何节点修改器
    # 这样才能将程序化生成的几何体转换为真实网格
    for obj in valid_objects:
        # 取消选择所有
        bpy.ops.object.select_all(action='DESELECT')
        # 选择当前物体
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # 应用所有修改器
        for modifier in list(obj.modifiers):
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            except Exception as e:
                print(f"⚠ 警告: 无法应用修改器 {modifier.name}: {e}")
    
    # 取消选择所有物体
    bpy.ops.object.select_all(action='DESELECT')
    
    # 选择要合并的物体
    for obj in valid_objects:
        obj.select_set(True)
    
    # 设置活动物体
    bpy.context.view_layer.objects.active = valid_objects[0]
    
    # 执行合并
    bpy.ops.object.join()
    
    # 重命名
    merged = bpy.context.active_object
    merged.name = name
    
    return merged


def instance_on_object(instance: bpy.types.Object, 
                       target: bpy.types.Object,
                       density: float = 10.0,
                       seed: int = 0,
                       align_to_normal: bool = True,
                       name: str = "Instanced_Model") -> bpy.types.Object:
    """
    在目标物体表面实例化另一个物体（Instance on Points 的便捷封装）
    
    这是复杂度的核心来源：
    - 生成 1 个精细的螺丝，在复杂表面实例化 1000 次
    - 模型瞬间变得极其复杂，但计算量很小
    
    Args:
        instance: 要实例化的物体（如：螺丝、铆钉）
        target: 目标物体（在其表面散布）
        density: 密度（每单位面积的实例数）
        seed: 随机种子
        align_to_normal: 是否对齐法线
        name: 输出物体名称
        
    Returns:
        实例化后的物体
        
    Example:
        # 创建一个精细的螺丝
        screw = create_detailed_screw()
        
        # 在复杂表面散布螺丝
        panel = create_metal_panel()
        result = instance_on_object(screw, panel, density=50, name="Panel_With_Screws")
    """
    # 创建新物体用于实例化结果
    builder = GNodesBuilder(name)
    
    # 使用 G_Scatter_On_Top 的逻辑，但更通用
    # 需要一个更通用的 Instance on Points 节点组
    # 这里使用简化的实现：复制 + 随机放置
    
    # TODO: 实现完整的 Instance on Points 逻辑
    # 目前返回一个简单的占位实现
    builder.add_node_group("G_Base_Cube", inputs={"Size": (1, 1, 1)})
    builder.finalize()
    
    return builder.get_object()


# ========== 节点组验证工具 ==========

def validate_node_group(group_name: str) -> Dict[str, Any]:
    """
    验证节点组是否符合S.I.O协议
    
    S (Size/Scale): 接受Vector尺寸输入
    I (Integers/Seed): 随机效果暴露Seed接口
    O (Origin): 输出原点在底部中心
    
    Returns:
        验证结果字典
    """
    if group_name not in bpy.data.node_groups:
        return {"valid": False, "error": f"节点组 '{group_name}' 不存在"}
    
    group = bpy.data.node_groups[group_name]
    result = {
        "valid": True,
        "warnings": [],
        "inputs": [inp.name for inp in group.interface.items_tree if inp.in_out == 'INPUT']
    }
    
    # 检查是否有Size/Scale输入
    has_size = any('size' in inp.name.lower() or 'scale' in inp.name.lower() 
                   for inp in group.interface.items_tree if inp.in_out == 'INPUT')
    if not has_size:
        result["warnings"].append("建议添加Size/Scale输入参数")
    
    return result


def list_available_groups(prefix: str = "G_") -> List[str]:
    """
    列出所有可用的节点组
    
    Args:
        prefix: 节点组名称前缀
        
    Returns:
        节点组名称列表
    """
    return [name for name in bpy.data.node_groups.keys() if name.startswith(prefix)]
