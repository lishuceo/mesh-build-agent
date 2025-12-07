# 赛道/道路 API 改进方案

## 背景

AI Agent 在生成赛道、道路等"沿路径的几何体"时遇到困难：
1. 用方块拼接会有缝隙
2. `G_Curve_To_Mesh` 需要双输入，当前链式 API 难以支持
3. 缺少高层模板函数，代码冗长

## 改进方案

### 方案一：添加底层节点组（推荐）

#### 1. `G_Track_Ring` - 椭圆环形赛道

**功能**：直接生成椭圆环形网格（无缝）

**参数**：
- `Outer_Radius_X` (Float): 外圈X半径
- `Outer_Radius_Y` (Float): 外圈Y半径  
- `Width` (Float): 赛道宽度
- `Height` (Float): 赛道厚度
- `Segments` (Int): 分段数

**输出**：完美无缝的椭圆环形网格

**实现思路**：
```
1. 使用 Curve Circle 生成圆形曲线
2. 缩放成椭圆
3. 生成内圈和外圈两条曲线
4. 使用 Fill Curve 或直接构建网格
```

#### 2. `G_Road_Segment` - 道路段

**功能**：沿任意曲线路径生成道路

**参数**：
- `Path` (Geometry): 路径曲线（输入）
- `Width` (Float): 道路宽度
- `Thickness` (Float): 道路厚度

**输出**：沿路径的道路网格

#### 3. `G_Barrier_Ring` - 护栏环

**功能**：生成椭圆形护栏

**参数**：
- `Radius_X` (Float): X半径
- `Radius_Y` (Float): Y半径
- `Width` (Float): 护栏宽度
- `Height` (Float): 护栏高度

### 方案二：添加高层模板函数

在 `templates.py` 中添加：

```python
def create_oval_track(
    name: str,
    location: Tuple[float, float, float] = (0, 0, 0),
    outer_radius_x: float = 25.0,
    outer_radius_y: float = 15.0,
    track_width: float = 6.0,
    track_thickness: float = 0.3,
    barrier_height: float = 0.8,
    include_barriers: bool = True,
    include_start_line: bool = True
) -> List[bpy.types.Object]:
    """
    一行创建完整的椭圆形赛道
    
    包含：
    - 赛道路面（无缝椭圆环形）
    - 内外护栏
    - 起跑线（可选）
    
    Example:
        # 简单调用
        track = create_oval_track("KartTrack", (0, 0, 0))
        
        # 自定义尺寸
        track = create_oval_track("BigTrack", 
            outer_radius_x=50, outer_radius_y=30,
            track_width=8)
    """
    pass


def create_road_along_path(
    name: str,
    path_points: List[Tuple[float, float, float]],
    width: float = 4.0,
    thickness: float = 0.2,
    include_curbs: bool = True
) -> List[bpy.types.Object]:
    """
    沿指定路径点创建道路
    
    Example:
        points = [(0, 0, 0), (10, 5, 0), (20, 0, 0), (30, -5, 0)]
        road = create_road_along_path("Highway", points, width=6.0)
    """
    pass
```

### 方案三：改进 Builder API 支持双输入

在 `builder.py` 中添加：

```python
def connect_curve_to_mesh(self, path_builder, profile_builder, fill_caps=True):
    """
    连接路径和截面到 Curve to Mesh 节点
    
    Args:
        path_builder: 路径曲线的 builder
        profile_builder: 截面曲线的 builder
        fill_caps: 是否封闭端面
    
    Example:
        # 创建路径
        path = GNodesBuilder("Path")
        path.add_node_group("G_Curve_Circle", inputs={"Radius": 10})
        
        # 创建截面
        profile = GNodesBuilder("Profile")
        profile.add_node_group("G_Curve_Rectangle", inputs={"Width": 6, "Height": 0.3})
        
        # 合并
        road = GNodesBuilder("Road")
        road.connect_curve_to_mesh(path, profile)
        road.finalize()
    """
    pass
```

## 推荐实现顺序

1. **第一步**：在 `templates.py` 中添加 `create_oval_track()` 函数
   - 使用 bmesh 直接创建网格（已验证可行）
   - AI Agent 立即可用

2. **第二步**：在 `create_node_library.py` 中添加 `G_Track_Ring` 节点组
   - 更灵活，可被其他节点组合使用
   - 保持与现有架构一致

3. **第三步**：改进 builder API 支持双输入
   - 长期改进
   - 让 `G_Curve_To_Mesh` 更易用

## AI Agent 使用体验对比

### 当前（需要 400+ 行代码）

```python
# AI 需要手动处理：
# 1. 椭圆参数计算
# 2. 分段拼接
# 3. 切线角度计算
# 4. 护栏位置计算
# ... 大量代码
```

### 改进后（一行搞定）

```python
from gnodes_builder import create_oval_track

# 一行创建完整赛道
track = create_oval_track("KartTrack", (0, 0, 0), 
    outer_radius_x=25, outer_radius_y=15,
    track_width=6, barrier_height=0.8)
```

## 文档更新

在 `ai_agent_prompt.md` 中添加：

```markdown
### 任务N：生成赛道

**用户需求**："生成一个卡丁车赛道"

```python
from gnodes_builder import create_oval_track

# 一行搞定！
track = create_oval_track("KartTrack", (0, 0, 0),
    outer_radius_x=25, outer_radius_y=15,
    track_width=6, barrier_height=0.8)
```
```

## 扩展性

这个模式可以扩展到其他"路径类"结构：
- `create_river()` - 河流
- `create_wall_ring()` - 环形围墙
- `create_moat()` - 护城河
- `create_bridge()` - 桥梁

