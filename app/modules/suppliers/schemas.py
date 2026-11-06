# app/modules/suppliers/schemas.py
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Status(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class StatusFilter(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ALL = "ALL"


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


class BrandIn(_Base):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)

    _code = field_validator("code")(_upper_code)
    _web = field_validator("website")(_check_url)


class BrandPatch(_Base):
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[Status] = None

    _code = field_validator("code")(_upper_code)
    _web = field_validator("website")(_check_url)


BRAND_REQUIRED = {"code", "name", "status"}