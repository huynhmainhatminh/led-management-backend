from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.auth.schemas import UserCreate, UserLogin, UserResponse, Token
from app.modules.auth.service import AuthService
from app.common.response import SuccessResponse
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=SuccessResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    user = await service.register(user_in)
    return SuccessResponse(data=UserResponse.model_validate(user), message="User registered successfully")


@router.post("/login", response_model=SuccessResponse[Token])
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    token = await service.login(user_in)
    return SuccessResponse(data=token, message="Login successful")


@router.get("/me", response_model=SuccessResponse[UserResponse])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return SuccessResponse(data=UserResponse.model_validate(current_user))
