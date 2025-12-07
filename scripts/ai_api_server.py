"""
AI API 服务器
提供 HTTP API 接口，接收 AI 生成的代码并执行

使用方法：
1. 安装依赖：pip install flask
2. 启动服务：python scripts/ai_api_server.py
3. 发送请求：POST /execute {"code": "..."}

注意：此服务器用于开发测试，生产环境需要加强安全措施
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path

# 尝试导入 Flask
try:
    from flask import Flask, request, jsonify
except ImportError:
    print("❌ 请先安装 Flask: pip install flask")
    sys.exit(1)

app = Flask(__name__)

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
BLENDER_PATH = os.environ.get("BLENDER_PATH", "blender")  # 可通过环境变量配置


def execute_in_blender(code: str, output_path: str = None) -> dict:
    """
    在 Blender 中执行代码
    
    Args:
        code: Python 代码
        output_path: 输出文件路径
    
    Returns:
        执行结果字典
    """
    # 创建临时代码文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(code)
        code_file = f.name
    
    try:
        # 构建命令
        library_path = PROJECT_ROOT / "assets" / "node_library.blend"
        executor_path = PROJECT_ROOT / "scripts" / "ai_executor.py"
        
        cmd = [
            BLENDER_PATH,
            str(library_path),
            "--background",
            "--python", str(executor_path),
            "--",
            "--file", code_file,
        ]
        
        if output_path:
            cmd.extend(["--output", output_path])
        
        # 执行
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60秒超时
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "执行超时（60秒）"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        # 清理临时文件
        os.unlink(code_file)


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok"})


@app.route('/execute', methods=['POST'])
def execute():
    """
    执行 AI 生成的代码
    
    Request Body:
        {
            "code": "Python 代码",
            "output_path": "可选，输出文件路径"
        }
    
    Response:
        {
            "success": true/false,
            "stdout": "标准输出",
            "stderr": "错误输出"
        }
    """
    data = request.get_json()
    
    if not data or 'code' not in data:
        return jsonify({"error": "缺少 code 参数"}), 400
    
    code = data['code']
    output_path = data.get('output_path')
    
    result = execute_in_blender(code, output_path)
    
    return jsonify(result)


@app.route('/node_groups', methods=['GET'])
def list_node_groups():
    """返回可用的节点组列表"""
    node_groups = [
        {
            "name": "G_Base_Cube",
            "description": "生成标准倒角立方体",
            "inputs": {
                "Size": {"type": "Vector", "default": [1.0, 1.0, 1.0]},
                "Bevel": {"type": "Float", "default": 0.0, "range": [0.0, 1.0]}
            }
        },
        {
            "name": "G_Base_Cylinder",
            "description": "生成标准圆柱",
            "inputs": {
                "Radius": {"type": "Float", "default": 0.5},
                "Height": {"type": "Float", "default": 2.0},
                "Resolution": {"type": "Int", "default": 16, "range": [3, 64]}
            }
        },
        {
            "name": "G_Base_Sphere",
            "description": "生成标准球体",
            "inputs": {
                "Radius": {"type": "Float", "default": 1.0},
                "Resolution": {"type": "Int", "default": 16}
            }
        },
        {
            "name": "G_Damage_Edges",
            "description": "边缘破损效果",
            "inputs": {
                "Amount": {"type": "Float", "default": 0.5, "range": [0.0, 1.0]},
                "Scale": {"type": "Float", "default": 2.0},
                "Seed": {"type": "Int", "default": 0}
            }
        },
        {
            "name": "G_Scatter_Moss",
            "description": "在表面散布苔藓",
            "inputs": {
                "Density": {"type": "Float", "default": 50.0},
                "Seed": {"type": "Int", "default": 0}
            }
        },
        {
            "name": "G_Scatter_On_Top",
            "description": "在物体顶部散布",
            "inputs": {
                "Density": {"type": "Float", "default": 10.0},
                "Seed": {"type": "Int", "default": 0}
            }
        },
        {
            "name": "G_Boolean_Cut",
            "description": "布尔切割",
            "inputs": {
                "Cut_Geometry": {"type": "Geometry"}
            }
        },
        {
            "name": "G_Voxel_Remesh",
            "description": "体素重建",
            "inputs": {
                "Voxel_Size": {"type": "Float", "default": 0.1}
            }
        },
        {
            "name": "G_Align_Ground",
            "description": "对齐地面（必须最后调用）",
            "inputs": {}
        }
    ]
    return jsonify({"node_groups": node_groups})


@app.route('/template', methods=['GET'])
def get_template():
    """返回代码模板"""
    template = '''# AI 生成的 Blender 几何节点代码
builder = GNodesBuilder("Model_Name")

# 添加基础几何体
builder.add_node_group("G_Base_Cube", inputs={"Size": (1.0, 1.0, 1.0)})

# 添加效果（可选）
# builder.add_node_group("G_Damage_Edges", inputs={"Amount": 0.5})

# 最后必须对齐地面
builder.add_node_group("G_Align_Ground")

builder.finalize()
'''
    return jsonify({"template": template})


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AI API 服务器启动")
    print("=" * 60)
    print(f"项目路径: {PROJECT_ROOT}")
    print(f"Blender 路径: {BLENDER_PATH}")
    print("\n可用端点:")
    print("  GET  /health      - 健康检查")
    print("  GET  /node_groups - 获取节点组列表")
    print("  GET  /template    - 获取代码模板")
    print("  POST /execute     - 执行代码")
    print("\n示例请求:")
    print('  curl -X POST http://localhost:5000/execute \\')
    print('       -H "Content-Type: application/json" \\')
    print('       -d \'{"code": "builder = GNodesBuilder(\\"Test\\")\\nbuilder.add_node_group(\\"G_Base_Cube\\")\\nbuilder.add_node_group(\\"G_Align_Ground\\")\\nbuilder.finalize()"}\'')
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

