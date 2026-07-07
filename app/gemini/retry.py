import asyncio
from typing import Callable, Any
from app.core.logging import logger


class RetryManager:
    """
    Orchestrates retry logic, timeout tracking, and exponential backoff
    for external API calls, safeguarding the platform from rate limit throttling.
    """

    @staticmethod
    async def execute_with_retry(
        func: Callable[[], Any],
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0
    ) -> Any:
        """
        Executes an async task function with retries and exponential delays.
        """
        delay = initial_delay
        last_exception = None

        for attempt in range(1, max_retries + 1):
            try:
                logger.debug(f"RetryManager: Attempt {attempt} of {max_retries}...")
                return await func()
            except Exception as e:
                last_exception = e
                # Check if it looks like a rate limit error (status 429) or connection error
                e_msg = str(e).lower()
                is_rate_limit = "rate limit" in e_msg or "429" in e_msg
                
                if attempt == max_retries:
                    logger.error(f"RetryManager: Failed after {max_retries} attempts. Last error: {e}")
                    break

                logger.warning(
                    f"RetryManager: Attempt {attempt} failed: {e}. "
                    f"Retrying in {delay:.2f}s (RateLimit={is_rate_limit})..."
                )
                
                # Sleep with exponential delay
                await asyncio.sleep(delay)
                delay *= backoff_factor
                if is_rate_limit:
                    # Give extra delay cushion for rate limits
                    delay += 1.0

        raise last_exception
