"""
自动化习题解析批处理工具主程序
"""

import os
import sys
import json
import time
import logging
import argparse
import concurrent.futures
from typing import Dict, List, Any, Optional

# 导入自定义模块
from models.problem_fetcher import ProblemFetcher
from models.llm_solver import LLMSolver
from utils.data_exporter import DataExporter
from config import MAX_WORKERS

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auto_problem_solver_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AutoProblemSolver")

class AutoProblemSolver:
    """自动化习题解析批处理工具"""
    
    def __init__(self, api_key: Optional[str] = None, model_id: Optional[str] = None, prompt_template: Optional[str] = None):
        """
        初始化自动化习题解析批处理工具
        
        参数:
        - api_key: 火山方舟API密钥
        - model_id: 模型ID
        - prompt_template: 提示词模板
        """
        self.problem_fetcher = ProblemFetcher()
        self.llm_solver = LLMSolver(api_key, model_id, prompt_template)
        self.data_exporter = DataExporter()
        self.progress_callback = None
    
    def set_progress_callback(self, callback):
        """
        设置进度回调函数
        
        参数:
        - callback: 回调函数，接受三个参数：当前进度，总数，消息
        """
        self.progress_callback = callback
    
    def run(self, problem_ids_file: str, max_workers: int = MAX_WORKERS) -> str:
        """
        运行批处理工具
        
        参数:
        - problem_ids_file: 问题ID文件路径
        - max_workers: 最大并发数
        
        返回:
        - 导出文件的路径
        """
        logger.info(f"Starting auto problem solver with {max_workers} workers")
        
        # 加载问题ID
        if self.progress_callback:
            self.progress_callback(0, 100, "正在加载问题ID...")
            
        problem_ids = self.problem_fetcher.load_problem_ids_from_file(problem_ids_file)
        if not problem_ids:
            logger.error(f"No problem IDs found in {problem_ids_file}")
            return ""
        
        logger.info(f"Loaded {len(problem_ids)} problem IDs")
        if self.progress_callback:
            self.progress_callback(5, 100, f"已加载 {len(problem_ids)} 个问题ID")
        
        # 获取问题数据
        if self.progress_callback:
            self.progress_callback(10, 100, "正在获取问题数据...")
            
        problems = self.problem_fetcher.get_problems(problem_ids)
        if not problems:
            logger.error("Failed to fetch problems")
            return ""
        
        logger.info(f"Fetched {len(problems)} problems")
        if self.progress_callback:
            self.progress_callback(20, 100, f"已获取 {len(problems)} 个问题数据")
        
        # 使用大模型解题
        if self.progress_callback:
            self.progress_callback(25, 100, "开始使用大模型解题...")
            
        solutions = self._solve_problems_parallel(problems, max_workers)
        
        # 格式化数据用于导出
        if self.progress_callback:
            self.progress_callback(90, 100, "正在格式化数据...")
            
        formatted_data = self.data_exporter.format_data_for_export(problems, solutions)
        
        # 导出到Excel
        if self.progress_callback:
            self.progress_callback(95, 100, "正在导出到Excel...")
            
        export_path = self.data_exporter.export_to_excel(formatted_data)
        
        logger.info(f"Process completed. Results exported to {export_path}")
        if self.progress_callback:
            self.progress_callback(100, 100, "处理完成！")
            
        return export_path
    
    def _solve_problems_parallel(self, problems: List[Dict], max_workers: int) -> Dict[str, str]:
        """
        并行解题
        
        参数:
        - problems: 问题数据列表
        - max_workers: 最大并发数
        
        返回:
        - 问题ID到解答的映射
        """
        solutions = {}
        total = len(problems)
        
        logger.info(f"Starting to solve {total} problems with {max_workers} workers")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_problem = {
                executor.submit(self._solve_single_problem, problem): problem
                for problem in problems
            }
            
            # 处理结果
            for i, future in enumerate(concurrent.futures.as_completed(future_to_problem)):
                problem = future_to_problem[future]
                problem_id = problem.get("id", "")
                
                try:
                    solution = future.result()
                    solutions[problem_id] = solution
                    logger.info(f"Progress: {i+1}/{total} - Solved problem {problem_id}")
                    
                    # 更新进度
                    if self.progress_callback:
                        progress = 25 + int(65 * (i+1) / total)  # 从25%到90%
                        self.progress_callback(progress, 100, f"已解决 {i+1}/{total} 个问题")
                        
                except Exception as e:
                    logger.error(f"Error solving problem {problem_id}: {str(e)}")
                    solutions[problem_id] = f"解题失败: {str(e)}"
                    
                    # 更新进度（即使出错也更新）
                    if self.progress_callback:
                        progress = 25 + int(65 * (i+1) / total)
                        self.progress_callback(progress, 100, f"已处理 {i+1}/{total} 个问题（有错误）")
        
        return solutions
    
    def _solve_single_problem(self, problem: Dict) -> str:
        """
        解答单个问题
        
        参数:
        - problem: 问题数据
        
        返回:
        - 解答
        """
        problem_id = problem.get("id", "unknown")
        logger.info(f"Solving problem {problem_id}")
        
        try:
            solution = self.llm_solver.solve_problem(problem)
            return solution
        except Exception as e:
            logger.error(f"Error solving problem {problem_id}: {str(e)}")
            raise
    
    def update_llm_config(self, api_key: Optional[str] = None, model_id: Optional[str] = None, prompt_template: Optional[str] = None):
        """
        更新大模型配置
        
        参数:
        - api_key: 新的API密钥
        - model_id: 新的模型ID
        - prompt_template: 新的提示词模板
        """
        self.llm_solver.update_config(api_key, model_id, prompt_template)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Auto Problem Solver")
    parser.add_argument("--problem-ids-file", type=str, required=True, help="Path to the problem IDs JSON file")
    parser.add_argument("--api-key", type=str, help="Ark API key (if not set in environment)")
    parser.add_argument("--model-id", type=str, help="Model ID to use")
    parser.add_argument("--prompt-template", type=str, help="Custom prompt template")
    parser.add_argument("--max-workers", type=int, default=MAX_WORKERS, help="Maximum number of concurrent workers")
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 创建自动化习题解析批处理工具
    solver = AutoProblemSolver(
        api_key=args.api_key,
        model_id=args.model_id,
        prompt_template=args.prompt_template
    )
    
    # 运行批处理工具
    export_path = solver.run(args.problem_ids_file, args.max_workers)
    
    if export_path:
        print(f"\nResults exported to: {export_path}")
        return 0
    else:
        print("\nFailed to process problems")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 