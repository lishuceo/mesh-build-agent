# 使用指南 - AI驱动的建模工具

## 快速开始

### 1. 更新节点库

```bash
blender --background --python scripts/create_node_library.py
```

生成 `assets/node_library.blend`（包含24个节点组）

### 2. 运行演示

```bash
# 基础演示
blender assets/node_library.blend --python examples/demo_test.py

# 建筑场景演示
blender assets/node_library.blend --python examples/architecture_demo.py

# 新API演示
blender assets/node_library.blend --python examples/new_api_demo.py

# 新旧对比
blender assets/node_library.blend --python examples/before_after_comparison.py
```

## 三种使用方式

### Level 1：组合模板（最简单，推荐）

适合：常见结构（桌椅、门框、栅栏）

```python
from gnodes_builder import create_table_with_chairs

# 一行代码创建整套餐桌
create_table_with_chairs("Dining", (0, 0, 0), num_chairs=4)
```

**优点**：
- 代码极简（1行）
- 不会出错
- 空间关系自动处理

**缺点**：
- 灵活性有限
- 只能用于预定义的结构

---

### Level 2：GNodesBuilder + 语义化API（灵活）

适合：自定义结构 + 空间关系处理

```python
from gnodes_builder import GNodesBuilder

builder = GNodesBuilder("MyObject")
builder.add_node_group("G_Base_Cube", inputs={"Size": (2, 1, 0.5)})
builder.add_node_group("G_Taper", inputs={"Factor": 0.3})
builder.add_node_group("G_Align_Ground")
builder.finalize()

builder.set_location(3, 5, 0)
builder.face_towards(0, 0)  # 语义化API - 自动朝向
```

**优点**：
- 灵活性高
- 语义清晰
- 仍然避免了角度计算

**缺点**：
- 需要多行代码

---

### Level 3：GNodesBuilder + 手动旋转（完全自定义）

适合：特殊场景

```python
builder = GNodesBuilder("Custom")
builder.add_node_group("G_Base_Cube", ...)
builder.finalize()

# 完全手动控制
builder.set_location(x, y, z)
builder.set_rotation(rx, ry, rz)
```

**优点**：
- 完全控制

**缺点**：
- 容易出错
- 需要计算角度

## 选择决策树

```
你的需求是什么？
│
├─ 创建常见结构（桌椅、门框、栅栏）？
│  └─ ✅ 使用组合模板 (Level 1)
│      create_table_with_chairs()
│      create_fence()
│      create_door_frame()
│
├─ 需要朝向控制（箭头、椅子）？
│  └─ ✅ 使用语义化API (Level 2)
│      builder.face_towards()
│      builder.face_away_from()
│
├─ 环形阵列？
│  └─ ✅ 使用组合模板 (Level 1)
│      create_table_with_chairs()
│
└─ 完全自定义？
   └─ ✅ 使用 GNodesBuilder (Level 3)
       builder.add_node_group()
```

## 常见场景最佳实践

### 场景1：会议室

```python
from gnodes_builder import create_table_with_chairs

# 主会议桌
create_table_with_chairs("MainTable", (0, 0, 0.75), 
                         table_radius=1.5, num_chairs=8)

# 角落小桌
create_table_with_chairs("SideTable", (5, 5, 0.75), 
                         table_radius=0.5, num_chairs=2)
```

### 场景2：庭院

```python
from gnodes_builder import create_fence, GNodesBuilder

# 围栏
create_fence("Fence_North", (-10, 8), (10, 8), num_posts=12)
create_fence("Fence_South", (-10, -8), (10, -8), num_posts=12)

# 装饰柱（带扭曲）
builder = GNodesBuilder("Pillar")
builder.add_node_group("G_Base_Cylinder", inputs={"Radius": 0.2, "Height": 2.0})
builder.add_node_group("G_Twist", inputs={"Angle": math.pi})
builder.add_node_group("G_Align_Ground")
builder.finalize()
builder.set_location(-5, 0, 0)
```

### 场景3：走廊

```python
from gnodes_builder import create_door_frame, GNodesBuilder

# 门框
create_door_frame("Door_01", (0, 0, 0))
create_door_frame("Door_02", (5, 0, 0))

# 墙体
builder = GNodesBuilder("Wall")
builder.add_node_group("G_Base_Cube", inputs={"Size": (10, 0.2, 2.5)})
builder.add_node_group("G_Align_Ground")
builder.finalize()
```

## 调试技巧

### 1. 分步调试

```python
# 先创建不旋转
builder = GNodesBuilder("Test")
builder.add_node_group("G_Base_Cube", inputs={"Size": (2, 0.5, 0.5)})
builder.add_node_group("G_Align_Ground")
builder.finalize()
builder.set_location(0, 0, 0)

# 检查位置正确后，再添加旋转
builder.face_towards(5, 5)
```

### 2. 画出俯视图

```python
# 在注释中画图
"""
圆桌俯视图：

        0°
         ↑
   270° ← ● → 90°
         ↓
       180°

椅子朝向：
- 0°位置 → 面向180°（桌子中心）
- face_direction = angle + π
"""
```

### 3. 先测试单个

```python
# 先测试第一个椅子（i=0）
# 确认位置和朝向正确后，再循环
```

## 性能建议

### Resolution 参数

| 场景 | 推荐值 |
|------|--------|
| 远景物体 | 6-8 |
| 中景物体 | 12-16 |
| 近景物体 | 24-32 |
| 不要超过 | 32 |

### G_Smooth Level

| Level | 顶点数 | 用途 |
|-------|--------|------|
| 1 | 4x | 轻微圆润 |
| 2 | 16x | 明显平滑 |
| 3 | 64x | 很平滑（慢） |
| 4 | 256x | 极致平滑（很慢） |

⚠️ 推荐：Level 1-2

## 常见错误

### 错误1：忘记 G_Align_Ground

```python
# ❌ 错误
builder.add_node_group("G_Base_Cube", ...)
builder.finalize()  # 物体会"插进地里"

# ✅ 正确
builder.add_node_group("G_Base_Cube", ...)
builder.add_node_group("G_Align_Ground")  # 必须！
builder.finalize()
```

### 错误2：Centered 版本也调用 G_Align_Ground

```python
# ❌ 错误
builder.add_node_group("G_Base_Cylinder_Centered", ...)
builder.add_node_group("G_Align_Ground")  # Centered 版本不需要！

# ✅ 正确
builder.add_node_group("G_Base_Cylinder_Centered", ...)
builder.finalize()  # 直接完成
```

### 错误3：手动计算角度

```python
# ❌ 旧方式（容易错）
back.rotation_euler = (0, 0, angle + math.pi / 2)  # 为什么加 π/2?

# ✅ 新方式（不会错）
back.align_tangent_to_circle(table_x, table_y)  # 语义清晰
```

## 总结

| 使用场景 | 推荐方式 | 代码量 | 错误率 |
|---------|---------|--------|--------|
| 常见结构 | 组合模板 | 1行 | 0% |
| 朝向控制 | 语义化API | 5-10行 | 低 |
| 完全自定义 | GNodesBuilder | 20+行 | 中 |

**建议**：优先使用组合模板和语义化API，只在必要时才手动计算。

