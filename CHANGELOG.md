# 更新日志

## v2.0.0 - 2025-12-06

### 🎯 重大改进：语义化API与组合模板

#### 新增功能

**语义化空间API** - 避免角度计算错误
- `face_towards(x, y)` - 自动朝向目标
- `face_away_from(x, y)` - 自动背对目标  
- `align_tangent_to_circle(cx, cy)` - 对齐到圆的切线
- `rotate_around_z(angle)` - Z轴额外旋转

**组合物体模板** - 复杂结构一行搞定
- `create_chair(name, location, face_direction)` - 椅子（座面+靠背）
- `create_table_with_chairs(...)` - 圆桌+椅子组合
- `create_fence(start, end, num_posts)` - 栅栏（柱子+横杆）
- `create_door_frame(location, width, height)` - 门框（3部件）

**新增节点组** - 从12个扩展到24个
- 曲线：`G_Curve_Circle`, `G_Curve_Line`, `G_Curve_To_Mesh`, `G_Pipe`
- 变形：`G_Bend`, `G_Twist`（在已有的 `G_Taper`, `G_Shear`, `G_Smooth` 基础上）
- 阵列：`G_Array_Linear`, `G_Array_Circular`
- Centered版本：`G_Base_Cube_Centered`, `G_Base_Cylinder_Centered`, `G_Base_Sphere_Centered`
- 新几何体：`G_Base_Wedge`

#### 文档重组

```
docs/
├── ai/              ← AI Agent 专用
│   ├── ai_agent_prompt.md
│   └── api_quick_reference.md
└── dev/             ← 开发者专用
    ├── usage_guide.md
    ├── api_improvements.md
    ├── api_priority_guide.md
    ├── node_group_specifications.md
    └── feasibility_analysis.md
```

#### 示例更新

- 新增：`examples/new_api_demo.py` - 新API演示
- 新增：`examples/before_after_comparison.py` - 新旧对比（70行 vs 1行）
- 更新：`examples/architecture_demo.py` - 使用新模板

#### 效果对比

| 指标 | v1.0 | v2.0 | 提升 |
|-----|------|------|------|
| 节点组数量 | 12 | 24 | 100% |
| API数量 | 3 | 11 | 267% |
| 椅子代码行数 | 70 | 1 | 70x |
| 角度计算错误率 | 高 | 0 | 100% |

#### 破坏性变化

**无** - 完全向后兼容

---

## v1.0.0 - 2025-12-05

### 初始版本

#### 核心功能
- GNodesBuilder 构建器类
- 12个基础节点组
- S.I.O 协议
- 链式调用API

#### 节点组列表
- 基础：`G_Base_Cube`, `G_Base_Cylinder`, `G_Base_Sphere`
- 效果：`G_Damage_Edges`, `G_Scatter_Moss`, `G_Scatter_On_Top`
- 工具：`G_Boolean_Cut`, `G_Voxel_Remesh`, `G_Align_Ground`

#### 示例
- `examples/demo_test.py`
- `examples/golden_gate_bridge.py`
- `examples/living_room.py`
- `examples/tricycle.py`

---

## 升级指南

### 从 v1.0 升级到 v2.0

1. **更新节点库**
   ```bash
   blender --background --python scripts/create_node_library.py
   ```

2. **更新代码（可选，推荐）**
   ```python
   # v1.0 代码仍然可以运行
   builder.set_rotation(0, 0, angle)
   
   # v2.0 推荐使用
   builder.face_towards(target_x, target_y)
   ```

3. **学习新API**
   - 阅读 [docs/ai/api_quick_reference.md](docs/ai/api_quick_reference.md)
   - 运行 `examples/new_api_demo.py` 查看示例

**无需修改现有代码** - 完全向后兼容！

