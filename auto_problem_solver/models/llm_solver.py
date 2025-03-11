"""
大模型交互模块，用于与火山方舟API交互进行习题解答
"""

import os
import json
import time
import logging
import requests
import base64
import tempfile
import re
from typing import Dict, List, Any, Optional, Union, Tuple

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ARK_API_URL, ARK_API_MODEL, DEFAULT_PROMPT_TEMPLATE, MAX_RETRIES, RETRY_DELAY, ENABLE_MULTIMODAL
from utils.logger import get_logger

# 获取日志记录器
logger = get_logger("LLMSolver")

class LLMSolver:
    """大模型解题类"""
    
    def __init__(self, api_key: Optional[str] = None, model_id: Optional[str] = None, prompt_template: Optional[str] = None, enable_multimodal: Optional[bool] = None):
        """
        初始化大模型解题器
        
        参数:
        - api_key: 火山方舟API密钥，如果为None则从环境变量获取
        - model_id: 模型ID，如果为None则使用默认模型
        - prompt_template: 提示词模板，如果为None则使用默认模板
        - enable_multimodal: 是否启用多模态功能，如果为None则使用配置文件中的设置
        """
        self.api_url = ARK_API_URL
        self.api_key = api_key or os.environ.get("ARK_API_KEY", "")
        self.model_id = model_id or ARK_API_MODEL
        self.prompt_template = prompt_template or DEFAULT_PROMPT_TEMPLATE
        self.enable_multimodal = enable_multimodal if enable_multimodal is not None else ENABLE_MULTIMODAL
        self.temp_dir = tempfile.mkdtemp(prefix="llm_solver_images_")
        
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
        
        # 记录原始问题数据，用于调试
        logger.debug(f"原始问题数据: {json.dumps(problem, ensure_ascii=False)}")
        logger.debug(f"原始题干: {question}")
        logger.debug(f"原始答案: {correct_answer}")
        
        # 构建提示词和提取图片URL
        prompt, image_urls_dict = self._prepare_prompt(problem)
        
        # 记录处理后的数据，用于调试
        logger.debug(f"处理后的提示词: {prompt}")
        logger.debug(f"提取的图片URL: {json.dumps(image_urls_dict, ensure_ascii=False)}")
        
        # 调用API
        for attempt in range(MAX_RETRIES):
            try:
                response = self._call_llm_api(prompt, image_urls_dict)
                return response
            except Exception as e:
                logger.error(f"LLM API call failed (attempt {attempt+1}/{MAX_RETRIES}): {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))  # 指数退避
                else:
                    logger.error(f"All {MAX_RETRIES} attempts failed for problem {problem.get('id', 'unknown')}")
        
        return "错误：大模型API调用失败"
    
    def _prepare_prompt(self, problem: Dict) -> Tuple[str, Dict[str, List[str]]]:
        """
        准备提示词和提取图片URL
        
        参数:
        - problem: 问题数据
        
        返回:
        - 格式化后的提示词和图片URL字典（按来源分类）
        """
        # 获取并预处理问题和正确答案
        question = problem.get("question", "")
        correct_answer = problem.get("correctAnswer", "")
        
        # 处理问题中的图片
        processed_question, question_image_urls = self.extract_images_from_html(question)
        
        # 处理正确答案中的图片
        processed_correct_answer, answer_image_urls = self.extract_images_from_html(correct_answer)
        
        # 使用自定义提示词模板
        prompt = self.prompt_template.format(
            subject=problem.get("subject", ""),
            grade=problem.get("grade", ""),
            type=problem.get("type", ""),
            question=processed_question,
            correctAnswers=processed_correct_answer
        )
        
        # 收集所有图片URL
        image_urls_dict = {
            "question": question_image_urls,
            "answer": answer_image_urls
        }
        
        return prompt, image_urls_dict
    
    def _call_llm_api(self, prompt: str, image_urls_dict: Dict[str, List[str]] = None) -> str:
        """
        调用大模型API
        
        参数:
        - prompt: 提示词
        - image_urls_dict: 图片URL字典，按来源分类
        
        返回:
        - 大模型的回答
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 准备消息内容
        content = []
        
        # 添加文本内容
        content.append({
            "type": "text",
            "text": prompt
        })
        
        # 如果启用了多模态功能并且有图片URL，添加图片内容
        if self.enable_multimodal and image_urls_dict:
            all_image_urls = []
            for source, urls in image_urls_dict.items():
                all_image_urls.extend(urls)
            
            if all_image_urls:
                logger.info(f"准备处理 {len(all_image_urls)} 个图片")
                
                # 下载并处理图片
                for url in all_image_urls:
                    try:
                        # 规范化URL（移除引号等）
                        clean_url = self._normalize_url(url)
                        logger.info(f"处理图片URL: {clean_url}")
                        
                        # 添加图片内容
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": clean_url
                            }
                        })
                        logger.info(f"成功添加图片URL到请求")
                    except Exception as e:
                        logger.error(f"处理图片时出错: {str(e)}")
        
        payload = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }
        
        # 记录API请求负载（但不包含完整图片数据，以避免日志过大）
        safe_payload = json.loads(json.dumps(payload))
        if "content" in safe_payload["messages"][0]:
            content_list = safe_payload["messages"][0]["content"]
            for i, item in enumerate(content_list):
                if item.get("type") == "image_url":
                    content_list[i] = {"type": "image_url", "image_url": {"url": "[图片URL]"}}
        
        logger.debug(f"API请求负载: {json.dumps(safe_payload, ensure_ascii=False)}")
        
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
    
    def update_config(self, api_key: Optional[str] = None, model_id: Optional[str] = None, prompt_template: Optional[str] = None, enable_multimodal: Optional[bool] = None):
        """
        更新配置
        
        参数:
        - api_key: 新的API密钥
        - model_id: 新的模型ID
        - prompt_template: 新的提示词模板
        - enable_multimodal: 是否启用多模态功能
        """
        if api_key:
            self.api_key = api_key
        
        if model_id:
            self.model_id = model_id
        
        if prompt_template:
            self.prompt_template = prompt_template
            
        if enable_multimodal is not None:
            self.enable_multimodal = enable_multimodal

    def extract_images_from_html(self, html_content: str) -> Tuple[str, List[str]]:
        """
        从HTML内容中提取图片URL
        
        参数:
        - html_content: HTML内容
        
        返回:
        - 处理后的文本内容和图片URL列表
        """
        if not html_content:
            return "", []
        
        # 检查是否包含图片
        has_image = 'img src=' in html_content or "img src='" in html_content
        
        # 提取图片URL (如果有)
        image_urls = []
        if has_image:
            # 匹配双引号和单引号的图片URL
            img_patterns = [
                r'<img\s+src="([^"]+)"',  # 双引号
                r"<img\s+src='([^']+)'"   # 单引号
            ]
            
            for pattern in img_patterns:
                image_matches = re.findall(pattern, html_content)
                if image_matches:
                    logger.info(f"使用模式 '{pattern}' 找到 {len(image_matches)} 个图片URL")
                    image_urls.extend([url for url in image_matches if url])
            
            logger.info(f"从内容中提取到 {len(image_urls)} 个图片URL: {image_urls}")
        
        # 移除所有HTML标签
        clean_content = re.sub(r'<.*?>', '', html_content)
        
        # 保留LaTeX格式但确保格式一致
        clean_content = clean_content.replace('$ ', '$').replace(' $', '$')
        
        # 如果启用了多模态功能，不需要在文本中添加图片描述
        # 如果没有启用多模态功能，添加图片描述
        if not self.enable_multimodal and image_urls:
            image_desc = "\n[内容包含图片，请根据文字部分进行对比]"
            for i, url in enumerate(image_urls):
                image_desc += f"\n图片{i+1}链接: {url}"
            clean_content += image_desc
        
        return clean_content.strip(), image_urls
    
    def _normalize_url(self, url: str) -> str:
        """
        规范化URL，移除引号等
        
        参数:
        - url: 原始URL
        
        返回:
        - 规范化后的URL
        """
        # 移除URL两端的引号
        url = url.strip('"\'')
        
        # 确保URL是绝对路径
        if not url.startswith(('http://', 'https://')):
            if url.startswith('//'):
                url = 'https:' + url
            else:
                url = 'https://' + url
        
        return url
    
    def download_image(self, url: str) -> Optional[bytes]:
        """
        下载图片
        
        参数:
        - url: 图片URL
        
        返回:
        - 图片数据
        """
        try:
            # 规范化URL
            clean_url = self._normalize_url(url)
            
            # 设置请求头，模拟浏览器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(clean_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 检查内容类型
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                logger.warning(f"URL返回的内容类型不是图片: {content_type}, URL: {clean_url}")
            
            return response.content
        except Exception as e:
            logger.error(f"下载图片失败: {url}, 错误: {str(e)}")
            return None
    
    def preprocess_correct_answer(self, answer: str) -> Tuple[str, List[str]]:
        """
        预处理正确答案，提取图片URL
        
        参数:
        - answer: 原始答案字符串
        
        返回:
        - 处理后的答案文本和图片URL列表
        """
        return self.extract_images_from_html(answer) 