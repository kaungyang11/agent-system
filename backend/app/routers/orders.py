from typing import List
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

@router.get("")
async def list_orders(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取订单列表（包含客户和产品名称）"""
    from app.models.customer import Customer
    from app.models.product import Product
    
    orders = db.query(Order).offset(skip).limit(limit).all()
    
    # 构建返回数据，包含名称
    result = []
    for order in orders:
        customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
        product = db.query(Product).filter(Product.id == order.product_id).first()
        result.append({
            "id": order.id,
            "order_no": f"ORD{order.id:06d}",
            "customer_id": order.customer_id,
            "customer_name": customer.name if customer else "",
            "product_id": order.product_id,
            "product_name": product.name if product else "",
            "quantity": order.quantity,
            "price": order.unit_price,
            "status": order.status,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else "",
            "agent_id": order.agent_id,
        })
    return result

@router.get("/agent/{agent_id}", response_model=List[OrderResponse])
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

@router.post("")
async def create_order(
    order_data: OrderCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建订单（客户下单，自动扣减库存）
    """
    from app.models.customer import Customer
    from app.models.product import Product
    
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
    
    # 返回创建的数据
    customer = db.query(Customer).filter(Customer.id == order_data.customer_id).first()
    product = db.query(Product).filter(Product.id == order_data.product_id).first()
    return {
        "id": new_order.id,
        "order_no": f"ORD{new_order.id:06d}",
        "customer_id": new_order.customer_id,
        "customer_name": customer.name if customer else "",
        "product_id": new_order.product_id,
        "product_name": product.name if product else "",
        "quantity": new_order.quantity,
        "price": new_order.unit_price,
        "status": new_order.status,
        "created_at": new_order.created_at.strftime("%Y-%m-%d %H:%M:%S") if new_order.created_at else "",
        "agent_id": new_order.agent_id,
    }

@router.get("/{order_id}")
async def get_order(
    order_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取订单详情"""
    from app.models.customer import Customer
    from app.models.product import Product
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    product = db.query(Product).filter(Product.id == order.product_id).first()
    return {
        "id": order.id,
        "order_no": f"ORD{order.id:06d}",
        "customer_id": order.customer_id,
        "customer_name": customer.name if customer else "",
        "product_id": order.product_id,
        "product_name": product.name if product else "",
        "quantity": order.quantity,
        "price": order.unit_price,
        "status": order.status,
        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else "",
        "agent_id": order.agent_id,
    }

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新订单状态"""
    from app.models.customer import Customer
    from app.models.product import Product
    
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
    
    # 返回更新后的数据
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    product = db.query(Product).filter(Product.id == order.product_id).first()
    return {
        "id": order.id,
        "order_no": f"ORD{order.id:06d}",
        "customer_id": order.customer_id,
        "customer_name": customer.name if customer else "",
        "product_id": order.product_id,
        "product_name": product.name if product else "",
        "quantity": order.quantity,
        "price": order.unit_price,
        "status": order.status,
        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else "",
        "agent_id": order.agent_id,
    }