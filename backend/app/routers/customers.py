from typing import List
"""
客户管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/customers", tags=["客户管理"])

@router.get("", response_model=List[CustomerResponse])
async def list_customers(
    agent_id: int = None,
    sales_id: int = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取客户列表（可选按代理商/销售筛选）"""
    # 权限控制：客户不能查看客户列表
    if current_user.role == 'customer':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    
    query = db.query(Customer)
    
    if agent_id:
        query = query.filter(Customer.agent_id == agent_id)
    if sales_id:
        query = query.filter(Customer.sales_id == sales_id)
    
    customers = query.offset(skip).limit(limit).all()
    return customers

@router.post("", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """销售添加客户"""
    new_customer = Customer(
        name=customer_data.name,
        phone=customer_data.phone,
        email=customer_data.email,
        agent_id=customer_data.agent_id,
        sales_id=customer_data.sales_id
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取客户详情"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="客户不存在")
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int, 
    customer_data: CustomerUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新客户信息"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="客户不存在")
    
    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    return customer