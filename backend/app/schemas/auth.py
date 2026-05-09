"""
认证 schemas
"""
from pydantic import BaseModel
from datetime import datetime

class Token(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token数据"""
    username: str | None = None
    user_id: int | None = None
    role: str | None = None

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str

class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    password: str
    real_name: str | None = None
    phone: str | None = None