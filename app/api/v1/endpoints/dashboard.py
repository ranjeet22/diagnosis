from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_composition import DashboardCompositionService
from app.repositories.dashboard_repository import DashboardRepository
from app.dependencies.services import (
    get_dashboard_composition_service,
    get_dashboard_repository
)
from app.core.exceptions import DatasetNotFound
from app.core.logging import logger

router = APIRouter()


@router.get(
    "/{dataset_id}/dashboard",
    response_model=DashboardResponse,
    status_code=200,
    summary="Get dashboard configuration",
    description="Loads the cached dashboard.json. If missing from storage, it triggers the composition engine to compose and save the dashboard."
)
async def get_dataset_dashboard(
    dataset_id: str,
    service: DashboardCompositionService = Depends(get_dashboard_composition_service),
    repository: DashboardRepository = Depends(get_dashboard_repository)
) -> DashboardResponse:
    logger.info(f"Retrieve dashboard configuration request received for dataset ID: {dataset_id}")

    recalculated = False
    try:
        # Load from cache
        config = await repository.get_dashboard(dataset_id=dataset_id)
        logger.info(f"Dashboard cache hit for dataset {dataset_id}.")
    except DatasetNotFound:
        # Cache miss: compose and save dashboard
        logger.info(f"Dashboard cache miss for dataset {dataset_id}. Triggering composition engine...")
        config = await service.compose_dashboard(dataset_id=dataset_id)
        recalculated = True

    return DashboardResponse(
        dataset_id=dataset_id,
        dashboard_config=config,
        recalculated=recalculated
    )


@router.post(
    "/{dataset_id}/dashboard/rebuild",
    response_model=DashboardResponse,
    status_code=200,
    summary="Force rebuild dashboard configuration",
    description="Forces the composition engine to rebuild the dashboard configuration, mapping visual layouts, and overwriting dashboard.json."
)
async def rebuild_dataset_dashboard(
    dataset_id: str,
    service: DashboardCompositionService = Depends(get_dashboard_composition_service)
) -> DashboardResponse:
    logger.info(f"Forced dashboard rebuild requested for dataset ID: {dataset_id}")

    config = await service.compose_dashboard(dataset_id=dataset_id)

    return DashboardResponse(
        dataset_id=dataset_id,
        dashboard_config=config,
        recalculated=True
    )


@router.get(
    "/{dataset_id}/dashboard/pages",
    response_model=List[Dict[str, Any]],
    status_code=200,
    summary="Get dashboard page metadata",
    description="Returns metadata (ID, title, widget count) for all pages in the composed dashboard."
)
async def get_dataset_dashboard_pages(
    dataset_id: str,
    service: DashboardCompositionService = Depends(get_dashboard_composition_service),
    repository: DashboardRepository = Depends(get_dashboard_repository)
) -> List[Dict[str, Any]]:
    logger.info(f"Retrieve dashboard page metadata request received for dataset ID: {dataset_id}")

    try:
        config = await repository.get_dashboard(dataset_id=dataset_id)
    except DatasetNotFound:
        config = await service.compose_dashboard(dataset_id=dataset_id)

    pages_meta = []
    for page in config.dashboard.pages:
        widget_cnt = sum(len(sec.widgets) for sec in page.sections)
        pages_meta.append({
            "id": page.id,
            "title": page.title,
            "widget_count": widget_cnt
        })

    return pages_meta
