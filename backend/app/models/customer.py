"""
客户模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base
from datetime import datetime

class Customer(Base):
    """客户模型"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    agent_id = Column(Integer, ForeignKey("agents.id"))  # 所属代理商
    sales_id = Column(Integer, ForeignKey("users.id"))  # 负责销售
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}')>"