"""Rate limiting service for HN API."""

import asyncio
import time
from collections import deque


class RateLimiter:
    """Token bucket rate limiter for API requests.

    Implements token bucket algorithm to respect HN API rate limits
    (10,000 requests/hour per IP).
    """

    def __init__(self, max_requests: int = 10000, time_window: float = 3600.0) -> None:
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds (default: 1 hour)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self._requests: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to make a request.

        Blocks if rate limit is exceeded until a slot becomes available.
        """
        async with self._lock:
            now = time.time()

            # Remove old requests outside the time window
            while self._requests and self._requests[0] < now - self.time_window:
                self._requests.popleft()

            # Check if we're at the limit
            if len(self._requests) >= self.max_requests:
                # Calculate wait time until oldest request expires
                wait_time = (self._requests[0] + self.time_window) - now
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    # Try again after waiting
                    await self.acquire()
                    return

            # Record this request
            self._requests.append(now)

    def get_remaining(self) -> int:
        """Get number of remaining requests in current window.

        Returns:
            Number of requests available
        """
        now = time.time()

        # Count valid requests in current window
        valid_requests = sum(1 for req_time in self._requests if req_time >= now - self.time_window)

        return max(0, self.max_requests - valid_requests)

    def get_reset_time(self) -> float:
        """Get time until rate limit resets.

        Returns:
            Seconds until oldest request expires (0 if no requests)
        """
        if not self._requests:
            return 0.0

        now = time.time()
        oldest = self._requests[0]
        reset_time = (oldest + self.time_window) - now

        return max(0.0, reset_time)
