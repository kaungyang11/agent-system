"""
认证 schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Token(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token数据"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str

class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    password: str
    real_name: Optional[str] = None
    phone: Optional[str] = None