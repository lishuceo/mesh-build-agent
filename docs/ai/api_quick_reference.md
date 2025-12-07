# API 快速参考卡片

## 🎯 四步决策流程

```
步骤0：是复杂模型吗？（多个部件）
  ├─ 是 → 使用多流构建模式（见下文）
  └─ 否 → 步骤1

步骤1：能用组合模板吗？
  ├─ 是 → create_table_with_chairs() / create_fence() / ...
  └─ 否 → 步骤2

步骤2：需要旋转吗？
  ├─ 朝向某点 → face_towards(x, y)
  ├─ 背对某点 → face_away_from(x, y)
  ├─ 环形切线 → align_tangent_to_circle(cx, cy)
  ├─ 已知角度 → set_rotation_degrees(0, 0, angle)
  └─ 不需要 → 步骤3

步骤3：组装几何体
  └─ GNodesBuilder().add_node_group()...
```

---

## ⭐ 多流构建模式（复杂模型）

```python
from gnodes_builder import GNodesBuilder, merge_objects

# 步骤1：独立构建各部件（子函数）
def build_part_a():
    builder = GNodesBuilder("Part_A")
    builder.add_node_group("G_Base_Cylinder", inputs={"Radius": 1, "Height": 3})
    builder.add_node_group("G_Taper", inputs={"Factor": 0.3})
    builder.add_node_group("G_Align_Ground")
    builder.finalize()
    return builder.get_object()

def build_part_b():
    builder = GNodesBuilder("Part_B")
    # ... 其他部件
    builder.finalize()
    obj = builder.get_object()
    obj.location = (0, 0, 3)  # 定位
    return obj

# 步骤2：合并所有部件
part_a = build_part_a()
part_b = build_part_b()
final = merge_objects(part_a, part_b, name="Complex_Model")
```

**何时使用**：模型有 3+ 个逻辑部件时

---

## 📋 常用API速查

### 多流构建辅助函数

```python
from gnodes_builder import merge_objects, apply_modifiers

# 合并多个物体（自动应用修改器）
final = merge_objects(obj1, obj2, obj3, name="Merged")

# 单独应用修改器（不合并）
apply_modifiers(obj)
```

### 创建完整结构（一行搞定）

```python
from gnodes_builder import (
    create_chair,
    create_table_with_chairs,
    create_fence,
    create_door_frame
)

# 椅子
create_chair("Chair", (0, 0, 0), face_direction=0)

# 圆桌+椅子
create_table_with_chairs("Dining", (0, 0, 0.7), num_chairs=4)

# 栅栏
create_fence("Fence", start_pos=(-5, 0), end_pos=(5, 0), num_posts=10)

# 门框
create_door_frame("Door", (0, 0, 0), width=1.0, height=2.1)
```

### 旋转控制（语义化）

```python
builder.set_location(x, y, z)

# 朝向/背对
builder.face_towards(target_x, target_y)      # 朝向目标
builder.face_away_from(target_x, target_y)    # 背对目标

# 环形阵列
builder.align_tangent_to_circle(cx, cy)       # 切线方向

# 固定角度
builder.set_rotation_degrees(0, 0, 45)        # 朝向东北
```

### 基础几何体

```python
from gnodes_builder import GNodesBuilder

builder = GNodesBuilder("Object")

# 立方体
builder.add_node_group("G_Base_Cube", inputs={
    "Size": (x, y, z),
    "Bevel": 0.1
})

# 圆柱
builder.add_node_group("G_Base_Cylinder", inputs={
    "Radius": 0.5,
    "Height": 2.0,
    "Resolution": 16
})

# 球体
builder.add_node_group("G_Base_Sphere", inputs={
    "Radius": 1.0,
    "Resolution": 16
})

# 楔形
builder.add_node_group("G_Base_Wedge", inputs={
    "Size": (x, y, z)
})
```

### 变形效果

```python
# 锥形（顶部收窄）
builder.add_node_group("G_Taper", inputs={"Factor": 0.3})

# 剪切（倾斜）
builder.add_node_group("G_Shear", inputs={"Amount": 0.2})

# 平滑（圆润）
builder.add_node_group("G_Smooth", inputs={"Level": 1})

# 弯曲
builder.add_node_group("G_Bend", inputs={"Angle": math.pi/2})

# 扭曲
builder.add_node_group("G_Twist", inputs={"Angle": math.pi})
```

### 效果处理

```python
# 破损边缘
builder.add_node_group("G_Damage_Edges", inputs={
    "Amount": 0.7,
    "Scale": 2.0,
    "Seed": 123
})

# 苔藓
builder.add_node_group("G_Scatter_Moss", inputs={
    "Density": 50.0,
    "Seed": 456
})

# 必须调用！（非 Centered 版本）
builder.add_node_group("G_Align_Ground")
```

### 复杂度倍增器 ⭐ 新增

```python
# 点实例化（1个模型 → 1000个实例）
builder.add_node_group("G_Instance_On_Points", inputs={
    "Scale": 1.0,
    "Align_To_Normal": True,
    "Seed": 0
})

# 面板网格（玻璃幕墙）
builder.add_node_group("G_Panel_Grid", inputs={
    "Rows": 4,
    "Columns": 4,
    "Gap": 0.02,
    "Inset": 0.01
})

# 随机布尔雕刻（机械凹槽）
builder.add_node_group("G_Boolean_Random_Cut", inputs={
    "Count": 5,
    "Cut_Size": 0.3,
    "Depth": 0.2,
    "Seed": 0
})

# 边缘细节（霓虹灯带）
builder.add_node_group("G_Edge_Detail", inputs={
    "Radius": 0.02,
    "Resolution": 8
})
```

---

## 🚨 常见错误速查

| 错误代码 | 问题 | 正确写法 |
|---------|------|---------|
| `angle = atan2(dy, dx)`<br>`set_rotation(0, 0, angle)` | 手动计算角度 | `face_towards(x, y)` |
| `rotation = (0, 0, angle + π)` | 角度关系混乱 | `face_away_from(x, y)` |
| 创建椅子手动组装 | 70行代码 | `create_chair()` 1行 |
| `G_Base_Cube_Centered`<br>`G_Align_Ground` | Centered不需要对齐 | 删除 `G_Align_Ground` |
| `G_Base_Cube` 后直接 `finalize()` | 忘记对齐地面 | 添加 `G_Align_Ground` |

---

## 📚 相关文档

**AI Agent文档**：
- [ai_agent_prompt.md](ai_agent_prompt.md) - 完整的系统提示词

**开发者文档**（如需了解设计原理）：
- [../dev/api_priority_guide.md](../dev/api_priority_guide.md) - 详细的API选择说明
- [../dev/usage_guide.md](../dev/usage_guide.md) - 完整的使用教程
- [../dev/api_improvements.md](../dev/api_improvements.md) - 设计原理

