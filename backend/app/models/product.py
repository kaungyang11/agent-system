"""
产品模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Float
from app.database import Base
from datetime import datetime

class Product(Base):
    """产品模型"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, index=True)  # 产品编码
    description = Column(String(500))
    lp_price = Column(Float)  # 算能→代理商价
    pdc_price = Column(Float)  # 代理商→客户价(指导价)
    moq = Column(Integer, default=1)  # 最小起订量
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', code='{self.code}')>"