"""
加密工具，用于加密和解密API密钥
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_encryption_key():
    """
    获取加密密钥，如果不存在则创建
    
    返回:
    - 加密密钥
    """
    key_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".encryption_key")
    
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            key = f.read()
    else:
        # 生成一个随机密钥
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
    
    return key

def encrypt_text(text):
    """
    加密文本
    
    参数:
    - text: 要加密的文本
    
    返回:
    - 加密后的文本
    """
    if not text:
        return ""
    
    key = get_encryption_key()
    f = Fernet(key)
    encrypted_text = f.encrypt(text.encode())
    return base64.b64encode(encrypted_text).decode()

def decrypt_text(encrypted_text):
    """
    解密文本
    
    参数:
    - encrypted_text: 加密后的文本
    
    返回:
    - 解密后的文本
    """
    if not encrypted_text:
        return ""
    
    try:
        key = get_encryption_key()
        f = Fernet(key)
        decrypted_text = f.decrypt(base64.b64decode(encrypted_text))
        return decrypted_text.decode()
    except Exception:
        # 如果解密失败，返回空字符串
        return "" 