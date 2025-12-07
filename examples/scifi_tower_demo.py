"""
科幻通信塔 - 多重构建流演示
展示"独立部件构建 -> 最后合并"的架构模式

这个示例演示了：
1. 将复杂模型拆解为逻辑组件
2. 每个组件独立构建（子函数）
3. 最后使用 merge_objects 合并
4. 使用 Instance on Points 大幅提升复杂度

使用方法：
1. 先更新节点库：blender --background --python scripts/create_node_library.py
2. 运行演示：blender assets/node_library.blend --python examples/scifi_tower_demo.py
"""

import bpy
import sys
import os
import math

# 添加项目路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from gnodes_builder import GNodesBuilder, merge_objects


def clear_scene():
    """清理默认物体"""
    for obj in list(bpy.data.objects):
        if obj.type in ('MESH', 'CURVE'):
            bpy.data.objects.remove(obj, do_unlink=True)


# ========== 子组件 1：塔身骨架 ==========
def build_tower_structure():
    """
    生成塔身骨架 - 垂直堆叠的几何体
    
    构成：
    - 底座：大圆柱
    - 中段：锥形收窄
    - 顶部：细长柱
    """
    print("  📦 构建塔身骨架...")
    
    objects = []
    
    # 底座 - 大圆柱
    builder = GNodesBuilder("Tower_Base")
    builder.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 1.5,
        "Height": 2.0,
        "Resolution": 24
    })
    builder.add_node_group("G_Taper", inputs={"Factor": 0.2})  # 轻微锥形
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    base = builder.get_object()
    base.location = (0, 0, 0)
    objects.append(base)
    
    # 中段 - 收窄的主体
    builder2 = GNodesBuilder("Tower_Middle")
    builder2.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 1.0,
        "Height": 4.0,
        "Resolution": 16
    })
    builder2.add_node_group("G_Taper", inputs={"Factor": 0.4})  # 明显锥形
    builder2.add_node_group("G_Align_Ground")
    builder2.finalize()
    middle = builder2.get_object()
    middle.location = (0, 0, 2.0)  # 放在底座上
    objects.append(middle)
    
    # 顶部 - 细长柱
    builder3 = GNodesBuilder("Tower_Top")
    builder3.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.3,
        "Height": 3.0,
        "Resolution": 12
    })
    builder3.add_node_group("G_Taper", inputs={"Factor": 0.6})
    builder3.add_node_group("G_Align_Ground")
    builder3.finalize()
    top = builder3.get_object()
    top.location = (0, 0, 6.0)  # 放在中段上
    objects.append(top)
    
    return objects


# ========== 子组件 2：雷达天线盘 ==========
def build_radar_dish():
    """
    生成雷达天线盘
    
    构成：
    - 主盘：半球（使用球体+布尔切割模拟）
    - 支架：管道
    """
    print("  📦 构建雷达天线...")
    
    objects = []
    
    # 天线盘 - 使用扁球体
    builder = GNodesBuilder("Radar_Dish")
    builder.add_node_group("G_Base_Sphere", inputs={
        "Radius": 1.2,
        "Resolution": 16
    })
    builder.add_node_group("G_Taper", inputs={"Factor": 0.8})  # 压扁成盘状
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    dish = builder.get_object()
    # 旋转使其朝向侧面
    dish.rotation_euler = (0, math.radians(45), 0)
    dish.location = (1.5, 0, 7.5)
    objects.append(dish)
    
    # 天线支架
    builder2 = GNodesBuilder("Radar_Arm")
    builder2.add_node_group("G_Pipe", inputs={
        "Radius": 0.08,
        "Length": 1.5,
        "Resolution": 8
    })
    builder2.finalize()
    arm = builder2.get_object()
    arm.rotation_euler = (0, math.radians(90), 0)
    arm.location = (0.3, 0, 7.5)
    objects.append(arm)
    
    return objects


# ========== 子组件 3：装饰管道 ==========
def build_decoration_pipes():
    """
    生成装饰管道 - 螺旋环绕塔身
    """
    print("  📦 构建装饰管道...")
    
    objects = []
    
    # 环形管道 - 使用环形阵列
    builder = GNodesBuilder("Pipe_Ring_1")
    builder.add_node_group("G_Base_Cylinder_Centered", inputs={
        "Radius": 0.05,
        "Height": 0.3,
        "Resolution": 8
    })
    builder.add_node_group("G_Array_Circular", inputs={
        "Count": 8,
        "Radius": 1.3
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    ring1 = builder.get_object()
    ring1.location = (0, 0, 1.5)
    objects.append(ring1)
    
    # 第二个环（更高更小）
    builder2 = GNodesBuilder("Pipe_Ring_2")
    builder2.add_node_group("G_Base_Cylinder_Centered", inputs={
        "Radius": 0.04,
        "Height": 0.25,
        "Resolution": 8
    })
    builder2.add_node_group("G_Array_Circular", inputs={
        "Count": 6,
        "Radius": 0.8
    })
    builder2.add_node_group("G_Align_Ground")
    builder2.finalize()
    ring2 = builder2.get_object()
    ring2.location = (0, 0, 4.5)
    objects.append(ring2)
    
    # 竖直管道
    for i in range(4):
        angle = i * (math.pi / 2)
        x = 1.2 * math.cos(angle)
        y = 1.2 * math.sin(angle)
        
        builder = GNodesBuilder(f"Vertical_Pipe_{i}")
        builder.add_node_group("G_Pipe", inputs={
            "Radius": 0.06,
            "Length": 5.0,
            "Resolution": 8
        })
        builder.add_node_group("G_Align_Ground")
        builder.finalize()
        pipe = builder.get_object()
        pipe.location = (x, y, 0.5)
        objects.append(pipe)
    
    return objects


# ========== 子组件 4：细节点缀 ==========
def build_detail_elements():
    """
    生成细节点缀 - 小型装饰物
    
    这些元素会被大量实例化，是复杂度的来源
    """
    print("  📦 构建细节元素...")
    
    objects = []
    
    # 小型指示灯（线性阵列）
    builder = GNodesBuilder("Indicator_Lights")
    builder.add_node_group("G_Base_Sphere", inputs={
        "Radius": 0.04,
        "Resolution": 8
    })
    builder.add_node_group("G_Array_Linear", inputs={
        "Count": 10,
        "Offset": (0, 0, 0.3)
    })
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    lights = builder.get_object()
    lights.location = (0.35, 0, 2.0)
    objects.append(lights)
    
    # 第二列灯（对称位置）
    builder2 = GNodesBuilder("Indicator_Lights_2")
    builder2.add_node_group("G_Base_Sphere", inputs={
        "Radius": 0.04,
        "Resolution": 8
    })
    builder2.add_node_group("G_Array_Linear", inputs={
        "Count": 10,
        "Offset": (0, 0, 0.3)
    })
    builder2.add_node_group("G_Align_Ground")
    builder2.finalize()
    lights2 = builder2.get_object()
    lights2.location = (-0.35, 0, 2.0)
    objects.append(lights2)
    
    # 小型天线（顶部）
    builder3 = GNodesBuilder("Small_Antenna")
    builder3.add_node_group("G_Base_Cylinder", inputs={
        "Radius": 0.02,
        "Height": 0.8,
        "Resolution": 6
    })
    builder3.add_node_group("G_Taper", inputs={"Factor": 0.9})
    builder3.add_node_group("G_Align_Ground")
    builder3.finalize()
    antenna = builder3.get_object()
    antenna.location = (0, 0, 9.0)
    objects.append(antenna)
    
    return objects


# ========== 主装配函数 ==========
def assemble_scifi_tower():
    """
    主装配函数 - 组装所有部件
    
    这是多重构建流的核心：
    1. 调用各个子函数获取部件
    2. 合并所有部件
    3. 应用全局统一处理
    """
    print("\n🔧 开始组装科幻通信塔...")
    print("=" * 50)
    
    all_objects = []
    
    # Step 1: 构建各个独立部件
    all_objects.extend(build_tower_structure())
    all_objects.extend(build_radar_dish())
    all_objects.extend(build_decoration_pipes())
    all_objects.extend(build_detail_elements())
    
    print(f"\n📊 部件统计：共 {len(all_objects)} 个独立物体")
    
    # Step 2: 合并所有部件
    print("\n🔗 合并所有部件...")
    final_tower = merge_objects(*all_objects, name="SciFi_Communication_Tower")
    
    # Step 3: 全局后处理（可选）
    # 如果有 G_Unified_Material 或 G_Edge_Detail，可以在这里应用
    # 但由于合并后是单一物体，需要重新创建 GNodesBuilder
    # 这里保持简单，不做额外处理
    
    print(f"\n✅ 科幻通信塔组装完成！")
    print(f"   最终物体：{final_tower.name}")
    
    return final_tower


def create_ground():
    """创建地面"""
    builder = GNodesBuilder("Ground")
    builder.add_node_group("G_Base_Cube", inputs={"Size": (10, 10, 0.1)})
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    
    ground = builder.get_object()
    ground.location = (0, 0, 0)
    return ground


def setup_camera():
    """设置相机"""
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
    else:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
    
    cam.location = (12, -12, 8)
    cam.rotation_euler = (1.1, 0, 0.8)
    bpy.context.scene.camera = cam


def setup_lighting():
    """设置灯光"""
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # 主光源
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 15))
    sun = bpy.context.object
    sun.data.energy = 3
    sun.rotation_euler = (0.8, 0.2, 0.5)
    
    # 补光
    bpy.ops.object.light_add(type='AREA', location=(-5, 5, 5))
    fill = bpy.context.object
    fill.data.energy = 100


def main():
    print("\n" + "=" * 60)
    print("🏗️ 科幻通信塔 - 多重构建流演示")
    print("=" * 60)
    print("\n演示的架构模式：")
    print("  1. 将复杂模型拆解为 4 个逻辑组件")
    print("  2. 每个组件独立构建（子函数）")
    print("  3. 使用 merge_objects() 合并所有部件")
    print("  4. 使用 G_Array_* 节点大幅提升复杂度")
    print("\n组件分解：")
    print("  • build_tower_structure() - 塔身骨架（底座+中段+顶部）")
    print("  • build_radar_dish()      - 雷达天线盘")
    print("  • build_decoration_pipes()- 装饰管道（环形+竖直）")
    print("  • build_detail_elements() - 细节点缀（指示灯+小天线）")
    
    # 清理场景
    clear_scene()
    
    # 创建地面
    create_ground()
    
    # 组装塔
    tower = assemble_scifi_tower()
    
    # 设置场景
    setup_camera()
    setup_lighting()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("\n💡 关键点：")
    print("  • 每个子函数独立构建，易于维护和复用")
    print("  • 使用 G_Taper 创建锥形变化")
    print("  • 使用 G_Array_Circular 创建环形阵列")
    print("  • 使用 G_Array_Linear 创建线性阵列")
    print("  • 最后 merge_objects() 合并为单一物体")
    print("\n  这种模式下，AI 只需要 ~100 行代码")
    print("  就能生成一个相当复杂的科幻建筑！")
    
    # 保存
    if bpy.app.background:
        out = os.path.join(project_root, "assets", "scifi_tower_demo.blend")
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print(f"\n💾 保存: {out}")


if __name__ == "__main__":
    main()

