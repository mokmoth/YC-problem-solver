"""
测试LLM输出格式化功能
"""

import json
import logging
from utils.text_formatter import format_latex_for_readability

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("llm_output_format_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LLMOutputFormatTest")

def test_llm_output_format():
    """测试LLM输出格式化功能"""
    
    # 测试用例
    test_cases = [
        {
            "name": "带转义符的LLM输出",
            "input": """本题可根据自然数的顺序和大小关系来找出比\\(7\\)大且比\\(9\\)小的数。

### 步骤一：明确自然数的概念和顺序
自然数是用以计量事物的件数或表示事物次序的数，即用数码\\(0\\)，\\(1\\)，\\(2\\)，\\(3\\)，\\(4\\cdots\\cdots\\)所表示的数。按照从小到大的顺序，常见的自然数依次为\\(0\\)、\\(1\\)、\\(2\\)、\\(3\\)、\\(4\\)、\\(5\\)、\\(6\\)、\\(7\\)、\\(8\\)、\\(9\\)、\\(10\\cdots\\cdots\\) 。

### 步骤二：找出符合条件的数
从上述自然数的顺序中可以看出，比\\(7\\)大的数依次有\\(8\\)、\\(9\\)、\\(10\\cdots\\cdots\\)，比\\(9\\)小的数依次有\\(8\\)、\\(7\\)、\\(6\\cdots\\cdots\\) 。
那么同时满足比\\(7\\)大且比\\(9\\)小这两个条件的数只有\\(8\\)。

综上，横线处应填\\(8\\)。""",
            "expected_contains": ["比7大且比9小的数", "自然数依次为0、1、2、3、4、5、6、7、8、9", "横线处应填8"],
            "expected_not_contains": ["\\(7\\)", "\\(8\\)", "\\(9\\)", "\\cdots"]
        },
        {
            "name": "带LaTeX公式的LLM输出",
            "input": """解题步骤：
1. 计算$\\left( 1 - \\sqrt 2 \\right) ^ { 2 }$
2. 开方得到$1 - \\sqrt{2}$""",
            "expected_contains": ["计算", "1 - √2", "开方得到"],
            "expected_not_contains": ["$", "\\sqrt", "\\left", "\\right"]
        }
    ]
    
    # 运行测试
    for i, test in enumerate(test_cases):
        logger.info(f"测试 {i+1}: {test['name']}")
        logger.debug(f"输入: {test['input']}")
        
        # 格式化LLM输出
        formatted_output = format_latex_for_readability(test['input'])
        logger.debug(f"格式化后的输出: {formatted_output}")
        
        # 验证结果
        all_found = True
        for expected in test['expected_contains']:
            if expected not in formatted_output:
                # 检查是否有空格差异
                if expected.replace(" ", "") in formatted_output.replace(" ", ""):
                    logger.info(f"找到预期内容(忽略空格): '{expected}'")
                else:
                    logger.warning(f"未找到预期内容: '{expected}'")
                    all_found = False
        
        # 验证不应包含的内容
        if 'expected_not_contains' in test:
            for not_expected in test['expected_not_contains']:
                if not_expected in formatted_output:
                    logger.warning(f"找到了不应包含的内容: '{not_expected}'")
                    all_found = False
        
        if all_found:
            logger.info("测试通过 ✓")
        else:
            logger.warning("测试失败 ✗")
    
    logger.info("所有LLM输出格式化测试完成")

def test_real_world_examples():
    """测试真实世界的例子"""
    
    # 真实世界的例子
    real_examples = [
        {
            "name": "真实LLM输出1",
            "input": """本题可根据自然数的顺序和大小关系来找出比\\(7\\)大且比\\(9\\)小的数。

### 步骤一：明确自然数的概念和顺序
自然数是用以计量事物的件数或表示事物次序的数，即用数码\\(0\\)，\\(1\\)，\\(2\\)，\\(3\\)，\\(4\\cdots\\cdots\\)所表示的数。按照从小到大的顺序，常见的自然数依次为\\(0\\)、\\(1\\)、\\(2\\)、\\(3\\)、\\(4\\)、\\(5\\)、\\(6\\)、\\(7\\)、\\(8\\)、\\(9\\)、\\(10\\cdots\\cdots\\) 。

### 步骤二：找出符合条件的数
从上述自然数的顺序中可以看出，比\\(7\\)大的数依次有\\(8\\)、\\(9\\)、\\(10\\cdots\\cdots\\)，比\\(9\\)小的数依次有\\(8\\)、\\(7\\)、\\(6\\cdots\\cdots\\) 。
那么同时满足比\\(7\\)大且比\\(9\\)小这两个条件的数只有\\(8\\)。

综上，横线处应填\\(8\\)。""",
            "expected_contains": ["比7大且比9小的数", "常见的自然数依次为0、1、2、3、4、5、6、7、8、9", "横线处应填8"],
            "expected_not_contains": ["\\(7\\)", "\\(8\\)", "\\(9\\)", "\\cdots"]
        },
        {
            "name": "真实LLM输出2",
            "input": """这道题目要求我们根据加减法算式中各部分的关系来求解。

### 分析题目
题目给出了算式 _____ - 5 = 4，我们需要求出横线处应填的数。

### 解题步骤
1. 根据减法的意义，被减数减去减数等于差。
2. 在这个算式中，被减数是横线处的数，减数是5，差是4。
3. 要求被减数，可以用差加上减数，即：被减数 = 差 + 减数。
4. 代入数值：被减数 = 4 + 5 = 9。

### 答案
所以，横线处应填数字9。

### 验证
9 - 5 = 4 ✓

因此，_____ - 5 = 4 中，横线处应填9。""",
            "expected_contains": ["被减数减去减数等于差", "被减数 = 差 + 减数", "被减数 = 4 + 5 = 9", "横线处应填9"],
            "expected_not_contains": ["\\(", "\\)"]
        }
    ]
    
    logger.info("测试真实世界的例子")
    
    # 运行测试
    for i, test in enumerate(real_examples):
        logger.info(f"真实例子 {i+1}: {test['name']}")
        logger.debug(f"输入: {test['input']}")
        
        # 格式化LLM输出
        formatted_output = format_latex_for_readability(test['input'])
        logger.debug(f"格式化后的输出: {formatted_output}")
        
        # 验证结果
        all_found = True
        for expected in test['expected_contains']:
            if expected not in formatted_output:
                # 检查是否有空格差异
                if expected.replace(" ", "") in formatted_output.replace(" ", ""):
                    logger.info(f"找到预期内容(忽略空格): '{expected}'")
                else:
                    logger.warning(f"未找到预期内容: '{expected}'")
                    all_found = False
        
        # 验证不应包含的内容
        if 'expected_not_contains' in test:
            for not_expected in test['expected_not_contains']:
                if not_expected in formatted_output:
                    logger.warning(f"找到了不应包含的内容: '{not_expected}'")
                    all_found = False
        
        if all_found:
            logger.info("测试通过 ✓")
        else:
            logger.warning("测试失败 ✗")
    
    logger.info("真实世界例子测试完成")

if __name__ == "__main__":
    logger.info("开始测试LLM输出格式化功能")
    test_llm_output_format()
    test_real_world_examples()
    logger.info("所有测试完成") 