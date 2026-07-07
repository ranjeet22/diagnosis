class DiagnosisException(Exception):
    """Base exception class for all errors in the Diagnōsis platform."""
    def __init__(self, message: str, details: dict = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


# ==========================================
# Core & Configuration Errors
# ==========================================

class ConfigurationError(DiagnosisException):
    """Raised when application configuration is invalid or missing."""
    pass


# ==========================================
# Validation & Ingestion Errors
# ==========================================

class ValidationError(DiagnosisException):
    """Base exception for input or schema validation failures."""
    pass


class DatasetTooLarge(ValidationError):
    """Raised when the uploaded dataset exceeds size limitations."""
    pass


class InvalidCSV(ValidationError):
    """Raised when CSV parser fails to parse structure, delimiter, or columns."""
    pass


class InvalidEncoding(ValidationError):
    """Raised when the uploaded dataset does not match supported string encodings."""
    pass


class UnsupportedFormat(ValidationError):
    """Raised when file extension or MIME type is not supported."""
    pass


class EmptyDataset(ValidationError):
    """Raised when the uploaded dataset contains no rows/data."""
    pass


class DatasetNotFound(DiagnosisException):
    """Raised when looking for a dataset UUID that does not exist in storage."""
    pass


# ==========================================
# Storage & Data Errors
# ==========================================

class StorageFailure(DiagnosisException):
    """Raised when local filesystem or cloud bucket operations fail."""
    pass


class DatabaseError(DiagnosisException):
    """Raised when analytics store (BigQuery or equivalent) queries fail."""
    pass


# ==========================================
# Processing, Analytics, and AI Errors
# ==========================================

class AnalyticsError(DiagnosisException):
    """Raised when deterministic computation/statistics generation fails."""
    pass


class AIError(DiagnosisException):
    """Raised when Gemini or LLM API processing encounters problems."""
    pass
