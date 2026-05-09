"""
业绩 schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PerformanceBase(BaseModel):
    """业绩基础schema"""
    order_id: int
    sales_id: int
    agent_id: int
    customer_id: int
    product_id: int
    quantity: int
    lp_price: float
    pdc_price: float
    reward_amount: float
    proof_images: Optional[List[str]] = None

class PerformanceCreate(PerformanceBase):
    """业绩创建schema"""
    pass

class PerformanceResponse(PerformanceBase):
    """业绩响应schema"""
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PerformanceApprove(BaseModel):
    """业绩审核schema"""
    approved: bool
    remark: Optional[str] = None

class PerformanceSettle(BaseModel):
    """业绩发放确认schema"""
    """管理员确认发放业绩到代理商余额"""
    remark: Optional[str] = None