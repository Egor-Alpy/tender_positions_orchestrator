import httpx
import logging
from typing import Dict, Any, Optional

from src.core.config import settings
from src.core.exceptions import ServiceUnavailable, ServiceError

logger = logging.getLogger(__name__)


class ServiceClient:
    """HTTP клиент для вызова микросервисов"""

    def __init__(self, timeout: float = None):
        self.timeout = timeout or settings.REQUEST_TIMEOUT
        self._client = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    def _get_headers(self, service: str) -> Dict[str, str]:
        """Получить заголовки для сервиса"""
        headers = {"Content-Type": "application/json"}

        if service == "classifier" and settings.CLASSIFIER_API_KEY:
            headers["X-API-Key"] = settings.CLASSIFIER_API_KEY
        elif service == "standardizer" and settings.STANDARDIZER_API_KEY:
            headers["X-API-Key"] = settings.STANDARDIZER_API_KEY
        elif service == "matcher" and settings.MATCHER_API_KEY:
            headers["X-API-Key"] = settings.MATCHER_API_KEY

        return headers

    async def call_classifier(self, tender_data: Dict[str, Any]) -> Dict[str, Any]:
        """Вызвать сервис классификации"""
        return await self._call_service(
            service_name="classifier",
            url=settings.CLASSIFIER_URL,
            data=tender_data
        )

    async def call_standardizer(self, tender_data: Dict[str, Any]) -> Dict[str, Any]:
        """Вызвать сервис стандартизации"""
        return await self._call_service(
            service_name="standardizer",
            url=settings.STANDARDIZER_URL,
            data=tender_data
        )

    async def call_matcher(self, tender_data: Dict[str, Any]) -> Dict[str, Any]:
        """Вызвать сервис подбора товаров"""
        return await self._call_service(
            service_name="matcher",
            url=settings.MATCHER_URL,
            data=tender_data
        )

    async def _call_service(
            self,
            service_name: str,
            url: str,
            data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Универсальный метод вызова сервиса"""
        try:
            if not self._client:
                raise RuntimeError("ServiceClient must be used as async context manager")

            headers = self._get_headers(service_name)

            logger.debug(f"Calling {service_name} service at {url}")
            response = await self._client.post(url, json=data, headers=headers)

            response.raise_for_status()
            return response.json()

        except httpx.ConnectError:
            logger.error(f"Cannot connect to {service_name} service at {url}")
            raise ServiceUnavailable(f"Service '{service_name}' is unavailable")

        except httpx.TimeoutException:
            logger.error(f"Timeout calling {service_name} service")
            raise ServiceError(f"Service '{service_name}' timeout")

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error from {service_name}: "
                f"{e.response.status_code} - {e.response.text}"
            )
            raise ServiceError(
                f"Service '{service_name}' returned error: {e.response.text}"
            )

    async def check_health(self, service_name: str, health_url: str) -> Dict[str, Any]:
        """Проверить здоровье сервиса"""
        try:
            if not self._client:
                self._client = httpx.AsyncClient(timeout=5.0)

            response = await self._client.get(health_url)

            return {
                "service": service_name,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds()
            }

        except Exception as e:
            logger.warning(f"Health check failed for {service_name}: {str(e)}")
            return {
                "service": service_name,
                "status": "unavailable",
                "error": str(e)
            }