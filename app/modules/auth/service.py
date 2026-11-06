# app/modules/auth/service.py
import uuid
from datetime import timedelta
from typing import Optional, Dict, Any

from app.modules.auth.schemas import UserLogin, Token
from app.core.security import create_access_token, verify_password
from app.core.exceptions import CredentialsException
from app.core.config import settings


class AuthService:
    def __init__(self, users_repo):
        self.repo = users_repo

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        username_clean = username.strip().lower()
        return next(
            (u for u in self.repo.all() if u.get("username", "").lower() == username_clean),
            None,
        )

    def _check_password(self, plain_password: str, user: Dict[str, Any]) -> bool:
        if "password" in user and user["password"] == plain_password:
            return True
        if "hashed_password" in user:
            return verify_password(plain_password, user["hashed_password"])
        return False

    def format_user_profile(self, user: Dict[str, Any]) -> Dict[str, Any]:
        role = user.get("role", "staff")
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": role,
            "is_active": user.get("is_active", True),
            "is_superuser": user.get("is_superuser", role == "admin"),
        }

    async def login(self, user_in: UserLogin) -> Token:
        with self.repo.lock:
            user = self.get_by_username(user_in.username)

            if not user or not self._check_password(user_in.password, user):
                raise CredentialsException()

            if not user.get("is_active", True):
                raise CredentialsException()

            # 1. Sinh mã phiên (session_id) duy nhất cho lần đăng nhập này
            session_id = str(uuid.uuid4())

            # 2. Ghi đè current_session_id vào users.json (vô hiệu hóa mọi phiên cũ trước đó)
            self.repo.update(user["id"], {"current_session_id": session_id})

            # 3. Nhúng session_id vào JWT payload
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={
                    "sub": user["username"],
                    "user_id": user["id"],
                    "role": user.get("role", "staff"),
                    "session_id": session_id,
                },
                expires_delta=access_token_expires,
            )
            return Token(access_token=access_token)

    async def logout(self, user_id: int) -> None:
        """Hủy phiên đăng nhập hiện tại của user"""
        with self.repo.lock:
            self.repo.update(user_id, {"current_session_id": None})
