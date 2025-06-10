from fastapi import APIRouter, Depends, HTTPException
import logging

from src.api.dependencies import verify_api_key
from src.models.tender import TenderRequest
from src.services.orchestrator import TenderOrchestrator
from src.services.service_client import ServiceClient
from src.core.exceptions import ServiceUnavailable, ServiceError, ProcessingError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/process-tender")
async def process_tender(
        tender: TenderRequest,
        api_key: str = Depends(verify_api_key)
):
    """
    Обработать тендер через все сервисы:
    1. Классификация ОКПД2
    2. Стандартизация характеристик
    3. Подбор подходящих товаров
    """
    try:
        async with ServiceClient() as client:
            orchestrator = TenderOrchestrator(client)
            result = await orchestrator.process_tender(tender)
            return result

    except ServiceUnavailable as e:
        logger.error(f"Service unavailable: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

    except ServiceError as e:
        logger.error(f"Service error: {str(e)}")
        raise HTTPException(status_code=502, detail=str(e))

    except ProcessingError as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")