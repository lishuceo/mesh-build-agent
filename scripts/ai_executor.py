"""
AI 代码执行器
接收 AI 生成的代码并在 Blender 中执行

使用方法：
1. 通过文件传递代码：
   blender assets/node_library.blend --background --python scripts/ai_executor.py -- --file code.py

2. 通过命令行传递代码（适合短代码）：
   blender assets/node_library.blend --background --python scripts/ai_executor.py -- --code "builder = GNodesBuilder('Test')"

3. 启动交互模式（标准输入）：
   blender assets/node_library.blend --background --python scripts/ai_executor.py -- --stdin
"""

import bpy
import sys
import os

# 设置路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_dir = os.path.join(project_root, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 导入构建器
from gnodes_builder import GNodesBuilder, load_node_library


def setup_environment():
    """设置执行环境"""
    # 确保节点组库已加载
    library_path = os.path.join(project_root, "assets", "node_library.blend")
    if os.path.exists(library_path):
        load_node_library(library_path)
        print(f"✓ 已加载节点组库")
    else:
        print(f"⚠️ 节点组库不存在: {library_path}")


def execute_code(code: str, output_path: str = None):
    """
    执行 AI 生成的代码
    
    Args:
        code: Python 代码字符串
        output_path: 输出文件路径（可选）
    """
    print("\n" + "=" * 60)
    print("🤖 执行 AI 生成的代码...")
    print("=" * 60)
    print(code)
    print("=" * 60 + "\n")
    
    # 准备执行环境
    exec_globals = {
        'bpy': bpy,
        'GNodesBuilder': GNodesBuilder,
        '__name__': '__main__',
    }
    
    try:
        exec(code, exec_globals)
        print("\n✅ 代码执行成功！")
        
        # 保存结果
        if output_path:
            bpy.ops.wm.save_as_mainfile(filepath=output_path)
            print(f"💾 结果已保存到: {output_path}")
            
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """主函数"""
    setup_environment()
    
    # 解析命令行参数
    code = None
    output_path = None
    
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1:]
        
        for i, arg in enumerate(argv):
            if arg == "--file" and i + 1 < len(argv):
                # 从文件读取代码
                code_file = argv[i + 1]
                if os.path.exists(code_file):
                    with open(code_file, 'r', encoding='utf-8') as f:
                        code = f.read()
                else:
                    print(f"❌ 文件不存在: {code_file}")
                    return
                    
            elif arg == "--code" and i + 1 < len(argv):
                # 直接传入代码
                code = argv[i + 1]
                
            elif arg == "--stdin":
                # 从标准输入读取
                print("📝 请输入代码（输入 'END' 结束）：")
                lines = []
                while True:
                    try:
                        line = input()
                        if line.strip() == 'END':
                            break
                        lines.append(line)
                    except EOFError:
                        break
                code = '\n'.join(lines)
                
            elif arg in ("--output", "-o") and i + 1 < len(argv):
                output_path = argv[i + 1]
    
    if code:
        execute_code(code, output_path)
    else:
        print("❌ 未提供代码")
        print("\n使用方法：")
        print("  --file <path>    从文件读取代码")
        print("  --code <code>    直接传入代码字符串")
        print("  --stdin          从标准输入读取")
        print("  --output <path>  保存结果到文件")


if __name__ == "__main__":
    main()

