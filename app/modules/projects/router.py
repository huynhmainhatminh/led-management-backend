from typing import Optional

from fastapi import APIRouter, Depends, Query, Request

from app.common.response import SuccessResponse
from app.modules.auth.dependencies import get_current_active_user
from app.modules.projects.schemas import (
    ProjectOrderCreate,
    ProjectOrderOut,
    ProjectOrderPage,
    ProjectOrderStatus,
    ProjectOrderStatusUpdate,
)
from app.modules.projects.service import ProjectOrderService


router = APIRouter(
    prefix="/project-orders",
    tags=["Đơn hàng công trình"],
    dependencies=[Depends(get_current_active_user)],
)


def get_project_order_service(request: Request) -> ProjectOrderService:
    return ProjectOrderService(
        orders_repo=request.app.state.project_orders,
        components_repo=request.app.state.components,
    )


@router.post(
    "",
    status_code=201,
    response_model=SuccessResponse[ProjectOrderOut],
    summary="Tạo đơn hàng công trình và tính tổng tiền",
    description="Tự lấy đơn giá linh kiện đang hoạt động; thành tiền = đơn giá × số lượng; đơn mới ở trạng thái Chuẩn bị.",
)
def create_project_order(
    body: ProjectOrderCreate,
    service: ProjectOrderService = Depends(get_project_order_service),
):
    return SuccessResponse(data=service.create_order(body), message="Tạo đơn hàng công trình thành công")


@router.get(
    "",
    response_model=SuccessResponse[ProjectOrderPage],
    summary="Danh sách đơn hàng công trình",
)
def list_project_orders(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1, le=100),
    status: Optional[ProjectOrderStatus] = None,
    service: ProjectOrderService = Depends(get_project_order_service),
):
    return SuccessResponse(data=service.list_orders(page=page, size=size, status=status))


@router.get(
    "/{order_id}",
    response_model=SuccessResponse[ProjectOrderOut],
    summary="Chi tiết đơn hàng công trình",
)
def get_project_order(
    order_id: int,
    service: ProjectOrderService = Depends(get_project_order_service),
):
    return SuccessResponse(data=service.get_order(order_id))


@router.patch(
    "/{order_id}/status",
    response_model=SuccessResponse[ProjectOrderOut],
    summary="Cập nhật trạng thái đơn hàng",
)
def update_project_order_status(
    order_id: int,
    body: ProjectOrderStatusUpdate,
    service: ProjectOrderService = Depends(get_project_order_service),
):
    return SuccessResponse(
        data=service.update_status(order_id, body.status),
        message="Cập nhật trạng thái đơn hàng thành công",
    )
