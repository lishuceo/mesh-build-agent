"""
测试脚本：验证GNodesBuilder功能
在Blender的文本编辑器中运行此脚本
"""

import bpy
from ai_gnodes_helper import (
    GNodesBuilder, 
    list_available_groups,
    validate_node_group,
    create_from_library
)
from node_library_loader import NodeLibraryManager


def test_basic_functionality():
    """测试基本功能"""
    print("\n" + "="*60)
    print("测试1: 基本功能")
    print("="*60)
    
    # 清理场景（可选）
    # bpy.ops.object.select_all(action='SELECT')
    # bpy.ops.object.delete()
    
    # 创建构建器
    builder = GNodesBuilder("Test_Object_01")
    print("✓ 构建器创建成功")
    
    # 检查可用节点组
    groups = list_available_groups()
    print(f"✓ 可用节点组: {groups}")
    
    return builder


def test_node_group_validation():
    """测试节点组验证"""
    print("\n" + "="*60)
    print("测试2: 节点组验证")
    print("="*60)
    
    groups = list_available_groups()
    for group_name in groups[:3]:  # 只测试前3个
        result = validate_node_group(group_name)
        print(f"\n节点组: {group_name}")
        print(f"  有效: {result.get('valid', False)}")
        if result.get('warnings'):
            for warning in result['warnings']:
                print(f"  警告: {warning}")
        if result.get('inputs'):
            print(f"  输入: {', '.join(result['inputs'])}")


def test_simple_build():
    """测试简单构建（如果节点组存在）"""
    print("\n" + "="*60)
    print("测试3: 简单构建")
    print("="*60)
    
    groups = list_available_groups()
    
    if not groups:
        print("⚠ 没有可用的节点组，跳过构建测试")
        print("提示：请先创建或加载节点组库")
        return
    
    # 尝试使用第一个节点组
    test_group = groups[0]
    print(f"使用节点组: {test_group}")
    
    try:
        builder = GNodesBuilder("Test_Build")
        
        # 尝试添加节点组（使用默认参数）
        builder.add_node_group(test_group)
        print("✓ 节点组添加成功")
        
        # 尝试添加对齐节点（如果存在）
        if "G_Align_Ground" in groups:
            builder.add_node_group("G_Align_Ground")
            print("✓ 对齐节点添加成功")
        
        builder.finalize()
        print("✓ 构建完成")
        
    except Exception as e:
        print(f"✗ 构建失败: {e}")


def test_library_loading():
    """测试库加载功能"""
    print("\n" + "="*60)
    print("测试4: 库加载")
    print("="*60)
    
    # 这里需要实际的库文件路径
    # library_path = "/path/to/node_library.blend"
    # 
    # try:
    #     manager = NodeLibraryManager()
    #     loaded = manager.load_library(library_path)
    #     print(f"✓ 加载了 {len(loaded)} 个节点组")
    # except Exception as e:
    #     print(f"✗ 加载失败: {e}")
    
    print("提示：取消注释上面的代码并提供库文件路径以测试")


def test_error_handling():
    """测试错误处理"""
    print("\n" + "="*60)
    print("测试5: 错误处理")
    print("="*60)
    
    builder = GNodesBuilder("Test_Error")
    
    # 尝试使用不存在的节点组
    try:
        builder.add_node_group("G_NonExistent_Group")
        print("✗ 应该抛出错误但没有")
    except ValueError as e:
        print(f"✓ 正确捕获错误: {e}")
    
    # 尝试使用错误的参数
    groups = list_available_groups()
    if groups:
        try:
            builder = GNodesBuilder("Test_Wrong_Params")
            builder.add_node_group(groups[0], inputs={"WrongParam": 123})
            print("⚠ 参数错误被忽略（这是预期的行为）")
        except Exception as e:
            print(f"✓ 参数错误被处理: {e}")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始运行测试套件")
    print("="*60)
    
    test_basic_functionality()
    test_node_group_validation()
    test_simple_build()
    test_library_loading()
    test_error_handling()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
