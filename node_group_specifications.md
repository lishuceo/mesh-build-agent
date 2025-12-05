# 节点组规范文档 (Node Group Specifications)

本文档定义了所有节点组的接口规范，遵循 **S.I.O 协议**。

## S.I.O 协议说明

- **S (Size/Scale)**: 所有生成器必须接受 Vector(X, Y, Z) 作为尺寸输入
- **I (Integers/Seed)**: 所有随机效果必须暴露 Seed 整数接口
- **O (Origin)**: 所有输出几何体的原点（Pivot）必须强制在 **底部中心 (Bottom Center)**

## 节点组详细规范

### 1. G_Base_Cube

**功能**: 生成标准倒角立方体

**输入接口**:
- `Size` (Vector): 尺寸 (X, Y, Z)，单位：米
  - 默认值: (1.0, 1.0, 1.0)
- `Bevel` (Float): 倒角大小
  - 范围: 0.0 - 1.0
  - 默认值: 0.0

**输出接口**:
- `Geometry` (Geometry): 生成的立方体几何体

**实现要点**:
- 原点必须在底部中心
- 使用 `Set Position` 节点将几何体底部对齐到 Z=0
- 倒角使用 `Bevel Edges` 节点

**Blender节点组创建步骤**:
1. 创建新的 Geometry Node Group，命名为 `G_Base_Cube`
2. 添加输入接口：
   - `Size` (Vector)
   - `Bevel` (Float)
3. 添加节点：
   - `Mesh Cube` → 设置尺寸
   - `Bevel Edges` → 应用倒角
   - `Set Position` → 对齐到底部中心
4. 连接输出接口：`Geometry`

---

### 2. G_Base_Cylinder

**功能**: 生成标准圆柱/管道

**输入接口**:
- `Radius` (Float): 半径，单位：米
  - 默认值: 0.5
- `Height` (Float): 高度，单位：米
  - 默认值: 2.0
- `Resolution` (Int): 分段数
  - 范围: 3 - 64
  - 默认值: 16

**输出接口**:
- `Geometry` (Geometry): 生成的圆柱几何体

**实现要点**:
- 原点在底部中心
- 使用 `Mesh Cylinder` 节点
- 通过 `Set Position` 对齐底部

---

### 3. G_Base_Sphere

**功能**: 生成标准球体

**输入接口**:
- `Radius` (Float): 半径，单位：米
  - 默认值: 1.0
- `Resolution` (Int): 分段数
  - 范围: 4 - 64
  - 默认值: 16

**输出接口**:
- `Geometry` (Geometry): 生成的球体几何体

---

### 4. G_Damage_Edges

**功能**: 边缘破损效果

**输入接口**:
- `Geometry` (Geometry): 输入几何体（自动连接）
- `Amount` (Float): 破损强度
  - 范围: 0.0 - 1.0
  - 默认值: 0.5
- `Scale` (Float): 噪声缩放
  - 默认值: 2.0
- `Seed` (Int): 随机种子
  - 默认值: 0

**输出接口**:
- `Geometry` (Geometry): 处理后的几何体

**实现要点**:
- 使用 `Noise Texture` 生成随机破损
- 使用 `Extrude Mesh` 或 `Delete Geometry` 创建破损效果
- 保持几何体完整性

---

### 5. G_Scatter_Moss

**功能**: 在表面散布苔藓

**输入接口**:
- `Geometry` (Geometry): 输入几何体
- `Density` (Float): 密度
  - 范围: 0.0 - 200.0
  - 默认值: 50.0
- `Seed` (Int): 随机种子
  - 默认值: 0

**输出接口**:
- `Geometry` (Geometry): 带苔藓的几何体

**实现要点**:
- 使用 `Distribute Points on Faces` 生成散布点
- 使用 `Instance on Points` 实例化苔藓模型
- 苔藓模型可以是简单的立方体或更复杂的几何体

---

### 6. G_Scatter_On_Top

**功能**: 在物体顶部撒点东西（草/石头）

**输入接口**:
- `Geometry` (Geometry): 输入几何体
- `Density` (Float): 密度
  - 默认值: 10.0
- `Seed` (Int): 随机种子
  - 默认值: 0

**输出接口**:
- `Geometry` (Geometry): 处理后的几何体

**实现要点**:
- 使用 `Mesh to Points` 在顶部表面生成点
- 过滤：只保留 Z 坐标最大的点
- 实例化草/石头模型

---

### 7. G_Boolean_Cut

**功能**: 挖洞/布尔运算

**输入接口**:
- `Geometry` (Geometry): 主几何体
- `Cut_Geometry` (Geometry): 用于切割的几何体
- `Operation` (String): 操作类型
  - 选项: "Difference", "Union", "Intersect"
  - 默认值: "Difference"

**输出接口**:
- `Geometry` (Geometry): 布尔运算后的几何体

**实现要点**:
- 使用 `Mesh Boolean` 节点
- 确保两个几何体都是网格类型

---

### 8. G_Voxel_Remesh

**功能**: 风格化处理（统一体素化）

**输入接口**:
- `Geometry` (Geometry): 输入几何体
- `Voxel_Size` (Float): 体素大小
  - 范围: 0.01 - 1.0
  - 默认值: 0.1

**输出接口**:
- `Geometry` (Geometry): 体素化后的几何体

**实现要点**:
- 使用 `Voxel Remesh` 节点（如果可用）
- 或使用 `Remesh` 节点替代

---

### 9. G_Align_Ground ⚠️ **核心节点组**

**功能**: 强制对齐地面（将 Min Z 归零）

**输入接口**:
- `Geometry` (Geometry): 输入几何体

**输出接口**:
- `Geometry` (Geometry): 对齐后的几何体

**实现要点**:
1. 使用 `Bounding Box` 节点获取几何体的边界框
2. 计算最小 Z 值
3. 使用 `Set Position` 节点将几何体向下移动，使最小 Z = 0
4. **这是防止模型"插进地里"的关键节点组**

**Blender节点组创建步骤**:
```
输入 Geometry
  ↓
Bounding Box → 获取 Min Z
  ↓
Math (Subtract) → 计算偏移量 (0 - Min_Z)
  ↓
Set Position → 应用偏移到 Z 轴
  ↓
输出 Geometry
```

---

## 创建节点组库的完整流程

### 步骤1：在Blender中创建节点组

1. 打开 Blender
2. 切换到 `Geometry Nodes` 编辑器
3. 创建新的 Geometry Node Group：
   - `Shift + A` → `Group` → `New Geometry Nodes Group`
   - 或通过 `Node` → `Group` → `New Geometry Nodes Group`

### 步骤2：设置接口

1. 在节点组编辑器中，点击 `Interface` 面板
2. 添加输入接口：
   - 点击 `+ Input`
   - 设置名称、类型、默认值
3. 添加输出接口：
   - 点击 `+ Output`
   - 通常只需要一个 `Geometry` 输出

### 步骤3：连接节点逻辑

按照每个节点组的"实现要点"连接节点

### 步骤4：标记为Fake User

1. 在 `Outliner` 中找到节点组
2. 右键 → `Fake User`（或按 `F`）
3. 这防止节点组在未使用时被清除

### 步骤5：保存库文件

1. `File` → `Save As`
2. 保存为 `node_library.blend`（或任意名称）
3. 确保所有节点组都已标记为 Fake User

### 步骤6：在Python中加载

```python
from node_library_loader import load_node_library

load_node_library("path/to/node_library.blend")
```

---

## 测试节点组

创建节点组后，可以使用以下代码测试：

```python
from ai_gnodes_helper import GNodesBuilder, validate_node_group

# 验证节点组
result = validate_node_group("G_Base_Cube")
print(result)

# 测试使用
builder = GNodesBuilder("Test_Cube")
builder.add_node_group("G_Base_Cube", inputs={"Size": (2, 1, 0.5)})
builder.add_node_group("G_Align_Ground")
builder.finalize()
```

---

## 扩展节点组

当需要新的节点组时：

1. 遵循 S.I.O 协议
2. 使用清晰的命名（`G_` 前缀）
3. 在本文档中添加规范
4. 提供实现要点和示例

---

## 常见问题

**Q: 节点组创建后找不到？**
A: 确保节点组名称以 `G_` 开头，且已标记为 Fake User

**Q: 如何调试节点组？**
A: 在节点组编辑器中，使用 `Viewer` 节点查看中间结果

**Q: 节点组可以嵌套吗？**
A: 可以！节点组可以调用其他节点组，实现模块化

**Q: 如何优化性能？**
A: 
- 减少不必要的细分
- 使用 `LOD`（细节层次）节点组
- 合理设置 Resolution 参数
