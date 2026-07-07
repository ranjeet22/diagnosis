from fastapi import APIRouter, Depends
from app.schemas.profile import ProfileResponse
from app.analytics.profiler import DatasetProfiler
from app.repositories.profile_repository import ProfileRepository
from app.dependencies.services import get_dataset_profiler, get_profile_repository
from app.core.exceptions import DatasetNotFound
from app.core.logging import logger

router = APIRouter()


@router.get(
    "/{dataset_id}/profile",
    response_model=ProfileResponse,
    status_code=200,
    summary="Get dataset profile schema and data quality analysis",
    description="Attempts to fetch the cached profile for the dataset. If missing, it triggers the profiling engine to build, save, and return the profile."
)
async def get_dataset_profile(
    dataset_id: str,
    profiler: DatasetProfiler = Depends(get_dataset_profiler),
    repository: ProfileRepository = Depends(get_profile_repository)
) -> ProfileResponse:
    logger.info(f"Retrieve profile request received for dataset ID: {dataset_id}")
    
    recalculated = False
    try:
        # Check cache (try reading JSON from storage)
        profile = await repository.get_profile(dataset_id=dataset_id)
        logger.info(f"Profile cache hit for dataset {dataset_id}.")
    except DatasetNotFound:
        # Cache miss: generate and persist the profile
        logger.info(f"Profile cache miss for dataset {dataset_id}. Triggering profiling engine...")
        profile = await profiler.profile_dataset(dataset_id=dataset_id)
        await repository.save_profile(dataset_id=dataset_id, profile=profile)
        recalculated = True
        
    return ProfileResponse(
        dataset_id=dataset_id,
        profile=profile,
        recalculated=recalculated
    )


@router.post(
    "/{dataset_id}/profile/refresh",
    response_model=ProfileResponse,
    status_code=200,
    summary="Force refresh / rebuild dataset profile",
    description="Forces the profiling engine to re-run calculations over the dataset on disk, overwriting the cached profile.json."
)
async def refresh_dataset_profile(
    dataset_id: str,
    profiler: DatasetProfiler = Depends(get_dataset_profiler),
    repository: ProfileRepository = Depends(get_profile_repository)
) -> ProfileResponse:
    logger.info(f"Force profile refresh requested for dataset ID: {dataset_id}")
    
    profile = await profiler.profile_dataset(dataset_id=dataset_id)
    await repository.save_profile(dataset_id=dataset_id, profile=profile)
    
    return ProfileResponse(
        dataset_id=dataset_id,
        profile=profile,
        recalculated=True
    )
