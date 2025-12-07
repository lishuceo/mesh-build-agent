"""
节点组库验证脚本
用于验证节点组库是否正确创建，以及测试基本功能

使用方法：
方式1（推荐）：直接运行，会自动加载库文件
  blender --background --python verify_node_library.py

方式2：指定库文件路径
  blender --background --python verify_node_library.py -- --library path/to/node_library.blend
"""

import bpy
import sys
import os
from typing import List, Dict, Tuple


def load_library_file(library_path: str = None) -> bool:
    """
    加载节点组库文件
    
    Args:
        library_path: 库文件路径，默认为脚本同目录下的 node_library.blend
    
    Returns:
        是否成功加载
    """
    if library_path is None:
        # 默认路径：assets/node_library.blend
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        library_path = os.path.join(project_root, "assets", "node_library.blend")
    
    if not os.path.exists(library_path):
        print(f"⚠️ 库文件不存在: {library_path}")
        print("请先运行 create_node_library.py 创建节点组库")
        return False
    
    print(f"📂 加载库文件: {library_path}")
    
    try:
        # 从库文件加载所有节点组
        with bpy.data.libraries.load(library_path, link=False) as (data_from, data_to):
            # 加载所有以 G_ 开头的节点组
            data_to.node_groups = [name for name in data_from.node_groups if name.startswith('G_')]
        
        # 加载后重新设置 Fake User
        loaded_groups = [ng for ng in bpy.data.node_groups if ng.name.startswith('G_')]
        for ng in loaded_groups:
            ng.use_fake_user = True
        
        print(f"✓ 已加载 {len(loaded_groups)} 个节点组\n")
        return True
        
    except Exception as e:
        print(f"❌ 加载库文件失败: {e}")
        return False


class NodeLibraryVerifier:
    """节点组库验证器"""
    
    # 预期的节点组列表
    EXPECTED_GROUPS = [
        "G_Base_Cube",
        "G_Base_Cylinder", 
        "G_Base_Sphere",
        "G_Damage_Edges",
        "G_Scatter_Moss",
        "G_Scatter_On_Top",
        "G_Boolean_Cut",
        "G_Voxel_Remesh",
        "G_Align_Ground",
    ]
    
    # 每个节点组的预期接口
    EXPECTED_INTERFACES = {
        "G_Base_Cube": {
            "inputs": ["Size", "Bevel"],
            "outputs": ["Geometry"]
        },
        "G_Base_Cylinder": {
            "inputs": ["Radius", "Height", "Resolution"],
            "outputs": ["Geometry"]
        },
        "G_Base_Sphere": {
            "inputs": ["Radius", "Resolution"],
            "outputs": ["Geometry"]
        },
        "G_Damage_Edges": {
            "inputs": ["Geometry", "Amount", "Scale", "Seed"],
            "outputs": ["Geometry"]
        },
        "G_Scatter_Moss": {
            "inputs": ["Geometry", "Density", "Seed"],
            "outputs": ["Geometry"]
        },
        "G_Scatter_On_Top": {
            "inputs": ["Geometry", "Density", "Seed"],
            "outputs": ["Geometry"]
        },
        "G_Boolean_Cut": {
            "inputs": ["Geometry", "Cut_Geometry"],
            "outputs": ["Geometry"]
        },
        "G_Voxel_Remesh": {
            "inputs": ["Geometry", "Voxel_Size"],
            "outputs": ["Geometry"]
        },
        "G_Align_Ground": {
            "inputs": ["Geometry"],
            "outputs": ["Geometry"]
        },
    }
    
    def __init__(self):
        self.results: List[Dict] = []
        self.passed = 0
        self.failed = 0
    
    def verify_group_exists(self, group_name: str) -> bool:
        """验证节点组是否存在"""
        exists = group_name in bpy.data.node_groups
        self._record_result(
            f"节点组存在: {group_name}",
            exists,
            "" if exists else f"节点组 '{group_name}' 不存在"
        )
        return exists
    
    def verify_group_interface(self, group_name: str) -> bool:
        """验证节点组接口"""
        if group_name not in bpy.data.node_groups:
            return False
        
        group = bpy.data.node_groups[group_name]
        expected = self.EXPECTED_INTERFACES.get(group_name, {})
        
        # 获取实际接口
        actual_inputs = []
        actual_outputs = []
        
        for item in group.interface.items_tree:
            if item.in_out == 'INPUT':
                actual_inputs.append(item.name)
            elif item.in_out == 'OUTPUT':
                actual_outputs.append(item.name)
        
        # 验证输入
        expected_inputs = expected.get("inputs", [])
        missing_inputs = [inp for inp in expected_inputs if inp not in actual_inputs]
        
        if missing_inputs:
            self._record_result(
                f"接口验证: {group_name}",
                False,
                f"缺少输入: {missing_inputs}"
            )
            return False
        
        # 验证输出
        expected_outputs = expected.get("outputs", [])
        missing_outputs = [out for out in expected_outputs if out not in actual_outputs]
        
        if missing_outputs:
            self._record_result(
                f"接口验证: {group_name}",
                False,
                f"缺少输出: {missing_outputs}"
            )
            return False
        
        self._record_result(
            f"接口验证: {group_name}",
            True,
            f"输入: {actual_inputs}, 输出: {actual_outputs}"
        )
        return True
    
    def verify_group_has_fake_user(self, group_name: str) -> bool:
        """验证节点组是否标记为 Fake User"""
        if group_name not in bpy.data.node_groups:
            return False
        
        group = bpy.data.node_groups[group_name]
        has_fake_user = group.use_fake_user
        
        self._record_result(
            f"Fake User: {group_name}",
            has_fake_user,
            "" if has_fake_user else "未标记为 Fake User，可能会被意外清除"
        )
        return has_fake_user
    
    def _record_result(self, test_name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        result = {
            "test": test_name,
            "passed": passed,
            "message": message
        }
        self.results.append(result)
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def run_all_verifications(self) -> bool:
        """运行所有验证"""
        print("\n" + "=" * 60)
        print("🔍 开始验证节点组库...")
        print("=" * 60 + "\n")
        
        all_passed = True
        
        for group_name in self.EXPECTED_GROUPS:
            print(f"\n检查 {group_name}:")
            
            # 验证存在性
            if not self.verify_group_exists(group_name):
                all_passed = False
                continue
            
            # 验证接口
            if not self.verify_group_interface(group_name):
                all_passed = False
            
            # 验证 Fake User
            if not self.verify_group_has_fake_user(group_name):
                all_passed = False
        
        self._print_summary()
        return all_passed
    
    def _print_summary(self):
        """打印验证摘要"""
        print("\n" + "=" * 60)
        print("📊 验证结果摘要")
        print("=" * 60)
        
        for result in self.results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}")
            if result["message"] and not result["passed"]:
                print(f"   └─ {result['message']}")
        
        print("\n" + "-" * 60)
        total = self.passed + self.failed
        print(f"总计: {total} 项测试")
        print(f"通过: {self.passed} ✅")
        print(f"失败: {self.failed} ❌")
        
        if self.failed == 0:
            print("\n🎉 所有验证通过！节点组库已就绪。")
        else:
            print(f"\n⚠️ 有 {self.failed} 项验证失败，请检查节点组库。")
        
        print("=" * 60 + "\n")


def test_basic_usage():
    """测试基本使用流程"""
    print("\n" + "=" * 60)
    print("🧪 测试基本使用流程...")
    print("=" * 60 + "\n")
    
    try:
        # 导入构建器
        import sys
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        src_dir = os.path.join(project_root, "src")
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        
        from gnodes_builder import GNodesBuilder
        
        # 测试1：创建简单立方体
        print("测试1: 创建简单立方体...")
        builder = GNodesBuilder("Test_Cube")
        builder.add_node_group("G_Base_Cube", inputs={"Size": (2.0, 1.0, 0.5)})
        builder.add_node_group("G_Align_Ground")
        builder.finalize()
        print("  ✅ 成功创建 Test_Cube")
        
        # 测试2：创建带效果的圆柱
        print("\n测试2: 创建带破损效果的圆柱...")
        builder2 = GNodesBuilder("Test_Cylinder")
        builder2.add_node_group("G_Base_Cylinder", inputs={"Radius": 0.5, "Height": 2.0})
        builder2.add_node_group("G_Damage_Edges", inputs={"Amount": 0.3})
        builder2.add_node_group("G_Align_Ground")
        builder2.finalize()
        print("  ✅ 成功创建 Test_Cylinder")
        
        # 测试3：创建带散布效果的球体
        print("\n测试3: 创建带苔藓的球体...")
        builder3 = GNodesBuilder("Test_Sphere")
        builder3.add_node_group("G_Base_Sphere", inputs={"Radius": 1.0})
        builder3.add_node_group("G_Scatter_Moss", inputs={"Density": 30.0, "Seed": 42})
        builder3.add_node_group("G_Align_Ground")
        builder3.finalize()
        print("  ✅ 成功创建 Test_Sphere")
        
        print("\n" + "-" * 60)
        print("🎉 所有基本使用测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    # 解析命令行参数
    library_path = None
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1:]
        for i, arg in enumerate(argv):
            if arg in ("--library", "-l") and i + 1 < len(argv):
                library_path = argv[i + 1]
    
    # 先尝试加载库文件
    if not load_library_file(library_path):
        print("\n" + "=" * 60)
        print("💡 使用提示：")
        print("=" * 60)
        print("1. 先创建节点组库：")
        print("   blender --background --python create_node_library.py")
        print("\n2. 然后验证：")
        print("   blender --background --python verify_node_library.py")
        print("=" * 60 + "\n")
        return
    
    # 验证节点组库
    verifier = NodeLibraryVerifier()
    library_valid = verifier.run_all_verifications()
    
    # 如果库有效，运行使用测试
    if library_valid:
        test_basic_usage()
    else:
        print("\n⚠️ 节点组库验证未通过，跳过使用测试。")
        print("请检查 create_node_library.py 是否正确运行。")


if __name__ == "__main__":
    main()

