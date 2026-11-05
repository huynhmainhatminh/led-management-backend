from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.modules.products.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.modules.products.service import ProductService
from app.common.response import SuccessResponse
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=SuccessResponse[List[ProductResponse]])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ProductService(db)
    products = await service.get_products(skip, limit)
    return SuccessResponse(data=products)


@router.get("/{product_id}", response_model=SuccessResponse[ProductResponse])
async def read_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ProductService(db)
    product = await service.get_product(product_id)
    return SuccessResponse(data=product)


@router.post("/", response_model=SuccessResponse[ProductResponse], status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ProductService(db)
    product = await service.create_product(product_in)
    return SuccessResponse(data=product, message="Product created successfully")


@router.put("/{product_id}", response_model=SuccessResponse[ProductResponse])
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ProductService(db)
    product = await service.update_product(product_id, product_in)
    return SuccessResponse(data=product, message="Product updated successfully")


@router.delete("/{product_id}", response_model=SuccessResponse)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = ProductService(db)
    await service.delete_product(product_id)
    return SuccessResponse(message="Product deleted successfully")
