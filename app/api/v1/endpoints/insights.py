from fastapi import APIRouter, Depends
from app.schemas.insight import InsightResponse
from app.services.insight_generation import InsightGenerationService
from app.repositories.insight_repository import InsightRepository
from app.dependencies.services import (
    get_insight_generation_service,
    get_insight_repository
)
from app.core.exceptions import DatasetNotFound
from app.core.logging import logger

router = APIRouter()


@router.get(
    "/{dataset_id}/insights",
    response_model=InsightResponse,
    status_code=200,
    summary="Get AI insights",
    description="Loads the cached AI insights.json. If missing from storage, it triggers the engine to generate new insights."
)
async def get_dataset_insights(
    dataset_id: str,
    service: InsightGenerationService = Depends(get_insight_generation_service),
    repository: InsightRepository = Depends(get_insight_repository)
) -> InsightResponse:
    logger.info(f"Retrieve AI insights request received for dataset ID: {dataset_id}")

    recalculated = False
    try:
        # Load from cache
        config = await repository.get_insights(dataset_id=dataset_id)
        logger.info(f"Insights cache hit for dataset {dataset_id}.")
    except DatasetNotFound:
        # Cache miss: generate and save insights
        logger.info(f"Insights cache miss for dataset {dataset_id}. Triggering generation engine...")
        config = await service.generate_insights(dataset_id=dataset_id, force=False)
        recalculated = True

    return InsightResponse(
        dataset_id=dataset_id,
        insights=config,
        recalculated=recalculated
    )


@router.post(
    "/{dataset_id}/insights/generate",
    response_model=InsightResponse,
    status_code=200,
    summary="Generate AI insights",
    description="Runs the AI generation engine to explain deterministic outcomes. Respects cache unless results are newer."
)
async def generate_dataset_insights(
    dataset_id: str,
    service: InsightGenerationService = Depends(get_insight_generation_service)
) -> InsightResponse:
    logger.info(f"AI insights generation requested for dataset ID: {dataset_id}")

    config = await service.generate_insights(dataset_id=dataset_id, force=False)

    return InsightResponse(
        dataset_id=dataset_id,
        insights=config,
        recalculated=True
    )


@router.post(
    "/{dataset_id}/insights/refresh",
    response_model=InsightResponse,
    status_code=200,
    summary="Force regenerate AI insights",
    description="Forces the AI generation engine to regenerate insights, bypassing caching checks."
)
async def refresh_dataset_insights(
    dataset_id: str,
    service: InsightGenerationService = Depends(get_insight_generation_service)
) -> InsightResponse:
    logger.info(f"Forced AI insights refresh requested for dataset ID: {dataset_id}")

    config = await service.generate_insights(dataset_id=dataset_id, force=True)

    return InsightResponse(
        dataset_id=dataset_id,
        insights=config,
        recalculated=True
    )
