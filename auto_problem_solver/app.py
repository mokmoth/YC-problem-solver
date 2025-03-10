"""
自动化习题解析批处理工具Web应用
"""

import os
import sys
import json
import time
import logging
import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime

# 导入自定义模块
sys.path.append(os.path.dirname(__file__))
from config import ARK_API_MODEL, DEFAULT_PROMPT_TEMPLATE, MAX_WORKERS
from main import AutoProblemSolver

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auto_problem_solver_debug.log", mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AutoProblemSolver")

# 设置页面配置
st.set_page_config(
    page_title="自动化习题解析批处理工具",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def test_imports():
    """测试所有必要的模块是否可以正确导入"""
    try:
        import os
        import sys
        import json
        import time
        import logging
        import streamlit as st
        from typing import Dict, List, Any, Optional
        
        logging.info("所有必要的模块都已成功导入")
        return True
    except ImportError as e:
        logging.error(f"导入模块时出错: {str(e)}")
        return False

def main():
    """主函数"""
    # 测试导入
    test_imports()
    
    # 设置标题
    st.title("自动化习题解析批处理工具")
    
    # 侧边栏配置
    st.sidebar.header("配置")
    
    # API密钥配置
    api_key = st.sidebar.text_input(
        "火山方舟API密钥", 
        value=st.session_state.persistent_settings.get("api_key", ""),
        type="password", 
        help="输入您的火山方舟API密钥"
    )
    
    # 模型ID配置
    model_id = st.sidebar.text_input(
        "模型ID", 
        value=st.session_state.persistent_settings.get("model_id", ARK_API_MODEL),
        help="输入要使用的模型ID"
    )
    
    # 提示词模板管理
    st.sidebar.subheader("提示词模板管理")
    
    # 初始化提示词模板库
    if "prompt_templates" not in st.session_state:
        # 从持久化设置中加载模板库
        templates = st.session_state.persistent_settings.get("prompt_templates", {})
        if not templates:
            # 如果没有模板库，创建默认模板
            templates = {
                "默认模板": DEFAULT_PROMPT_TEMPLATE
            }
            # 如果有单个模板，将其添加到模板库
            if "prompt_template" in st.session_state.persistent_settings:
                templates["上次使用的模板"] = st.session_state.persistent_settings["prompt_template"]
        st.session_state.prompt_templates = templates
    
    # 如果没有当前选择的模板，设置为第一个模板
    if "current_template_name" not in st.session_state:
        st.session_state.current_template_name = next(iter(st.session_state.prompt_templates.keys()))
    
    # 创建模板选择列表，添加"+ 新建模板"选项
    template_names = list(st.session_state.prompt_templates.keys())
    template_options = template_names + ["+ 新建模板"]
    
    # 模板选择
    selected_option = st.sidebar.selectbox(
        "选择模板",
        template_options,
        index=template_options.index(st.session_state.current_template_name) if st.session_state.current_template_name in template_options else 0
    )
    
    # 自定义默认提示词
    DEFAULT_NEW_TEMPLATE = "你是一位智慧的AI助理，响应用户的各种需求"
    
    # 处理"+ 新建模板"选项
    if selected_option == "+ 新建模板":
        # 显示新建模板的输入框
        new_template_name = st.sidebar.text_input("输入新模板名称", key="new_template_name")
        
        # 显示默认提示词输入框
        new_template_content = st.sidebar.text_area(
            "编辑提示词内容", 
            value=DEFAULT_NEW_TEMPLATE,
            height=200,
            help="编辑新模板的提示词内容"
        )
        
        if st.sidebar.button("创建模板"):
            if new_template_name and new_template_name not in st.session_state.prompt_templates:
                st.session_state.prompt_templates[new_template_name] = new_template_content
                st.session_state.current_template_name = new_template_name
                st.rerun()
            elif not new_template_name:
                st.sidebar.error("请输入模板名称")
            else:
                st.sidebar.error("模板名称已存在")
    else:
        # 更新当前选择的模板
        if selected_option != st.session_state.current_template_name:
            st.session_state.current_template_name = selected_option
    
    # 显示当前选择的模板内容
    if selected_option != "+ 新建模板":
        # 显示当前模板内容编辑区
        prompt_template = st.sidebar.text_area(
            "编辑提示词内容", 
            value=st.session_state.prompt_templates.get(selected_option, DEFAULT_PROMPT_TEMPLATE),
            height=200,
            help="编辑当前选择的提示词模板，可以使用{subject}、{grade}、{type}、{question}、{correctAnswers}等变量"
        )
        
        # 更新模板内容
        if prompt_template != st.session_state.prompt_templates.get(selected_option):
            st.session_state.prompt_templates[selected_option] = prompt_template
        
        # 编辑模板名称和删除模板
        col1, col2 = st.sidebar.columns([3, 1])
        
        with col1:
            new_name = st.text_input("重命名模板", value=selected_option, key="rename_template")
            if new_name != selected_option and st.button("保存名称"):
                if new_name and new_name not in st.session_state.prompt_templates:
                    st.session_state.prompt_templates[new_name] = st.session_state.prompt_templates[selected_option]
                    del st.session_state.prompt_templates[selected_option]
                    st.session_state.current_template_name = new_name
                    st.rerun()
                elif not new_name:
                    st.sidebar.error("请输入模板名称")
                else:
                    st.sidebar.error("模板名称已存在")
        
        with col2:
            if st.button("删除模板"):
                if len(st.session_state.prompt_templates) > 1:
                    del st.session_state.prompt_templates[selected_option]
                    st.session_state.current_template_name = next(iter(st.session_state.prompt_templates.keys()))
                    st.rerun()
                else:
                    st.sidebar.error("至少保留一个模板")
    
    # 并发数配置
    max_workers = st.sidebar.slider(
        "最大并发数", 
        min_value=1, 
        max_value=10, 
        value=st.session_state.persistent_settings.get("max_workers", MAX_WORKERS),
        help="设置最大并发数，越大处理速度越快，但可能会触发API限流"
    )
    
    # 保存设置按钮
    if st.sidebar.button("保存设置"):
        # 确保不是在"+ 新建模板"选项下保存设置
        current_template = selected_option
        if current_template == "+ 新建模板":
            current_template = st.session_state.current_template_name
        
        st.session_state.persistent_settings = {
            "api_key": api_key,
            "model_id": model_id,
            "prompt_template": st.session_state.prompt_templates.get(current_template, DEFAULT_PROMPT_TEMPLATE),
            "prompt_templates": st.session_state.prompt_templates,
            "current_template_name": current_template,
            "max_workers": max_workers
        }
        
        # 保存到磁盘
        try:
            from utils.crypto import encrypt_text
            
            settings_to_save = {
                "model_id": model_id,
                "prompt_template": st.session_state.prompt_templates.get(current_template, DEFAULT_PROMPT_TEMPLATE),
                "prompt_templates": st.session_state.prompt_templates,
                "current_template_name": current_template,
                "max_workers": max_workers
            }
            
            # 加密API密钥
            if api_key:
                settings_to_save["api_key"] = encrypt_text(api_key)
            
            with open("settings.json", "w") as f:
                json.dump(settings_to_save, f)
            
            st.sidebar.success("设置已保存")
        except Exception as e:
            st.sidebar.error(f"保存设置失败: {str(e)}")
    
    # 主界面
    tab1, tab2, tab3, tab4 = st.tabs(["上传文件", "处理进度", "结果查看", "历史记录"])
    
    with tab1:
        st.header("上传问题ID文件")
        
        # 文件格式说明
        st.markdown("""
        ### 文件格式说明
        
        请上传包含问题ID的JSON文件，格式如下：
        
        ```json
        {
            "小学": {
                "数学": ["问题ID1", "问题ID2", ...],
                "语文": ["问题ID1", "问题ID2", ...]
            },
            "初中": {
                "数学": ["问题ID1", "问题ID2", ...],
                "物理": ["问题ID1", "问题ID2", ...]
            }
        }
        ```
        
        其中，外层键为学段（如"小学"、"初中"、"高中"），内层键为学科（如"数学"、"语文"、"物理"），值为问题ID列表。
        """)
        
        # 文件上传
        uploaded_file = st.file_uploader("选择JSON文件", type=["json"])
        
        if uploaded_file is not None:
            st.success("文件上传成功！")
            
            try:
                # 读取文件内容为字符串
                file_content = uploaded_file.getvalue().decode('utf-8')
                logging.info(f"文件大小: {len(file_content)} 字符")
                
                # 保存文件到临时位置
                temp_file_path = "temp_problem_ids.json"
                with open(temp_file_path, "w", encoding="utf-8") as f:
                    f.write(file_content)
                logging.info(f"文件已保存到临时位置: {temp_file_path}")
                
                # 解析JSON
                try:
                    data = json.loads(file_content)
                    logging.info("JSON解析成功")
                    
                    # 显示JSON内容
                    st.json(data)
                    
                    # 计算问题总数
                    total_problems = 0
                    for stage, subjects in data.items():
                        for subject, ids in subjects.items():
                            total_problems += len(ids)
                    
                    logging.info(f"文件包含 {total_problems} 个问题ID")
                    st.info(f"文件包含 {total_problems} 个问题ID")
                    
                    # 启动处理按钮
                    if st.button("开始处理", type="primary"):
                        if not api_key:
                            st.error("请先配置火山方舟API密钥")
                            logging.error("未配置API密钥")
                        else:
                            # 确保不是在"+ 新建模板"选项下启动处理
                            current_template = selected_option
                            if current_template == "+ 新建模板":
                                current_template = st.session_state.current_template_name
                            
                            # 设置会话状态
                            st.session_state.processing = True
                            st.session_state.problem_ids_file = temp_file_path
                            st.session_state.api_key = api_key
                            st.session_state.model_id = model_id
                            st.session_state.prompt_template = st.session_state.prompt_templates.get(current_template, DEFAULT_PROMPT_TEMPLATE)
                            st.session_state.max_workers = max_workers
                            st.session_state.progress = 0
                            st.session_state.total_problems = total_problems
                            st.session_state.export_path = ""
                            
                            logging.info("设置会话状态成功，准备切换到处理进度标签页")
                            
                            # 切换到处理进度标签页
                            st.rerun()
                
                except json.JSONDecodeError as e:
                    logging.error(f"解析JSON文件时出错: {str(e)}")
                    st.error(f"解析JSON文件时出错: {str(e)}")
                    st.error("请确保上传的文件是有效的JSON格式")
            
            except Exception as e:
                logging.error(f"处理文件时出错: {str(e)}")
                st.error(f"处理文件时出错: {str(e)}")
                # 显示更详细的错误信息
                import traceback
                error_details = traceback.format_exc()
                logging.error(f"错误详情: {error_details}")
                st.error("请检查日志获取更多详细信息")
    
    with tab2:
        st.header("处理进度")
        
        if st.session_state.get("processing", False):
            progress_bar = st.progress(0)
            status_text = st.empty()
            error_container = st.empty()
            
            # 创建自动化习题解析批处理工具
            solver = AutoProblemSolver(
                api_key=st.session_state.api_key,
                model_id=st.session_state.model_id,
                prompt_template=st.session_state.prompt_template
            )
            
            # 设置进度回调函数
            def progress_callback(current, total, message=""):
                progress = min(current / total, 1.0) if total > 0 else 0
                progress_bar.progress(progress)
                status_text.text(f"进度: {current}/{total} - {message}")
                
            solver.set_progress_callback(progress_callback)
            
            try:
                # 运行批处理工具
                status_text.text("正在加载问题ID...")
                export_path = solver.run(st.session_state.problem_ids_file, st.session_state.max_workers)
                
                if export_path:
                    progress_bar.progress(100)
                    status_text.text("处理完成！")
                    st.success(f"结果已导出到: {export_path}")
                    
                    # 更新会话状态
                    st.session_state.processing = False
                    st.session_state.export_path = export_path
                    
                    # 添加到历史记录
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    history_item = {
                        "timestamp": timestamp,
                        "export_path": export_path,
                        "total_problems": st.session_state.total_problems,
                        "model_id": st.session_state.model_id,
                        "template_name": st.session_state.current_template_name
                    }
                    st.session_state.history.append(history_item)
                    
                    # 切换到结果查看标签页
                    st.rerun()
                else:
                    progress_bar.progress(100)
                    status_text.text("处理失败！")
                    error_container.error("处理问题时出错，请查看日志")
                    
                    # 更新会话状态
                    st.session_state.processing = False
            except Exception as e:
                progress_bar.progress(100)
                status_text.text("处理出错！")
                error_container.error(f"发生错误: {str(e)}")
                st.session_state.processing = False
        else:
            st.info("请先上传问题ID文件并开始处理")
    
    with tab3:
        st.header("结果查看")
        
        export_path = st.session_state.get("export_path", "")
        if export_path and os.path.exists(export_path):
            st.success(f"结果文件: {export_path}")
            
            # 提供下载链接
            with open(export_path, "rb") as file:
                st.download_button(
                    label="下载Excel文件",
                    data=file,
                    file_name=os.path.basename(export_path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            # 显示结果预览
            try:
                import pandas as pd
                df = pd.read_excel(export_path)
                st.dataframe(df)
            except Exception as e:
                st.error(f"无法预览结果: {str(e)}")
        else:
            st.info("尚未生成结果文件，请先处理问题")
    
    with tab4:
        st.header("历史记录")
        
        if not st.session_state.history:
            st.info("暂无历史记录")
        else:
            for i, item in enumerate(reversed(st.session_state.history)):
                with st.expander(f"运行 {item['timestamp']} - {item['total_problems']} 个问题"):
                    st.write(f"**时间**: {item['timestamp']}")
                    st.write(f"**导出路径**: {item['export_path']}")
                    st.write(f"**问题数量**: {item['total_problems']}")
                    st.write(f"**使用模型**: {item['model_id']}")
                    st.write(f"**使用模板**: {item.get('template_name', '未记录')}")
                    
                    # 提供下载链接
                    if os.path.exists(item['export_path']):
                        with open(item['export_path'], "rb") as file:
                            st.download_button(
                                label="下载Excel文件",
                                data=file,
                                file_name=os.path.basename(item['export_path']),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"download_{i}"
                            )
                        
                        # 显示结果预览
                        try:
                            import pandas as pd
                            df = pd.read_excel(item['export_path'])
                            st.dataframe(df)
                        except Exception as e:
                            st.error(f"无法预览结果: {str(e)}")
                    else:
                        st.error("文件不存在，可能已被删除")
            
            # 清空历史记录按钮
            if st.button("清空历史记录"):
                st.session_state.history = []
                st.rerun()

# 初始化会话状态
if "processing" not in st.session_state:
    st.session_state.processing = False
if "problem_ids_file" not in st.session_state:
    st.session_state.problem_ids_file = ""
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model_id" not in st.session_state:
    st.session_state.model_id = ARK_API_MODEL
if "prompt_template" not in st.session_state:
    st.session_state.prompt_template = DEFAULT_PROMPT_TEMPLATE
if "prompt_templates" not in st.session_state:
    st.session_state.prompt_templates = {"默认模板": DEFAULT_PROMPT_TEMPLATE}
if "current_template_name" not in st.session_state:
    st.session_state.current_template_name = "默认模板"
if "max_workers" not in st.session_state:
    st.session_state.max_workers = MAX_WORKERS
if "progress" not in st.session_state:
    st.session_state.progress = 0
if "total_problems" not in st.session_state:
    st.session_state.total_problems = 0
if "export_path" not in st.session_state:
    st.session_state.export_path = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "persistent_settings" not in st.session_state:
    # 尝试从磁盘加载设置
    try:
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                
                # 解密API密钥
                if "api_key" in settings:
                    try:
                        from utils.crypto import decrypt_text
                        settings["api_key"] = decrypt_text(settings["api_key"])
                    except Exception as e:
                        logging.error(f"解密API密钥失败: {str(e)}")
                        settings["api_key"] = ""
                
                st.session_state.persistent_settings = settings
        else:
            st.session_state.persistent_settings = {}
    except Exception as e:
        logging.error(f"加载设置失败: {str(e)}")
        st.session_state.persistent_settings = {}

if __name__ == "__main__":
    main() 