"""
配置管理模块
从环境变量加载配置
"""
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Config:
    """配置类"""

    # API配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'openai/gpt-4o')

    # 翻译设置
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '25'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '5'))

    # 网页抓取
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))

    # 输出文件夹
    WEBPAGES_DIR = 'webpages'
    WORDS_DIR = 'words'
    DOCUMENTS_DIR = 'documents'
    IMAGES_DIR = 'images'

    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY未设置，请在.env文件中配置")
        return True

# 创建配置实例
config = Config()
