# 工具集

本目录包含辅助开发的独立工具。

## 赛道曲线编辑器 (track_curve_editor.py)

一个可视化的曲线编辑器，用于设计赛道路径。

### 功能特性

- 🖱️ **可视化绘制**：在画布上直观地添加、移动、删除控制点
- 📐 **比例尺设置**：设置画布尺寸与物理世界尺寸的映射关系
- 🔄 **实时预览**：使用 Catmull-Rom 样条曲线实时预览平滑路径
- 📤 **多种导出格式**：
  - JSON 格式（可重新导入）
  - Python 代码（可直接在 Blender 中运行）
  - 复制 waypoints 到剪贴板
- 🚀 **一键生成**：直接调用 Blender 生成 3D 赛道模型

### 使用方法

```bash
# 直接运行
python tools/track_curve_editor.py

# 或者在项目根目录
python -m tools.track_curve_editor
```

### 操作说明

| 操作 | 功能 |
|------|------|
| 左键点击空白处 | 添加新控制点 |
| 左键拖动控制点 | 移动控制点 |
| 右键点击控制点 | 删除控制点 |
| Delete 键 | 删除选中的控制点 |
| Ctrl+Z | 撤销 |

### 画布尺寸说明

画布尺寸设置控制了画布像素与物理世界米数的对应关系：

- **宽度/高度（米）**：设置画布代表的物理世界尺寸
- **比例尺**：自动计算显示，如 "1 像素 ≈ 0.12 米"

例如，设置画布为 100m x 75m，则：
- 画布中心对应物理世界原点 (0, 0)
- 画布左边缘对应 x = -50m
- 画布右边缘对应 x = +50m

### 赛道参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 赛道宽度 | 6.0m | 赛道路面的宽度 |
| 路面厚度 | 0.3m | 路面的垂直厚度 |
| 护栏高度 | 0.6m | 两侧护栏的高度 |
| 包含护栏 | 是 | 是否生成护栏 |

### 导出格式

#### JSON 格式

```json
{
  "version": "1.0",
  "world_size": {
    "width": 100.0,
    "height": 75.0
  },
  "waypoints": [
    {"x": 0.0, "y": 0.0},
    {"x": 30.0, "y": 15.0},
    ...
  ],
  "track_params": {
    "track_width": 6.0,
    "track_thickness": 0.3,
    "barrier_height": 0.6,
    "include_barriers": true,
    "closed": true
  }
}
```

#### Python 代码

导出的 Python 代码可以直接在 Blender 中运行：

```bash
blender assets/node_library.blend --python generated_track.py
```

### 截图

（待添加）

### 依赖

- Python 3.x
- tkinter（Python 标准库，通常已安装）
- Blender 3.6+ （用于生成 3D 赛道）

