# # API versioning, tổng hợp router
# from fastapi import APIRouter
# from app.modules.auth.router import router as auth_router
# from app.modules.products.router import router as products_router
# from app.modules.suppliers.router import router as suppliers_router
# from app.modules.quotations.router import router as quotations_router
#
# api_router = APIRouter()
#
# api_router.include_router(auth_router)
# api_router.include_router(products_router)
# api_router.include_router(suppliers_router)
# api_router.include_router(quotations_router)


from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.products.router import router as products_router
from app.modules.suppliers.router import router as suppliers_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(products_router)
api_router.include_router(suppliers_router)
