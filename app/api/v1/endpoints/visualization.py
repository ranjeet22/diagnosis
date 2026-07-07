from fastapi import APIRouter, Depends, Query
from app.schemas.visualization import VisualizationPlanResponse
from app.services.visualization_recommendation import VisualizationRecommendationService
from app.repositories.visualization_repository import VisualizationRepository
from app.dependencies.services import (
    get_visualization_recommendation_service,
    get_visualization_repository
)
from app.core.exceptions import DatasetNotFound
from app.core.logging import logger

router = APIRouter()


@router.get(
    "/{dataset_id}/visualization-plan",
    response_model=VisualizationPlanResponse,
    status_code=200,
    summary="Get computed visualization plan",
    description="Loads the cached visualization_plan.json. If missing from storage, it triggers the visualization engine to recommend and save plans."
)
async def get_dataset_visualization_plan(
    dataset_id: str,
    theme: str = Query("light", description="Theme recommendation layout: 'light' or 'dark'"),
    accessibility: str = Query("default", description="Accessibility overrides: 'default', 'color_blind', 'high_contrast', 'print'"),
    service: VisualizationRecommendationService = Depends(get_visualization_recommendation_service),
    repository: VisualizationRepository = Depends(get_visualization_repository)
) -> VisualizationPlanResponse:
    logger.info(f"Retrieve visualization plan request received for dataset ID: {dataset_id}")

    recalculated = False
    try:
        # Load from cache
        plan = await repository.get_plan(dataset_id=dataset_id)
        logger.info(f"Visualization plan cache hit for dataset {dataset_id}.")
    except DatasetNotFound:
        # Cache miss: generate and save plan
        logger.info(f"Visualization plan cache miss for dataset {dataset_id}. Triggering recommendation engine...")
        plan = await service.generate_visualization_plan(
            dataset_id=dataset_id,
            theme_name=theme,
            accessibility_mode=accessibility
        )
        recalculated = True

    return VisualizationPlanResponse(
        dataset_id=dataset_id,
        visualization_plan=plan,
        recalculated=recalculated
    )


@router.post(
    "/{dataset_id}/visualization-plan/rebuild",
    response_model=VisualizationPlanResponse,
    status_code=200,
    summary="Force rebuild visualization plan",
    description="Forces the recommendation engine to regenerate the visualization plan, updating theme colors and legends definitions, overwriting visualization_plan.json."
)
async def rebuild_dataset_visualization_plan(
    dataset_id: str,
    theme: str = Query("light", description="Theme recommendation layout: 'light' or 'dark'"),
    accessibility: str = Query("default", description="Accessibility overrides: 'default', 'color_blind', 'high_contrast', 'print'"),
    service: VisualizationRecommendationService = Depends(get_visualization_recommendation_service)
) -> VisualizationPlanResponse:
    logger.info(f"Forced visualization plan rebuild requested for dataset ID: {dataset_id}")

    plan = await service.generate_visualization_plan(
        dataset_id=dataset_id,
        theme_name=theme,
        accessibility_mode=accessibility
    )

    return VisualizationPlanResponse(
        dataset_id=dataset_id,
        visualization_plan=plan,
        recalculated=True
    )
