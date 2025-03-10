"""
测试文本格式化功能
"""

import json
import logging
from utils.text_formatter import format_latex_for_readability, format_problem_data

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("formatter_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("FormatterTest")

def test_latex_formatting():
    """测试LaTeX格式化功能"""
    
    # 测试用例
    test_cases = [
        {
            "name": "简单数学公式",
            "input": "计算：$\\sqrt { \\left( 1 - \\sqrt 2 \\right) ^ { 2 } } = $____$.$",
            "check_for": ["√", "1 - √2", "_____"]  # 检查关键部分是否存在
        },
        {
            "name": "分数",
            "input": "化简：$\\frac{x^2-4}{x-2} = $____$.$",
            "check_for": ["x^2", "/", "x-2", "_____"]
        },
        {
            "name": "带HTML标签的文本",
            "input": "解方程：$2x + 3 = 7$<br>$x = $____$.$",
            "check_for": ["2x + 3 = 7", "x = _____"]
        },
        {
            "name": "带图片的文本",
            "input": "观察图形：<div><img src=\"https://example.com/image.jpg\"></div>计算面积。",
            "check_for": ["[图片]", "计算面积"]
        }
    ]
    
    # 运行测试
    for i, test in enumerate(test_cases):
        logger.info(f"测试 {i+1}: {test['name']}")
        logger.debug(f"输入: {test['input']}")
        
        result = format_latex_for_readability(test['input'])
        logger.debug(f"输出: {result}")
        
        # 检查关键部分是否存在
        all_found = True
        for check in test['check_for']:
            if check not in result:
                logger.warning(f"未找到预期内容: '{check}'")
                all_found = False
        
        if all_found:
            logger.info("测试通过 ✓")
        else:
            logger.warning("测试失败 ✗")
    
    logger.info("所有格式化测试完成")

def test_problem_formatting():
    """测试问题数据格式化功能"""
    
    # 测试问题数据
    test_problem = {
        "id": "test123",
        "question": "计算：$\\sqrt { \\left( 1 - \\sqrt 2 \\right) ^ { 2 } } = $____$.$",
        "correctAnswer": "$1 - \\sqrt{2}$",
        "subject": "数学",
        "grade": "初中",
        "type": "填空题",
        "llmAnswer": "解题步骤：\n1. 计算$\\left( 1 - \\sqrt 2 \\right) ^ { 2 }$\n2. 开方得到$1 - \\sqrt{2}$"
    }
    
    logger.info("测试问题数据格式化")
    logger.debug(f"原始问题数据: {json.dumps(test_problem, ensure_ascii=False)}")
    
    formatted_problem = format_problem_data(test_problem)
    logger.debug(f"格式化后的问题数据: {json.dumps(formatted_problem, ensure_ascii=False)}")
    
    # 验证格式化是否成功
    question_checks = ["√", "1 - √2", "_____"]
    question_success = all(check in formatted_problem["question"] for check in question_checks)
    
    if question_success:
        logger.info("问题文本格式化成功 ✓")
    else:
        logger.warning("问题文本格式化失败 ✗")
    
    if "1 - √2" in formatted_problem["correctAnswer"]:
        logger.info("正确答案格式化成功 ✓")
    else:
        logger.warning("正确答案格式化失败 ✗")
    
    llm_answer_checks = ["解题步骤", "计算", "开方", "√2"]
    llm_answer_success = all(check in formatted_problem["llmAnswer"] for check in llm_answer_checks)
    
    if llm_answer_success:
        logger.info("大模型解答格式化成功 ✓")
    else:
        logger.warning("大模型解答格式化失败 ✗")
    
    logger.info("问题数据格式化测试完成")

def test_real_world_examples():
    """测试真实世界的例子"""
    
    # 真实世界的例子
    real_examples = [
        {
            "name": "复杂数学公式",
            "input": "已知函数$f(x)=\\frac{1}{1+e^{-x}}$，求$f'(x)$。",
            "check_for": ["f(x)", "1/1+e^-x", "f'(x)"]
        },
        {
            "name": "带有多个公式的文本",
            "input": "若$a>0,b>0$，且$\\frac{a}{b}+\\frac{b}{a}=2$，则$a=b$。判断此命题的真假。",
            "check_for": ["a>0", "b>0", "a/b+b/a=2", "a=b", "判断此命题的真假"]
        }
    ]
    
    logger.info("测试真实世界的例子")
    
    # 运行测试
    for i, test in enumerate(real_examples):
        logger.info(f"真实例子 {i+1}: {test['name']}")
        logger.debug(f"输入: {test['input']}")
        
        result = format_latex_for_readability(test['input'])
        logger.debug(f"输出: {result}")
        
        # 检查关键部分是否存在
        all_found = True
        for check in test['check_for']:
            if check not in result and check.replace(" ", "") not in result.replace(" ", ""):
                logger.warning(f"未找到预期内容: '{check}'")
                all_found = False
        
        if all_found:
            logger.info("测试通过 ✓")
        else:
            logger.warning("测试失败 ✗")
    
    logger.info("真实世界例子测试完成")

if __name__ == "__main__":
    logger.info("开始测试文本格式化功能")
    
    # 测试LaTeX格式化
    test_latex_formatting()
    
    # 测试问题数据格式化
    test_problem_formatting()
    
    # 测试真实世界的例子
    test_real_world_examples()
    
    logger.info("所有测试完成") 