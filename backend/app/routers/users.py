from typing import List
"""
用户管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.routers.auth import get_current_user, get_password_hash

router = APIRouter(prefix="/users", tags=["用户管理"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("")
async def list_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户列表 - 仅管理员和销售可访问"""
    # 权限控制：代理商和客户不能查看用户列表
    if current_user.role in ['agent', 'customer']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    
    users = db.query(User).offset(skip).limit(limit).all()
    
    # 返回简化数据（不包含密码）
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "real_name": u.real_name,
            "phone": u.phone,
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else ""
        })
    return result

@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建用户（仅管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可以创建用户")
    
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        real_name=user_data.real_name,
        phone=user_data.phone,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, 
    user_data: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    
    # 只能管理员修改其他用户，或用户修改自己的信息
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改此用户")
    
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除用户（仅管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可以删除用户")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    return {"message": "删除成功"}