# 自动化习题解析批处理工具

这是一个自动化批处理工具，用于从API批量获取习题信息，并使用大语言模型（火山方舟API）进行解题，最终将结果导出为Excel表格。

## 功能特点

- 从API批量获取习题数据（题干、正确答案、学科、学段、题目类型、ID）
- 使用火山方舟大模型API对习题进行解答
- 支持多提示词模板管理，可以存储和切换不同的提示词模板
- 并发处理，提高效率
- 结果导出为Excel表格
- 历史记录功能，保存所有处理结果
- 提供Web界面，操作简单直观

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/auto-problem-solver.git
cd auto-problem-solver
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 设置火山方舟API密钥（可选，也可以在Web界面中设置）：

```bash
export ARK_API_KEY="YOUR_API_KEY"
```

## 使用方法

### Web界面方式

```bash
cd auto_problem_solver
streamlit run app.py
```

然后在浏览器中打开显示的URL（通常是 http://localhost:8501）。

### 命令行方式

```bash
python main.py --problem-ids-file data/problem_ids.json
```

可选参数：

- `--api-key`: 火山方舟API密钥（如果未在环境变量中设置）
- `--model-id`: 要使用的模型ID
- `--prompt-template`: 自定义提示词模板
- `--max-workers`: 最大并发数

## Web界面使用指南

1. **配置设置**：
   - 在侧边栏设置火山方舟API密钥
   - 选择或创建提示词模板
   - 设置模型ID和并发数

2. **上传文件**：
   - 上传包含问题ID的JSON文件
   - 查看解析后的问题ID数量

3. **处理问题**：
   - 点击"开始处理"按钮
   - 在"处理进度"标签页查看实时进度

4. **查看结果**：
   - 在"结果查看"标签页查看和下载Excel文件
   - 在"历史记录"标签页查看所有历史处理记录

## 提示词模板管理

- **选择模板**：从下拉列表中选择已保存的模板
- **创建模板**：选择"+ 新建模板"，输入名称和内容
- **编辑模板**：直接在文本区域编辑当前模板内容
- **重命名模板**：输入新名称并点击"保存名称"
- **删除模板**：点击"删除模板"按钮

提示词模板支持以下变量：
- `{subject}`: 学科
- `{grade}`: 年级
- `{type}`: 题目类型
- `{question}`: 题目内容
- `{correctAnswers}`: 正确答案

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
│   ├── data_exporter.py     # 数据处理和导出模块
│   ├── text_formatter.py    # 文本格式化工具
│   └── crypto.py            # 加密工具
├── output/                  # 输出目录
└── settings.json            # 设置文件（自动生成）
```

## 注意事项

- 确保网络连接稳定，以便与API通信
- 大量并发请求可能导致API限流，请适当调整并发数
- 处理大量题目可能需要较长时间，请耐心等待
- API密钥会加密保存在本地，但仍建议妥善保管

## 许可证

[MIT License](LICENSE) 