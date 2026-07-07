from fastapi import APIRouter, Depends
from app.schemas.semantic import SemanticModelResponse
from app.services.semantic_mapping import SemanticMappingService
from app.repositories.semantic_repository import SemanticModelRepository
from app.dependencies.services import get_semantic_mapping_service, get_semantic_model_repository
from app.core.exceptions import DatasetNotFound
from app.core.logging import logger

router = APIRouter()


@router.get(
    "/{dataset_id}/semantic-model",
    response_model=SemanticModelResponse,
    status_code=200,
    summary="Get healthcare semantic model",
    description="Loads the cached semantic model.json for a dataset. If cache is missing, it triggers the semantic builder to generate, save, and return the model."
)
async def get_dataset_semantic_model(
    dataset_id: str,
    service: SemanticMappingService = Depends(get_semantic_mapping_service),
    repository: SemanticModelRepository = Depends(get_semantic_model_repository)
) -> SemanticModelResponse:
    logger.info(f"Retrieve semantic model request received for dataset ID: {dataset_id}")
    
    recalculated = False
    try:
        # Load from cache
        model = await repository.get_model(dataset_id=dataset_id)
        logger.info(f"Semantic model cache hit for dataset {dataset_id}.")
    except DatasetNotFound:
        # Cache miss: generate and persist model
        logger.info(f"Semantic model cache miss for dataset {dataset_id}. Running semantic mapping service...")
        model = await service.generate_semantic_model(dataset_id=dataset_id)
        recalculated = True
        
    return SemanticModelResponse(
        dataset_id=dataset_id,
        semantic_model=model,
        recalculated=recalculated
    )


@router.post(
    "/{dataset_id}/semantic-model/rebuild",
    response_model=SemanticModelResponse,
    status_code=200,
    summary="Forced rebuild of semantic model",
    description="Forces the mapping engine to run, rebuilding the healthcare semantic model from the dataset profile. Overwrites the cached semantic_model.json."
)
async def rebuild_dataset_semantic_model(
    dataset_id: str,
    service: SemanticMappingService = Depends(get_semantic_mapping_service)
) -> SemanticModelResponse:
    logger.info(f"Forced semantic model rebuild requested for dataset ID: {dataset_id}")
    
    model = await service.generate_semantic_model(dataset_id=dataset_id)
    
    return SemanticModelResponse(
        dataset_id=dataset_id,
        semantic_model=model,
        recalculated=True
    )
