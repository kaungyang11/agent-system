"""
代理商 schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AgentBase(BaseModel):
    """代理商基础schema"""
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    level: str = "normal"

class AgentCreate(AgentBase):
    """代理商创建schema"""
    pass

class AgentUpdate(BaseModel):
    """代理商更新schema"""
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    level: Optional[str] = None

class AgentResponse(AgentBase):
    """代理商响应schema"""
    id: int
    balance: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class AgentBalanceAdjust(BaseModel):
    """代理商余额调整schema"""
    amount: float
    reason: str = "手动调整"