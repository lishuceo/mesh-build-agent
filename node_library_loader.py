"""
节点组库加载和管理工具
支持从外部.blend文件加载节点组，并提供库管理功能
"""

import bpy
import os
from typing import List, Dict, Optional


class NodeLibraryManager:
    """节点组库管理器"""
    
    def __init__(self, library_path: Optional[str] = None):
        """
        初始化库管理器
        
        Args:
            library_path: 默认库文件路径
        """
        self.library_path = library_path
        self.loaded_groups: List[str] = []
    
    def load_library(self, library_path: str, prefix: str = "G_") -> List[str]:
        """
        从.blend文件加载节点组
        
        Args:
            library_path: .blend文件路径
            prefix: 只加载以该前缀开头的节点组
            
        Returns:
            已加载的节点组名称列表
        """
        if not os.path.exists(library_path):
            raise FileNotFoundError(f"库文件不存在: {library_path}")
        
        loaded = []
        try:
            with bpy.data.libraries.load(library_path, link=False) as (data_from, data_to):
                # 过滤出符合前缀的节点组
                groups_to_load = [name for name in data_from.node_groups 
                                if name.startswith(prefix)]
                data_to.node_groups = groups_to_load
                loaded = groups_to_load
            
            # 标记为伪用户，防止被清除
            for group_name in loaded:
                if group_name in bpy.data.node_groups:
                    bpy.data.node_groups[group_name].use_fake_user = True
            
            self.loaded_groups.extend(loaded)
            print(f"✓ 已加载 {len(loaded)} 个节点组: {', '.join(loaded)}")
            
        except Exception as e:
            raise RuntimeError(f"加载库文件失败: {e}")
        
        return loaded
    
    def unload_library(self, library_path: str):
        """
        卸载指定库的节点组（谨慎使用）
        
        Args:
            library_path: 库文件路径
        """
        # 注意：Blender不直接追踪节点组来源
        # 这里只是标记，实际需要手动管理
        print("⚠ 注意：Blender不直接支持卸载已加载的节点组")
        print("   如需清理，请手动删除或重新打开文件")
    
    def list_loaded_groups(self, prefix: str = "G_") -> List[str]:
        """
        列出已加载的节点组
        
        Args:
            prefix: 过滤前缀
            
        Returns:
            节点组名称列表
        """
        all_groups = [name for name in bpy.data.node_groups.keys() 
                     if name.startswith(prefix)]
        return [g for g in all_groups if g in self.loaded_groups or 
                bpy.data.node_groups[g].use_fake_user]
    
    def get_group_info(self, group_name: str) -> Dict:
        """
        获取节点组信息
        
        Args:
            group_name: 节点组名称
            
        Returns:
            节点组信息字典
        """
        if group_name not in bpy.data.node_groups:
            return {"error": f"节点组 '{group_name}' 不存在"}
        
        group = bpy.data.node_groups[group_name]
        info = {
            "name": group_name,
            "inputs": [],
            "outputs": [],
            "description": ""
        }
        
        for item in group.interface.items_tree:
            if item.in_out == 'INPUT':
                info["inputs"].append({
                    "name": item.name,
                    "type": item.socket_type,
                    "default": getattr(item, 'default_value', None)
                })
            elif item.in_out == 'OUTPUT':
                info["outputs"].append({
                    "name": item.name,
                    "type": item.socket_type
                })
        
        return info


# ========== 便捷函数 ==========

def load_node_library(library_path: str, prefix: str = "G_") -> List[str]:
    """
    快速加载节点组库
    
    Args:
        library_path: .blend文件路径
        prefix: 节点组前缀
        
    Returns:
        已加载的节点组列表
    """
    manager = NodeLibraryManager()
    return manager.load_library(library_path, prefix)


def create_minimal_library_template(blend_path: str):
    """
    创建一个最小化的库模板文件（用于测试）
    
    注意：这个函数需要在Blender中运行，且需要手动创建节点组
    这里只是提供创建模板的指导
    
    Args:
        blend_path: 保存路径
    """
    print("=" * 60)
    print("创建节点组库模板的步骤：")
    print("1. 在Blender中创建新的Geometry Node Group")
    print("2. 命名为 G_Base_Cube（或其他G_开头的名称）")
    print("3. 添加输入输出接口")
    print("4. 连接节点逻辑")
    print("5. 标记为Fake User（防止被清除）")
    print("6. 保存为 .blend 文件")
    print(f"7. 保存路径: {blend_path}")
    print("=" * 60)
