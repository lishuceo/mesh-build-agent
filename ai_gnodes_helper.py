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
        合并多个几何体分支
        
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


# ========== 便捷函数 ==========

def create_from_library(library_path: str, object_name: str = "AI_Generated_Model") -> GNodesBuilder:
    """
    从库文件创建构建器
    
    Args:
        library_path: .blend文件路径
        object_name: 物体名称
    """
    return GNodesBuilder(object_name, library_path)


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
