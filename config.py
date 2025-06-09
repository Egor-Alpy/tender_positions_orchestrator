import os
from typing import Optional


class Config:
    """Конфигурация оркестратора"""

    # Версия сервиса
    VERSION = "1.0.0"

    # Сервис классификации
    CLASSIFIER_URL: str = os.getenv(
        "CLASSIFIER_URL",
        "http://classifier:8000/api/v1/tender/classify-tender"
    )
    CLASSIFIER_API_KEY: Optional[str] = os.getenv("CLASSIFIER_API_KEY")

    # Сервис стандартизации
    STANDARDIZER_URL: str = os.getenv(
        "STANDARDIZER_URL",
        "http://standardizer:8000/api/v1/standardize"
    )
    STANDARDIZER_API_KEY: Optional[str] = os.getenv("STANDARDIZER_API_KEY")

    # Сервис подбора товаров
    MATCHER_URL: str = os.getenv(
        "MATCHER_URL",
        "http://matcher:8000/api/v1/match"
    )
    MATCHER_API_KEY: Optional[str] = os.getenv("MATCHER_API_KEY")

    # Общие настройки
    REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT", "300"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # API настройки оркестратора
    ORCHESTRATOR_API_KEY: Optional[str] = os.getenv("ORCHESTRATOR_API_KEY")
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"

    @classmethod
    def validate(cls):
        """Проверить конфигурацию"""
        errors = []

        if not cls.CLASSIFIER_URL:
            errors.append("CLASSIFIER_URL is required")

        if not cls.STANDARDIZER_URL:
            errors.append("STANDARDIZER_URL is required")

        if not cls.MATCHER_URL:
            errors.append("MATCHER_URL is required")

        if cls.REQUIRE_API_KEY and not cls.ORCHESTRATOR_API_KEY:
            errors.append("ORCHESTRATOR_API_KEY is required when REQUIRE_API_KEY=true")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

    @classmethod
    def get_service_headers(cls, service: str) -> dict:
        """Получить заголовки для сервиса"""
        headers = {}

        if service == "classifier" and cls.CLASSIFIER_API_KEY:
            headers["X-API-Key"] = cls.CLASSIFIER_API_KEY
        elif service == "standardizer" and cls.STANDARDIZER_API_KEY:
            headers["X-API-Key"] = cls.STANDARDIZER_API_KEY
        elif service == "matcher" and cls.MATCHER_API_KEY:
            headers["X-API-Key"] = cls.MATCHER_API_KEY

        return headers


config = Config()
