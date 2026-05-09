"""
库存 schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InventoryBase(BaseModel):
    """库存基础schema"""
    agent_id: int
    product_id: int
    quantity: int

class InventoryCreate(InventoryBase):
    """库存创建schema"""
    pass

class InventoryUpdate(BaseModel):
    """库存更新schema"""
    quantity: int

class InventoryResponse(InventoryBase):
    """库存响应schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InventoryDeduct(BaseModel):
    """库存扣减schema"""
    product_id: int
    quantity: int