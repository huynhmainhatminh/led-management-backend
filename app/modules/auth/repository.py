# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from app.modules.auth.models import User
# from app.modules.auth.schemas import UserCreate
# from app.core.security import get_password_hash
#
#
# class AuthRepository:
#     def __init__(self, db: AsyncSession):
#         self.db = db
#
#     async def get_by_username(self, username: str) -> User | None:
#         result = await self.db.execute(select(User).where(User.username == username))
#         return result.scalar_one_or_none()
#
#     async def get_by_email(self, email: str) -> User | None:
#         result = await self.db.execute(select(User).where(User.email == email))
#         return result.scalar_one_or_none()
#
#     async def create(self, user_in: UserCreate) -> User:
#         hashed_password = get_password_hash(user_in.password)
#         db_user = User(
#             username=user_in.username,
#             email=user_in.email,
#             hashed_password=hashed_password
#         )
#         self.db.add(db_user)
#         await self.db.commit()
#         await self.db.refresh(db_user)
#         return db_user
