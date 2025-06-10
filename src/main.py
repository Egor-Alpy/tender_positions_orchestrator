import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.endpoints import tender, health
from src.core.config import settings

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("Starting Tender Orchestrator...")
    logger.info(f"Classifier URL: {settings.CLASSIFIER_URL}")
    logger.info(f"Standardizer URL: {settings.STANDARDIZER_URL}")
    logger.info(f"Matcher URL: {settings.MATCHER_URL}")
    yield
    logger.info("Shutting down Tender Orchestrator...")


app = FastAPI(
    title="Tender Processing Orchestrator",
    version="1.0.0",
    description="Orchestrates tender processing through classification, standardization and matching services",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(tender.router, prefix="/api/v1", tags=["tender"])
app.include_router(health.router, tags=["health"])


@app.get("/")
async def root():
    """Информация о сервисе"""
    return {
        "service": "Tender Processing Orchestrator",
        "version": "1.0.0",
        "endpoints": {
            "process_tender": "/api/v1/process-tender",
            "health": "/health",
            "health_detailed": "/health/detailed"
        }
    }