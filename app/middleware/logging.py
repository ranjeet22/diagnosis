import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that intercepts incoming HTTP requests and logs execution metrics,
    including paths, status codes, methods, and durations.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        
        # Log request receipt
        client_host = request.client.host if request.client else "unknown"
        logger.debug(
            f"Incoming request: {request.method} {request.url.path} from {client_host}"
        )
        
        try:
            response = await call_next(request)
            
            process_time = (time.perf_counter() - start_time) * 1000  # in ms
            
            # Log successful response metrics
            logger.info(
                f"Completed: {request.method} {request.url.path} | "
                f"Status: {response.status_code} | "
                f"Duration: {process_time:.2f}ms"
            )
            return response
            
        except Exception as e:
            process_time = (time.perf_counter() - start_time) * 1000
            
            # Log uncaught middleware exceptions
            logger.error(
                f"Failed: {request.method} {request.url.path} | "
                f"Error: {str(e)} | "
                f"Duration: {process_time:.2f}ms",
                exc_info=True
            )
            raise e
