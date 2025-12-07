# API 使用优先级指南

## 问题：API选择困惑

工具现在有多套API可以实现相同功能，AI可能不知道该用哪个。

### 示例：让物体朝向原点

```python
# 方式1：手动计算角度（旧）
dx = 0 - obj.location.x
dy = 0 - obj.location.y
angle = math.atan2(dy, dx)
builder.set_rotation(0, 0, angle)

# 方式2：语义化API（新）
builder.face_towards(0, 0)
```

AI会困惑：**用哪个？**

---

## ⭐ 使用优先级规则

### 规则1：优先使用组合模板

| 需求 | 优先方案 | 备选方案 |
|-----|---------|---------|
| 创建椅子 | `create_chair()` | 手动组装 |
| 创建圆桌+椅子 | `create_table_with_chairs()` | 手动环形阵列 |
| 创建栅栏 | `create_fence()` | 手动阵列+横杆 |
| 创建门框 | `create_door_frame()` | 手动3个部件 |

**原则**：如果有现成模板，**永远优先用模板**。

---

### 规则2：旋转API优先级

| 场景 | 优先使用 | 避免使用 |
|-----|---------|---------|
| **朝向某点** | `face_towards(x, y)` | `set_rotation()` + atan2 |
| **背对某点** | `face_away_from(x, y)` | `set_rotation()` + 计算 |
| **环形阵列的切线** | `align_tangent_to_circle(cx, cy)` | `set_rotation()` + π/2 |
| **3轴旋转** | `set_rotation_degrees(x, y, z)` | `set_rotation()` 弧度版 |
| **已知精确角度** | `set_rotation_degrees(0, 0, 45)` | 计算弧度 |

**原则**：
1. **能用语义化API就不用手动计算**
2. **能用角度制就不用弧度制**（`degrees` > 弧度）
3. **完全不知道角度时，用语义化API**

---

### 规则3：决策树

```
需要旋转物体？
│
├─ 需要朝向/背对某个位置？
│  ├─ 朝向 → face_towards(x, y)          ⭐ 优先
│  └─ 背对 → face_away_from(x, y)        ⭐ 优先
│
├─ 在环形阵列中？
│  └─ align_tangent_to_circle(cx, cy)    ⭐ 优先
│
├─ 需要微调现有旋转？
│  └─ rotate_around_z(angle)             ⭐ 优先
│
├─ 已知精确角度（如45°、90°）？
│  └─ set_rotation_degrees(0, 0, 45)     ⭐ 优先
│
└─ 需要3轴复杂旋转？
   └─ set_rotation(rx, ry, rz)           最后选择
```

---

## 废弃建议

以下API**不建议废弃**，但应该**降低优先级**：

| API | 状态 | 何时使用 |
|-----|------|---------|
| `set_rotation(弧度)` | 保留 | 仅当需要精确弧度值时 |
| `set_rotation_degrees(角度)` | 保留 | 已知精确角度时 |

**原则**：保留底层API，但AI应优先使用高层API。

---

## AI使用指南

### ✅ 推荐模式

```python
# 1. 优先：组合模板
create_table_with_chairs("Dining", (0, 0, 0))

# 2. 次优：语义化API
builder.set_location(3, 5, 0)
builder.face_towards(0, 0)

# 3. 最后：手动
builder.set_rotation_degrees(0, 0, 45)
```

### ❌ 避免模式

```python
# 不推荐：手动计算角度
dx = target_x - obj.x
dy = target_y - obj.y
angle = math.atan2(dy, dx)
builder.set_rotation(0, 0, angle)

# 应该用：
builder.face_towards(target_x, target_y)
```

---

## 文档标注规范

在 `ai_agent_prompt.md` 中用优先级标记：

```markdown
| 方法 | 说明 | 优先级 |
|------|------|--------|
| `face_towards(x, y)` | 朝向目标 | ⭐⭐⭐ |
| `set_rotation_degrees(x, y, z)` | 手动设置角度 | ⭐ |
| `set_rotation(x, y, z)` | 手动设置弧度 | (避免使用) |
```

---

## 总结

| 问题 | 解决方案 |
|-----|---------|
| API重复 | ✅ 是的，确实有重复 |
| 影响 | AI可能困惑选择 |
| 方案 | 明确优先级 + 决策树 + 标注 |
| 是否废弃 | ❌ 不废弃，保留灵活性 |

**核心原则**：
- **语义化API优先**（face_towards）
- **组合模板优先**（create_chair）
- **手动计算最后**（set_rotation + atan2）

