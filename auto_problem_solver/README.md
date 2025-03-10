# 自动化习题解析批处理工具

这是一个自动化批处理工具，用于从API批量获取习题信息，并使用大语言模型（火山方舟API）进行解题，最终将结果导出为Excel表格。

## 功能特点

- 从API批量获取习题数据（题干、正确答案、学科、学段、题目类型、ID）
- 使用火山方舟大模型API对习题进行解答
- 支持自定义提示词模板
- 并发处理，提高效率
- 结果导出为Excel表格
- 提供命令行和Web界面两种使用方式

## 安装

1. 克隆仓库：

```bash
git clone <repository-url>
cd auto_problem_solver
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 设置火山方舟API密钥：

```bash
export ARK_API_KEY="YOUR_API_KEY"
```

## 使用方法

### 命令行方式

```bash
python main.py --problem-ids-file data/problem_ids.json
```

可选参数：

- `--api-key`: 火山方舟API密钥（如果未在环境变量中设置）
- `--model-id`: 要使用的模型ID
- `--prompt-template`: 自定义提示词模板
- `--max-workers`: 最大并发数

### Web界面方式

```bash
streamlit run app.py
```

然后在浏览器中打开显示的URL（通常是 http://localhost:8501）。

## 输入文件格式

问题ID文件应为JSON格式，结构如下：

```json
{
  "小学": {
    "数学": ["problem_id_1", "problem_id_2"],
    "语文": ["problem_id_3", "problem_id_4"]
  },
  "初中": {
    "数学": ["problem_id_5", "problem_id_6"],
    "物理": ["problem_id_7", "problem_id_8"]
  }
}
```

## 输出格式

输出为Excel表格，包含以下列：

- 题目ID
- 题目题干（question）
- 题目正确答案（correctAnswer）
- 题目学科（subject）
- 题目年级（grade）
- 题目类型（type）
- 大模型解题内容（llmAnswer）

## 项目结构

```
auto_problem_solver/
├── config.py                # 配置文件
├── main.py                  # 命令行主程序
├── app.py                   # Web界面
├── models/
│   ├── problem_fetcher.py   # 问题数据获取模块
│   └── llm_solver.py        # 大模型交互模块
├── utils/
│   └── data_exporter.py     # 数据处理和导出模块
├── data/                    # 数据目录
└── output/                  # 输出目录
```

## 自定义提示词模板

提示词模板支持以下变量：

- `{subject}`: 学科
- `{grade}`: 年级
- `{type}`: 题目类型
- `{question}`: 题目内容

默认模板：

```
请你作为一名专业的{subject}{grade}老师，解答下面的{type}题目。
题目：{question}
请给出详细的解题过程和最终答案。
```

## 注意事项

- 确保网络连接稳定，以便与API通信
- 大量并发请求可能导致API限流，请适当调整并发数
- 处理大量题目可能需要较长时间，请耐心等待

## 许可证

[MIT License](LICENSE) 