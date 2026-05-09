"""
业绩管理路由
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.performance import Performance
from app.models.agent import Agent
from app.schemas.performance import PerformanceCreate, PerformanceResponse, PerformanceApprove, PerformanceSettle
from app.routers.auth import get_current_user
from app.routers.orders import calculate_reward

router = APIRouter(prefix="/performance", tags=["业绩管理"])

@router.get("", response_model=list[PerformanceResponse])
async def list_performance(
    sales_id: int = None,
    agent_id: int = None,
    status: str = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取业绩记录列表"""
    query = db.query(Performance)
    
    if sales_id:
        query = query.filter(Performance.sales_id == sales_id)
    if agent_id:
        query = query.filter(Performance.agent_id == agent_id)
    if status:
        query = query.filter(Performance.status == status)
    
    performance = query.offset(skip).limit(limit).all()
    return performance

@router.post("", response_model=PerformanceResponse)
async def create_performance(
    performance_data: PerformanceCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建业绩记录"""
    # 如果没有提供奖励金额，自动计算
    if performance_data.reward_amount == 0:
        performance_data.reward_amount = calculate_reward(
            performance_data.quantity,
            performance_data.lp_price,
            performance_data.pdc_price
        )
    
    # 处理凭证图片JSON
    proof_images_json = json.dumps(performance_data.proof_images) if performance_data.proof_images else None
    
    new_performance = Performance(
        order_id=performance_data.order_id,
        sales_id=performance_data.sales_id,
        agent_id=performance_data.agent_id,
        customer_id=performance_data.customer_id,
        product_id=performance_data.product_id,
        quantity=performance_data.quantity,
        lp_price=performance_data.lp_price,
        pdc_price=performance_data.pdc_price,
        reward_amount=performance_data.reward_amount,
        proof_images=proof_images_json,
        status="pending"
    )
    db.add(new_performance)
    db.commit()
    db.refresh(new_performance)
    return new_performance

@router.get("/{performance_id}", response_model=PerformanceResponse)
async def get_performance(
    performance_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取业绩记录详情"""
    performance = db.query(Performance).filter(Performance.id == performance_id).first()
    if not performance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="业绩记录不存在")
    return performance

@router.put("/{performance_id}/approve")
async def approve_performance(
    performance_id: int, 
    approve_data: PerformanceApprove, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """审核业绩（通过/拒绝）"""
    performance = db.query(Performance).filter(Performance.id == performance_id).first()
    if not performance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="业绩记录不存在")
    
    if approve_data.approved:
        performance.status = "approved"
        message = "业绩审核通过"
    else:
        performance.status = "rejected"
        message = "业绩审核拒绝"
    
    db.commit()
    db.refresh(performance)
    
    return {
        "message": message,
        "performance_id": performance.id,
        "status": performance.status,
        "reward_amount": performance.reward_amount
    }

@router.put("/{performance_id}/reject")
async def reject_performance(
    performance_id: int,
    remark: str = Query(None, description="拒绝原因"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """审核业绩拒绝"""
    performance = db.query(Performance).filter(Performance.id == performance_id).first()
    if not performance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="业绩记录不存在")

    performance.status = "rejected"
    db.commit()
    db.refresh(performance)

    return {
        "message": "业绩审核拒绝",
        "performance_id": performance.id,
        "status": performance.status,
        "remark": remark
    }

@router.post("/{performance_id}/settle")
async def settle_performance(
    performance_id: int,
    settle_data: PerformanceSettle,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    确认发放业绩到代理商余额
    流程：审核通过(approved) → 管理员确认发放 → 余额增加
    """
    # 验证管理员权限
    if current_user.role not in ['admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可发放业绩")
    
    # 获取业绩记录
    performance = db.query(Performance).filter(Performance.id == performance_id).first()
    if not performance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="业绩记录不存在")
    
    # 检查状态：必须是已审核通过且未发放
    if performance.status != "approved":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该业绩未通过审核，无法发放")
    
    if performance.settled == 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该业绩已发放")
    
    # 获取代理商
    agent = db.query(Agent).filter(Agent.id == performance.agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="代理商不存在")
    
    # 发放奖励：增加代理商余额
    agent.balance += performance.reward_amount
    
    # 更新业绩状态为已发放
    performance.settled = 1
    
    db.commit()
    db.refresh(agent)
    db.refresh(performance)
    
    return {
        "message": "业绩已发放到代理商账户",
        "performance_id": performance.id,
        "agent_id": agent.id,
        "agent_name": agent.name,
        "reward_amount": performance.reward_amount,
        "new_balance": agent.balance,
        "settled": True
    }