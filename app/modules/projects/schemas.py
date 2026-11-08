from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectOrderStatus(str, Enum):
    """Machine-readable status codes; API responses also include Vietnamese labels."""

    PREPARING = "PREPARING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


PROJECT_ORDER_STATUS_LABELS = {
    ProjectOrderStatus.PREPARING: "Chuẩn bị",
    ProjectOrderStatus.IN_PROGRESS: "Đang thực hiện",
    ProjectOrderStatus.COMPLETED: "Hoàn thành",
    ProjectOrderStatus.CANCELLED: "Đã hủy",
}


class _Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class ProjectOrderItemIn(_Base):
    componentId: int = Field(ge=1)
    quantity: int = Field(gt=0, le=1_000_000)


class ProjectOrderCreate(_Base):
    projectName: str = Field(min_length=1, max_length=200)
    customerName: str = Field(min_length=1, max_length=150)
    customerPhone: Optional[str] = Field(None, max_length=30)
    address: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    items: list[ProjectOrderItemIn] = Field(
        min_length=1,
        max_length=100,
        description="Linh kiện và số lượng. Đơn giá được lấy từ danh mục tại thời điểm tạo đơn.",
    )


class ProjectOrderStatusUpdate(_Base):
    status: ProjectOrderStatus = Field(
        description=(
            "PREPARING (Chuẩn bị), IN_PROGRESS (Đang thực hiện), "
            "COMPLETED (Hoàn thành), CANCELLED (Đã hủy)."
        )
    )


class ProjectOrderItemOut(_Base):
    componentId: int
    code: str
    name: str
    unit: str
    unitPrice: int = Field(description="Đơn giá tại thời điểm tạo đơn, VND")
    quantity: int
    subtotal: int = Field(description="unitPrice × quantity, VND")


class ProjectOrderOut(_Base):
    id: int
    projectName: str
    customerName: str
    customerPhone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    items: list[ProjectOrderItemOut]
    totalAmount: int = Field(description="Tổng thành tiền các dòng, VND")
    currency: str
    status: ProjectOrderStatus
    statusLabel: str
    createdAt: str
    updatedAt: str


class ProjectOrderPage(_Base):
    content: list[ProjectOrderOut]
    page: int
    size: int
    totalElements: int
    totalPages: int
