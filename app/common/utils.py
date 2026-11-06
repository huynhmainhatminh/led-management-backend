# Common utilities
# app/common/utils.py

import httpx
from app.core.config import settings
from math import ceil
from app.core.exceptions import AppError


async def make_http_request(url: str, method: str = "GET", **kwargs) -> dict:
    async with httpx.AsyncClient(timeout=settings.HTTPX_TIMEOUT) as client:
        response = await client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()


def paginate(items: list, page: int, size: int) -> dict:
    total = len(items)
    start = page * size
    return {
        "content": items[start : start + size],
        "page": page,
        "size": size,
        "totalElements": total,
        "totalPages": ceil(total / size) if total else 0,
    }


def sort_items(items: list, sort: str, allowed: set) -> list:
    field, _, direction = sort.partition(",")
    field, direction = field.strip(), (direction.strip() or "asc").lower()
    if field not in allowed or direction not in ("asc", "desc"):
        raise AppError(
            400,
            "VALIDATION_ERROR",
            f"sort không hợp lệ. Trường cho phép: {', '.join(sorted(allowed))}; hướng: asc hoặc desc",
        )

    def key(item: dict):
        v = item.get(field)
        return (v is None, v.lower() if isinstance(v, str) else v)

    return sorted(items, key=key, reverse=(direction == "desc"))


def contains(q: str, *values) -> bool:
    q = q.strip().lower()
    return any(q in str(v).lower() for v in values if v is not None)


def reject_nulls(changes: dict, required: set) -> None:
    bad = sorted(k for k in required if k in changes and changes[k] is None)
    if bad:
        raise AppError(400, "VALIDATION_ERROR", f"Trường không được null: {', '.join(bad)}")