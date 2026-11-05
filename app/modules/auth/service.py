from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import UserCreate, UserLogin, Token
from app.core.security import verify_password, create_access_token
from app.core.exceptions import CredentialsException, BadRequestException
from datetime import timedelta
from app.core.config import settings


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repository = AuthRepository(db)

    async def register(self, user_in: UserCreate):
        existing = await self.repository.get_by_username(user_in.username)
        if existing:
            raise BadRequestException("Username already registered")
        existing_email = await self.repository.get_by_email(user_in.email)
        if existing_email:
            raise BadRequestException("Email already registered")
        return await self.repository.create(user_in)

    async def login(self, user_in: UserLogin) -> Token:
        user = await self.repository.get_by_username(user_in.username)
        if not user or not verify_password(user_in.password, user.hashed_password):
            raise CredentialsException()
        if not user.is_active:
            raise CredentialsException()
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token)
