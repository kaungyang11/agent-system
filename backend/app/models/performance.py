"""
业绩模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from app.database import Base
from datetime import datetime

class Performance(Base):
    """业绩记录模型"""
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    sales_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    lp_price = Column(Float, nullable=False)  # 算能→代理商价
    pdc_price = Column(Float, nullable=False)  # 代理商→客户价
    reward_amount = Column(Float, default=0.0)  # 奖励金额
    proof_images = Column(String(500))  # 合同/付款/发货凭证(JSON数组)
    status = Column(String(20), default="pending")  # pending/approved/rejected
    settled = Column(Integer, default=0)  # 0=未发放, 1=已发放
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Performance(id={self.id}, status='{self.status}', settled={self.settled}, reward_amount={self.reward_amount})>"