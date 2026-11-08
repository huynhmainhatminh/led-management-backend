# app/modules/auth/dependencies.py
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.exceptions import AppError
from app.core.security import decode_access_token
from app.core.exceptions import CredentialsException
from app.modules.auth.service import AuthService

security = HTTPBearer()


def get_auth_service(request: Request) -> AuthService:
    return AuthService(users_repo=request.app.state.users)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: AuthService = Depends(get_auth_service),
) -> dict:
    """Lấy user hiện tại và kiểm tra tính hợp lệ của phiên đơn (Single-Session)"""
    token = credentials.credentials

    payload = decode_access_token(token)
    if payload is None:
        raise CredentialsException()

    username: str = payload.get("sub")
    token_session_id: str = payload.get("session_id")

    if username is None or token_session_id is None:
        raise CredentialsException()

    user = service.get_by_username(username)
    if user is None:
        raise CredentialsException()

    # KIỂM TRA ĐƠN PHIÊN:
    # Nếu user đã logout (current_session_id là None) hoặc đã đăng nhập ở nơi khác (session_id khác nhau)
    active_session_id = user.get("current_session_id")
    if not active_session_id or token_session_id != active_session_id:
        raise CredentialsException("Phiên đăng nhập không hợp lệ hoặc tài khoản đã đăng nhập ở thiết bị khác")

    return service.format_user_profile(user)


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_roles(*allowed_roles: str):
    """Dependency kiểm tra role của user (ví dụ: require_roles('admin', 'manage'))"""
    async def role_checker(current_user: dict = Depends(get_current_active_user)) -> dict:
        user_role = current_user.get("role", "staff")
        if user_role not in allowed_roles:
            raise AppError(
                403,
                "FORBIDDEN",
                f"Bạn không có quyền thực hiện thao tác này (Yêu cầu quyền: {', '.join(allowed_roles)})",
            )
        return current_user

    return role_checker
