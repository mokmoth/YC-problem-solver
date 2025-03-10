"""
测试图片URL提取功能
"""

import json
import logging
from utils.text_formatter import format_latex_for_readability, format_problem_data

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("image_url_extract_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ImageURLExtractTest")

def test_image_url_extraction():
    """测试图片URL提取功能"""
    
    # 测试用例
    test_cases = [
        {
            "name": "带图片URL的答案",
            "input": "$6$<div><img src=\"https://course.yangcong345.com/pdc/9e532d1a-cd06-45d8-ac38-a59bd497def8.png\" /></div>",
            "expected_contains": ["6", "图片URL", "https://course.yangcong345.com/pdc/9e532d1a-cd06-45d8-ac38-a59bd497def8.png"],
            "expected_not_contains": ["<div>", "<img", "</div>"]
        },
        {
            "name": "纯文本答案",
            "input": "$2+5=7$；$5+2=7$；$7-5=2$；$7-2=5$",
            "expected_contains": ["2 + 5 = 7", "5 + 2 = 7", "7 - 5 = 2", "7 - 2 = 5"],
            "expected_not_contains": ["$"]
        },
        {
            "name": "混合内容",
            "input": "答案是：$6$<div><img src=\"https://example.com/image.jpg\" /></div>解释：$2+4=6$",
            "expected_contains": ["答案是", "6", "图片URL", "https://example.com/image.jpg", "解释"],
            "expected_not_contains": ["<div>", "<img", "</div>"]
        }
    ]
    
    # 运行测试
    for i, test in enumerate(test_cases):
        logger.info(f"测试 {i+1}: {test['name']}")
        logger.debug(f"输入: {test['input']}")
        
        # 创建测试问题数据
        test_problem = {
            "id": f"test{i+1}",
            "question": "测试问题",
            "correctAnswer": test['input'],
            "subject": "数学",
            "grade": "小学",
            "type": "填空题"
        }
        
        # 格式化问题数据
        formatted_problem = format_problem_data(test_problem)
        logger.debug(f"格式化后的正确答案: {formatted_problem['correctAnswer']}")
        
        # 验证结果
        all_found = True
        for expected in test['expected_contains']:
            if expected not in formatted_problem['correctAnswer']:
                logger.warning(f"未找到预期内容: '{expected}'")
                all_found = False
        
        # 验证不应包含的内容
        if 'expected_not_contains' in test:
            for not_expected in test['expected_not_contains']:
                if not_expected in formatted_problem['correctAnswer']:
                    logger.warning(f"找到了不应包含的内容: '{not_expected}'")
                    all_found = False
        
        if all_found:
            logger.info("测试通过 ✓")
        else:
            logger.warning("测试失败 ✗")
    
    logger.info("所有图片URL提取测试完成")

def test_real_world_examples():
    """测试真实世界的例子"""
    
    # 真实世界的例子
    real_examples = [
        {
            "name": "带图片的答案1",
            "input": "$ 6 $<div><img src=\"https://course.yangcong345.com/pdc/9e532d1a-cd06-45d8-ac38-a59bd497def8.png\" /></div>",
            "expected_contains": ["6", "图片URL", "https://course.yangcong345.com/pdc/9e532d1a-cd06-45d8-ac38-a59bd497def8.png"],
            "expected_not_contains": ["<div>", "<img", "</div>"]
        },
        {
            "name": "带图片的答案2",
            "input": "$2$<div><img src=\"https://course.yangcong345.com/pdc/426770f7-3e4c-400f-9fd7-4d89dde1ff83.png\" /></div>",
            "expected_contains": ["2", "图片URL", "https://course.yangcong345.com/pdc/426770f7-3e4c-400f-9fd7-4d89dde1ff83.png"],
            "expected_not_contains": ["<div>", "<img", "</div>"]
        }
    ]
    
    logger.info("测试真实世界的例子")
    
    # 运行测试
    for i, test in enumerate(real_examples):
        logger.info(f"真实例子 {i+1}: {test['name']}")
        logger.debug(f"输入: {test['input']}")
        
        # 创建测试问题数据
        test_problem = {
            "id": f"real{i+1}",
            "question": "测试问题",
            "correctAnswer": test['input'],
            "subject": "数学",
            "grade": "小学",
            "type": "填空题"
        }
        
        # 格式化问题数据
        formatted_problem = format_problem_data(test_problem)
        logger.debug(f"格式化后的正确答案: {formatted_problem['correctAnswer']}")
        
        # 验证结果
        all_found = True
        for expected in test['expected_contains']:
            if expected not in formatted_problem['correctAnswer']:
                logger.warning(f"未找到预期内容: '{expected}'")
                all_found = False
        
        # 验证不应包含的内容
        if 'expected_not_contains' in test:
            for not_expected in test['expected_not_contains']:
                if not_expected in formatted_problem['correctAnswer']:
                    logger.warning(f"找到了不应包含的内容: '{not_expected}'")
                    all_found = False
        
        if all_found:
            logger.info("测试通过 ✓")
        else:
            logger.warning("测试失败 ✗")
    
    logger.info("真实世界例子测试完成")

if __name__ == "__main__":
    logger.info("开始测试图片URL提取功能")
    test_image_url_extraction()
    test_real_world_examples()
    logger.info("所有测试完成") 