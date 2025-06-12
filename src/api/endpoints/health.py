from fastapi import APIRouter
import logging

from src.services.service_client import ServiceClient
from src.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Базовая проверка здоровья оркестратора"""
    return {
        "status": "healthy",
        "service": "tender-orchestrator",
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """Детальная проверка здоровья всех сервисов"""
    health_status = {
        "orchestrator": "healthy",
        "services": {}
    }

    # Формируем URL для health checks
    health_urls = {
        "classifier": settings.CLASSIFIER_URL.replace("/api/v1/tender/classify-tender", "/health"),
        "standardizer": settings.STANDARDIZER_URL.replace("/api/v1/standardization/tender/standardize", "/health"),
        "matcher": settings.MATCHER_URL.replace("/api/v1/tenders/match", "/health")
    }

    logger.info(f"health urls:\n{health_urls}")

    async with ServiceClient(timeout=5.0) as client:
        # Проверяем каждый сервис
        for service_name, health_url in health_urls.items():
            health_result = await client.check_health(service_name, health_url)
            health_status["services"][service_name] = health_result

    # Определяем общий статус
    all_healthy = all(
        service.get("status") == "healthy"
        for service in health_status["services"].values()
    )

    health_status["overall"] = "healthy" if all_healthy else "degraded"

    return health_status