"""
统一的日志配置模块，用于所有文件共享
"""

import os
import logging
from logging.handlers import RotatingFileHandler

# 日志文件路径
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
DEBUG_LOG_FILE = os.path.join(LOG_DIR, "auto_problem_solver_debug.log")
INFO_LOG_FILE = os.path.join(LOG_DIR, "auto_problem_solver_info.log")

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 创建处理器
# 调试日志文件处理器（记录所有级别的日志）
debug_file_handler = RotatingFileHandler(
    DEBUG_LOG_FILE,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
debug_file_handler.setLevel(logging.DEBUG)
debug_file_handler.setFormatter(formatter)

# 信息日志文件处理器（只记录INFO及以上级别的日志）
info_file_handler = RotatingFileHandler(
    INFO_LOG_FILE,
    maxBytes=5*1024*1024,  # 5MB
    backupCount=3,
    encoding='utf-8'
)
info_file_handler.setLevel(logging.INFO)
info_file_handler.setFormatter(formatter)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# 配置根日志记录器
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)  # 设置为最低级别，让处理器决定记录哪些日志
root_logger.addHandler(debug_file_handler)
root_logger.addHandler(info_file_handler)
root_logger.addHandler(console_handler)

# 禁用第三方库的过多日志
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("streamlit").setLevel(logging.WARNING)

def get_logger(name):
    """
    获取指定名称的日志记录器
    
    参数:
    - name: 日志记录器名称
    
    返回:
    - 日志记录器
    """
    return logging.getLogger(name) 