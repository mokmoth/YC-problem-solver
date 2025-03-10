"""
大模型交互模块，用于与火山方舟API交互进行习题解答
"""

import os
import json
import time
import logging
import requests
from typing import Dict, List, Any, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ARK_API_URL, ARK_API_MODEL, DEFAULT_PROMPT_TEMPLATE, MAX_RETRIES, RETRY_DELAY

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LLMSolver")

class LLMSolver:
    """大模型解题类"""
    
    def __init__(self, api_key: Optional[str] = None, model_id: Optional[str] = None, prompt_template: Optional[str] = None):
        """
        初始化大模型解题器
        
        参数:
        - api_key: 火山方舟API密钥，如果为None则从环境变量获取
        - model_id: 模型ID，如果为None则使用默认模型
        - prompt_template: 提示词模板，如果为None则使用默认模板
        """
        self.api_url = ARK_API_URL
        self.api_key = api_key or os.environ.get("ARK_API_KEY", "")
        self.model_id = model_id or ARK_API_MODEL
        self.prompt_template = prompt_template or DEFAULT_PROMPT_TEMPLATE
        
        if not self.api_key:
            logger.warning("API key not provided. Please set ARK_API_KEY environment variable or provide it directly.")
    
    def solve_problem(self, problem: Dict) -> str:
        """
        使用大模型解答问题
        
        参数:
        - problem: 问题数据，包含题干、学科、年级等信息
        
        返回:
        - 大模型的解答
        """
        if not self.api_key:
            return "错误：未提供API密钥，无法调用大模型"
        
        # 获取问题信息
        question = problem.get('question', '')
        subject = problem.get('subject', '')
        grade = problem.get('grade', '')
        problem_type = problem.get('type', '')
        correct_answer = problem.get('correctAnswer', '')
        
        # 预处理正确答案，移除HTML标签和格式化LaTeX
        processed_correct_answer = self.preprocess_correct_answer(correct_answer)
        
        # 构建提示词
        prompt = self._prepare_prompt(problem)
        
        # 调用API
        for attempt in range(MAX_RETRIES):
            try:
                response = self._call_llm_api(prompt)
                return response
            except Exception as e:
                logger.error(f"LLM API call failed (attempt {attempt+1}/{MAX_RETRIES}): {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))  # 指数退避
                else:
                    logger.error(f"All {MAX_RETRIES} attempts failed for problem {problem.get('id', 'unknown')}")
        
        return "错误：大模型API调用失败"
    
    def _prepare_prompt(self, problem: Dict) -> str:
        """
        准备提示词
        
        参数:
        - problem: 问题数据
        
        返回:
        - 格式化后的提示词
        """
        # 获取并预处理正确答案
        correct_answer = problem.get("correctAnswer", "")
        processed_correct_answer = self.preprocess_correct_answer(correct_answer)
        
        # 使用自定义提示词模板
        return self.prompt_template.format(
            subject=problem.get("subject", ""),
            grade=problem.get("grade", ""),
            type=problem.get("type", ""),
            question=problem.get("question", ""),
            correctAnswers=processed_correct_answer  # 使用处理后的答案
        )
    
    def _call_llm_api(self, prompt: str) -> str:
        """
        调用大模型API
        
        参数:
        - prompt: 提示词
        
        返回:
        - 大模型的回答
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=60  # 设置较长的超时时间，因为大模型推理可能需要时间
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        # 提取回答内容
        try:
            answer = response_data["choices"][0]["message"]["content"]
            return answer
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract answer from response: {str(e)}")
            logger.debug(f"Response data: {json.dumps(response_data)}")
            raise Exception("Failed to extract answer from response")
    
    def update_config(self, api_key: Optional[str] = None, model_id: Optional[str] = None, prompt_template: Optional[str] = None):
        """
        更新配置
        
        参数:
        - api_key: 新的API密钥
        - model_id: 新的模型ID
        - prompt_template: 新的提示词模板
        """
        if api_key:
            self.api_key = api_key
        
        if model_id:
            self.model_id = model_id
        
        if prompt_template:
            self.prompt_template = prompt_template 

    def preprocess_correct_answer(self, answer):
        """预处理正确答案，移除HTML标签和格式化LaTeX"""
        if not answer:
            return "未提供标准答案"
        
        # 移除HTML标签但保留图片URL的描述
        import re
        
        # 检查是否包含图片
        has_image = 'img src=' in answer
        
        # 提取图片URL (如果有)
        image_urls = []
        if has_image:
            img_pattern = r'<img\s+src="([^"]+)"'
            image_matches = re.findall(img_pattern, answer)
            image_urls = [url for url in image_matches if url]
        
        # 移除所有HTML标签
        clean_answer = re.sub(r'<.*?>', '', answer)
        
        # 保留LaTeX格式但确保格式一致
        clean_answer = clean_answer.replace('$ ', '$').replace(' $', '$')
        
        # 如果有图片，添加图片描述
        if image_urls:
            image_desc = "\n[答案包含图片，请根据文字部分进行对比]"
            for i, url in enumerate(image_urls):
                image_desc += f"\n图片{i+1}链接: {url}"
            clean_answer += image_desc
        
        # 处理多个答案的情况（以分号分隔）
        if '；' in clean_answer:
            parts = clean_answer.split('；')
            clean_parts = [part.strip() for part in parts if part.strip()]
            clean_answer = '；'.join(clean_parts)
        
        return clean_answer.strip() 