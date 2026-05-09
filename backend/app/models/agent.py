"""
代理商模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Float
from app.database import Base
from datetime import datetime

class Agent(Base):
    """代理商模型"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(500))
    level = Column(String(20), default="normal")  # normal/gold/diamond
    balance = Column(Float, default=0.0)  # 余额
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', level='{self.level}')>"