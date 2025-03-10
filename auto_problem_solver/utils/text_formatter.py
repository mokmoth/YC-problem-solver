"""
文本格式化工具，用于处理LaTeX/KaTeX公式，使其更易读
"""

import re

def format_latex_for_readability(text):
    """
    将包含LaTeX/KaTeX公式的文本转换为更易读的格式
    
    参数:
    - text: 包含LaTeX/KaTeX公式的文本
    
    返回:
    - 转换后更易读的文本
    """
    if not text or not isinstance(text, str):
        return text
    
    # 处理HTML标签 - 保留换行符
    text = text.replace('<br />', '\n').replace('<br>', '\n')
    
    # 处理图片标签
    img_pattern = r'<div>?\s*<img src="([^"]+)"[^>]*>\s*</div>?'
    text = re.sub(img_pattern, r'[图片]', text)
    
    # 处理LLM输出中的特殊转义符，如\(7\)
    text = re.sub(r'\\[\(（]([^\\]*)\\[\)）]', r'\1', text)
    
    # 处理LLM输出中的其他常见转义符
    text = re.sub(r'\\cdots\\cdots', '......', text)
    text = re.sub(r'\\cdots', '......', text)
    
    # 替换常见的LaTeX符号
    latex_symbols = {
        r'\\square': '□',               # 方框
        r'\\bigcirc': '○',              # 圆圈
        r'\\gt': '>',                   # 大于号
        r'\\lt': '<',                   # 小于号
        r'\\ge': '≥',                   # 大于等于
        r'\\le': '≤',                   # 小于等于
        r'\\neq': '≠',                  # 不等于
        r'\\times': '×',                # 乘号
        r'\\div': '÷',                  # 除号
        r'\\pm': '±',                   # 加减号
        r'\\cdot': '·',                 # 点乘
        r'\\sum': '∑',                  # 求和
        r'\\prod': '∏',                 # 求积
        r'\\int': '∫',                  # 积分
        r'\\infty': '∞',                # 无穷
        r'\\pi': 'π',                   # 圆周率
        r'\\alpha': 'α',                # 希腊字母alpha
        r'\\beta': 'β',                 # 希腊字母beta
        r'\\gamma': 'γ',                # 希腊字母gamma
        r'\\delta': 'δ',                # 希腊字母delta
        r'\\theta': 'θ',                # 希腊字母theta
        r'\\lambda': 'λ',               # 希腊字母lambda
        r'\\mu': 'μ',                   # 希腊字母mu
        r'\\sigma': 'σ',                # 希腊字母sigma
        r'\\omega': 'ω',                # 希腊字母omega
    }
    
    # 应用替换规则
    for pattern, replacement in latex_symbols.items():
        text = text.replace(pattern, replacement)
    
    # 处理平方根
    text = re.sub(r'\\sqrt\s*\{\s*([^{}]*)\s*\}', r'√\1', text)
    text = re.sub(r'\\sqrt\s+([a-zA-Z0-9]+)', r'√\1', text)
    
    # 处理分数
    text = re.sub(r'\\frac\s*\{\s*([^{}]*)\s*\}\s*\{\s*([^{}]*)\s*\}', r'\1/\2', text)
    
    # 处理括号
    text = re.sub(r'\\left\s*\(', '(', text)
    text = re.sub(r'\\right\s*\)', ')', text)
    text = re.sub(r'\\left\s*\[', '[', text)
    text = re.sub(r'\\right\s*\]', ']', text)
    text = re.sub(r'\\left\s*\\{', '{', text)
    text = re.sub(r'\\right\s*\\}', '}', text)
    text = re.sub(r'\\left\s*\|', '|', text)
    text = re.sub(r'\\right\s*\|', '|', text)
    
    # 处理其他括号形式
    text = re.sub(r'\\left', '', text)
    text = re.sub(r'\\right', '', text)
    
    # 处理数学模式
    # 移除单个$符号，但保留内容
    text = re.sub(r'\$([^$]*)\$', r'\1', text)
    
    # 处理下划线（通常用于表示下标）
    text = re.sub(r'_\{\s*([^{}]*)\s*\}', r'_\1', text)
    text = re.sub(r'_([a-zA-Z0-9])', r'_\1', text)
    
    # 处理上标
    text = re.sub(r'\^\{\s*([^{}]*)\s*\}', r'^\1', text)
    text = re.sub(r'\^([a-zA-Z0-9])', r'^\1', text)
    
    # 处理填空符号
    text = text.replace('____', '_____')  # 使填空线更明显
    
    # 处理常见的LaTeX命令
    text = re.sub(r'\\text\{\s*([^{}]*)\s*\}', r'\1', text)
    text = re.sub(r'\\textbf\{\s*([^{}]*)\s*\}', r'\1', text)
    text = re.sub(r'\\textit\{\s*([^{}]*)\s*\}', r'\1', text)
    text = re.sub(r'\\mathrm\{\s*([^{}]*)\s*\}', r'\1', text)
    
    # 移除多余的空格，但保留换行符
    lines = text.split('\n')
    for i in range(len(lines)):
        lines[i] = re.sub(r'\s+', ' ', lines[i]).strip()
    text = '\n'.join(lines)
    
    # 美化格式
    # 在数学表达式之间添加适当的空格
    text = re.sub(r'(\d+)([+\-×÷=])', r'\1 \2', text)
    text = re.sub(r'([+\-×÷=])(\d+)', r'\1 \2', text)
    
    # 格式化分隔符
    text = text.replace('；', '；\n')  # 在中文分号后添加换行
    
    # 格式化数学表达式
    # 替换方框和圆圈为更易读的符号
    text = text.replace('□', '[  ]')  # 方框替换为方括号
    text = text.replace('○', '(  )')  # 圆圈替换为圆括号
    
    # 格式化填空题
    text = re.sub(r'([=<>])\s*_____', r'\1 _____', text)  # 确保等号后有空格
    
    return text

def format_problem_data(problem_data):
    """
    格式化问题数据，使其更易读
    
    参数:
    - problem_data: 包含问题数据的字典
    
    返回:
    - 格式化后的问题数据字典
    """
    if not problem_data or not isinstance(problem_data, dict):
        return problem_data
    
    # 创建一个新的字典，避免修改原始数据
    formatted_data = problem_data.copy()
    
    # 格式化问题文本
    if 'question' in formatted_data and formatted_data['question']:
        formatted_data['question'] = format_latex_for_readability(formatted_data['question'])
    
    # 处理正确答案
    if 'correctAnswer' in formatted_data:
        if isinstance(formatted_data['correctAnswer'], str):
            # 检查是否包含图片URL
            if re.search(r'<img\s+src="([^"]+)"', formatted_data['correctAnswer']):
                # 提取图片URL
                img_urls = re.findall(r'<img\s+src="([^"]+)"', formatted_data['correctAnswer'])
                if img_urls:
                    # 提取非HTML部分的文本（通常是数字或公式）
                    text_content = re.sub(r'<div>?\s*<img\s+src="[^"]+"[^>]*>\s*</div>?', '', formatted_data['correctAnswer'])
                    # 格式化文本内容
                    if text_content.strip():
                        text_content = format_latex_for_readability(text_content.strip())
                        # 组合文本内容和图片URL
                        formatted_data['correctAnswer'] = f"{text_content} [图片URL: {img_urls[0]}]"
                    else:
                        # 如果只有图片URL，则只保留URL
                        formatted_data['correctAnswer'] = f"[图片URL: {img_urls[0]}]"
            else:
                # 不包含图片URL，正常格式化
                formatted_data['correctAnswer'] = format_latex_for_readability(formatted_data['correctAnswer'])
        elif isinstance(formatted_data['correctAnswer'], list):
            # 处理列表形式的答案
            formatted_answers = []
            for answer in formatted_data['correctAnswer']:
                if isinstance(answer, str):
                    if re.search(r'<img\s+src="([^"]+)"', answer):
                        # 提取图片URL
                        img_urls = re.findall(r'<img\s+src="([^"]+)"', answer)
                        if img_urls:
                            # 提取非HTML部分的文本
                            text_content = re.sub(r'<div>?\s*<img\s+src="[^"]+"[^>]*>\s*</div>?', '', answer)
                            # 格式化文本内容
                            if text_content.strip():
                                text_content = format_latex_for_readability(text_content.strip())
                                # 组合文本内容和图片URL
                                formatted_answers.append(f"{text_content} [图片URL: {img_urls[0]}]")
                            else:
                                # 如果只有图片URL，则只保留URL
                                formatted_answers.append(f"[图片URL: {img_urls[0]}]")
                    else:
                        # 不包含图片URL，正常格式化
                        formatted_answers.append(format_latex_for_readability(answer))
                else:
                    formatted_answers.append(answer)
            formatted_data['correctAnswer'] = formatted_answers
    
    # 格式化大模型解答
    if 'llmAnswer' in formatted_data and formatted_data['llmAnswer']:
        formatted_data['llmAnswer'] = format_latex_for_readability(formatted_data['llmAnswer'])
    
    return formatted_data 