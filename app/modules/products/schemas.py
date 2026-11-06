from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Status(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class StatusFilter(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ALL = "ALL"


class Category(str, Enum):
    LED_CHIP = "LED_CHIP"
    LED_MODULE = "LED_MODULE"
    SENDING_CARD = "SENDING_CARD"
    RECEIVING_CARD = "RECEIVING_CARD"
    VIDEO_PROCESSOR = "VIDEO_PROCESSOR"
    POWER_SUPPLY = "POWER_SUPPLY"
    CABINET = "CABINET"
    OTHER = "OTHER"


CATEGORY_LABELS = {
    "LED_CHIP": "Chip LED, bóng LED RGB",
    "LED_MODULE": "Module LED",
    "SENDING_CARD": "Card phát",
    "RECEIVING_CARD": "Card nhận",
    "VIDEO_PROCESSOR": "Bộ xử lý hình ảnh",
    "POWER_SUPPLY": "Bộ nguồn DC",
    "CABINET": "Cabinet / khung",
    "OTHER": "Cáp, phụ kiện, vật tư khác",
}


def _upper_code(v):
    if v is None:
        return v
    v = v.strip().upper()
    if not v:
        raise ValueError("code không được rỗng")
    return v


def _check_url(v):
    if v is None or v == "":
        return None
    if not v.startswith(("http://", "https://")):
        raise ValueError("website phải bắt đầu bằng http:// hoặc https://")
    return v


class _Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class ComponentIn(_Base):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    category: Category
    brandId: int = Field(ge=1)
    model: Optional[str] = Field(None, max_length=100)
    unit: str = Field(min_length=1, max_length=30)
    unitPrice: int = Field(ge=0, description="Đơn giá, VND")
    specs: dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = Field(None, max_length=500)

    _code = field_validator("code")(_upper_code)


class ComponentPatch(_Base):
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    category: Optional[Category] = None
    brandId: Optional[int] = Field(None, ge=1)
    model: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, min_length=1, max_length=30)
    unitPrice: Optional[int] = Field(None, ge=0)
    specs: Optional[dict[str, Any]] = None
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[Status] = None

    _code = field_validator("code")(_upper_code)


COMPONENT_REQUIRED = {"code", "name", "category", "brandId", "unit", "unitPrice", "specs", "status"}
