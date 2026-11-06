# from fastapi import APIRouter, Depends, status
# # from sqlalchemy.ext.asyncio import AsyncSession
# # from app.db.session import get_db
# from app.modules.auth.schemas import UserCreate, UserLogin, UserResponse, Token
# from app.modules.auth.service import AuthService
# from app.common.response import SuccessResponse
# from app.modules.auth.dependencies import get_current_active_user
# from app.modules.auth.models import User
#
# router = APIRouter(prefix="/auth", tags=["auth"])
#
#
# # @router.post("/register", response_model=SuccessResponse[UserResponse], status_code=status.HTTP_201_CREATED)
# # async def register(
# #     user_in: UserCreate,
# #     db: AsyncSession = Depends(get_db)
# # ):
# #     service = AuthService(db)
# #     user = await service.register(user_in)
# #     return SuccessResponse(data=UserResponse.model_validate(user), message="User registered successfully")
#
#
# @router.post("/login", response_model=SuccessResponse[Token])
# async def login(
#     user_in: UserLogin,
#     db: AsyncSession = Depends(get_db)
# ):
#     service = AuthService(db)
#     token = await service.login(user_in)
#     return SuccessResponse(data=token, message="Login successful")
#
#
# @router.get("/me", response_model=SuccessResponse[UserResponse])
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return SuccessResponse(data=UserResponse.model_validate(current_user))

# app/modules/auth/router.py

# app/modules/auth/router.py
from fastapi import APIRouter, Depends
from app.modules.auth.schemas import UserLogin, UserResponse, Token
from app.modules.auth.service import AuthService
from app.common.response import SuccessResponse
from app.modules.auth.dependencies import get_current_active_user, get_auth_service

router = APIRouter(prefix="/auth", tags=["Xác thực (Auth)"])


@router.post("/login", response_model=SuccessResponse[Token], summary="Đăng nhập")
async def login(
    user_in: UserLogin,
    service: AuthService = Depends(get_auth_service),
):
    token = await service.login(user_in)
    return SuccessResponse(data=token, message="Đăng nhập thành công")


@router.post("/logout", response_model=SuccessResponse, summary="Đăng xuất")
async def logout(
    current_user: dict = Depends(get_current_active_user),
    service: AuthService = Depends(get_auth_service),
):
    """Đăng xuất và hủy hiệu lực JWT token hiện tại ngay lập tức."""
    await service.logout(current_user["id"])
    return SuccessResponse(data=None, message="Đăng xuất thành công")


@router.get("/me", response_model=SuccessResponse[UserResponse], summary="Thông tin tài khoản hiện tại")
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """Lấy thông tin user hiện tại từ JWT token"""
    return SuccessResponse(data=UserResponse(**current_user))