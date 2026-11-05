from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.core.exceptions import NotFoundException


class ProductService:
    def __init__(self, db: AsyncSession):
        self.repository = ProductRepository(db)

    async def get_product(self, product_id: int) -> ProductResponse:
        product = await self.repository.get(product_id)
        if not product:
            raise NotFoundException("Product not found")
        return ProductResponse.model_validate(product)

    async def get_products(self, skip: int = 0, limit: int = 100) -> List[ProductResponse]:
        products = await self.repository.get_all(skip, limit)
        return [ProductResponse.model_validate(p) for p in products]

    async def create_product(self, product_in: ProductCreate) -> ProductResponse:
        product = await self.repository.create(product_in)
        return ProductResponse.model_validate(product)

    async def update_product(self, product_id: int, product_in: ProductUpdate) -> ProductResponse:
        product = await self.repository.get(product_id)
        if not product:
            raise NotFoundException("Product not found")
        updated = await self.repository.update(product, product_in)
        return ProductResponse.model_validate(updated)

    async def delete_product(self, product_id: int) -> None:
        product = await self.repository.get(product_id)
        if not product:
            raise NotFoundException("Product not found")
        await self.repository.delete(product)
