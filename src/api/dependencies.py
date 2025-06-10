from fastapi import Header, HTTPException
from typing import Optional

from src.core.config import settings


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    """Проверка API ключа если требуется"""
    if settings.REQUIRE_API_KEY:
        if not x_api_key or x_api_key != settings.ORCHESTRATOR_API_KEY:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key"
            )
    return x_api_key