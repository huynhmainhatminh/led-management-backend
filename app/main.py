from fastapi import FastAPI
from app.core.config import settings
from app.api import api_router
from app.core.exceptions import CredentialsException, NotFoundException, BadRequestException
from fastapi.responses import JSONResponse
from app.common.response import ErrorResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(CredentialsException)
@app.exception_handler(NotFoundException)
@app.exception_handler(BadRequestException)
async def custom_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.detail).model_dump()
    )


@app.get("/")
async def root():
    return {"message": "Welcome to PC Management Backend", "docs": "/docs"}
