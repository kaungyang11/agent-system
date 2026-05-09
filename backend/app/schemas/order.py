"""
订单 schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrderBase(BaseModel):
    """订单基础schema"""
    customer_id: int
    agent_id: int
    product_id: int
    quantity: int
    unit_price: float

class OrderCreate(OrderBase):
    """订单创建schema"""
    pass

class OrderUpdate(BaseModel):
    """订单更新schema"""
    quantity: Optional[int] = None
    unit_price: Optional[float] = None

class OrderResponse(OrderBase):
    """订单响应schema"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    """订单状态更新schema"""
    status: str  # pending/paid/shipped/completed/cancelled