"""
订单模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from app.database import Base
from datetime import datetime

class Order(Base):
    """订单模型"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending/paid/shipped/completed/cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Order(id={self.id}, status='{self.status}', quantity={self.quantity})>"