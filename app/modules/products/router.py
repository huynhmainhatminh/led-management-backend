# from fastapi import APIRouter, Depends, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List
# from app.db.session import get_db
# from app.modules.products.schemas import ProductCreate, ProductUpdate, ProductResponse
# from app.modules.products.service import ProductService
# from app.common.response import SuccessResponse
# from app.modules.auth.dependencies import get_current_active_user
# from app.modules.auth.models import User
#
# router = APIRouter(prefix="/products", tags=["products"])
#
#
# @router.get("/", response_model=SuccessResponse[List[ProductResponse]])
# async def read_products(
#     skip: int = 0,
#     limit: int = 100,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_active_user)
# ):
#     service = ProductService(db)
#     products = await service.get_products(skip, limit)
#     return SuccessResponse(data=products)
#
#
# @router.get("/{product_id}", response_model=SuccessResponse[ProductResponse])
# async def read_product(
#     product_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_active_user)
# ):
#     service = ProductService(db)
#     product = await service.get_product(product_id)
#     return SuccessResponse(data=product)
#
#
# @router.post("/", response_model=SuccessResponse[ProductResponse], status_code=status.HTTP_201_CREATED)
# async def create_product(
#     product_in: ProductCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_active_user)
# ):
#     service = ProductService(db)
#     product = await service.create_product(product_in)
#     return SuccessResponse(data=product, message="Product created successfully")
#
#
# @router.put("/{product_id}", response_model=SuccessResponse[ProductResponse])
# async def update_product(
#     product_id: int,
#     product_in: ProductUpdate,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_active_user)
# ):
#     service = ProductService(db)
#     product = await service.update_product(product_id, product_in)
#     return SuccessResponse(data=product, message="Product updated successfully")
#
#
# @router.delete("/{product_id}", response_model=SuccessResponse)
# async def delete_product(
#     product_id: int,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_active_user)
# ):
#     service = ProductService(db)
#     await service.delete_product(product_id)
#     return SuccessResponse(message="Product deleted successfully")



# app/modules/products/router.py
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, Response
from app.modules.auth.dependencies import get_current_active_user
from app.common.response import SuccessResponse
from app.modules.products.service import ComponentService
from app.modules.products.schemas import (
    CATEGORY_LABELS, Category, StatusFilter, ComponentIn, ComponentPatch
)

# router = APIRouter(prefix="/components", tags=["Linh kiện"])


router = APIRouter(
    prefix="/components",
    tags=["Linh kiện"],
    dependencies=[Depends(get_current_active_user)],  # Bảo vệ toàn bộ route Linh kiện
)

# Dependency khởi tạo Service từ app.state
def get_component_service(request: Request) -> ComponentService:
    return ComponentService(
        components_repo=request.app.state.components,
        brands_repo=request.app.state.brands,
    )


@router.get("/categories", summary="Danh sách loại linh kiện")
def list_categories():
    return SuccessResponse(data=[{"code": k, "name": v} for k, v in CATEGORY_LABELS.items()])


@router.get("", summary="Danh sách linh kiện (phân trang)")
def list_components(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1, le=100),
    sort: str = "name,asc",
    q: Optional[str] = Query(None, description="Tìm theo mã, tên, model"),
    category: Optional[Category] = None,
    brandId: Optional[int] = None,
    minPrice: Optional[int] = Query(None, ge=0),
    maxPrice: Optional[int] = Query(None, ge=0),
    status: StatusFilter = StatusFilter.ACTIVE,
    service: ComponentService = Depends(get_component_service),
):
    data = service.list_components(
        page=page, size=size, sort=sort, q=q, category=category,
        brand_id=brandId, min_price=minPrice, max_price=maxPrice, status=status
    )
    return SuccessResponse(data=data)


@router.get("/{component_id}", summary="Chi tiết linh kiện")
def get_component(
    component_id: int,
    service: ComponentService = Depends(get_component_service),
):
    return SuccessResponse(data=service.get_component(component_id))


@router.post("", status_code=201, summary="Thêm linh kiện")
def create_component(
    body: ComponentIn,
    service: ComponentService = Depends(get_component_service),
):
    data = service.create_component(body)
    return SuccessResponse(data=data, message="Tạo linh kiện thành công")


@router.put("/{component_id}", summary="Cập nhật toàn bộ linh kiện")
def replace_component(
    component_id: int,
    body: ComponentIn,
    service: ComponentService = Depends(get_component_service),
):
    data = service.replace_component(component_id, body)
    return SuccessResponse(data=data, message="Cập nhật linh kiện thành công")


@router.patch("/{component_id}", summary="Cập nhật một phần linh kiện (kể cả status, đơn giá)")
def patch_component(
    component_id: int,
    body: ComponentPatch,
    service: ComponentService = Depends(get_component_service),
):
    data = service.patch_component(component_id, body)
    return SuccessResponse(data=data, message="Cập nhật linh kiện thành công")


@router.delete("/{component_id}", status_code=204, summary="Xóa mềm linh kiện")
def delete_component(
    component_id: int,
    service: ComponentService = Depends(get_component_service),
):
    service.delete_component(component_id)
    return Response(status_code=204)

