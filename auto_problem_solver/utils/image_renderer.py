"""
图像渲染模块，用于将文本和LaTeX公式渲染为图片
"""

import os
import time
import base64
import uuid
import shutil
from pathlib import Path
from typing import Optional
import logging
import re
from PIL import Image, ImageDraw, ImageFont
import textwrap

# 获取日志记录器
from utils.logger import get_logger
logger = get_logger("ImageRenderer")

class ImageRenderer:
    """图像渲染类，用于将文本和LaTeX公式渲染为图片"""
    
    def __init__(self, output_dir: str = 'rendered_images'):
        """
        初始化图像渲染器
        
        参数:
        - output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置默认字体和字体大小
        self.font_size = 16
        try:
            # 尝试加载Arial字体或系统默认字体
            self.font = ImageFont.truetype("Arial.ttf", self.font_size)
        except Exception:
            # 如果找不到指定字体，使用默认字体
            self.font = ImageFont.load_default()
    
    def _format_llm_answer(self, text: str) -> str:
        """
        格式化LLM回答，处理特殊标签
        
        参数:
        - text: LLM回答文本
        
        返回:
        - 格式化后的文本
        """
        # 处理<解题>...</解题>标签
        text = re.sub(r'<解题>(.*?)</解题>', r'[解题过程]\n\1\n', 
                     text, flags=re.DOTALL)
        
        # 处理<对比>...</对比>标签
        text = re.sub(r'<对比>(.*?)</对比>', r'[答案对比]\n\1\n', 
                     text, flags=re.DOTALL)
        
        # 处理<讲解>...</讲解>标签
        text = re.sub(r'<讲解>(.*?)</讲解>', r'[详细讲解]\n\1\n',
                     text, flags=re.DOTALL)
        
        return text
    
    def _replace_latex_with_placeholder(self, text: str) -> tuple:
        """
        将LaTeX公式替换为占位符
        
        参数:
        - text: 包含LaTeX公式的文本
        
        返回:
        - 替换后的文本和LaTeX公式列表
        """
        latex_formulas = []
        
        # 替换行内公式: $content$ -> [LATEX_n]
        def replace_inline(match):
            latex_formulas.append(match.group(1))
            return f"[LATEX_{len(latex_formulas)-1}]"
        
        # 替换行间公式: $$content$$ -> [LATEX_BLOCK_n]
        def replace_block(match):
            latex_formulas.append(match.group(1))
            return f"[LATEX_BLOCK_{len(latex_formulas)-1}]"
        
        # 替换单行公式: $(content)$ -> [LATEX_n]
        def replace_single(match):
            latex_formulas.append(match.group(1))
            return f"[LATEX_{len(latex_formulas)-1}]"
        
        # 先替换行间公式
        text = re.sub(r'\$\$(.*?)\$\$', replace_block, text, flags=re.DOTALL)
        
        # 再替换单行公式
        text = re.sub(r'\$\((.*?)\)\$', replace_single, text, flags=re.DOTALL)
        
        # 最后替换行内公式
        text = re.sub(r'\$(.*?)\$', replace_inline, text, flags=re.DOTALL)
        
        return text, latex_formulas
    
    def render_text_to_image(self, text: str, problem_id: str) -> Optional[str]:
        """
        将文本渲染为图片
        
        参数:
        - text: 要渲染的文本
        - problem_id: 问题ID，用于生成唯一的文件名
        
        返回:
        - 图片文件路径，如果渲染失败则返回None
        """
        if not text:
            logger.warning("Empty text provided for rendering")
            return None
        
        try:
            # 生成唯一的文件名
            unique_id = uuid.uuid4().hex[:8]
            output_file = f"{problem_id}_{unique_id}.png"
            output_path = os.path.join(self.output_dir, output_file)
            
            # 格式化文本
            formatted_text = self._format_llm_answer(text)
            
            # 替换LaTeX公式为占位符
            text_with_placeholders, latex_formulas = self._replace_latex_with_placeholder(formatted_text)
            
            # 计算文本宽度和高度
            lines = text_with_placeholders.split('\n')
            line_width = 80  # 每行字符数
            wrapped_lines = []
            
            for line in lines:
                if len(line) > line_width:
                    # 对长行进行换行处理
                    wrapped = textwrap.wrap(line, width=line_width)
                    wrapped_lines.extend(wrapped)
                else:
                    wrapped_lines.append(line)
            
            # 增加行高以容纳LaTeX公式等
            line_height = self.font_size + 6
            
            # 创建一个足够大的图片
            img_width = line_width * 10  # 估计宽度
            img_height = len(wrapped_lines) * line_height + 50  # 估计高度
            
            # 创建带有白色背景的图片
            image = Image.new('RGB', (img_width, img_height), color='white')
            draw = ImageDraw.Draw(image)
            
            # 绘制文本
            y_position = 10
            for line in wrapped_lines:
                # 检查行中是否有LaTeX占位符
                if '[LATEX_' in line or '[LATEX_BLOCK_' in line:
                    # 简单处理：将LaTeX占位符替换为"[公式]"
                    line = re.sub(r'\[LATEX_\d+\]', '[LaTeX公式]', line)
                    line = re.sub(r'\[LATEX_BLOCK_\d+\]', '[LaTeX公式(块)]', line)
                
                # 绘制当前行
                draw.text((10, y_position), line, font=self.font, fill='black')
                y_position += line_height
            
            # 保存图片
            image.save(output_path)
            
            logger.info(f"Successfully rendered image to {output_path}")
            return output_path
                
        except Exception as e:
            logger.error(f"Error rendering text to image: {str(e)}")
            logger.exception("Exception details:")
            return None
    
    def get_image_for_excel(self, image_path: str) -> Optional[bytes]:
        """
        获取图片用于Excel
        
        参数:
        - image_path: 图片文件路径
        
        返回:
        - 图片字节数据，如果获取失败则返回None
        """
        try:
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            logger.error(f"Error reading image file: {str(e)}")
            return None 