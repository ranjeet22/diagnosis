from fastapi import APIRouter, Depends
from app.schemas.plan import AnalyticsPlanResponse
from app.services.analytics_planning import AnalyticsPlanningService
from app.repositories.plan_repository import AnalyticsPlanRepository
from app.dependencies.services import get_analytics_planning_service, get_analytics_plan_repository
from app.core.exceptions import DatasetNotFound
from app.core.logging import logger

router = APIRouter()


@router.get(
    "/{dataset_id}/analytics-plan",
    response_model=AnalyticsPlanResponse,
    status_code=200,
    summary="Get analytics execution plan",
    description="Loads the cached analytics_plan.json for a dataset. If cache is missing, it triggers the analytics planner to generate, save, and return the plan."
)
async def get_dataset_analytics_plan(
    dataset_id: str,
    service: AnalyticsPlanningService = Depends(get_analytics_planning_service),
    repository: AnalyticsPlanRepository = Depends(get_analytics_plan_repository)
) -> AnalyticsPlanResponse:
    logger.info(f"Retrieve analytics plan request received for dataset ID: {dataset_id}")

    recalculated = False
    try:
        # Load from cache
        plan = await repository.get_plan(dataset_id=dataset_id)
        logger.info(f"Analytics plan cache hit for dataset {dataset_id}.")
    except DatasetNotFound:
        # Cache miss: generate and persist plan
        logger.info(f"Analytics plan cache miss for dataset {dataset_id}. Running planning service...")
        plan = await service.generate_plan(dataset_id=dataset_id)
        recalculated = True

    return AnalyticsPlanResponse(
        dataset_id=dataset_id,
        analytics_plan=plan,
        recalculated=recalculated
    )


@router.post(
    "/{dataset_id}/analytics-plan/rebuild",
    response_model=AnalyticsPlanResponse,
    status_code=200,
    summary="Forced rebuild of analytics execution plan",
    description="Forces the analytics planning engine to run, rebuilding the execution plan from the profile and semantic model. Overwrites the cached analytics_plan.json."
)
async def rebuild_dataset_analytics_plan(
    dataset_id: str,
    service: AnalyticsPlanningService = Depends(get_analytics_planning_service)
) -> AnalyticsPlanResponse:
    logger.info(f"Forced analytics plan rebuild requested for dataset ID: {dataset_id}")

    plan = await service.generate_plan(dataset_id=dataset_id)

    return AnalyticsPlanResponse(
        dataset_id=dataset_id,
        analytics_plan=plan,
        recalculated=True
    )
