"""
产品 schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProductBase(BaseModel):
    """产品基础schema"""
    name: str
    description: Optional[str] = None
    lp_price: float
    pdc_price: float
    moq: int = 1

class ProductCreate(ProductBase):
    """产品创建schema"""
    code: str
    image_url: Optional[str] = None

class ProductUpdate(BaseModel):
    """产品更新schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    lp_price: Optional[float] = None
    pdc_price: Optional[float] = None
    moq: Optional[int] = None
    image_url: Optional[str] = None

class ProductResponse(ProductBase):
    """产品响应schema"""
    id: int
    code: str
    image_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True