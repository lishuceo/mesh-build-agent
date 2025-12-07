"""
赛道曲线编辑器
===============

可视化绘制曲线，将绘制的曲线采样成离散的路径点，
然后调用生成赛道的工具来精准生成赛道。

功能：
- 在画布上绘制控制点
- 实时预览 Catmull-Rom 平滑曲线
- 设置画布尺寸与物理世界尺寸的映射（比例尺）
- 导出路径点到 Python 代码或 JSON
- 直接调用 Blender 生成赛道

使用方法：
    python tools/track_curve_editor.py

作者: AI Agent
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import json
import os
import subprocess
import sys


class GeometryUtils:
    """几何计算工具类"""
    
    @staticmethod
    def ccw(A, B, C):
        """判断三点是否逆时针排列"""
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    
    @staticmethod
    def segments_intersect(A, B, C, D):
        """
        检测两条线段是否相交（不包括端点重合的情况）
        
        Args:
            A, B: 第一条线段的两个端点
            C, D: 第二条线段的两个端点
        
        Returns:
            True 如果线段相交，False 否则
        """
        # 排除端点重合的情况
        eps = 1e-10
        if (abs(A[0] - C[0]) < eps and abs(A[1] - C[1]) < eps) or \
           (abs(A[0] - D[0]) < eps and abs(A[1] - D[1]) < eps) or \
           (abs(B[0] - C[0]) < eps and abs(B[1] - C[1]) < eps) or \
           (abs(B[0] - D[0]) < eps and abs(B[1] - D[1]) < eps):
            return False
        
        return (GeometryUtils.ccw(A, C, D) != GeometryUtils.ccw(B, C, D) and 
                GeometryUtils.ccw(A, B, C) != GeometryUtils.ccw(A, B, D))
    
    @staticmethod
    def check_new_segment_intersects(points, new_point):
        """
        检查新增点形成的线段是否与现有线段相交
        
        Args:
            points: 现有控制点列表
            new_point: 新增的点
        
        Returns:
            (bool, str): (是否相交, 相交描述)
        """
        if len(points) < 2:
            return False, ""
        
        # 新线段：从最后一个点到新点
        last_point = points[-1]
        new_segment = (last_point, new_point)
        
        # 检查与所有现有线段（除了相邻的）是否相交
        for i in range(len(points) - 2):  # 不检查最后一条线段（与新线段共享端点）
            segment = (points[i], points[i + 1])
            if GeometryUtils.segments_intersect(new_segment[0], new_segment[1], 
                                                 segment[0], segment[1]):
                return True, f"与线段 {i+1}-{i+2} 相交"
        
        return False, ""


class CatmullRomSpline:
    """Catmull-Rom 样条曲线计算"""
    
    @staticmethod
    def interpolate(p0, p1, p2, p3, t):
        """
        Catmull-Rom 样条插值
        
        Args:
            p0, p1, p2, p3: 四个控制点 (x, y)
            t: 参数 [0, 1]
        
        Returns:
            插值点 (x, y)
        """
        t2 = t * t
        t3 = t2 * t
        
        x = 0.5 * (
            (2 * p1[0]) +
            (-p0[0] + p2[0]) * t +
            (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
            (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3
        )
        
        y = 0.5 * (
            (2 * p1[1]) +
            (-p0[1] + p2[1]) * t +
            (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
            (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3
        )
        
        return (x, y)
    
    @staticmethod
    def generate_curve(control_points, segments_per_section=20, closed=True):
        """
        从控制点生成平滑曲线
        
        Args:
            control_points: 控制点列表 [(x, y), ...]
            segments_per_section: 每段之间的插值点数
            closed: 是否闭合曲线
        
        Returns:
            曲线点列表
        """
        if len(control_points) < 3:
            return control_points
        
        n = len(control_points)
        curve_points = []
        
        for i in range(n):
            # 获取4个控制点（循环）
            if closed:
                p0 = control_points[(i - 1) % n]
                p1 = control_points[i]
                p2 = control_points[(i + 1) % n]
                p3 = control_points[(i + 2) % n]
            else:
                # 开放曲线的边界处理
                p0 = control_points[max(0, i - 1)]
                p1 = control_points[i]
                p2 = control_points[min(n - 1, i + 1)]
                p3 = control_points[min(n - 1, i + 2)]
                
                if i == n - 1 and not closed:
                    continue
            
            # 生成插值点
            for j in range(segments_per_section):
                t = j / segments_per_section
                point = CatmullRomSpline.interpolate(p0, p1, p2, p3, t)
                curve_points.append(point)
        
        return curve_points


class TrackCurveEditor:
    """赛道曲线编辑器主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏎️ 赛道曲线编辑器")
        self.root.geometry("1200x800")
        
        # 控制点列表（画布坐标）
        self.control_points = []
        self.selected_point_index = None
        self.dragging = False
        
        # 画布和物理世界尺寸设置
        self.canvas_width = 800
        self.canvas_height = 600
        self.world_width = 100.0  # 物理世界宽度（米）
        self.world_height = 75.0  # 物理世界高度（米）
        
        # 显示选项
        self.show_grid = tk.BooleanVar(value=True)
        self.show_curve = tk.BooleanVar(value=True)
        self.show_points = tk.BooleanVar(value=True)
        self.closed_curve = tk.BooleanVar(value=True)
        
        # 赛道参数
        self.track_width = tk.DoubleVar(value=6.0)
        self.track_thickness = tk.DoubleVar(value=0.3)
        self.barrier_height = tk.DoubleVar(value=0.6)
        self.include_barriers = tk.BooleanVar(value=True)
        
        # 创建界面
        self._create_ui()
        self._bind_events()
        
        # 初始绘制
        self._draw_canvas()
    
    def _create_ui(self):
        """创建用户界面"""
        # 主布局：左边画布，右边控制面板
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左边：画布区域
        canvas_frame = ttk.LabelFrame(main_frame, text="画布")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(
            canvas_frame, 
            width=self.canvas_width, 
            height=self.canvas_height,
            bg='#2b2b2b',
            highlightthickness=0
        )
        self.canvas.pack(padx=5, pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value="点击画布添加控制点")
        status_label = ttk.Label(canvas_frame, textvariable=self.status_var)
        status_label.pack(pady=2)
        
        # 右边：控制面板
        control_frame = ttk.Frame(main_frame, width=350)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        control_frame.pack_propagate(False)
        
        # === 画布尺寸设置 ===
        size_frame = ttk.LabelFrame(control_frame, text="📐 画布尺寸（物理世界）")
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="宽度 (米):").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.world_width_var = tk.StringVar(value=str(self.world_width))
        ttk.Entry(size_frame, textvariable=self.world_width_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(size_frame, text="高度 (米):").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.world_height_var = tk.StringVar(value=str(self.world_height))
        ttk.Entry(size_frame, textvariable=self.world_height_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Button(size_frame, text="应用尺寸", command=self._apply_size).grid(row=2, column=0, columnspan=2, pady=5)
        
        # 比例尺显示
        self.scale_var = tk.StringVar()
        self._update_scale_display()
        ttk.Label(size_frame, textvariable=self.scale_var, foreground='gray').grid(row=3, column=0, columnspan=2, pady=2)
        
        # === 显示选项 ===
        display_frame = ttk.LabelFrame(control_frame, text="🎨 显示选项")
        display_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(display_frame, text="显示网格", variable=self.show_grid, 
                       command=self._draw_canvas).pack(anchor='w', padx=5)
        ttk.Checkbutton(display_frame, text="显示曲线", variable=self.show_curve,
                       command=self._draw_canvas).pack(anchor='w', padx=5)
        ttk.Checkbutton(display_frame, text="显示控制点", variable=self.show_points,
                       command=self._draw_canvas).pack(anchor='w', padx=5)
        ttk.Checkbutton(display_frame, text="闭合曲线", variable=self.closed_curve,
                       command=self._draw_canvas).pack(anchor='w', padx=5)
        
        # === 赛道参数 ===
        track_frame = ttk.LabelFrame(control_frame, text="🏎️ 赛道参数")
        track_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(track_frame, text="赛道宽度 (米):").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Entry(track_frame, textvariable=self.track_width, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(track_frame, text="路面厚度 (米):").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        ttk.Entry(track_frame, textvariable=self.track_thickness, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(track_frame, text="护栏高度 (米):").grid(row=2, column=0, padx=5, pady=2, sticky='w')
        ttk.Entry(track_frame, textvariable=self.barrier_height, width=10).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Checkbutton(track_frame, text="包含护栏", variable=self.include_barriers).grid(
            row=3, column=0, columnspan=2, pady=2, sticky='w', padx=5)
        
        # === 控制点信息 ===
        info_frame = ttk.LabelFrame(control_frame, text="📍 控制点信息")
        info_frame.pack(fill=tk.X, pady=5)
        
        self.points_info_var = tk.StringVar(value="控制点数量: 0")
        ttk.Label(info_frame, textvariable=self.points_info_var).pack(anchor='w', padx=5, pady=2)
        
        self.selected_info_var = tk.StringVar(value="选中: 无")
        ttk.Label(info_frame, textvariable=self.selected_info_var).pack(anchor='w', padx=5, pady=2)
        
        # === 操作按钮 ===
        action_frame = ttk.LabelFrame(control_frame, text="⚙️ 操作")
        action_frame.pack(fill=tk.X, pady=5)
        
        btn_frame1 = ttk.Frame(action_frame)
        btn_frame1.pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame1, text="清空所有点", command=self._clear_points).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        ttk.Button(btn_frame1, text="删除选中点", command=self._delete_selected).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        btn_frame2 = ttk.Frame(action_frame)
        btn_frame2.pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame2, text="撤销", command=self._undo).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        ttk.Button(btn_frame2, text="反转方向", command=self._reverse_points).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # === 导出按钮 ===
        export_frame = ttk.LabelFrame(control_frame, text="📤 导出")
        export_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(export_frame, text="导出为 JSON", command=self._export_json).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(export_frame, text="导出为 Python 代码", command=self._export_python).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(export_frame, text="复制 waypoints 到剪贴板", command=self._copy_waypoints).pack(fill=tk.X, padx=5, pady=2)
        
        # === 生成赛道 ===
        generate_frame = ttk.LabelFrame(control_frame, text="🚀 生成赛道")
        generate_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(generate_frame, text="在 Blender 中生成赛道", 
                  command=self._generate_track).pack(fill=tk.X, padx=5, pady=5)
        
        # === 导入 ===
        import_frame = ttk.LabelFrame(control_frame, text="📥 导入")
        import_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(import_frame, text="从 JSON 导入", command=self._import_json).pack(fill=tk.X, padx=5, pady=2)
        
        # === 使用说明 ===
        help_frame = ttk.LabelFrame(control_frame, text="❓ 使用说明")
        help_frame.pack(fill=tk.X, pady=5)
        
        help_text = """• 左键点击: 添加控制点
• 左键拖动: 移动控制点
• 右键点击: 删除控制点
• 滚轮: 缩放视图 (TODO)
• Delete键: 删除选中点"""
        ttk.Label(help_frame, text=help_text, justify='left').pack(padx=5, pady=5)
        
        # 撤销历史
        self.history = []
    
    def _bind_events(self):
        """绑定事件"""
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)
        self.canvas.bind('<Button-3>', self._on_right_click)
        self.canvas.bind('<Motion>', self._on_motion)
        self.root.bind('<Delete>', lambda e: self._delete_selected())
        self.root.bind('<Control-z>', lambda e: self._undo())
    
    def _canvas_to_world(self, x, y):
        """画布坐标转物理世界坐标"""
        # 画布原点在左上角，物理世界原点在中心
        world_x = (x - self.canvas_width / 2) * self.world_width / self.canvas_width
        world_y = (self.canvas_height / 2 - y) * self.world_height / self.canvas_height
        return (world_x, world_y)
    
    def _world_to_canvas(self, x, y):
        """物理世界坐标转画布坐标"""
        canvas_x = x * self.canvas_width / self.world_width + self.canvas_width / 2
        canvas_y = self.canvas_height / 2 - y * self.canvas_height / self.world_height
        return (canvas_x, canvas_y)
    
    def _update_scale_display(self):
        """更新比例尺显示"""
        pixels_per_meter_x = self.canvas_width / self.world_width
        pixels_per_meter_y = self.canvas_height / self.world_height
        avg_ppm = (pixels_per_meter_x + pixels_per_meter_y) / 2
        self.scale_var.set(f"比例尺: 1 像素 ≈ {1/avg_ppm:.2f} 米")
    
    def _apply_size(self):
        """应用尺寸设置"""
        try:
            self.world_width = float(self.world_width_var.get())
            self.world_height = float(self.world_height_var.get())
            self._update_scale_display()
            self._draw_canvas()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数值")
    
    def _find_point_at(self, x, y, radius=10):
        """查找指定位置附近的控制点"""
        for i, (px, py) in enumerate(self.control_points):
            cx, cy = self._world_to_canvas(px, py)
            if math.sqrt((x - cx)**2 + (y - cy)**2) <= radius:
                return i
        return None
    
    def _on_click(self, event):
        """鼠标左键点击"""
        # 检查是否点击到现有点
        idx = self._find_point_at(event.x, event.y)
        
        if idx is not None:
            # 选中点，准备拖动
            self.selected_point_index = idx
            self.dragging = True
        else:
            # 尝试添加新点
            world_pos = self._canvas_to_world(event.x, event.y)
            
            # 检查是否与现有线段相交
            intersects, msg = GeometryUtils.check_new_segment_intersects(
                self.control_points, world_pos
            )
            
            if intersects:
                # 不允许放置，显示闪烁效果和提示
                self._show_invalid_point_animation(event.x, event.y, msg)
                return
            
            # 合法，添加新点
            self._save_history()
            self.control_points.append(world_pos)
            self.selected_point_index = len(self.control_points) - 1
        
        self._update_info()
        self._draw_canvas()
    
    def _show_invalid_point_animation(self, x, y, error_msg):
        """显示无效点的闪烁动画和错误提示"""
        # 创建闪烁的点
        flash_id = None
        flash_count = [0]  # 使用列表以便在闭包中修改
        max_flashes = 6
        
        # 更新状态栏显示错误
        original_status = self.status_var.get()
        self.status_var.set(f"❌ 无法放置: {error_msg}")
        
        def flash():
            nonlocal flash_id
            
            if flash_count[0] >= max_flashes:
                # 动画结束，删除闪烁的点
                if flash_id:
                    self.canvas.delete(flash_id)
                # 恢复状态栏
                self.root.after(1000, lambda: self.status_var.set(original_status))
                return
            
            # 交替显示/隐藏
            if flash_count[0] % 2 == 0:
                # 显示红色警告点
                flash_id = self.canvas.create_oval(
                    x - 10, y - 10, x + 10, y + 10,
                    fill='#ff0000', outline='#ffff00', width=3,
                    tags='flash_point'
                )
                # 显示错误连线
                if len(self.control_points) >= 1:
                    last_pt = self._world_to_canvas(*self.control_points[-1])
                    self.canvas.create_line(
                        last_pt[0], last_pt[1], x, y,
                        fill='#ff0000', width=2, dash=(6, 3),
                        tags='flash_point'
                    )
            else:
                # 隐藏
                self.canvas.delete('flash_point')
            
            flash_count[0] += 1
            self.root.after(150, flash)
        
        # 开始闪烁动画
        flash()
    
    def _on_drag(self, event):
        """鼠标拖动"""
        if self.dragging and self.selected_point_index is not None:
            # 限制在画布范围内
            x = max(0, min(event.x, self.canvas_width))
            y = max(0, min(event.y, self.canvas_height))
            
            world_pos = self._canvas_to_world(x, y)
            self.control_points[self.selected_point_index] = world_pos
            
            self._update_info()
            self._draw_canvas()
    
    def _on_release(self, event):
        """鼠标释放"""
        if self.dragging:
            self._save_history()
        self.dragging = False
    
    def _on_right_click(self, event):
        """鼠标右键点击 - 删除点"""
        idx = self._find_point_at(event.x, event.y)
        if idx is not None:
            self._save_history()
            del self.control_points[idx]
            if self.selected_point_index == idx:
                self.selected_point_index = None
            elif self.selected_point_index is not None and self.selected_point_index > idx:
                self.selected_point_index -= 1
            
            self._update_info()
            self._draw_canvas()
    
    def _on_motion(self, event):
        """鼠标移动 - 更新状态栏"""
        world_pos = self._canvas_to_world(event.x, event.y)
        self.status_var.set(f"位置: ({world_pos[0]:.1f}, {world_pos[1]:.1f}) 米")
    
    def _update_info(self):
        """更新控制点信息"""
        self.points_info_var.set(f"控制点数量: {len(self.control_points)}")
        
        if self.selected_point_index is not None and self.selected_point_index < len(self.control_points):
            pt = self.control_points[self.selected_point_index]
            self.selected_info_var.set(f"选中: 点 {self.selected_point_index + 1} ({pt[0]:.1f}, {pt[1]:.1f})")
        else:
            self.selected_info_var.set("选中: 无")
    
    def _draw_canvas(self):
        """重绘画布"""
        self.canvas.delete('all')
        
        # 绘制网格
        if self.show_grid.get():
            self._draw_grid()
        
        # 绘制原点标记
        origin = self._world_to_canvas(0, 0)
        self.canvas.create_line(origin[0] - 10, origin[1], origin[0] + 10, origin[1], fill='#555555', width=1)
        self.canvas.create_line(origin[0], origin[1] - 10, origin[0], origin[1] + 10, fill='#555555', width=1)
        
        # 绘制平滑曲线
        if self.show_curve.get() and len(self.control_points) >= 3:
            segments_per_section = 20
            curve_points = CatmullRomSpline.generate_curve(
                self.control_points, 
                segments_per_section=segments_per_section,
                closed=self.closed_curve.get()
            )
            
            if len(curve_points) >= 2:
                # 转换为画布坐标
                canvas_curve = [self._world_to_canvas(p[0], p[1]) for p in curve_points]
                
                n = len(self.control_points)
                
                if self.closed_curve.get() and n >= 3:
                    # 分开绘制：主要部分（实线）和最后一段（虚线弱化）
                    # 最后一段是从第 (n-1)*segments_per_section 个点开始
                    last_segment_start = (n - 1) * segments_per_section
                    
                    # 绘制主要部分（前 n-1 段）- 实线
                    if last_segment_start > 0:
                        main_coords = []
                        for p in canvas_curve[:last_segment_start + 1]:  # +1 确保衔接
                            main_coords.extend(p)
                        self.canvas.create_line(*main_coords, fill='#00ff88', width=2, smooth=True)
                    
                    # 绘制最后一段（第 n 段，闭合部分）- 虚线弱化
                    last_coords = []
                    for p in canvas_curve[last_segment_start:]:
                        last_coords.extend(p)
                    # 闭合到起点
                    last_coords.extend(canvas_curve[0])
                    self.canvas.create_line(
                        *last_coords, 
                        fill='#00aa66',  # 更淡的绿色
                        width=2, 
                        smooth=True,
                        dash=(12, 10)  # 虚线（更大间隔）
                    )
                else:
                    # 非闭合曲线，全部用实线
                    flat_coords = []
                    for p in canvas_curve:
                        flat_coords.extend(p)
                    self.canvas.create_line(*flat_coords, fill='#00ff88', width=2, smooth=True)
        
        # 绘制控制点连线（辅助线）
        if len(self.control_points) >= 2:
            for i in range(len(self.control_points) - 1):
                p1 = self._world_to_canvas(*self.control_points[i])
                p2 = self._world_to_canvas(*self.control_points[i + 1])
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill='#444444', width=1, dash=(4, 4))
        
        # 绘制控制点
        if self.show_points.get():
            for i, pt in enumerate(self.control_points):
                cx, cy = self._world_to_canvas(pt[0], pt[1])
                
                # 判断是否选中
                if i == self.selected_point_index:
                    color = '#ff6600'
                    size = 8
                else:
                    color = '#ff4444'
                    size = 6
                
                self.canvas.create_oval(
                    cx - size, cy - size, cx + size, cy + size,
                    fill=color, outline='white', width=2
                )
                
                # 显示序号
                self.canvas.create_text(cx + 12, cy - 12, text=str(i + 1), fill='white', font=('Arial', 9))
    
    def _draw_grid(self):
        """绘制网格"""
        # 根据世界尺寸确定网格间距
        grid_world_size = 10  # 每10米一条网格线
        
        # 垂直线
        for x in range(int(-self.world_width/2), int(self.world_width/2) + 1, grid_world_size):
            cx, _ = self._world_to_canvas(x, 0)
            color = '#404040' if x != 0 else '#505050'
            self.canvas.create_line(cx, 0, cx, self.canvas_height, fill=color, width=1)
        
        # 水平线
        for y in range(int(-self.world_height/2), int(self.world_height/2) + 1, grid_world_size):
            _, cy = self._world_to_canvas(0, y)
            color = '#404040' if y != 0 else '#505050'
            self.canvas.create_line(0, cy, self.canvas_width, cy, fill=color, width=1)
    
    def _save_history(self):
        """保存当前状态到历史"""
        self.history.append(list(self.control_points))
        # 限制历史记录数量
        if len(self.history) > 50:
            self.history.pop(0)
    
    def _undo(self):
        """撤销"""
        if self.history:
            self.control_points = self.history.pop()
            self.selected_point_index = None
            self._update_info()
            self._draw_canvas()
    
    def _clear_points(self):
        """清空所有控制点"""
        if self.control_points:
            if messagebox.askyesno("确认", "确定要清空所有控制点吗？"):
                self._save_history()
                self.control_points = []
                self.selected_point_index = None
                self._update_info()
                self._draw_canvas()
    
    def _delete_selected(self):
        """删除选中的点"""
        if self.selected_point_index is not None:
            self._save_history()
            del self.control_points[self.selected_point_index]
            self.selected_point_index = None
            self._update_info()
            self._draw_canvas()
    
    def _reverse_points(self):
        """反转控制点顺序"""
        if self.control_points:
            self._save_history()
            self.control_points = list(reversed(self.control_points))
            self._draw_canvas()
    
    def _get_waypoints_string(self):
        """获取 waypoints 字符串"""
        if not self.control_points:
            return "[]"
        
        lines = ["["]
        for i, pt in enumerate(self.control_points):
            comma = "," if i < len(self.control_points) - 1 else ""
            lines.append(f"    ({pt[0]:.1f}, {pt[1]:.1f}){comma}")
        lines.append("]")
        return "\n".join(lines)
    
    def _copy_waypoints(self):
        """复制 waypoints 到剪贴板"""
        if not self.control_points:
            messagebox.showwarning("警告", "没有控制点可复制")
            return
        
        waypoints_str = self._get_waypoints_string()
        self.root.clipboard_clear()
        self.root.clipboard_append(waypoints_str)
        messagebox.showinfo("成功", f"已复制 {len(self.control_points)} 个控制点到剪贴板")
    
    def _export_json(self):
        """导出为 JSON 文件"""
        if not self.control_points:
            messagebox.showwarning("警告", "没有控制点可导出")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")],
            title="导出 JSON"
        )
        
        if filepath:
            data = {
                "version": "1.0",
                "world_size": {
                    "width": self.world_width,
                    "height": self.world_height
                },
                "waypoints": [{"x": pt[0], "y": pt[1]} for pt in self.control_points],
                "track_params": {
                    "track_width": self.track_width.get(),
                    "track_thickness": self.track_thickness.get(),
                    "barrier_height": self.barrier_height.get(),
                    "include_barriers": self.include_barriers.get(),
                    "closed": self.closed_curve.get()
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("成功", f"已导出到: {filepath}")
    
    def _import_json(self):
        """从 JSON 导入"""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")],
            title="导入 JSON"
        )
        
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self._save_history()
                
                # 加载世界尺寸
                if "world_size" in data:
                    self.world_width = data["world_size"].get("width", 100)
                    self.world_height = data["world_size"].get("height", 75)
                    self.world_width_var.set(str(self.world_width))
                    self.world_height_var.set(str(self.world_height))
                    self._update_scale_display()
                
                # 加载控制点
                self.control_points = [(pt["x"], pt["y"]) for pt in data["waypoints"]]
                
                # 加载赛道参数
                if "track_params" in data:
                    params = data["track_params"]
                    self.track_width.set(params.get("track_width", 6.0))
                    self.track_thickness.set(params.get("track_thickness", 0.3))
                    self.barrier_height.set(params.get("barrier_height", 0.6))
                    self.include_barriers.set(params.get("include_barriers", True))
                    self.closed_curve.set(params.get("closed", True))
                
                self.selected_point_index = None
                self._update_info()
                self._draw_canvas()
                
                messagebox.showinfo("成功", f"已导入 {len(self.control_points)} 个控制点")
                
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")
    
    def _export_python(self):
        """导出为 Python 代码"""
        if not self.control_points:
            messagebox.showwarning("警告", "没有控制点可导出")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python 文件", "*.py"), ("所有文件", "*.*")],
            title="导出 Python 代码",
            initialfile="generated_track.py"
        )
        
        if filepath:
            code = self._generate_python_code()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            messagebox.showinfo("成功", f"已导出到: {filepath}")
    
    def _generate_python_code(self, is_temp_script=False):
        """生成 Python 代码
        
        Args:
            is_temp_script: 是否是临时脚本（在项目根目录下）
        """
        waypoints_str = self._get_waypoints_string()
        
        # 根据脚本位置决定路径处理方式
        if is_temp_script:
            path_code = '''# 添加项目路径（临时脚本，在项目根目录下）
script_dir = os.path.dirname(os.path.abspath(__file__))
# 检测项目根目录（script_dir 本身或其父目录）
if os.path.exists(os.path.join(script_dir, "src")):
    project_root = script_dir
else:
    project_root = os.path.dirname(script_dir)
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)'''
        else:
            path_code = '''# 添加项目路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 检测项目根目录（向上查找直到找到 src 目录）
project_root = script_dir
for _ in range(5):  # 最多向上查找5层
    if os.path.exists(os.path.join(project_root, "src")):
        break
    project_root = os.path.dirname(project_root)
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)'''
        
        code = f'''"""
由赛道曲线编辑器生成的赛道
========================

世界尺寸: {self.world_width}m x {self.world_height}m
控制点数量: {len(self.control_points)}

使用方法：
blender assets/node_library.blend --python <this_file.py>
"""

import bpy
import sys
import os

{path_code}

from gnodes_builder import create_custom_track


# ============ 配置参数 ============
TRACK_WIDTH = {self.track_width.get()}           # 赛道宽度
TRACK_THICKNESS = {self.track_thickness.get()}       # 路面厚度
BARRIER_HEIGHT = {self.barrier_height.get()}        # 护栏高度
INCLUDE_BARRIERS = {self.include_barriers.get()}    # 是否包含护栏


# ============ 控制点定义 ============
waypoints = {waypoints_str}


# ============ 场景设置 ============
def clear_scene():
    """清理默认物体"""
    for obj in list(bpy.data.objects):
        if obj.type in ('MESH', 'CURVE'):
            bpy.data.objects.remove(obj, do_unlink=True)


def setup_camera():
    """设置相机 - 俯瞰视角"""
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
    else:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
    
    cam.location = (0, -{max(self.world_width, self.world_height) * 0.8}, {max(self.world_width, self.world_height)})
    cam.rotation_euler = (0.7, 0, 0)
    bpy.context.scene.camera = cam


def setup_lighting():
    """设置灯光"""
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    bpy.ops.object.light_add(type='SUN', location=(20, -20, 50))
    sun = bpy.context.object
    sun.data.energy = 3
    sun.rotation_euler = (0.6, 0.2, 0.3)


# ============ 主函数 ============
def main():
    print("\\n" + "=" * 60)
    print("🏎️ 生成赛道")
    print("=" * 60)
    
    clear_scene()
    
    print("🏗️ 构建赛道...")
    track_objects = create_custom_track(
        name="GeneratedTrack",
        waypoints=waypoints,
        location=(0, 0, 0),
        track_width=TRACK_WIDTH,
        track_thickness=TRACK_THICKNESS,
        barrier_height=BARRIER_HEIGHT,
        include_barriers=INCLUDE_BARRIERS,
        segments_per_section=16
    )
    
    print(f"✅ 赛道构建完成！共 {{len(track_objects)}} 个部件")
    
    setup_camera()
    setup_lighting()
    
    print("\\n" + "=" * 60)
    print("✅ 完成！")
    print("=" * 60)
    
    if bpy.app.background:
        out = os.path.join(project_root, "assets", "generated_track.blend")
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print(f"\\n💾 保存到: {{out}}")


if __name__ == "__main__":
    main()
'''
        return code
    
    def _generate_track(self):
        """在 Blender 中生成赛道"""
        if len(self.control_points) < 3:
            messagebox.showwarning("警告", "至少需要3个控制点才能生成赛道")
            return
        
        # 生成临时 Python 文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        temp_script = os.path.join(project_root, "temp_generated_track.py")
        
        code = self._generate_python_code(is_temp_script=True)
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # 构建 Blender 命令
        node_library = os.path.join(project_root, "assets", "node_library.blend")
        
        # 尝试找到 Blender
        blender_paths = [
            "blender",  # 系统路径
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        ]
        
        blender_exe = None
        for path in blender_paths:
            if os.path.exists(path) or path == "blender":
                blender_exe = path
                break
        
        if blender_exe is None:
            messagebox.showerror("错误", "找不到 Blender，请确保已安装并添加到系统路径")
            return
        
        # 显示生成选项对话框
        result = messagebox.askyesnocancel(
            "生成赛道",
            f"将使用 Blender 生成赛道:\n\n"
            f"控制点数量: {len(self.control_points)}\n"
            f"赛道宽度: {self.track_width.get()}m\n"
            f"护栏: {'是' if self.include_barriers.get() else '否'}\n\n"
            f"是 = 在 Blender GUI 中打开\n"
            f"否 = 后台生成并保存\n"
            f"取消 = 取消操作"
        )
        
        if result is None:
            # 取消
            if os.path.exists(temp_script):
                os.remove(temp_script)
            return
        
        try:
            if result:
                # 在 GUI 中打开
                cmd = [blender_exe, node_library, "--python", temp_script]
            else:
                # 后台生成
                cmd = [blender_exe, "--background", node_library, "--python", temp_script]
            
            self.status_var.set("正在生成赛道...")
            self.root.update()
            
            subprocess.Popen(cmd)
            
            if result:
                messagebox.showinfo("成功", "Blender 已启动，赛道正在生成中...")
            else:
                messagebox.showinfo("成功", "后台生成任务已启动，完成后将保存到 assets/generated_track.blend")
            
        except Exception as e:
            messagebox.showerror("错误", f"启动 Blender 失败: {str(e)}")
        
        finally:
            self.status_var.set("点击画布添加控制点")


def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置样式
    style = ttk.Style()
    style.theme_use('clam')
    
    app = TrackCurveEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()

