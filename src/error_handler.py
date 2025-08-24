"""
Error handling utilities for FastRTC voice agent.
"""
import asyncio
import logging
from functools import wraps
from typing import Any, Callable

from aiortc.exceptions import InvalidStateError
from loguru import logger


def handle_webrtc_errors(func: Callable) -> Callable:
    """
    Decorator to handle WebRTC connection errors gracefully.
    
    Args:
        func: Function to wrap with error handling
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except InvalidStateError as e:
            logger.error(f"WebRTC connection closed during operation in {func.__name__}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except InvalidStateError as e:
            logger.error(f"WebRTC connection closed during operation in {func.__name__}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def patch_fastrtc_logging():
    """
    Patch FastRTC logging to handle InvalidStateError gracefully.
    This logs the error but allows the process to continue.
    """
    # Patch the asyncio.run call in FastRTC's logging
    original_run = asyncio.run
    
    def safe_run(coro):
        try:
            return original_run(coro)
        except InvalidStateError as e:
            logger.error(f"FastRTC logging failed - data channel closed: {e}")
            # Continue execution instead of crashing
            return None
        except Exception as e:
            logger.error(f"FastRTC logging error: {e}")
            # Re-raise other exceptions
            raise
    
    asyncio.run = safe_run