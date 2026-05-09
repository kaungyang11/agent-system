"""
产品管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/products", tags=["产品管理"])

@router.get("", response_model=list[ProductResponse])
async def list_products(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取产品列表"""
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@router.post("", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建产品"""
    # 检查产品编码是否已存在
    existing = db.query(Product).filter(Product.code == product_data.code).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="产品编码已存在")
    
    new_product = Product(
        name=product_data.name,
        code=product_data.code,
        description=product_data.description,
        lp_price=product_data.lp_price,
        pdc_price=product_data.pdc_price,
        moq=product_data.moq,
        image_url=product_data.image_url
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取产品详情"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int, 
    product_data: ProductUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新产品"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")
    
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除产品"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")
    
    db.delete(product)
    db.commit()
    return {"message": "删除成功"}