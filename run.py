#!/usr/bin/env python
"""
自动化习题解析批处理工具启动脚本
"""

import os
import sys
import argparse

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="自动化习题解析批处理工具")
    parser.add_argument("--mode", choices=["cli", "web"], default="web", help="运行模式：cli（命令行）或web（Web界面）")
    parser.add_argument("--problem-ids-file", type=str, help="问题ID文件路径（仅CLI模式需要）")
    parser.add_argument("--api-key", type=str, help="火山方舟API密钥")
    parser.add_argument("--model-id", type=str, help="模型ID")
    parser.add_argument("--max-workers", type=int, help="最大并发数")
    args = parser.parse_args()
    
    # 设置API密钥环境变量
    if args.api_key:
        os.environ["ARK_API_KEY"] = args.api_key
    
    # 切换到auto_problem_solver目录
    os.chdir("auto_problem_solver")
    
    if args.mode == "cli":
        # 命令行模式
        if not args.problem_ids_file:
            print("错误：CLI模式需要指定问题ID文件路径")
            parser.print_help()
            return 1
        
        # 构建命令行参数
        cmd_args = ["python", "main.py", f"--problem-ids-file={args.problem_ids_file}"]
        
        if args.api_key:
            cmd_args.append(f"--api-key={args.api_key}")
        
        if args.model_id:
            cmd_args.append(f"--model-id={args.model_id}")
        
        if args.max_workers:
            cmd_args.append(f"--max-workers={args.max_workers}")
        
        # 执行命令
        os.execvp("python", cmd_args)
    else:
        # Web界面模式
        os.execvp("streamlit", ["streamlit", "run", "app.py"])

if __name__ == "__main__":
    sys.exit(main()) 