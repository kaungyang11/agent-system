from typing import List
"""
代理商政策路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse, AgentBalanceAdjust
from app.routers.auth import get_current_user

router = APIRouter(prefix="/agents", tags=["代理商管理"])

@router.get("")
async def list_agents(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取代理商列表 - 客户不可访问"""
    if current_user.role == 'customer':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    
    agents = db.query(Agent).offset(skip).limit(limit).all()
    return [{"id": a.id, "name": a.name, "contact_person": a.contact_person, "phone": a.phone, "level": a.level, "balance": a.balance} for a in agents]

@router.post("")
async def create_agent(
    agent_data: AgentCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建代理商 - 仅管理员"""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可创建代理商")
    
    new_agent = Agent(
        name=agent_data.name,
        contact_person=agent_data.contact_person,
        phone=agent_data.phone,
        email=agent_data.email,
        address=agent_data.address,
        level=agent_data.level
    )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return {"id": new_agent.id, "name": new_agent.name, "balance": new_agent.balance}

@router.get("/{agent_id}")
async def get_agent(
    agent_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取代理商详情"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="代理商不存在")
    
    # 客户不能查看代理商详情
    if current_user.role == 'customer':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    
    return {"id": agent.id, "name": agent.name, "contact_person": agent.contact_person, "phone": agent.phone, "level": agent.level, "balance": agent.balance}

@router.put("/{agent_id}")
async def update_agent(
    agent_id: int, 
    agent_data: AgentUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新代理商信息 - 仅管理员"""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可修改代理商")
    
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="代理商不存在")
    
    update_data = agent_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    db.commit()
    db.refresh(agent)
    return {"id": agent.id, "name": agent.name, "balance": agent.balance}

@router.get("/{agent_id}/balance")
async def get_agent_balance(
    agent_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """查询代理商余额"""
    # 客户不能查看代理商余额
    if current_user.role == 'customer':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="代理商不存在")
    return {"agent_id": agent.id, "name": agent.name, "balance": agent.balance}

@router.post("/{agent_id}/adjust-balance")
async def adjust_agent_balance(
    agent_id: int, 
    adjust_data: AgentBalanceAdjust, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """调整代理商余额 - 仅管理员"""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可调整余额")
    
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="代理商不存在")
    
    agent.balance += adjust_data.amount
    db.commit()
    db.refresh(agent)
    return {
        "message": "余额调整成功",
        "agent_id": agent.id,
        "new_balance": agent.balance,
        "adjust_amount": adjust_data.amount,
        "reason": adjust_data.reason
    }