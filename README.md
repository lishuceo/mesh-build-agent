# AI驱动的Blender几何节点生成管线

通过**"胶水代码（Glue Code）"模式**，将 Blender 强大的几何节点能力封装成简单的 API，供 AI Agent 调用。

---

## 🚀 快速入口

| 你是谁？ | 从这里开始 |
|---------|-----------|
| **AI Agent** | 📖 [AI系统提示词](docs/ai/ai_agent_prompt.md) |
| **开发者（首次使用）** | 📖 [使用教程](docs/dev/usage_guide.md) |
| **开发者（API选择困惑）** | 📖 [API速查表](docs/ai/api_quick_reference.md) |
| **开发者（扩展开发）** | 📖 [节点组规范](docs/dev/node_group_specifications.md) |

**⚡ 60秒快速开始**：[docs/QUICK_START.md](docs/QUICK_START.md)  
**📁 完整文档索引**：[docs/README.md](docs/README.md)  
**🗺️ 文档导航地图**：[docs/NAVIGATION.md](docs/NAVIGATION.md)

---

## 核心哲学

- **人类负责**：定义"原子级"的规则（Node Groups）
- **AI负责**：进行"分子级"的组装
- **结果**：既保证模型绝对工整（不歪），又赋予 AI 极大的创作自由

## 方案优势

✅ **稳定性**：AI不需要直接操作顶点坐标，避免模型扭曲  
✅ **可扩展性**：通过添加新的节点组扩展能力  
✅ **可维护性**：节点组由人类专家创建，保证质量  
✅ **易用性**：AI只需要调用简单的API，无需深入Blender细节  
✅ **语义化**：用"朝向目标"替代"计算角度"，避免空间推理错误  
✅ **模板化**：常用结构一行搞定（椅子、桌子、门框、栅栏）  

## 项目结构

```
mesh-build-agent/
├── README.md                           # 本文件
├── .gitignore                          # Git 忽略配置
│
├── docs/                               # 📚 文档
│   ├── README.md                       # 文档索引
│   ├── ai/                             # 🤖 AI Agent 专用文档
│   │   ├── README.md
│   │   ├── ai_agent_prompt.md          # AI 系统提示词（主文档）
│   │   └── api_quick_reference.md      # API 速查表
│   └── dev/                            # 👨‍💻 开发者文档
│       ├── README.md
│       ├── usage_guide.md              # 使用教程
│       ├── api_improvements.md         # API 设计说明
│       ├── api_priority_guide.md       # API 优先级指南
│       ├── node_group_specifications.md # 节点组规范
│       └── feasibility_analysis.md     # 可行性分析
│
├── src/                                # 📦 源代码
│   └── gnodes_builder/                 # 核心库
│       ├── __init__.py                 # 包入口
│       ├── builder.py                  # GNodesBuilder（含语义化API）
│       ├── loader.py                   # NodeLibraryManager
│       └── templates.py                # 组合物体模板 ⚠️ 新增
│
├── scripts/                            # 🔧 脚本
│   ├── create_node_library.py          # 创建节点组库（24个节点组）
│   ├── verify_node_library.py          # 验证节点组库
│   ├── ai_api_server.py                # AI API 服务器
│   └── ai_executor.py                  # AI 执行器
│
├── examples/                           # 💡 示例
│   ├── demo_test.py                    # 基础演示
│   ├── architecture_demo.py            # 建筑场景演示
│   ├── new_api_demo.py                 # 新API演示 ⚠️ 新增
│   ├── before_after_comparison.py      # 新旧对比 ⚠️ 新增
│   ├── golden_gate_bridge.py           # 金门大桥
│   ├── living_room.py                  # 客厅场景
│   └── tricycle.py                     # 三轮车
│
├── tests/                              # 🧪 测试
│   └── test_gnodes_builder.py          # 单元测试
│
└── assets/                             # 🎨 资源文件
    └── node_library.blend              # 节点组库（24个节点组）
```

## 快速开始

⚠️ **首次使用请阅读**：[使用教程](docs/dev/usage_guide.md) | [API速查表](docs/ai/api_quick_reference.md)

### 1. 生成节点组库

```bash
# 在项目根目录运行
blender --background --python scripts/create_node_library.py
```

这会在 `assets/` 目录下生成 `node_library.blend` 文件，包含 24 个预制节点组。

### 2. 验证节点组库

```bash
blender --background --python scripts/verify_node_library.py
```

### 3. 运行演示

```bash
# 打开 Blender GUI 查看效果
blender assets/node_library.blend --python examples/demo_test.py
```

### 4. 在 Blender 中使用

```python
import sys
sys.path.append("/path/to/mesh-build-agent/src")

from gnodes_builder import GNodesBuilder, load_node_library

# 加载节点组库
load_node_library("/path/to/mesh-build-agent/assets/node_library.blend")

# 创建模型
builder = GNodesBuilder("My_Model")
builder.add_node_group("G_Base_Cube", inputs={"Size": (2.0, 1.0, 0.5), "Bevel": 0.1})
builder.add_node_group("G_Align_Ground")
builder.finalize()
```

## 可用的节点组

### 基础几何体

| 节点组 | 功能 | 主要参数 |
|--------|------|----------|
| `G_Base_Cube` | 标准立方体（原点在底部） | Size, Bevel |
| `G_Base_Cylinder` | 标准圆柱（原点在底部） | Radius, Height, Resolution |
| `G_Base_Sphere` | 标准球体（原点在底部） | Radius, Resolution |
| `G_Base_Wedge` | 楔形体（斜面） | Size |
| `G_Base_Cube_Centered` | 立方体（原点在中心） | Size |
| `G_Base_Cylinder_Centered` | 圆柱（原点在中心） | Radius, Height, Resolution |
| `G_Base_Sphere_Centered` | 球体（原点在中心） | Radius, Resolution |

### 变形节点

| 节点组 | 功能 | 主要参数 |
|--------|------|----------|
| `G_Taper` | 锥形变形 - 顶部收窄 | Factor (0-1) |
| `G_Shear` | 剪切变形 - 倾斜 | Amount |
| `G_Smooth` | 细分平滑 - 变圆润 | Level (1-4) |
| `G_Bend` | **弯曲变形** - 沿Z轴弯曲 | Angle |
| `G_Twist` | **扭曲变形** - 绕Z轴扭曲 | Angle |

### 曲线节点 ⚠️ 新增

| 节点组 | 功能 | 主要参数 |
|--------|------|----------|
| `G_Curve_Circle` | 圆形曲线（截面） | Radius, Resolution |
| `G_Curve_Line` | 直线曲线（路径） | Start, End |
| `G_Curve_To_Mesh` | 曲线转网格（沿路径挤出） | Curve, Profile, Fill_Caps |
| `G_Pipe` | **便捷管道** | Radius, Length, Resolution |

### 阵列节点 ⚠️ 新增

| 节点组 | 功能 | 主要参数 |
|--------|------|----------|
| `G_Array_Linear` | **线性阵列** | Count, Offset |
| `G_Array_Circular` | **环形阵列** | Count, Radius |

### 效果与后处理

| 节点组 | 功能 | 主要参数 |
|--------|------|----------|
| `G_Damage_Edges` | 边缘破损效果 | Amount, Scale, Seed |
| `G_Scatter_Moss` | 表面苔藓散布 | Density, Seed |
| `G_Scatter_On_Top` | 顶部物体散布 | Density, Seed |
| `G_Boolean_Cut` | 布尔切割 | Cut_Geometry |
| `G_Voxel_Remesh` | 体素重建 | Voxel_Size |
| `G_Align_Ground` | **地面对齐（核心）** | - |

## 核心概念

### S.I.O 协议

所有节点组遵循统一接口规范：

- **S (Size/Scale)**: 接受Vector尺寸输入
- **I (Integers/Seed)**: 随机效果暴露Seed接口
- **O (Origin)**: 输出原点在底部中心

### 节点组命名规范

- 必须以 `G_` 开头
- 使用下划线分隔（如 `G_Base_Cube`）
- 名称清晰描述功能

## 使用示例

### 示例1：简单墙体

```python
builder = GNodesBuilder("Wall_01")
builder.add_node_group("G_Base_Cube", inputs={"Size": (4.0, 0.3, 2.5)})
builder.add_node_group("G_Align_Ground")
builder.finalize()
```

### 示例2：破损石柱

```python
builder = GNodesBuilder("Ancient_Pillar")
builder.add_node_group("G_Base_Cylinder", inputs={"Radius": 0.5, "Height": 4.0, "Resolution": 16})
builder.add_node_group("G_Damage_Edges", inputs={"Amount": 0.8})
builder.add_node_group("G_Scatter_Moss", inputs={"Density": 50.0, "Seed": 1024})
builder.add_node_group("G_Align_Ground")
builder.finalize()
```

### 示例3：语义化空间API ⚠️ 新增

```python
from gnodes_builder import GNodesBuilder

# 创建一个箭头
builder = GNodesBuilder("Arrow")
builder.add_node_group("G_Base_Cube", inputs={"Size": (2.0, 0.2, 0.2)})
builder.add_node_group("G_Align_Ground")
builder.finalize()

builder.set_location(-3, 5, 0.5)
# 自动朝向目标，无需手动计算角度！
builder.face_towards(0, 0)
```

### 示例4：组合物体模板 ⚠️ 新增

```python
from gnodes_builder import create_table_with_chairs, create_door_frame

# 一行代码创建整套餐桌（桌子+4把椅子）
create_table_with_chairs("Dining", location=(0, 0, 0.7), num_chairs=4)

# 一行代码创建门框（左柱+右柱+门楣）
create_door_frame("MainDoor", location=(0, 5, 0), width=1.0, height=2.1)
```

## AI Agent 集成

### 系统提示词

使用 `docs/ai_agent_prompt.md` 中的提示词模板配置 AI Agent。

### 关键要点

1. AI 不需要理解 Blender 内部实现
2. AI 只需要知道节点组名称和参数
3. 所有操作通过链式调用完成
4. **最后必须调用 `G_Align_Ground`**

## 新特性 ⚠️ v2.0

### 语义化空间API - 避免角度计算错误

```python
builder.face_towards(target_x, target_y)      # 朝向目标
builder.face_away_from(target_x, target_y)    # 背对目标
builder.align_tangent_to_circle(cx, cy)      # 对齐切线
```

### 组合物体模板 - 复杂结构一行搞定

```python
create_table_with_chairs("Dining", (0, 0, 0), num_chairs=4)
create_fence("Fence", start_pos=(-5, 0), end_pos=(5, 0))
create_door_frame("Door", (0, 0, 0), width=1.0)
create_chair("Chair", (0, 0, 0), face_direction=0)
```

**效果**：70行代码 → 1行代码，空间关系自动处理

## 文档

📁 **[完整文档索引](docs/README.md)**

### 🤖 AI Agent 文档
- [AI Agent 系统提示词](docs/ai/ai_agent_prompt.md) - **AI配置必读**
- [API 快速参考](docs/ai/api_quick_reference.md) - 速查表

### 👨‍💻 开发者文档
- [使用指南](docs/dev/usage_guide.md) - **推荐首先阅读**
- [API 改进说明](docs/dev/api_improvements.md) - 设计原理
- [API 优先级指南](docs/dev/api_priority_guide.md) - 避免API混淆
- [节点组规范](docs/dev/node_group_specifications.md) - 扩展开发
- [可行性分析](docs/dev/feasibility_analysis.md) - 技术背景

## 扩展开发

### 添加新节点组

1. 在 `scripts/create_node_library.py` 中添加创建函数
2. 在 `docs/node_group_specifications.md` 中添加规范
3. 在 `docs/ai_agent_prompt.md` 中更新工具箱列表
4. 重新运行 `create_node_library.py` 生成库

### 改进构建器

`GNodesBuilder` 类设计为可扩展的：

- 支持自定义节点（`add_custom_node`）
- 支持分支和合并（`branch`, `join_geometries`）
- 支持库文件加载

## 常见问题

**Q: 节点组找不到？**  
A: 确保已运行 `create_node_library.py` 并加载了库文件

**Q: 模型插进地里？**  
A: 确保最后调用了 `G_Align_Ground` 节点组

**Q: 如何调试？**  
A: 在 Blender 的 Geometry Nodes 编辑器中查看生成的节点树

**Q: 性能如何？**  
A: 取决于节点组复杂度，建议合理设置 Resolution 参数

## 项目进度

### v2.0 - 语义化API与组合模板 ✅
- [x] 核心构建器实现
- [x] 节点组库自动生成脚本
- [x] 24 个节点组
- [x] 变形节点组（Taper, Shear, Smooth, Bend, Twist）
- [x] 曲线节点组（Curve_Circle, Curve_Line, Curve_To_Mesh, Pipe）
- [x] 阵列节点组（Array_Linear, Array_Circular）
- [x] **语义化空间API**（face_towards, face_away_from, align_tangent_to_circle）
- [x] **组合物体模板**（create_chair, create_table_with_chairs, create_fence, create_door_frame）
- [x] AI Agent 提示词模板
- [x] 完整文档

### 未来计划
- [ ] 更多组合模板（楼梯、书架、桥梁等）
- [ ] 更多曲线路径类型（贝塞尔曲线、螺旋线）
- [ ] 参数化约束系统
- [ ] 性能优化

## 许可证

本项目采用 MIT 许可证。

---

**注意**：这是一个实验性项目，用于探索 AI 驱动的 3D 建模工作流。在生产环境中使用前，请充分测试。
