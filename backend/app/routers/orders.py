"""
订单管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List

from app.database import get_db
from app.models.order import Order
from app.models.inventory import Inventory
from app.models.performance import Performance
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderStatusUpdate
from app.routers.auth import get_current_user
from app.routers.inventory import deduct_inventory

router = APIRouter(prefix="/orders", tags=["订单管理"])

def calculate_reward(quantity: int, lp_price: float, pdc_price: float) -> float:
    """
    计算奖励金额
    公式: quantity * (lp_price - 0.9 * pdc_price)
    """
    return quantity * (lp_price - 0.9 * pdc_price)

@router.get("", response_model=list[OrderResponse])
async def list_orders(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取订单列表"""
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders

@router.get("/agent/{agent_id}", response_model=list[OrderResponse])
async def get_agent_orders(
    agent_id: int,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取代理商的订单列表"""
    orders = db.query(Order).filter(Order.agent_id == agent_id).offset(skip).limit(limit).all()
    return orders

@router.post("", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建订单（客户下单，自动扣减库存）
    """
    # 检查库存是否充足
    inventory = db.query(Inventory).filter(
        and_(
            Inventory.agent_id == order_data.agent_id,
            Inventory.product_id == order_data.product_id
        )
    ).first()
    
    if not inventory or inventory.quantity < order_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="库存不足，无法下单"
        )
    
    # 创建订单
    new_order = Order(
        customer_id=order_data.customer_id,
        agent_id=order_data.agent_id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        unit_price=order_data.unit_price,
        status="pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # 扣减库存（事务性）
    inventory.quantity -= order_data.quantity
    db.commit()
    
    return new_order

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取订单详情"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return order

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新订单状态"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

    valid_statuses = ["pending", "paid", "shipped", "completed", "cancelled"]
    if status_data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效状态，支持: {valid_statuses}"
        )

    # 如果取消订单，恢复库存
    if status_data.status == "cancelled" and order.status != "cancelled":
        inventory = db.query(Inventory).filter(
            and_(
                Inventory.agent_id == order.agent_id,
                Inventory.product_id == order.product_id
            )
        ).first()

        if inventory:
            inventory.quantity += order.quantity
            db.commit()

    order.status = status_data.status
    db.commit()
    db.refresh(order)
    return order