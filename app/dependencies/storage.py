from functools import lru_cache
from app.core.config import settings
from app.storage.interface import StorageInterface
from app.storage.local import LocalStorageProvider


@lru_cache()
def get_storage_provider() -> StorageInterface:
    """
    Dependency provider that returns a singleton StorageInterface instance.
    Determines provider type (local or gcs) from application settings.
    """
    if settings.STORAGE_TYPE.lower() == "gcs":
        # Future TODO: Import and return GCSStorageProvider
        # For now, fallback to local storage or raise exception
        pass
        
    # Default local storage provider
    return LocalStorageProvider(upload_dir=settings.STORAGE_LOCAL_DIR)
