# Common utilities
import httpx
from app.core.config import settings

async def make_http_request(url: str, method: str = "GET", **kwargs) -> dict:
    async with httpx.AsyncClient(timeout=settings.HTTPX_TIMEOUT) as client:
        response = await client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
