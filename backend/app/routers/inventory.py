"""
库存管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse, InventoryDeduct
from app.routers.auth import get_current_user

router = APIRouter(prefix="/inventory", tags=["库存管理"])

@router.get("", response_model=list[InventoryResponse])
async def list_inventory(
    agent_id: int = None,
    product_id: int = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取库存列表（可选按代理商/产品筛选）"""
    query = db.query(Inventory)
    
    if agent_id:
        query = query.filter(Inventory.agent_id == agent_id)
    if product_id:
        query = query.filter(Inventory.product_id == product_id)
    
    inventory = query.offset(skip).limit(limit).all()
    return inventory

@router.post("", response_model=InventoryResponse)
async def create_inventory(
    inventory_data: InventoryCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """代理商备货采购（创建/更新库存）"""
    # 检查是否已存在该代理商的该产品库存
    existing = db.query(Inventory).filter(
        and_(
            Inventory.agent_id == inventory_data.agent_id,
            Inventory.product_id == inventory_data.product_id
        )
    ).first()
    
    if existing:
        # 更新库存数量
        existing.quantity += inventory_data.quantity
        db.commit()
        db.refresh(existing)
        return existing
    
    new_inventory = Inventory(
        agent_id=inventory_data.agent_id,
        product_id=inventory_data.product_id,
        quantity=inventory_data.quantity
    )
    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)
    return new_inventory

@router.put("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(
    inventory_id: int, 
    inventory_data: InventoryUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新库存"""
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="库存记录不存在")
    
    inventory.quantity = inventory_data.quantity
    db.commit()
    db.refresh(inventory)
    return inventory

@router.post("/deduct")
async def deduct_inventory(
    agent_id: int,
    deduct_data: InventoryDeduct, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    下单扣减库存（事务性操作）
    """
    # 查找库存记录
    inventory = db.query(Inventory).filter(
        and_(
            Inventory.agent_id == agent_id,
            Inventory.product_id == deduct_data.product_id
        )
    ).first()
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="库存记录不存在"
        )
    
    # 检查库存是否充足
    if inventory.quantity < deduct_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"库存不足，当前库存: {inventory.quantity}，需要: {deduct_data.quantity}"
        )
    
    # 扣减库存（事务性操作）
    inventory.quantity -= deduct_data.quantity
    db.commit()
    db.refresh(inventory)
    
    return {
        "message": "库存扣减成功",
        "inventory_id": inventory.id,
        "product_id": deduct_data.product_id,
        "deducted_quantity": deduct_data.quantity,
        "remaining_quantity": inventory.quantity
    }