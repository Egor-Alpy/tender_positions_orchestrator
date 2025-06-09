from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import httpx
from typing import Dict, Any, Optional
import logging
import time
from config import config

# Настройка логирования
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Проверка конфигурации при запуске
try:
    config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise

app = FastAPI(
    title="Tender Processing Orchestrator",
    version=config.VERSION,
    description="Orchestrator service for processing tenders through classification, standardization and matching services"
)


class TenderRequest(BaseModel):
    tenderInfo: Dict[str, Any]
    items: list
    generalRequirements: Dict[str, Any]
    attachments: list


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Проверка API ключа если требуется"""
    if config.REQUIRE_API_KEY:
        if not x_api_key or x_api_key != config.ORCHESTRATOR_API_KEY:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key"
            )
    return x_api_key


@app.post("/process-tender")
async def process_tender(
        tender: TenderRequest,
        api_key: Optional[str] = Depends(verify_api_key)
):
    """
    Обработать тендер через все сервисы:
    1. Классификация ОКПД2
    2. Стандартизация
    3. Подбор подходящих товаров
    """
    start_time = time.time()
    metrics = {}

    async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT) as client:
        try:
            tender_data = tender.dict()
            logger.info(f"Processing tender with {len(tender_data['items'])} items")

            # 1. Классификация ОКПД2
            logger.info("Step 1: Calling classifier service...")
            step_start = time.time()
            classifier_response = await client.post(
                config.CLASSIFIER_URL,
                json=tender_data,
                headers=config.get_service_headers("classifier")
            )
            classifier_response.raise_for_status()
            classified_data = classifier_response.json()
            metrics['classifier_time'] = time.time() - step_start

            logger.info(
                f"Classifier response: {classified_data.get('statistics', {})} (time: {metrics['classifier_time']:.2f}s)")

            # Извлекаем обновленный тендер из ответа классификатора
            if "tender" in classified_data:
                tender_data = classified_data["tender"]
            else:
                tender_data = classified_data

            # 2. Стандартизация
            logger.info("Step 2: Calling standardizer service...")
            step_start = time.time()
            standardizer_response = await client.post(
                config.STANDARDIZER_URL,
                json=tender_data,
                headers=config.get_service_headers("standardizer")
            )
            standardizer_response.raise_for_status()
            standardized_data = standardizer_response.json()
            metrics['standardizer_time'] = time.time() - step_start

            logger.info(f"Standardizer response received (time: {metrics['standardizer_time']:.2f}s)")

            # Извлекаем обновленный тендер из ответа стандартизатора
            if "tender" in standardized_data:
                tender_data = standardized_data["tender"]
            else:
                tender_data = standardized_data

            # 3. Подбор товаров
            logger.info("Step 3: Calling matcher service...")
            step_start = time.time()
            matcher_response = await client.post(
                config.MATCHER_URL,
                json=tender_data,
                headers=config.get_service_headers("matcher")
            )
            matcher_response.raise_for_status()
            final_result = matcher_response.json()
            metrics['matcher_time'] = time.time() - step_start

            # Общее время обработки
            metrics['total_time'] = time.time() - start_time

            logger.info(f"All services processed successfully (total time: {metrics['total_time']:.2f}s)")
            logger.info(f"Processing metrics: {metrics}")

            # Добавляем метрики в результат
            if isinstance(final_result, dict):
                final_result['processing_metrics'] = metrics

            return final_result

        except httpx.ConnectError as e:
            logger.error(f"Connection error: {str(e)}")
            service_name = "unknown"
            if config.CLASSIFIER_URL in str(e):
                service_name = "classifier"
            elif config.STANDARDIZER_URL in str(e):
                service_name = "standardizer"
            elif config.MATCHER_URL in str(e):
                service_name = "matcher"
            raise HTTPException(
                status_code=503,
                detail=f"Service '{service_name}' is unavailable"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from service: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Service error: {e.response.text}"
            )
        except httpx.TimeoutException:
            logger.error("Request timeout")
            raise HTTPException(status_code=504, detail="Service timeout")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "service": "tender-orchestrator"}


@app.get("/health/detailed")
async def detailed_health_check():
    """Детальная проверка здоровья всех сервисов"""
    health_status = {
        "orchestrator": "healthy",
        "services": {}
    }

    async with httpx.AsyncClient(timeout=5.0) as client:
        # Проверка классификатора
        try:
            resp = await client.get(
                config.CLASSIFIER_URL.replace("/classify-tender", "").replace("/api/v1/tender", "/health"))
            health_status["services"]["classifier"] = "healthy" if resp.status_code == 200 else "unhealthy"
        except:
            health_status["services"]["classifier"] = "unavailable"

        # Проверка стандартизатора
        try:
            resp = await client.get(config.STANDARDIZER_URL.replace("/standardize", "").replace("/api/v1", "/health"))
            health_status["services"]["standardizer"] = "healthy" if resp.status_code == 200 else "unhealthy"
        except:
            health_status["services"]["standardizer"] = "unavailable"

        # Проверка сервиса подбора
        try:
            resp = await client.get(config.MATCHER_URL.replace("/match", "").replace("/api/v1", "/health"))
            health_status["services"]["matcher"] = "healthy" if resp.status_code == 200 else "unhealthy"
        except:
            health_status["services"]["matcher"] = "unavailable"

    # Общий статус
    all_healthy = all(status == "healthy" for status in health_status["services"].values())
    health_status["overall"] = "healthy" if all_healthy else "degraded"

    return health_status


@app.get("/")
async def root():
    """Информация о сервисе"""
    return {
        "service": "Tender Processing Orchestrator",
        "version": config.VERSION,
        "endpoints": {
            "process_tender": "/process-tender",
            "health": "/health",
            "health_detailed": "/health/detailed"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    