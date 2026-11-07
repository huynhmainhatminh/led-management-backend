# app/modules/suppliers/router.py
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, Response
from app.modules.auth.dependencies import get_current_active_user
from app.common.response import SuccessResponse
from app.modules.products.schemas import Category
from app.modules.suppliers.schemas import BrandIn, BrandPatch, StatusFilter
from app.modules.suppliers.service import BrandService

# router = APIRouter(prefix="/brands", tags=["Thương hiệu"])
router = APIRouter(
    prefix="/brands",
    tags=["Thương hiệu"],
    dependencies=[Depends(get_current_active_user)],  # Bảo vệ toàn bộ route Thương hiệu
)

def get_brand_service(request: Request) -> BrandService:
    return BrandService(
        brands_repo=request.app.state.brands,
        components_repo=request.app.state.components,
    )


@router.get("", summary="Danh sách thương hiệu (phân trang)")
def list_brands(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1, le=100),
    sort: str = "name,asc",
    q: Optional[str] = Query(None, description="Tìm theo mã, tên, quốc gia"),
    category: Optional[Category] = Query(None, description="Chỉ thương hiệu có linh kiện thuộc loại này"),
    status: StatusFilter = StatusFilter.ACTIVE,
    service: BrandService = Depends(get_brand_service),
):
    data = service.list_brands(
        page=page, size=size, sort=sort, q=q, category=category, status=status
    )
    return SuccessResponse(data=data)


@router.get("/{brand_id}", summary="Chi tiết thương hiệu")
def get_brand(
    brand_id: int,
    service: BrandService = Depends(get_brand_service),
):
    return SuccessResponse(data=service.get_brand(brand_id))


@router.post("", status_code=201, summary="Thêm thương hiệu")
def create_brand(
    body: BrandIn,
    service: BrandService = Depends(get_brand_service),
):
    record = service.create_brand(body)
    return SuccessResponse(data=record, message="Tạo thương hiệu thành công")


@router.put("/{brand_id}", summary="Cập nhật toàn bộ thương hiệu")
def replace_brand(
    brand_id: int,
    body: BrandIn,
    service: BrandService = Depends(get_brand_service),
):
    record = service.replace_brand(brand_id, body)
    return SuccessResponse(data=record, message="Cập nhật thương hiệu thành công")


@router.patch("/{brand_id}", summary="Cập nhật một phần thương hiệu (kể cả status)")
def patch_brand(
    brand_id: int,
    body: BrandPatch,
    service: BrandService = Depends(get_brand_service),
):
    record = service.patch_brand(brand_id, body)
    return SuccessResponse(data=record, message="Cập nhật thương hiệu thành công")


@router.delete("/{brand_id}", status_code=204, summary="Xóa mềm thương hiệu")
def delete_brand(
    brand_id: int,
    service: BrandService = Depends(get_brand_service),
):
    service.delete_brand(brand_id)
    return Response(status_code=204)