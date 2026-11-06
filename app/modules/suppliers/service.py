# app/modules/suppliers/service.py
from typing import Optional

from app.core.exceptions import AppError
from app.modules.products.schemas import Category
from app.common.utils import paginate, sort_items, contains, reject_nulls
from app.modules.suppliers.schemas import (
    BRAND_REQUIRED,
    BrandIn,
    BrandPatch,
    Status,
    StatusFilter,
)

SORT_FIELDS = {"id", "code", "name", "country", "status", "createdAt", "updatedAt"}


class BrandService:
    def __init__(self, brands_repo, components_repo):
        self.repo = brands_repo
        self.components_repo = components_repo


    # --- Private Validation Helpers ---
    def _get_or_404(self, brand_id: int) -> dict:
        brand = self.repo.get(brand_id)
        if not brand:
            raise AppError(404, "BRAND_NOT_FOUND", f"Không tìm thấy thương hiệu id={brand_id}")
        return brand

    def _check_code_unique(self, code: str, exclude_id: Optional[int] = None) -> None:
        if any(b["code"] == code and b["id"] != exclude_id for b in self.repo.all()):
            raise AppError(409, "BRAND_CODE_DUPLICATED", f"Mã thương hiệu '{code}' đã tồn tại")

    def _check_not_in_use(self, brand_id: int) -> None:
        in_use = any(
            c["brandId"] == brand_id and c["status"] == Status.ACTIVE.value
            for c in self.components_repo.all()
        )
        if in_use:
            raise AppError(
                409,
                "BRAND_IN_USE",
                "Thương hiệu còn linh kiện đang hoạt động, không thể ngừng sử dụng",
            )

    # --- Main Business Methods ---
    def list_brands(
        self,
        page: int = 0,
        size: int = 10,
        sort: str = "name,asc",
        q: Optional[str] = None,
        category: Optional[Category] = None,
        status: StatusFilter = StatusFilter.ACTIVE,
    ) -> dict:
        items = self.repo.all()
        if status != StatusFilter.ALL:
            items = [b for b in items if b["status"] == status.value]
        if q:
            items = [b for b in items if contains(q, b["code"], b["name"], b.get("country"))]
        if category:
            ids = {
                c["brandId"]
                for c in self.components_repo.all()
                if c["category"] == category.value and c["status"] == Status.ACTIVE.value
            }
            items = [b for b in items if b["id"] in ids]
        items = sort_items(items, sort, SORT_FIELDS)
        return paginate(items, page, size)

    def get_brand(self, brand_id: int) -> dict:
        return self._get_or_404(brand_id)

    def create_brand(self, body: BrandIn) -> dict:
        with self.repo.lock:
            self._check_code_unique(body.code)
            return self.repo.insert({**body.model_dump(), "status": Status.ACTIVE.value})

    def replace_brand(self, brand_id: int, body: BrandIn) -> dict:
        with self.repo.lock:
            self._get_or_404(brand_id)
            self._check_code_unique(body.code, exclude_id=brand_id)
            return self.repo.update(brand_id, body.model_dump())

    def patch_brand(self, brand_id: int, body: BrandPatch) -> dict:
        changes = body.model_dump(exclude_unset=True, mode="json")
        reject_nulls(changes, BRAND_REQUIRED)
        with self.repo.lock:
            current = self._get_or_404(brand_id)
            if "code" in changes:
                self._check_code_unique(changes["code"], exclude_id=brand_id)
            if (
                changes.get("status") == Status.INACTIVE.value
                and current["status"] == Status.ACTIVE.value
            ):
                self._check_not_in_use(brand_id)
            return self.repo.update(brand_id, changes)

    def delete_brand(self, brand_id: int) -> None:
        with self.repo.lock:
            current = self._get_or_404(brand_id)
            if current["status"] == Status.ACTIVE.value:
                self._check_not_in_use(brand_id)
                self.repo.update(brand_id, {"status": Status.INACTIVE.value})
