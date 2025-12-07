"""
GNodes Builder - AI驱动的Blender几何节点构建器

通过"胶水代码"模式，将Blender Geometry Nodes封装成简单API供AI调用

基本使用示例:
    from gnodes_builder import GNodesBuilder, load_node_library
    
    # 加载节点组库
    load_node_library("path/to/node_library.blend")
    
    # 创建模型
    builder = GNodesBuilder("My_Model")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (2.0, 1.0, 0.5)})
    builder.add_node_group("G_Align_Ground")
    builder.finalize()

多流构建模式 (Multi-Stream Building):
    from gnodes_builder import GNodesBuilder, merge_objects
    
    # 步骤1：独立构建各部件（子函数）
    def build_part_a():
        builder = GNodesBuilder("Part_A")
        builder.add_node_group("G_Base_Cube", inputs={"Size": (1, 1, 2)})
        builder.finalize()
        return builder.get_object()
    
    def build_part_b():
        builder = GNodesBuilder("Part_B")
        builder.add_node_group("G_Base_Sphere", inputs={"Radius": 0.5})
        builder.finalize()
        obj = builder.get_object()
        obj.location = (0, 0, 2.5)
        return obj
    
    # 步骤2：合并所有部件
    part_a = build_part_a()
    part_b = build_part_b()
    final = merge_objects(part_a, part_b, name="Combined_Model")
"""

from .builder import (
    GNodesBuilder,
    create_from_library,
    validate_node_group,
    list_available_groups,
    # 便捷工厂函数
    create_cube,
    create_cylinder,
    create_sphere,
    # 多流构建辅助函数
    apply_modifiers,
    merge_objects,
    instance_on_object,
)

from .loader import (
    NodeLibraryManager,
    load_node_library,
    create_minimal_library_template,
)

from .templates import (
    create_chair,
    create_table_with_chairs,
    create_fence,
    create_door_frame,
    create_arch,
    # 赛道系统 - 路径生成函数
    generate_stadium_path,
    generate_oval_path,
    generate_circle_path,
    generate_figure8_path,
    generate_custom_path,
    # 赛道系统 - 赛道生成函数
    create_track_from_path,
    create_oval_track,
    create_figure8_track,
    create_custom_track,
)

__version__ = "2.1.0"  # 新增多流构建支持
__author__ = "AI Agent Team"

__all__ = [
    # Builder
    "GNodesBuilder",
    "create_from_library",
    "validate_node_group",
    "list_available_groups",
    # 便捷工厂函数
    "create_cube",
    "create_cylinder",
    "create_sphere",
    # 多流构建辅助函数
    "apply_modifiers",
    "merge_objects",
    "instance_on_object",
    # 组合物体模板
    "create_chair",
    "create_table_with_chairs",
    "create_fence",
    "create_door_frame",
    "create_arch",
    # 赛道系统 - 路径生成
    "generate_stadium_path",
    "generate_oval_path",
    "generate_circle_path",
    "generate_figure8_path",
    "generate_custom_path",
    # 赛道系统 - 赛道生成
    "create_track_from_path",
    "create_oval_track",
    "create_figure8_track",
    "create_custom_track",
    # Loader
    "NodeLibraryManager",
    "load_node_library",
    "create_minimal_library_template",
]

