from fastapi import APIRouter, Depends
from app.schemas.results import AnalyticsResultResponse
from app.services.analytics_execution import AnalyticsExecutionService
from app.repositories.result_repository import AnalyticsResultRepository
from app.dependencies.services import get_analytics_execution_service, get_analytics_result_repository
from app.core.exceptions import DatasetNotFound
from app.core.logging import logger

router = APIRouter()


@router.get(
    "/{dataset_id}/analytics",
    response_model=AnalyticsResultResponse,
    status_code=200,
    summary="Get computed analytics results",
    description="Loads the cached analytics_results.json for a dataset. If cache is missing, it triggers the analytics execution engine to compute, save, and return the results."
)
async def get_dataset_analytics_results(
    dataset_id: str,
    service: AnalyticsExecutionService = Depends(get_analytics_execution_service),
    repository: AnalyticsResultRepository = Depends(get_analytics_result_repository)
) -> AnalyticsResultResponse:
    logger.info(f"Retrieve analytics results request received for dataset ID: {dataset_id}")

    recalculated = False
    try:
        # Load from cache
        results = await repository.get_results(dataset_id=dataset_id)
        logger.info(f"Analytics results cache hit for dataset {dataset_id}.")
    except DatasetNotFound:
        # Cache miss: compute and persist results
        logger.info(f"Analytics results cache miss for dataset {dataset_id}. Running execution service...")
        results = await service.execute_analytics(dataset_id=dataset_id)
        recalculated = True

    return AnalyticsResultResponse(
        dataset_id=dataset_id,
        analytics_results=results,
        recalculated=recalculated
    )


@router.post(
    "/{dataset_id}/analytics/run",
    response_model=AnalyticsResultResponse,
    status_code=200,
    summary="Execute analytics plan",
    description="Loads the execution plan, runs the calculations, saves the computed statistics, and returns the analytics results."
)
async def run_dataset_analytics(
    dataset_id: str,
    service: AnalyticsExecutionService = Depends(get_analytics_execution_service)
) -> AnalyticsResultResponse:
    logger.info(f"Run analytics execution requested for dataset ID: {dataset_id}")

    results = await service.execute_analytics(dataset_id=dataset_id)

    return AnalyticsResultResponse(
        dataset_id=dataset_id,
        analytics_results=results,
        recalculated=True
    )


@router.post(
    "/{dataset_id}/analytics/refresh",
    response_model=AnalyticsResultResponse,
    status_code=200,
    summary="Forced recomputation of analytics",
    description="Forces the execution engine to recompute the analytics results, overwriting the cached analytics_results.json."
)
async def refresh_dataset_analytics(
    dataset_id: str,
    service: AnalyticsExecutionService = Depends(get_analytics_execution_service)
) -> AnalyticsResultResponse:
    logger.info(f"Forced analytics refresh requested for dataset ID: {dataset_id}")

    results = await service.execute_analytics(dataset_id=dataset_id)

    return AnalyticsResultResponse(
        dataset_id=dataset_id,
        analytics_results=results,
        recalculated=True
    )
