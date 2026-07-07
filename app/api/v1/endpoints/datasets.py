from fastapi import APIRouter, File, UploadFile, Depends
from app.schemas.dataset import UploadResponse, DatasetMetadata
from app.services.dataset_upload import DatasetUploadService
from app.dependencies.services import get_dataset_upload_service
from app.storage.interface import StorageInterface
from app.dependencies.storage import get_storage_provider
from app.core.logging import logger

router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=201,
    summary="Upload and validate a healthcare dataset",
    description="Accepts a multipart form-data CSV upload, validates dimensions/encoding/size, extracts metadata, and saves raw file + metadata to storage."
)
async def upload_dataset(
    file: UploadFile = File(..., description="Healthcare CSV dataset file (Max 50MB)"),
    service: DatasetUploadService = Depends(get_dataset_upload_service)
) -> UploadResponse:
    logger.info(f"Received file upload request: {file.filename}")
    return await service.upload_dataset(file)


@router.get(
    "/{dataset_id}",
    response_model=DatasetMetadata,
    status_code=200,
    summary="Retrieve dataset metadata",
    description="Fetches extracted headers, row/column counts, delimiter, and other metadata properties for a given dataset UUID."
)
async def get_dataset_metadata(
    dataset_id: str,
    storage: StorageInterface = Depends(get_storage_provider)
) -> DatasetMetadata:
    logger.info(f"Received metadata query for dataset ID: {dataset_id}")
    return await storage.get_metadata(dataset_id)
