# 新增 config.py
import os


class Config:
    STREAMLIT_THEME = "light"
    PAGE_TITLE = "理财经理智能陪练系统"
    PAGE_ICON = "💰"
    LAYOUT = "wide"

    # Qwen API配置
    @property
    def QWEN_API_KEY(self):
        return os.getenv("DASHSCOPE_API_KEY", "sk-f048c8f9134d42058be81012f5cffb23")