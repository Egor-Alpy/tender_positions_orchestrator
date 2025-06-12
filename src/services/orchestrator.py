import logging
import time
from typing import Dict, Any

from src.models.tender import TenderRequest, ProcessingMetrics
from src.services.service_client import ServiceClient
from src.core.exceptions import ServiceUnavailable, ProcessingError

logger = logging.getLogger(__name__)


class TenderOrchestrator:
    """Оркестратор обработки тендеров"""

    def __init__(self, service_client: ServiceClient):
        self.service_client = service_client

    async def process_tender(self, tender: TenderRequest) -> Dict[str, Any]:
        """
        Обработать тендер через цепочку сервисов:
        1. Классификация
        2. Стандартизация
        3. Подбор товаров
        """
        start_time = time.time()
        metrics = {}

        tender_data = tender.dict()
        logger.info(f"Starting tender processing with {len(tender_data['items'])} items")

        try:
            # 1. Классификация
            classified_data = await self._classify(tender_data)
            metrics['classifier_time'] = classified_data.pop('processing_time', 0)

            # 2. Стандартизация
            standardized_data = await self._standardize(classified_data)
            metrics['standardizer_time'] = standardized_data.pop('processing_time', 0)

            # 3. Подбор товаров
            matched_data = await self._match(standardized_data)
            metrics['matcher_time'] = matched_data.pop('processing_time', 0)

            # Общее время
            metrics['total_time'] = time.time() - start_time

            # Добавляем метрики в результат
            if isinstance(matched_data, dict):
                matched_data['processing_metrics'] = ProcessingMetrics(**metrics)

            logger.info(f"Tender processed successfully in {metrics['total_time']:.2f}s")
            return matched_data

        except Exception as e:
            logger.error(f"Error processing tender: {str(e)}")
            raise ProcessingError(f"Failed to process tender: {str(e)}")

    async def _classify(self, tender_data: Dict[str, Any]) -> Dict[str, Any]:
        """Классифицировать товары"""
        logger.info("Step 1: Classifying tender items...")
        start = time.time()

        response = await self.service_client.call_classifier(tender_data)

        # Извлекаем обновленный тендер
        if "tender" in response:
            # result = response["tender"]
            result = response
        else:
            result = response

        result['processing_time'] = time.time() - start

        # Логируем статистику если есть
        if "statistics" in response:
            stats = response["statistics"]
            logger.info(
                f"Classification complete: "
                f"{stats.get('already_classified', 0)} already classified, "
                f"{stats.get('newly_classified', 0)} newly classified"
            )

        return result

    async def _standardize(self, tender_data: Dict[str, Any]) -> Dict[str, Any]:
        """Стандартизировать характеристики"""
        logger.info("Step 2: Standardizing item characteristics...")
        start = time.time()

        response = await self.service_client.call_standardizer(tender_data)

        # Извлекаем обновленный тендер
        if "tender" in response:
            result = response["tender"]
        else:
            result = response

        result['processing_time'] = time.time() - start

        # Логируем статистику если есть
        if "statistics" in response:
            stats = response["statistics"]
            logger.info(
                f"Standardization complete: "
                f"{stats.get('already_standardized', 0)} already standardized, "
                f"{stats.get('newly_standardized', 0)} newly standardized"
            )

        return result

    async def _match(self, tender_data: Dict[str, Any]) -> Dict[str, Any]:
        """Подобрать подходящие товары"""
        logger.info("Step 3: Matching products...")
        start = time.time()

        response = await self.service_client.call_matcher(tender_data)
        response['processing_time'] = time.time() - start

        # Логируем результаты
        logger.info(
            f"Matching complete: "
            f"{response.get('matched_items', 0)}/{response.get('total_items', 0)} items matched"
        )

        return response