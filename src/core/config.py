from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки оркестратора"""

    # URLs сервисов
    CLASSIFIER_URL: str = "http://localhost:8000/api/v1/tender/classify-tender"
    STANDARDIZER_URL: str = "http://standardizer:8000/api/v1/standardization/tender/standardize"
    MATCHER_URL: str = "http://matcher:8002/api/v1/tenders/match"

    # API ключи сервисов
    CLASSIFIER_API_KEY: Optional[str] = None
    STANDARDIZER_API_KEY: Optional[str] = None
    MATCHER_API_KEY: Optional[str] = None

    # Настройки безопасности оркестратора
    REQUIRE_API_KEY: bool = False
    ORCHESTRATOR_API_KEY: Optional[str] = None

    # Общие настройки
    REQUEST_TIMEOUT: float = 300.0
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()