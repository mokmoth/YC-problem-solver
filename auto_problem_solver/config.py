"""
配置文件，存储API URL和其他配置信息
"""

# 问题API配置
PROBLEM_API_URL = "https://api-test.yangcong345.com/study-course/problem/getDetailProblems"
PROBLEM_API_HEADERS = {"Content-Type": "application/json;charset=utf-8"}

# 火山方舟API配置
ARK_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
ARK_API_MODEL = "ep-20250208102341-sjk9f"  # 默认模型ID，可在前端修改

# 多模态支持配置
ENABLE_MULTIMODAL = True  # 默认启用多模态支持

# 默认提示词模板
DEFAULT_PROMPT_TEMPLATE = """你作为一名专业的<subject>{subject}</subject><grade>{grade}</grade>老师，要解答<type>{type}</type>题目。

题目是：<question>{question}</question>

请按照考试答题标准，给出详细的解题过程，并得出最终答案。在完成解题后，将解得的答案与标准答案<correctAnswers>{correctAnswers}</correctAnswers>进行对比，确保作答正确，如果答案不一致需要重新作答。

【重要】：本题目可能包含图片和选项。如果你看到了图片，请首先详细描述图片中的内容，然后再进行解题。图片可能出现在题目或标准答案中，请仔细观察并利用图片中的信息进行解答。如果你没有看到图片，请明确说明。

如果题目是选择题，请分析每个选项，说明为什么选择或排除该选项。最终答案应该是选项的字母（如A、B、C、D）。

请在<解题>标签内写下详细的解题过程和最终答案，在<对比>标签内说明答案与标准答案对比的情况，是否一致。

<解题>

[在此详细写出解题过程和最终答案]

</解题>

请在<讲解>标签内写下本题考察的{grade}{subject}知识点或考点，以及解题思路。

<讲解>

[在此详细写出本题考察的知识点或考点以及解题思路等等有助于学生理解这道题的信息]

</讲解>

请确保解题过程详细，符合考试答题规范，答案准确。"""

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 2  # 秒

# 并发配置
MAX_WORKERS = 5  # 最大并发数

# 输出配置
OUTPUT_DIR = "auto_problem_solver/output"
DEFAULT_OUTPUT_FILENAME = "problem_solutions.xlsx"