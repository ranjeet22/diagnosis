from enum import Enum
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class UploadStatus(str, Enum):
    """
    Enums tracking the lifecycle and processing stages of an uploaded dataset.
    """
    UPLOADED = "UPLOADED"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"
    # Future placeholders (e.g. CLEANED, PROFILED, ANALYZED)
    PROFILED = "PROFILED"
    CLEANED = "CLEANED"


class StorageResult(BaseModel):
    """
    Result properties returned by the storage provider upon saving a dataset.
    """
    dataset_id: str = Field(..., description="Unique UUID assigned to the dataset upload session.")
    stored_filename: str = Field(..., description="The filename under which the dataset is saved in storage.")
    file_size: int = Field(..., description="Size of the stored file in bytes.")
    storage_path: str = Field(..., description="Fully resolved path or URI representing the stored file location.")


class DatasetMetadata(BaseModel):
    """
    Comprehensive dataset metadata details generated during ingestion and profiling.
    """
    dataset_id: str = Field(..., description="Unique UUID assigned to the dataset.")
    original_filename: str = Field(..., description="The original filename uploaded by the user.")
    stored_filename: str = Field(..., description="The filename of the stored file.")
    upload_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp indicating when the upload completed.")
    file_size: int = Field(..., description="Size of the uploaded file in bytes.")
    encoding: str = Field(..., description="String character encoding detected for the dataset (e.g. utf-8, windows-1252).")
    delimiter: str = Field(..., description="Detected field separator delimiter character (e.g. ',', ';', '\\t').")
    rows: int = Field(..., description="Count of parsed data rows (excluding headers).")
    columns: int = Field(..., description="Count of columns found in the dataset.")
    column_names: List[str] = Field(..., description="Ordered list of column header labels.")
    storage_path: str = Field(..., description="Local path or cloud bucket URI referencing the dataset file.")
    status: UploadStatus = Field(default=UploadStatus.UPLOADED, description="Current lifecycle processing status.")
    initial_processing_state: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary for downstream status updates.")


class UploadResponse(BaseModel):
    """
    API Response model returned immediately upon successful dataset upload and metadata extraction.
    """
    dataset_id: str = Field(..., description="The generated unique ID for the uploaded dataset.")
    filename: str = Field(..., description="The original filename uploaded.")
    status: UploadStatus = Field(..., description="Status of the dataset lifecycle.")
    rows: int = Field(..., description="Number of rows parsed.")
    columns: int = Field(..., description="Number of columns parsed.")


class UploadRequest(BaseModel):
    """
    Pydantic schema representing any additional metadata or query options passed during upload.
    """
    description: Optional[str] = Field(None, description="Optional brief description of the dataset contents.")
