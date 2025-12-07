# 60秒快速开始

## 🤖 如果你是 AI Agent

### 必读文档（2个）

1. **[ai/ai_agent_prompt.md](ai/ai_agent_prompt.md)** - 你的系统提示词  
   → 阅读全文，理解所有节点组和API

2. **[ai/api_quick_reference.md](ai/api_quick_reference.md)** - API速查表  
   → 写代码时不确定用哪个API就看这里

### 核心原则（3条）

```python
# 1. 优先使用组合模板
create_table_with_chairs("Dining", (0, 0, 0))  # ✅ 最优

# 2. 需要旋转时用语义化API
builder.face_towards(0, 0)                      # ✅ 次优

# 3. 避免手动计算角度
angle = math.atan2(dy, dx)                      # ❌ 禁止
```

---

## 👨‍💻 如果你是开发者

### 第一次使用（3步）

```bash
# 1. 生成节点库
blender --background --python scripts/create_node_library.py

# 2. 运行演示
blender assets/node_library.blend --python examples/new_api_demo.py

# 3. 阅读教程
# 打开 docs/dev/usage_guide.md
```

### 核心文档（3个）

1. **[dev/usage_guide.md](dev/usage_guide.md)** - 使用教程  
   → 三种使用方式、场景实践、调试技巧

2. **[ai/api_quick_reference.md](ai/api_quick_reference.md)** - API速查  
   → 不知道用哪个API时查这里

3. **[dev/api_improvements.md](dev/api_improvements.md)** - 设计说明  
   → 理解为什么要这样设计

---

## 🎯 典型场景

### 场景1：创建圆桌+椅子

```python
from gnodes_builder import create_table_with_chairs

# 一行搞定（自动处理椅子朝向）
create_table_with_chairs("Dining", (0, 0, 0.7), num_chairs=4)
```

**详见**：[ai/ai_agent_prompt.md](ai/ai_agent_prompt.md) 任务5

---

### 场景2：创建栅栏

```python
from gnodes_builder import create_fence

# 一行搞定（自动计算角度）
create_fence("Fence", start_pos=(-5, 0), end_pos=(5, 0), num_posts=10)
```

**详见**：[ai/ai_agent_prompt.md](ai/ai_agent_prompt.md) 任务6

---

### 场景3：让物体朝向某点

```python
builder.set_location(3, 5, 0)
builder.face_towards(0, 0)  # 自动计算角度
```

**详见**：[ai/api_quick_reference.md](ai/api_quick_reference.md) 旋转控制

---

## 📋 检查清单

在编写代码前，检查：

- [ ] 能用组合模板吗？（`create_xxx`）
- [ ] 需要旋转吗？用语义化API（`face_towards`）
- [ ] 是否在手动计算 `atan2()`？**禁止！**
- [ ] Centered版本调用了 `G_Align_Ground`？**错误！**
- [ ] 非Centered版本忘记 `G_Align_Ground`？**错误！**

---

## 🚨 最常见的3个错误

### 错误1：手动计算角度

```python
# ❌ 错误
angle = math.atan2(dy, dx)
builder.set_rotation(0, 0, angle)

# ✅ 正确
builder.face_towards(target_x, target_y)
```

### 错误2：手动组装椅子

```python
# ❌ 错误（70行代码）
seat = create_cube(...)
back = create_cube(...)
# 计算靠背位置...
# 计算靠背角度... (容易错)

# ✅ 正确（1行代码）
create_chair("Chair", (x, y, z), face_direction)
```

### 错误3：Centered版本对齐地面

```python
# ❌ 错误
builder.add_node_group("G_Base_Cylinder_Centered", ...)
builder.add_node_group("G_Align_Ground")  # Centered不需要！

# ✅ 正确
builder.add_node_group("G_Base_Cylinder_Centered", ...)
builder.finalize()  # 直接完成
```

---

## 完整文档

- [文档导航地图](NAVIGATION.md) - 详细的导航指引
- [文档结构说明](STRUCTURE.md) - 设计原理

