"""
客户 schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CustomerBase(BaseModel):
    """客户基础schema"""
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None

class CustomerCreate(CustomerBase):
    """客户创建schema"""
    agent_id: int
    sales_id: int

class CustomerUpdate(BaseModel):
    """客户更新schema"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    agent_id: Optional[int] = None
    sales_id: Optional[int] = None

class CustomerResponse(CustomerBase):
    """客户响应schema"""
    id: int
    agent_id: int
    sales_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True