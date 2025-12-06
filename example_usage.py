"""
AI驱动的几何节点生成示例
演示如何使用GNodesBuilder创建3D模型
"""

import bpy
from ai_gnodes_helper import GNodesBuilder, list_available_groups


def example_ancient_pillar():
    """
    示例：生成破损的古代石柱
    用户需求："帮我生成一个破损的古代石柱，高度4米，半径0.5米，上面长点苔藓。"
    """
    print("\n" + "="*60)
    print("示例1: 古代石柱")
    print("="*60)
    
    # 1. 初始化构建器
    builder = GNodesBuilder("Ancient_Pillar_01")
    
    # 2. 生成基础几何体（圆柱）
    builder.add_node_group(
        "G_Base_Cylinder", 
        inputs={
            "Radius": 0.5, 
            "Height": 4.0, 
            "Resolution": 16
        }
    )
    
    # 3. 添加破损效果
    builder.add_node_group(
        "G_Damage_Edges",
        inputs={
            "Amount": 0.8,
            "Scale": 2.5
        }
    )
    
    # 4. 添加环境细节（苔藓）
    builder.add_node_group(
        "G_Scatter_Moss",
        inputs={
            "Density": 50.0,
            "Seed": 1024
        }
    )
    
    # 5. 【关键】强制对齐地面
    builder.add_node_group("G_Align_Ground")
    
    # 6. 完成
    builder.finalize()
    
    print("✓ 古代石柱生成完成！")


def example_table():
    """
    示例：生成桌子（组合物体）
    演示如何使用分支和合并功能
    """
    print("\n" + "="*60)
    print("示例2: 桌子（组合物体）")
    print("="*60)
    
    builder = GNodesBuilder("Table_01")
    
    # 桌面
    builder.add_node_group(
        "G_Base_Cube",
        inputs={"Size": (2.0, 1.0, 0.1), "Bevel": 0.02}
    )
    tabletop = builder.last_node
    
    # 桌腿（需要4条，这里简化演示）
    # 注意：实际应用中需要更复杂的实例化逻辑
    builder.add_node_group(
        "G_Base_Cylinder",
        inputs={"Radius": 0.05, "Height": 0.7}
    )
    leg = builder.last_node
    
    # 合并几何体（实际需要4条腿的实例化）
    # builder.join_geometries(tabletop, leg)
    
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    print("✓ 桌子生成完成！")


def example_simple_wall():
    """
    示例：生成简单墙体
    演示最基本的用法
    """
    print("\n" + "="*60)
    print("示例3: 简单墙体")
    print("="*60)
    
    builder = GNodesBuilder("Wall_01")
    
    builder.add_node_group(
        "G_Base_Cube",
        inputs={"Size": (4.0, 0.3, 2.5)}
    )
    
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    print("✓ 墙体生成完成！")


def check_available_groups():
    """检查可用的节点组"""
    print("\n" + "="*60)
    print("检查可用节点组")
    print("="*60)
    
    groups = list_available_groups("G_")
    if groups:
        print(f"✓ 找到 {len(groups)} 个节点组:")
        for group in groups:
            print(f"  - {group}")
    else:
        print("⚠ 未找到任何节点组（以G_开头）")
        print("\n提示：")
        print("1. 确保已加载节点组库文件")
        print("2. 或在当前场景中手动创建节点组")
        print("3. 节点组名称必须以 'G_' 开头")


if __name__ == "__main__":
    # 检查可用节点组
    check_available_groups()
    
    # 运行示例（如果节点组存在）
    # example_simple_wall()
    # example_ancient_pillar()
    # example_table()
    
    print("\n" + "="*60)
    print("提示：如果节点组不存在，请先创建或加载节点组库")
    print("="*60)
