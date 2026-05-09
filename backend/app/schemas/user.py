"""
用户 schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """用户基础schema"""
    username: str
    real_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    """用户创建schema"""
    password: str
    role: str = "sales"

class UserUpdate(BaseModel):
    """用户更新schema"""
    real_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None

class UserResponse(UserBase):
    """用户响应schema"""
    id: int
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True