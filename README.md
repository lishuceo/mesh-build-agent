# AI驱动的Blender几何节点生成管线

通过**"胶水代码（Glue Code）"模式**，将 Blender 强大的几何节点能力封装成简单的 API，供 AI Agent 调用。

## 核心哲学

- **人类负责**：定义"原子级"的规则（Node Groups）
- **AI负责**：进行"分子级"的组装
- **结果**：既保证模型绝对工整（不歪），又赋予 AI 极大的创作自由

## 方案优势

✅ **稳定性**：AI不需要直接操作顶点坐标，避免模型扭曲  
✅ **可扩展性**：通过添加新的节点组扩展能力  
✅ **可维护性**：节点组由人类专家创建，保证质量  
✅ **易用性**：AI只需要调用简单的API，无需深入Blender细节  

## 项目结构

```
.
├── ai_gnodes_helper.py          # 核心构建器类
├── node_library_loader.py       # 节点组库加载器
├── example_usage.py             # 使用示例
├── test_gnodes_builder.py       # 测试脚本
├── ai_agent_prompt.md           # AI Agent提示词模板
├── node_group_specifications.md # 节点组规范文档
└── README.md                    # 本文件
```

## 快速开始

### 1. 准备工作

在Blender中创建节点组库：

1. 打开Blender
2. 创建Geometry Node Groups（参考 `node_group_specifications.md`）
3. 命名规范：以 `G_` 开头（如 `G_Base_Cube`）
4. 标记为Fake User（防止被清除）
5. 保存为 `.blend` 文件

### 2. 在Blender中使用

```python
# 在Blender的文本编辑器中运行

import bpy
from ai_gnodes_helper import GNodesBuilder

# 创建模型
builder = GNodesBuilder("My_Model")
builder.add_node_group(
    "G_Base_Cube",
    inputs={"Size": (2.0, 1.0, 0.5), "Bevel": 0.1}
)
builder.add_node_group("G_Align_Ground")
builder.finalize()
```

### 3. 从库文件加载

```python
from node_library_loader import load_node_library

# 加载节点组库
load_node_library("/path/to/node_library.blend")

# 然后使用
builder = GNodesBuilder("Model_01")
# ...
```

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
builder.add_node_group(
    "G_Base_Cube",
    inputs={"Size": (4.0, 0.3, 2.5)}
)
builder.add_node_group("G_Align_Ground")
builder.finalize()
```

### 示例2：破损石柱

```python
builder = GNodesBuilder("Ancient_Pillar")
builder.add_node_group(
    "G_Base_Cylinder",
    inputs={"Radius": 0.5, "Height": 4.0, "Resolution": 16}
)
builder.add_node_group("G_Damage_Edges", inputs={"Amount": 0.8})
builder.add_node_group("G_Scatter_Moss", inputs={"Density": 50.0, "Seed": 1024})
builder.add_node_group("G_Align_Ground")
builder.finalize()
```

更多示例见 `example_usage.py`

## AI Agent集成

### 系统提示词

使用 `ai_agent_prompt.md` 中的提示词模板配置AI Agent。

### 关键要点

1. AI不需要理解Blender内部实现
2. AI只需要知道节点组名称和参数
3. 所有操作通过链式调用完成
4. 最后必须调用 `G_Align_Ground`

## 节点组规范

参考 `node_group_specifications.md` 了解：

- 每个节点组的详细接口
- 实现要点
- 创建步骤
- 测试方法

## 测试

运行测试脚本验证功能：

```python
# 在Blender文本编辑器中运行
exec(open("/path/to/test_gnodes_builder.py").read())
```

或直接运行：

```python
from test_gnodes_builder import run_all_tests
run_all_tests()
```

## 扩展开发

### 添加新节点组

1. 在Blender中创建节点组（遵循S.I.O协议）
2. 在 `node_group_specifications.md` 中添加规范
3. 在 `ai_agent_prompt.md` 中更新工具箱列表
4. 测试新节点组

### 改进构建器

`GNodesBuilder` 类设计为可扩展的：

- 支持自定义节点（`add_custom_node`）
- 支持分支和合并（`branch`, `join_geometries`）
- 支持库文件加载

## 常见问题

**Q: 节点组找不到？**  
A: 确保节点组名称以 `G_` 开头，且已加载到场景中

**Q: 模型插进地里？**  
A: 确保最后调用了 `G_Align_Ground` 节点组

**Q: 如何调试？**  
A: 在Blender的Geometry Nodes编辑器中查看生成的节点树

**Q: 性能如何？**  
A: 取决于节点组复杂度，建议合理设置Resolution参数

## 下一步

1. ✅ 创建基础节点组库
2. ✅ 集成到AI Agent系统
3. 🔄 扩展节点组功能
4. 🔄 优化性能和稳定性
5. 🔄 添加更多示例和文档

## 贡献

欢迎贡献：

- 新的节点组实现
- 改进的API设计
- 更多使用示例
- 文档完善

## 许可证

本项目采用MIT许可证。

---

**注意**：这是一个实验性项目，用于探索AI驱动的3D建模工作流。在生产环境中使用前，请充分测试。
