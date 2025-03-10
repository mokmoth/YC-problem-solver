"""
问题数据获取模块，负责从API获取习题数据
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Union

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROBLEM_API_URL, PROBLEM_API_HEADERS, MAX_RETRIES, RETRY_DELAY

# 全局映射表（常量）
SUBJECT_MAP = [
    {"id": 1, "name": "数学"},
    {"id": 2, "name": "物理"},
    {"id": 3, "name": "语文"},
    {"id": 4, "name": "化学"},
    {"id": 5, "name": "英语"},
    {"id": 6, "name": "生物"},
    {"id": 7, "name": "地理"},
    {"id": 8, "name": "自然"},
    {"id": 9, "name": "地球"},
    {"id": 10, "name": "实验"},
    {"id": 11, "name": "道德与法治"},
    {"id": 12, "name": "历史"},
    {"id": 13, "name": "信息技术"},
    {"id": 14, "name": "理化生实验"},
    {"id": 15, "name": "体育与健康"},
    {"id": 16, "name": "素养"}
]

STAGE_MAP = [
    {"id": 1, "name": "小学"},
    {"id": 2, "name": "初中"},
    {"id": 3, "name": "高中"},
    {"id": 4, "name": "中职"}
]

TYPE_MAP = [
    {"id": "single_choice", "name": "单选题"},
    {"id": "multi_choice", "name": "多选题"},
    {"id": "hybrid", "name": "下拉菜单+填空题"},
    {"id": "multi_blank", "name": "填空题"},
    {"id": "exam", "name": "主观题"},
    {"id": "combination", "name": "组合题"}
]

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ProblemFetcher")

class ProblemFetcher:
    """问题数据获取类"""
    
    def __init__(self):
        """初始化问题获取器"""
        self.api_url = PROBLEM_API_URL
        self.headers = PROBLEM_API_HEADERS
    
    def get_problems(self, problem_ids: List[str]) -> List[Dict]:
        """
        获取多个问题的详细信息
        
        参数:
        - problem_ids: 问题ID列表
        
        返回:
        - 格式化后的问题列表
        """
        if not problem_ids:
            logger.warning("No problem IDs provided")
            return []
        
        # 分批处理，每次最多处理50个问题
        batch_size = 50
        all_formatted_problems = []
        
        for i in range(0, len(problem_ids), batch_size):
            batch_ids = problem_ids[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}, size: {len(batch_ids)}")
            
            problems_response = self._get_problem_batch(batch_ids)
            problems_data = problems_response.get("problems", [])
            
            # 记录原始API响应
            logger.debug(f"Raw API response: {json.dumps(problems_response, ensure_ascii=False)[:1000]}...")
            logger.info(f"Received {len(problems_data)} problems from API")
            
            formatted_problems = []
            for problem in problems_data:
                try:
                    problem_id = problem.get("id", "unknown")
                    logger.debug(f"Processing problem {problem_id}")
                    logger.debug(f"Raw problem data: {json.dumps(problem, ensure_ascii=False)[:1000]}...")
                    
                    item = {
                        "question": "",
                        "correctAnswer": "",  # 将在后面设置
                        "subject": "",
                        "grade": "",
                        "type": "",
                        "id": ""
                    }
                    
                    # 优先使用correctAnswers字段
                    if "correctAnswers" in problem and problem["correctAnswers"]:
                        item["correctAnswer"] = problem["correctAnswers"]
                        logger.info(f"Problem {problem_id}: Using correctAnswers field: {item['correctAnswer']}")
                    # 其次使用correctAnswer字段
                    elif "correctAnswer" in problem and problem["correctAnswer"]:
                        item["correctAnswer"] = problem["correctAnswer"]
                        logger.info(f"Problem {problem_id}: Using correctAnswer field: {item['correctAnswer']}")
                    else:
                        # 如果都没有，尝试从其他字段获取
                        item["correctAnswer"] = self._get_original_answer(problem)
                        logger.info(f"Problem {problem_id}: No correctAnswer/correctAnswers field, using alternative: {item['correctAnswer']}")
                    
                    item["question"] = self._format_body(problem)
                    item["subject"] = self._format_subject(problem.get("subjectId"))
                    item["grade"] = self._format_stage(problem.get("stageId"))
                    item["type"] = self._format_type(problem.get("type"))
                    item["id"] = problem.get("id", "")
                    
                    logger.debug(f"Formatted problem {problem_id}: {json.dumps(item, ensure_ascii=False)}")
                    formatted_problems.append(item)
                except Exception as e:
                    logger.error(f"Error formatting problem {problem.get('id', 'unknown')}: {str(e)}")
            
            all_formatted_problems.extend(formatted_problems)
            
            # 避免频繁请求API
            if i + batch_size < len(problem_ids):
                time.sleep(1)
        
        return all_formatted_problems
    
    def _get_problem_batch(self, problem_ids: List[str]) -> Dict:
        """
        从API获取一批问题的详细信息
        
        参数:
        - problem_ids: 问题ID列表
        
        返回:
        - API响应数据
        """
        payload = {"ids": problem_ids}
        logger.debug(f"Sending request to API with payload: {json.dumps(payload, ensure_ascii=False)}")
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=30  # 设置超时时间
                )
                response.raise_for_status()
                response_data = response.json()
                logger.debug(f"API response status: {response.status_code}")
                return response_data
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt+1}/{MAX_RETRIES}): {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))  # 指数退避
                else:
                    logger.error(f"All {MAX_RETRIES} attempts failed for batch")
        
        return {"problems": []}
    
    def _format_body(self, problem: Dict) -> str:
        """
        格式化问题内容
        
        参数:
        - problem: 问题数据
        
        返回:
        - 格式化后的问题内容
        """
        body = problem.get("body", "")
        subproblems = problem.get("subproblems", [])
        
        for sub in subproblems:
            body += sub.get("body", "")
        
        # 转义特殊字符
        body = body.replace("\\", "\\\\").replace('"', "'")
        return body
    
    def _get_original_answer(self, problem: Dict) -> str:
        """
        获取原始答案
        
        参数:
        - problem: 问题数据
        
        返回:
        - 原始答案
        """
        problem_id = problem.get("id", "unknown")
        
        # 记录所有可能包含答案的字段
        logger.debug(f"Problem {problem_id}: Looking for answer in alternative fields")
        
        # 检查单选题和多选题的答案
        if problem.get("type") in ["single_choice", "multi_choice"]:
            choices = problem.get("choices", [])
            if choices and len(choices) > 0:
                # 获取第一组选项（通常只有一组）
                choice_group = choices[0]
                correct_choices = []
                
                # 查找正确选项
                for i, choice in enumerate(choice_group):
                    if choice.get("correct", False):
                        # 使用选项序号（A, B, C, D...）
                        correct_choices.append(chr(65 + i))  # 65是ASCII码中'A'的值
                
                if correct_choices:
                    result = ", ".join(correct_choices)
                    logger.debug(f"Problem {problem_id}: Using correct choices: {result}")
                    return result
        
        # 尝试从correctAnswers字段获取
        if "correctAnswers" in problem and problem["correctAnswers"]:
            result = problem["correctAnswers"]
            logger.debug(f"Problem {problem_id}: Using correctAnswers: {result}")
            return result
        
        # 尝试从correctAnswer字段获取
        if "correctAnswer" in problem and problem["correctAnswer"]:
            result = problem["correctAnswer"]
            logger.debug(f"Problem {problem_id}: Using correctAnswer: {result}")
            return result
        
        # 尝试从explains字段获取
        if "explains" in problem and problem["explains"]:
            explains = problem["explains"]
            logger.debug(f"Problem {problem_id}: Found explains: {explains}")
            if explains:
                if isinstance(explains, dict):
                    # 将字典转换为字符串
                    result = json.dumps(explains, ensure_ascii=False)
                    logger.debug(f"Problem {problem_id}: Using explains (dict): {result}")
                    return result
                result = str(explains)
                logger.debug(f"Problem {problem_id}: Using explains (str): {result}")
                return result
        
        # 尝试从answer字段获取
        if "answer" in problem and problem["answer"]:
            result = problem["answer"]
            logger.debug(f"Problem {problem_id}: Using answer: {result}")
            return result
        
        # 尝试从extendedBlanks字段获取
        if "extendedBlanks" in problem and problem["extendedBlanks"]:
            blanks = []
            for blank in problem["extendedBlanks"]:
                if blank and len(blank) > 0:
                    blanks.append(blank[0])
            if blanks:
                result = ", ".join(blanks)
                logger.debug(f"Problem {problem_id}: Using extendedBlanks: {result}")
                return result
        
        # 如果都没有，返回"答案不可用"
        logger.warning(f"Problem {problem_id}: No answer found in any field")
        return "答案不可用"
    
    def _format_subject(self, subject_id: int) -> str:
        """
        将学科ID转换为名称
        
        参数:
        - subject_id: 学科ID
        
        返回:
        - 学科名称
        """
        subject = next((s["name"] for s in SUBJECT_MAP if s["id"] == subject_id), "")
        return subject
    
    def _format_stage(self, stage_id: int) -> str:
        """
        将学段ID转换为名称
        
        参数:
        - stage_id: 学段ID
        
        返回:
        - 学段名称
        """
        stage = next((s["name"] for s in STAGE_MAP if s["id"] == stage_id), "")
        return stage
    
    def _format_type(self, type_id: str) -> str:
        """
        将题目类型ID转换为名称
        
        参数:
        - type_id: 题目类型ID
        
        返回:
        - 题目类型名称
        """
        type_entry = next((t["name"] for t in TYPE_MAP if t["id"] == type_id), "")
        return type_entry
    
    def load_problem_ids_from_file(self, file_path: str) -> List[str]:
        """
        从JSON文件加载问题ID
        
        参数:
        - file_path: JSON文件路径
        
        返回:
        - 问题ID列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取所有问题ID
            all_ids = []
            for stage, subjects in data.items():
                for subject, ids in subjects.items():
                    all_ids.extend(ids)
            
            return all_ids
        except Exception as e:
            logger.error(f"Error loading problem IDs from file {file_path}: {str(e)}")
            return [] 