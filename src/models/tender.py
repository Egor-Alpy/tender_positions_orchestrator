from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime


class TenderRequest(BaseModel):
    """Входящий запрос тендера"""
    tenderInfo: Dict[str, Any]
    items: List[Dict[str, Any]]
    generalRequirements: Dict[str, Any]
    attachments: List[Any]


class ProcessingMetrics(BaseModel):
    """Метрики обработки"""
    classifier_time: float
    standardizer_time: float
    matcher_time: float
    total_time: float


class ProcessingResult(BaseModel):
    """Результат обработки тендера"""
    tender_number: str
    tender_name: str
    processing_time: datetime
    total_items: int
    matched_items: int
    item_matches: List[Dict[str, Any]]
    summary: Dict[str, Any]
    processing_metrics: ProcessingMetrics


class ServiceHealth(BaseModel):
    """Статус здоровья сервиса"""
    service: str
    status: str  # healthy, unhealthy, unavailable
    response_time: Optional[float] = None
    error: Optional[str] = None