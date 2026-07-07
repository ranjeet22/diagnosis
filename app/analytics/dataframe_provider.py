import pandas as pd
from typing import Union
from app.core.logging import logger
from app.core.config import settings

# Global state tracking if GPU acceleration via cuDF is functional
_GPU_AVAILABLE = False

# Try importing and initializing cuDF if settings allow it
if settings.GPU_ENABLED:
    try:
        import cudf
        # Validate that cuDF is functional (avoids issues when CUDA is missing at runtime)
        test_df = cudf.DataFrame({"a": [1]})
        _GPU_AVAILABLE = True
        logger.info("cuDF GPU acceleration successfully initialized.")
    except Exception as e:
        logger.warning(
            f"cuDF was imported but GPU initialization failed: {e}. "
            "Falling back to standard CPU Pandas execution."
        )
else:
    logger.info("GPU acceleration is disabled in settings. Using standard CPU Pandas execution.")


def is_gpu_enabled() -> bool:
    """Returns True if the backend is currently using cuDF GPU acceleration."""
    return _GPU_AVAILABLE


def load_dataset_df(
    file_path: str, delimiter: str = ",", encoding: str = "utf-8"
) -> Union[pd.DataFrame, "cudf.DataFrame"]: # type: ignore
    """
    Loads a dataset CSV from disk into a DataFrame.
    Uses cuDF if GPU acceleration is active and working; falls back to standard pandas.
    """
    if _GPU_AVAILABLE:
        try:
            import cudf
            logger.debug(f"Loading dataset via cuDF: {file_path}")
            return cudf.read_csv(file_path, sep=delimiter, encoding=encoding)
        except Exception as e:
            logger.error(
                f"cuDF read_csv failed for path '{file_path}': {e}. "
                "Retrying with standard pandas CPU fallback..."
            )
            # Failover to pandas below
            
    logger.debug(f"Loading dataset via Pandas (CPU): {file_path}")
    return pd.read_csv(file_path, sep=delimiter, encoding=encoding)
