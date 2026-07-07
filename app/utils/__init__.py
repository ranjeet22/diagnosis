"""
Shared utility helper functions and classes.
"""

def format_bytes_to_mb(num_bytes: int) -> float:
    """
    Utility converting raw bytes into Megabytes.
    """
    return round(num_bytes / (1024 * 1024), 2)
