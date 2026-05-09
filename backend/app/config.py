"""
系统配置
"""
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """应用配置"""
    # 数据库
    DATABASE_URL: str = "sqlite:///./data.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    
    # 分页默认配置
    PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()