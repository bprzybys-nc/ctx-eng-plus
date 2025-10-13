"""Profiling utilities - performance analysis and caching.

Provides decorators and utilities for profiling function execution,
caching results, and optimizing performance bottlenecks.
"""

import cProfile
import pstats
import io
from typing import Callable, Any, Optional
import functools
from datetime import datetime, timedelta
from ce.logging_config import get_logger

logger = get_logger(__name__)


def profile_function(func: Callable) -> Callable:
    """Decorator to profile function execution.

    Args:
        func: Function to profile

    Returns:
        Wrapped function that prints profile stats

    Example:
        @profile_function
        def slow_function():
            # ... expensive operations ...

    Note: Profiles every invocation. Use selectively on suspected bottlenecks.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()

        # Print stats
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions

        logger.info(f"Profile for {func.__name__}:\n{stream.getvalue()}")

        return result

    return wrapper


def cache_result(ttl_seconds: int = 300, max_size: int = 128):
    """Decorator to cache function results with TTL and size limit.

    Args:
        ttl_seconds: Time-to-live in seconds (default: 300)
        max_size: Maximum cache entries (default: 128)

    Returns:
        Decorator function

    Example:
        @cache_result(ttl_seconds=600, max_size=256)
        def expensive_computation(x, y):
            return complex_calculation(x, y)

    Note: Uses simple dict cache. For production, consider Redis or memcached.
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_order = []  # Track insertion order for LRU

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key (args + kwargs)
            cache_key = (args, tuple(sorted(kwargs.items())))

            # Check cache
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if datetime.now() - timestamp < timedelta(seconds=ttl_seconds):
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result
                else:
                    # Expired - remove
                    del cache[cache_key]
                    cache_order.remove(cache_key)

            # Cache miss - compute
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)

            # Add to cache (with LRU eviction if needed)
            if len(cache) >= max_size:
                # Evict oldest entry
                oldest_key = cache_order.pop(0)
                del cache[oldest_key]

            cache[cache_key] = (result, datetime.now())
            cache_order.append(cache_key)

            return result

        # Add cache management methods
        wrapper.cache_clear = lambda: (cache.clear(), cache_order.clear())
        wrapper.cache_info = lambda: {
            "hits": sum(1 for k in cache_order if k in cache),
            "size": len(cache),
            "max_size": max_size,
            "ttl_seconds": ttl_seconds
        }

        return wrapper

    return decorator


def time_function(func: Callable) -> Callable:
    """Decorator to measure function execution time.

    Args:
        func: Function to time

    Returns:
        Wrapped function that logs execution time

    Example:
        @time_function
        def slow_operation():
            # ... expensive work ...

    Note: Logs timing via structured logger with duration field.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = datetime.now()

        result = func(*args, **kwargs)

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Function {func.__name__} completed",
            extra={"function": func.__name__, "duration": duration}
        )

        return result

    return wrapper


def memoize(func: Callable) -> Callable:
    """Simple memoization decorator (no TTL, no size limit).

    Args:
        func: Function to memoize

    Returns:
        Memoized function

    Example:
        @memoize
        def fibonacci(n):
            if n < 2:
                return n
            return fibonacci(n-1) + fibonacci(n-2)

    Note: Use for pure functions with deterministic output.
    For production with TTL/LRU, use cache_result instead.
    """
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = (args, tuple(sorted(kwargs.items())))

        if cache_key not in cache:
            cache[cache_key] = func(*args, **kwargs)

        return cache[cache_key]

    wrapper.cache_clear = cache.clear
    wrapper.cache_info = lambda: {"size": len(cache)}

    return wrapper


class PerformanceMonitor:
    """Monitor performance metrics across multiple function calls.

    Tracks timing data and call counts for performance analysis.

    Example:
        monitor = PerformanceMonitor()

        @monitor.track
        def operation1():
            # ... work ...

        @monitor.track
        def operation2():
            # ... work ...

        # Print summary
        monitor.print_summary()

    Attributes:
        stats: Dict of function stats (call_count, total_time, avg_time)
    """

    def __init__(self):
        """Initialize performance monitor."""
        self.stats = {}

    def track(self, func: Callable) -> Callable:
        """Decorator to track function performance.

        Args:
            func: Function to track

        Returns:
            Wrapped function that records performance stats
        """
        func_name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = datetime.now()

            result = func(*args, **kwargs)

            duration = (datetime.now() - start_time).total_seconds()

            # Update stats
            if func_name not in self.stats:
                self.stats[func_name] = {
                    "call_count": 0,
                    "total_time": 0.0,
                    "avg_time": 0.0
                }

            self.stats[func_name]["call_count"] += 1
            self.stats[func_name]["total_time"] += duration
            self.stats[func_name]["avg_time"] = (
                self.stats[func_name]["total_time"] / self.stats[func_name]["call_count"]
            )

            return result

        return wrapper

    def get_stats(self, func_name: Optional[str] = None) -> dict:
        """Get performance statistics.

        Args:
            func_name: Optional function name to filter by

        Returns:
            Dict of performance stats
        """
        if func_name:
            return self.stats.get(func_name, {})
        return self.stats

    def print_summary(self):
        """Print performance summary to logger."""
        if not self.stats:
            logger.info("No performance data collected")
            return

        summary = "\n📊 Performance Summary:\n"
        summary += "-" * 60 + "\n"
        summary += f"{'Function':<30} {'Calls':<10} {'Total(s)':<12} {'Avg(s)':<10}\n"
        summary += "-" * 60 + "\n"

        for func_name, data in sorted(self.stats.items(), key=lambda x: x[1]["total_time"], reverse=True):
            summary += f"{func_name:<30} {data['call_count']:<10} {data['total_time']:<12.3f} {data['avg_time']:<10.3f}\n"

        summary += "-" * 60

        logger.info(summary)

    def reset(self):
        """Clear all performance statistics."""
        self.stats.clear()
