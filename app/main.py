import os
import threading
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.api import api_router
from app.core.exceptions import (
    AppError,
    CredentialsException,
    NotFoundException,
    BadRequestException,
)
from app.common.response import ErrorResponse
from app.storage import JsonRepository, now_iso


def _find_data_dir() -> Path:
    """Tự động tìm thư mục data nằm ở gốc project."""
    current = Path(__file__).resolve().parent
    # Kiểm tra cả thư mục hiện tại (nếu main.py ở gốc) và thư mục cha (nếu main.py ở trong app/)
    for candidate in [current / "data", current.parent / "data"]:
        if (candidate / "components.json").exists():
            return candidate
    return current / "data"


def _error(status: int, code: str, message: str, errors: Optional[list] = None) -> JSONResponse:
    body = {"success": False, "code": code, "message": message, "timestamp": now_iso()}
    if errors:
        body["errors"] = errors
    return JSONResponse(status_code=status, content=body)


def create_app(data_dir: Optional[Path] = None) -> FastAPI:
    data_dir = Path(data_dir or os.getenv("DATA_DIR") or _find_data_dir())

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    lock = threading.RLock()
    app.state.brands = JsonRepository(data_dir / "brands.json", lock)
    app.state.components = JsonRepository(data_dir / "components.json", lock)
    app.state.users = JsonRepository(data_dir / "users.json", lock)
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError):
        return _error(
            getattr(exc, "status_code", 400),
            getattr(exc, "code", "APP_ERROR"),
            getattr(exc, "message", str(exc)),
        )

    @app.exception_handler(CredentialsException)
    @app.exception_handler(NotFoundException)
    @app.exception_handler(BadRequestException)
    async def custom_exception_handler(request: Request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(error=exc.detail).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError):
        errors = [
            {
                "field": ".".join(str(p) for p in e["loc"][1:]) or str(e["loc"][0]),
                "message": e["msg"],
            }
            for e in exc.errors()
        ]
        return _error(400, "VALIDATION_ERROR", "Dữ liệu đầu vào không hợp lệ", errors)

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(_: Request, exc: StarletteHTTPException):
        code = {404: "RESOURCE_NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}.get(exc.status_code, "HTTP_ERROR")
        return _error(exc.status_code, code, str(exc.detail))

    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/")
    async def root():
        return {"message": "Welcome to PC Management Backend", "docs": "/docs"}

    return app


app = create_app()