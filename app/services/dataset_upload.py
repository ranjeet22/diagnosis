import io
import csv
import uuid
import chardet
from datetime import datetime, timezone
from typing import Tuple, List
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import (
    DatasetTooLarge,
    EmptyDataset,
    InvalidCSV,
    InvalidEncoding,
    UnsupportedFormat
)
from app.core.logging import logger
from app.schemas.dataset import DatasetMetadata, UploadStatus, UploadResponse
from app.storage.interface import StorageInterface


class DatasetUploadService:
    """
    Service responsible for validating uploaded healthcare datasets,
    extracting metadata (dimensions, encoding, headers, delimiter),
    and saving the dataset and metadata to the registered storage provider.
    """
    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    async def upload_dataset(self, file: UploadFile) -> UploadResponse:
        """
        Orchestrates the validation, parsing, metadata extraction, and storage
        of a raw CSV dataset.
        
        Args:
            file: The FastAPI UploadFile stream.
            
        Returns:
            UploadResponse schema containing ID, dimensions, and status.
        """
        dataset_id = str(uuid.uuid4())
        logger.info(f"Initiating upload process for file: {file.filename} (assigned id: {dataset_id})")

        # 1. Validate File Extension and MIME Type
        self._validate_file_type(file)

        # 2. Read file contents and validate file size
        content = await file.read()
        file_size = len(content)
        self._validate_file_size(file_size)

        # 3. Detect and validate string encoding
        encoding = self._detect_encoding(content)
        decoded_content = self._decode_content(content, encoding)

        # 4. Detect CSV delimiter and parse dimensions/headers
        delimiter, column_names, row_count = self._parse_csv_structure(decoded_content)

        # 5. Write raw CSV file to storage
        storage_result = await self.storage.save_file(
            dataset_id=dataset_id,
            filename="original.csv",
            content=content
        )

        # 6. Generate metadata structure
        metadata = DatasetMetadata(
            dataset_id=dataset_id,
            original_filename=file.filename or "unknown.csv",
            stored_filename=storage_result.stored_filename,
            upload_timestamp=datetime.now(timezone.utc),
            file_size=file_size,
            encoding=encoding,
            delimiter=delimiter,
            rows=row_count,
            columns=len(column_names),
            column_names=column_names,
            storage_path=storage_result.storage_path,
            status=UploadStatus.VALIDATED,
            initial_processing_state={"ingested_by": "DatasetUploadService"}
        )

        # 7. Write metadata to storage
        await self.storage.save_metadata(dataset_id=dataset_id, metadata=metadata)
        logger.info(f"Successfully ingested and registered dataset {dataset_id} ({row_count} rows, {len(column_names)} cols)")

        return UploadResponse(
            dataset_id=dataset_id,
            filename=metadata.original_filename,
            status=metadata.status,
            rows=metadata.rows,
            columns=metadata.columns
        )

    def _validate_file_type(self, file: UploadFile) -> None:
        """Enforces CSV file extensions and basic MIME type structures."""
        filename = file.filename or ""
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        
        # Valid CSV extensions
        allowed_extensions = {"csv"}
        # Valid CSV MIME types
        allowed_mimes = {
            "text/csv",
            "application/csv",
            "text/plain",
            "application/vnd.ms-excel",
            "application/octet-stream"  # generic binary fallback
        }

        if ext not in allowed_extensions:
            logger.warning(f"Rejected upload due to extension: '{ext}'")
            raise UnsupportedFormat(f"Unsupported file format '.{ext}'. Only CSV is supported.")

        if file.content_type and file.content_type not in allowed_mimes:
            logger.warning(f"Rejected upload due to MIME type: '{file.content_type}'")
            raise UnsupportedFormat(f"Unsupported media type '{file.content_type}'.")

    def _validate_file_size(self, size: int) -> None:
        """Enforces non-empty content and maximum size limits."""
        if size == 0:
            logger.warning("Rejected empty file upload.")
            raise EmptyDataset("The uploaded file is empty.")

        max_bytes = settings.STORAGE_MAX_FILE_SIZE_MB * 1024 * 1024
        if size > max_bytes:
            logger.warning(f"Rejected file size: {size} bytes (limit: {max_bytes} bytes)")
            raise DatasetTooLarge(
                f"File size exceeds the limit of {settings.STORAGE_MAX_FILE_SIZE_MB}MB."
            )

    def _detect_encoding(self, content: bytes) -> str:
        """Heuristically determines the string character encoding of raw bytes."""
        # Grab a snippet to avoid scanning very large files entirely
        snippet = content[:50000]
        detection = chardet.detect(snippet)
        encoding = detection.get("encoding")
        confidence = detection.get("confidence", 0)

        if not encoding or confidence < 0.5:
            # Fallback to UTF-8 if confidence is low
            return "utf-8"
        return encoding.lower()

    def _decode_content(self, content: bytes, detected_encoding: str) -> str:
        """Attempts decoding using detected and fallback encodings."""
        encodings_to_try = [detected_encoding, "utf-8", "latin-1", "windows-1252"]
        
        # Remove duplicates while preserving order
        encodings_to_try = list(dict.fromkeys(encodings_to_try))

        for enc in encodings_to_try:
            try:
                decoded = content.decode(enc)
                logger.debug(f"Successfully decoded content using encoding: {enc}")
                return decoded
            except UnicodeDecodeError:
                continue

        logger.error("All character encoding decode attempts failed.")
        raise InvalidEncoding("Could not decode dataset file. Ensure it is a valid text/CSV encoding.")

    def _parse_csv_structure(self, content: str) -> Tuple[str, List[str], int]:
        """
        Parses CSV structure to resolve headers, count rows, and identify delimiter.
        Does not load whole row data array in memory to save system resources.
        """
        # Take a sample for delimiter sniffing
        sample_size = min(len(content), 10000)
        sample = content[:sample_size]

        # 1. Delimiter Sniffing
        delimiter = ","
        try:
            # Clean up double double-quotes which confuse the sniffer
            clean_sample = sample.replace('""', '"')
            dialect = csv.Sniffer().sniff(clean_sample)
            if dialect.delimiter in {",", ";", "\t", "|"}:
                delimiter = dialect.delimiter
        except Exception:
            # Fallback heuristic: count frequency of characters in first line
            first_line = sample.split("\n")[0]
            candidates = [",", ";", "\t", "|"]
            counts = {c: first_line.count(c) for c in candidates}
            max_cand = max(counts, key=counts.get) # type: ignore
            if counts[max_cand] > 0:
                delimiter = max_cand
        
        logger.debug(f"Detected CSV delimiter: {repr(delimiter)}")

        # 2. Parse Rows & Columns
        f = io.StringIO(content)
        reader = csv.reader(f, delimiter=delimiter)

        try:
            column_names = next(reader)
        except StopIteration:
            raise EmptyDataset("Dataset contains no headers or rows.")

        # Clean headers (strip spaces, resolve empty column names)
        column_names = [col.strip() for col in column_names]
        if not column_names or all(c == "" for c in column_names):
            raise InvalidCSV("CSV does not contain any valid column headers.")

        # Count data rows (skipping trailing empty lines)
        row_count = 0
        expected_cols = len(column_names)
        
        for idx, row in enumerate(reader, start=2):
            # Check for empty rows
            if not row or all(cell.strip() == "" for cell in row):
                continue
            
            # Enforce strict column counts for all data rows
            if len(row) != expected_cols:
                logger.warning(f"Row {idx} column count mismatch: expected {expected_cols}, got {len(row)}")
                raise InvalidCSV(f"Malformed CSV: Row {idx} has {len(row)} columns, expected {expected_cols}.")

            row_count += 1

        if row_count == 0:
            raise EmptyDataset("CSV contains headers but no data rows.")

        return delimiter, column_names, row_count
