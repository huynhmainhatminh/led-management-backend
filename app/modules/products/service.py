# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List
# from app.modules.products.repository import ProductRepository
# from app.modules.products.schemas import ProductCreate, ProductUpdate, ProductResponse
# from app.core.exceptions import NotFoundException
#
#
# class ProductService:
#     def __init__(self, db: AsyncSession):
#         self.repository = ProductRepository(db)
#
#     async def get_product(self, product_id: int) -> ProductResponse:
#         product = await self.repository.get(product_id)
#         if not product:
#             raise NotFoundException("Product not found")
#         return ProductResponse.model_validate(product)
#
#     async def get_products(self, skip: int = 0, limit: int = 100) -> List[ProductResponse]:
#         products = await self.repository.get_all(skip, limit)
#         return [ProductResponse.model_validate(p) for p in products]
#
#     async def create_product(self, product_in: ProductCreate) -> ProductResponse:
#         product = await self.repository.create(product_in)
#         return ProductResponse.model_validate(product)
#
#     async def update_product(self, product_id: int, product_in: ProductUpdate) -> ProductResponse:
#         product = await self.repository.get(product_id)
#         if not product:
#             raise NotFoundException("Product not found")
#         updated = await self.repository.update(product, product_in)
#         return ProductResponse.model_validate(updated)
#
#     async def delete_product(self, product_id: int) -> None:
#         product = await self.repository.get(product_id)
#         if not product:
#             raise NotFoundException("Product not found")
#         await self.repository.delete(product)


# app/modules/products/service.py
from typing import Optional
from app.core.exceptions import AppError
from app.common.utils import paginate, sort_items, contains, reject_nulls
from app.modules.products.schemas import (
    Category, Status, StatusFilter, ComponentIn, ComponentPatch, COMPONENT_REQUIRED
)

SORT_FIELDS = {
    "id", "code", "name", "category", "brandName",
    "unitPrice", "status", "createdAt", "updatedAt"
}


class ComponentService:
    def __init__(self, components_repo, brands_repo):
        self.repo = components_repo
        self.brands_repo = brands_repo

    # --- Private Helpers ---
    def _brands_by_id(self) -> dict:
        return {b["id"]: b for b in self.brands_repo.all()}

    def _with_brand_name(self, component: dict, brands_by_id: Optional[dict] = None) -> dict:
        if brands_by_id is None:
            brands_by_id = self._brands_by_id()
        brand = brands_by_id.get(component["brandId"])
        return {**component, "brandName": brand["name"] if brand else None}

    def _get_or_404(self, component_id: int) -> dict:
        item = self.repo.get(component_id)
        if not item:
            raise AppError(404, "COMPONENT_NOT_FOUND", f"Không tìm thấy linh kiện id={component_id}")
        return item

    def _check_code_unique(self, code: str, exclude_id: Optional[int] = None) -> None:
        if any(c["code"] == code and c["id"] != exclude_id for c in self.repo.all()):
            raise AppError(409, "COMPONENT_CODE_DUPLICATED", f"Mã linh kiện '{code}' đã tồn tại")

    def _check_brand_usable(self, brand_id: int) -> None:
        brand = self.brands_repo.get(brand_id)
        if not brand:
            raise AppError(404, "BRAND_NOT_FOUND", f"Không tìm thấy thương hiệu id={brand_id}")
        if brand["status"] != Status.ACTIVE.value:
            raise AppError(400, "BRAND_INACTIVE", "Thương hiệu đã ngừng sử dụng")

    # --- Main Business Methods ---
    def list_components(
        self,
        page: int = 0,
        size: int = 10,
        sort: str = "name,asc",
        q: Optional[str] = None,
        category: Optional[Category] = None,
        brand_id: Optional[int] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        status: StatusFilter = StatusFilter.ACTIVE,
    ) -> dict:
        brands = self._brands_by_id()
        items = [self._with_brand_name(c, brands) for c in self.repo.all()]

        if status != StatusFilter.ALL:
            items = [c for c in items if c["status"] == status.value]
        if q:
            items = [c for c in items if contains(q, c["code"], c["name"], c.get("model"))]
        if category:
            items = [c for c in items if c["category"] == category.value]
        if brand_id is not None:
            items = [c for c in items if c["brandId"] == brand_id]
        if min_price is not None:
            items = [c for c in items if c["unitPrice"] >= min_price]
        if max_price is not None:
            items = [c for c in items if c["unitPrice"] <= max_price]

        items = sort_items(items, sort, SORT_FIELDS)
        return paginate(items, page, size)

    def get_component(self, component_id: int) -> dict:
        item = self._get_or_404(component_id)
        return self._with_brand_name(item)

    def create_component(self, body: ComponentIn) -> dict:
        with self.repo.lock:
            self._check_brand_usable(body.brandId)
            self._check_code_unique(body.code)
            record = self.repo.insert({**body.model_dump(mode="json"), "status": Status.ACTIVE.value})
        return self._with_brand_name(record)

    def replace_component(self, component_id: int, body: ComponentIn) -> dict:
        with self.repo.lock:
            current = self._get_or_404(component_id)
            if body.brandId != current["brandId"]:
                self._check_brand_usable(body.brandId)
            self._check_code_unique(body.code, exclude_id=component_id)
            record = self.repo.update(component_id, body.model_dump(mode="json"))
        return self._with_brand_name(record)

    def patch_component(self, component_id: int, body: ComponentPatch) -> dict:
        changes = body.model_dump(exclude_unset=True, mode="json")
        reject_nulls(changes, COMPONENT_REQUIRED)
        with self.repo.lock:
            current = self._get_or_404(component_id)
            if "code" in changes:
                self._check_code_unique(changes["code"], exclude_id=component_id)
            brand_changed = "brandId" in changes and changes["brandId"] != current["brandId"]
            reactivated = changes.get("status") == Status.ACTIVE.value and current["status"] != Status.ACTIVE.value
            if brand_changed or reactivated:
                self._check_brand_usable(changes.get("brandId", current["brandId"]))
            record = self.repo.update(component_id, changes)
        return self._with_brand_name(record)

    def delete_component(self, component_id: int) -> None:
        with self.repo.lock:
            self._get_or_404(component_id)
            self.repo.update(component_id, {"status": Status.INACTIVE.value})
