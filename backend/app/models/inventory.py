"""
库存模型
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from app.database import Base
from datetime import datetime

class Inventory(Base):
    """代理商库存模型"""
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Inventory(id={self.id}, agent_id={self.agent_id}, product_id={self.product_id}, quantity={self.quantity})>"