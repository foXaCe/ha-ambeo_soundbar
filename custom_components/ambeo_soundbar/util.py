import asyncio
from collections.abc import Callable
from functools import wraps
import logging
from typing import Any, TypeVar

_LOGGER = logging.getLogger(__name__)

T = TypeVar("T")


def find_title_by_id(id, search_list):
    """Find title by ID from a list."""
    for source in search_list:
        if source.get("id") == id:
            return source.get("title")
    return None


def find_id_by_title(title, search_list):
    """Find ID by title from a list."""
    for source in search_list:
        if source.get("title") == title:
            return source.get("id")
    return None


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """Decorator to retry async functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation
        exceptions: Tuple of exceptions to catch and retry
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as ex:
                    last_exception = ex

                    if attempt == max_retries:
                        # Log at debug level to avoid polluting logs when device is offline
                        _LOGGER.debug(
                            "Failed after %d attempts: %s",
                            max_retries + 1,
                            ex,
                        )
                        raise

                    # Use debug level for intermediate retries
                    _LOGGER.debug(
                        "Attempt %d/%d failed: %s. Retrying in %.1fs...",
                        attempt + 1,
                        max_retries + 1,
                        ex,
                        delay,
                    )

                    await asyncio.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)

            if last_exception:
                raise last_exception
            return None

        return wrapper

    return decorator
