import os
import sys
import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict
from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs log records as single-line JSON structures.
    Useful for production log aggregation systems (e.g. Stackdriver, ELK).
    """
    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Capture extra fields if passed
        if hasattr(record, "extra") and isinstance(record.extra, dict): # type: ignore
            log_payload.update(record.extra) # type: ignore
            
        # Capture exception info if available
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_payload)


def setup_logging() -> None:
    """
    Configure global logging configuration with console and file handlers.
    Creates log directory if it does not exist.
    """
    log_level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    
    level = log_level_map.get(settings.LOG_LEVEL.lower(), logging.INFO)
    
    # Ensure log directory exists
    log_dir = os.path.dirname(settings.LOG_FILE_PATH)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Define formatter based on settings
    if settings.LOG_FORMAT.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z"
        )
        
    # Console Handler (Stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File Handler
    try:
        file_handler = logging.FileHandler(settings.LOG_FILE_PATH, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to initialize file logger: {e}", file=sys.stderr)


# Run setup on import to configure logs for the app
setup_logging()

# Export a default logger instance
logger = logging.getLogger("diagnosis")
