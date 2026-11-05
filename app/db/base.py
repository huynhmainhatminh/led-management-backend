from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so Alembic can detect them
from app.modules.auth.models import User  # noqa: F401
from app.modules.products.models import Product  # noqa: F401
