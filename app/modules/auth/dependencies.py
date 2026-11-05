from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.auth.repository import AuthRepository
from app.core.exceptions import CredentialsException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise CredentialsException()
    username: str = payload.get("sub")
    if username is None:
        raise CredentialsException()
    
    repository = AuthRepository(db)
    user = await repository.get_by_username(username)
    if user is None:
        raise CredentialsException()
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
