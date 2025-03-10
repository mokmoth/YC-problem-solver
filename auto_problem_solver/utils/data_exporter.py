"""
数据处理和导出模块，用于将结果导出为Excel
"""

import os
import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OUTPUT_DIR, DEFAULT_OUTPUT_FILENAME
from utils.text_formatter import format_problem_data

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DataExporter")

class DataExporter:
    """数据导出类"""
    
    def __init__(self, output_dir: Optional[str] = None, filename: Optional[str] = None):
        """
        初始化数据导出器
        
        参数:
        - output_dir: 输出目录，如果为None则使用默认目录
        - filename: 输出文件名，如果为None则使用默认文件名
        """
        self.output_dir = output_dir or OUTPUT_DIR
        self.filename = filename or DEFAULT_OUTPUT_FILENAME
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export_to_excel(self, problems_with_solutions: List[Dict]) -> str:
        """
        将问题和解答导出为Excel
        
        参数:
        - problems_with_solutions: 包含问题和解答的字典列表
        
        返回:
        - 导出文件的路径
        """
        if not problems_with_solutions:
            logger.warning("No data to export")
            return ""
        
        try:
            # 创建DataFrame
            df = pd.DataFrame(problems_with_solutions)
            logger.debug(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
            
            # 重新排列列顺序
            columns = [
                "id", "question", "correctAnswer", "subject", 
                "grade", "type", "llmAnswer"
            ]
            
            # 确保所有列都存在
            for col in columns:
                if col not in df.columns:
                    logger.warning(f"Column {col} not found in DataFrame, adding empty column")
                    df[col] = ""
            
            # 选择并排序列
            df = df[columns]
            
            # 记录DataFrame的基本信息
            logger.debug(f"DataFrame columns: {df.columns.tolist()}")
            logger.debug(f"DataFrame shape: {df.shape}")
            
            # 检查correctAnswer列的内容
            empty_answers = df["correctAnswer"].isnull().sum() + (df["correctAnswer"] == "").sum()
            logger.info(f"Number of empty correctAnswer values: {empty_answers}")
            
            # 记录每个问题的correctAnswer
            for idx, row in df.iterrows():
                problem_id = row["id"]
                correct_answer = row["correctAnswer"]
                logger.debug(f"Problem {problem_id}: correctAnswer in DataFrame: {correct_answer}")
            
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_parts = os.path.splitext(self.filename)
            timestamped_filename = f"{filename_parts[0]}_{timestamp}{filename_parts[1]}"
            
            # 导出路径
            export_path = os.path.join(self.output_dir, timestamped_filename)
            
            # 导出到Excel
            df.to_excel(export_path, index=False, engine='openpyxl')
            logger.debug(f"Exported DataFrame to {export_path}")
            
            # 使用openpyxl添加格式化
            from openpyxl import load_workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter
            
            # 加载工作簿
            wb = load_workbook(export_path)
            ws = wb.active
            
            # 设置样式
            header_font = Font(bold=True, size=12)
            header_fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
            thin_border = Border(
                left=Side(style='thin'), 
                right=Side(style='thin'), 
                top=Side(style='thin'), 
                bottom=Side(style='thin')
            )
            
            # 设置列宽
            for i, column in enumerate(columns, 1):
                col_letter = get_column_letter(i)
                if column == "question":
                    ws.column_dimensions[col_letter].width = 60
                elif column == "correctAnswer":
                    ws.column_dimensions[col_letter].width = 40  # 增加宽度以显示更多内容
                elif column == "llmAnswer":
                    ws.column_dimensions[col_letter].width = 60
                else:
                    ws.column_dimensions[col_letter].width = 15
            
            # 设置标题行样式
            for cell in ws[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                cell.border = thin_border
            
            # 设置所有单元格样式
            for row in ws.iter_rows(min_row=2):
                for cell in row:
                    cell.alignment = Alignment(vertical='top', wrap_text=True)
                    cell.border = thin_border
            
            # 保存工作簿
            wb.save(export_path)
            
            logger.info(f"Data exported to {export_path}")
            return export_path
        
        except Exception as e:
            logger.error(f"Error exporting data to Excel: {str(e)}")
            logger.exception("Exception details:")
            return ""
    
    def format_data_for_export(self, problems: List[Dict], solutions: Dict[str, str]) -> List[Dict]:
        """
        格式化数据用于导出
        
        参数:
        - problems: 问题数据列表
        - solutions: 问题ID到解答的映射
        
        返回:
        - 格式化后的数据列表
        """
        formatted_data = []
        logger.info(f"Formatting {len(problems)} problems for export")
        
        for problem in problems:
            problem_id = problem.get("id", "")
            logger.debug(f"Formatting problem {problem_id} for export")
            logger.debug(f"Original problem data: {json.dumps(problem, ensure_ascii=False)}")
            
            # 创建新的字典，包含问题数据和解答
            item = problem.copy()
            
            # 添加大模型解答
            item["llmAnswer"] = solutions.get(problem_id, "")
            
            # 确保correctAnswer字段存在且不为空
            if not item.get("correctAnswer"):
                logger.warning(f"Problem {problem_id}: correctAnswer is empty or missing")
                item["correctAnswer"] = "答案不可用"
                logger.debug(f"Problem {problem_id}: Empty correctAnswer set to '答案不可用'")
            else:
                logger.debug(f"Problem {problem_id}: correctAnswer is {item['correctAnswer']}")
            
            # 应用文本格式化，使LaTeX公式更易读
            logger.debug(f"Applying text formatting for problem {problem_id}")
            item = format_problem_data(item)
            logger.debug(f"Formatted problem data: {json.dumps(item, ensure_ascii=False)}")
            
            formatted_data.append(item)
        
        logger.info(f"Formatted {len(formatted_data)} problems for export")
        return formatted_data 