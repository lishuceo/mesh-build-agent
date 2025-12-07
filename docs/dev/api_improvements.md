# API改进说明 - 语义化空间API与组合模板

## 问题背景

在环形阵列等场景中，手动计算旋转角度容易出错：

```python
# ❌ 容易出错的代码
angle = i * (2 * math.pi / num_chairs)
x = radius * math.cos(angle)
y = radius * math.sin(angle)

# 这个角度应该是多少？angle? angle+π? angle+π/2?
back.rotation_euler = (0, 0, ???)  # 困惑！
```

**根本原因**：AI（和人类）很难在脑海中推理3D空间的旋转关系。

## 解决方案

### 方案1：语义化空间API

用**意图**替代**计算**：

| 旧API | 新API | 效果 |
|-------|-------|------|
| `rotation_euler = (0, 0, angle)` | `face_towards(x, y)` | 清晰：朝向目标 |
| `rotation_euler = (0, 0, angle+π)` | `face_away_from(x, y)` | 清晰：背对目标 |
| `rotation_euler = (0, 0, angle+π/2)` | `align_tangent_to_circle(cx, cy)` | 清晰：沿切线 |

#### 示例对比

**之前（容易错）**：
```python
# 让椅子靠背朝向正确
back_offset = 0.15
back_x = x + back_offset * math.cos(angle)
back_y = y + back_offset * math.sin(angle)
back.location = (back_x, back_y, 0.45)
back.rotation_euler = (0, 0, angle + math.pi / 2)  # 为什么是 π/2?
```

**现在（不会错）**：
```python
# 让椅子靠背朝向正确
back.set_location(back_x, back_y, 0.45)
back.align_tangent_to_circle(table_x, table_y)  # 语义清晰！
```

### 方案2：组合物体模板

把常用的复合结构封装成函数：

| 模板函数 | 封装的部件 | 自动处理的空间关系 |
|---------|-----------|-------------------|
| `create_chair()` | 座面 + 靠背 | 靠背位置和朝向 |
| `create_table_with_chairs()` | 桌子 + N把椅子 | 环形排列 + 朝向 |
| `create_fence()` | N根柱子 + 横杆 | 间距 + 横杆角度 |
| `create_door_frame()` | 左柱 + 右柱 + 门楣 | 对称位置 |

#### 示例对比

**之前（70行代码）**：
```python
def create_circular_table():
    objects = []
    
    # 桌面
    builder = GNodesBuilder("Table_Top")
    builder.add_node_group("G_Base_Cylinder", ...)
    builder.finalize()
    table_top = builder.get_object()
    table_top.location = (0, -3, 0.7)
    objects.append(table_top)
    
    # 桌腿
    builder2 = GNodesBuilder("Table_Leg")
    ...
    
    # 椅子（需要循环，计算每个角度...）
    for i in range(4):
        angle = i * (2 * math.pi / 4)
        x = ...
        y = ...
        
        # 座面
        builder_seat = GNodesBuilder(...)
        ...
        
        # 靠背
        builder_back = GNodesBuilder(...)
        # 计算靠背位置
        back_x = x + 0.15 * math.cos(angle)
        back_y = y + 0.15 * math.sin(angle)
        back.location = (back_x, back_y, 0.45)
        back.rotation_euler = (0, 0, angle + math.pi / 2)  # 容易错！
        ...
    
    return objects
```

**现在（1行代码）**：
```python
def create_circular_table():
    # 一行搞定，空间关系全自动！
    return create_table_with_chairs("Dining", (0, -3, 0.7), num_chairs=4)
```

## API设计原则

### 1. 语义化优于数学化

```python
# ❌ 差：需要理解数学关系
obj.rotation_euler = (0, 0, math.atan2(dy, dx) + math.pi)

# ✅ 好：直接表达意图
obj.face_away_from(target_x, target_y)
```

### 2. 组合优于原子

```python
# ❌ 差：每次都要重复组装
seat = create_cube(...)
back = create_cube(...)
# 计算靠背位置...
# 计算靠背角度...

# ✅ 好：封装常用组合
chair = create_chair(name, location, face_direction)
```

### 3. 参数语义化

```python
# ❌ 差：magic number
create_chair("Chair", (0, 0, 0), 3.14159)  # 3.14159 是什么？

# ✅ 好：命名参数
create_chair("Chair", location=(0, 0, 0), face_direction=math.pi)
```

## 使用建议

### 简单场景：使用组合模板

```python
# 推荐：一行搞定
create_table_with_chairs("Dining", (0, 0, 0))
create_fence("Fence", (-5, 0), (5, 0))
create_door_frame("Door", (0, 0, 0))
```

### 复杂场景：组合模板 + 语义化API

```python
# 先用模板创建基础结构
chair = create_chair("VIP_Chair", (5, 5, 0.5), math.pi/2)

# 再用语义化API微调
for obj in chair:
    if "Back" in obj.name:
        obj.scale.z = 1.5  # 加高靠背
```

### 特殊场景：直接使用GNodesBuilder

```python
# 完全自定义
builder = GNodesBuilder("Custom")
builder.add_node_group("G_Base_Cube", ...)
builder.add_node_group("G_Twist", ...)
builder.finalize()
builder.face_towards(target_x, target_y)
```

## 效果对比

| 维度 | 旧API | 新API |
|------|-------|-------|
| 代码行数 | 70行 | 1行 |
| 出错概率 | 高（角度计算） | 低（语义清晰） |
| 可读性 | 差（数学公式） | 好（自然语言） |
| 维护性 | 差（重复代码） | 好（集中管理） |

## 总结

**核心思想**：AI不擅长3D空间推理，但擅长调用API。

- **语义化API**：用"朝向目标"替代"计算角度"
- **组合模板**：用"创建椅子"替代"组装部件"

这样AI可以专注于**高层次的场景组织**，而不是底层的**数学计算**。

