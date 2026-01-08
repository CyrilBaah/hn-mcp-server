"""Unit tests for rate limiter."""

import asyncio
import time

import pytest

from hn_mcp_server.services import RateLimiter


@pytest.mark.asyncio
class TestRateLimiter:
    """Test RateLimiter class."""

    async def test_basic_acquire(self):
        """Test basic request acquisition."""
        limiter = RateLimiter(max_requests=5, time_window=1.0)

        # Should allow first 5 requests immediately
        for _ in range(5):
            await limiter.acquire()

        assert limiter.get_remaining() == 0

    async def test_blocks_when_limit_reached(self):
        """Test that acquire blocks when limit is reached."""
        limiter = RateLimiter(max_requests=2, time_window=0.5)

        # Make 2 requests
        await limiter.acquire()
        await limiter.acquire()

        # Third request should block briefly
        start = time.time()
        await limiter.acquire()
        elapsed = time.time() - start

        # Should have waited around 0.5 seconds
        assert elapsed >= 0.4  # Allow some tolerance

    async def test_get_remaining(self):
        """Test get_remaining method."""
        limiter = RateLimiter(max_requests=5, time_window=1.0)

        assert limiter.get_remaining() == 5

        await limiter.acquire()
        assert limiter.get_remaining() == 4

        await limiter.acquire()
        await limiter.acquire()
        assert limiter.get_remaining() == 2  # 5 - 3 = 2 remaining

    async def test_get_reset_time(self):
        """Test get_reset_time method."""
        limiter = RateLimiter(max_requests=5, time_window=1.0)

        # No requests yet
        assert limiter.get_reset_time() == 0.0

        # Make a request
        await limiter.acquire()

        # Should have reset time around 1.0 seconds
        reset_time = limiter.get_reset_time()
        assert 0.9 <= reset_time <= 1.1

    async def test_window_expiration(self):
        """Test that old requests expire from window."""
        limiter = RateLimiter(max_requests=2, time_window=0.3)

        # Fill the limit
        await limiter.acquire()
        await limiter.acquire()

        assert limiter.get_remaining() == 0

        # Wait for window to expire
        await asyncio.sleep(0.4)

        # Should have capacity again
        assert limiter.get_remaining() == 2

    async def test_concurrent_access(self):
        """Test concurrent access to rate limiter."""
        limiter = RateLimiter(max_requests=10, time_window=1.0)

        # Try to acquire from multiple coroutines
        async def acquire_multiple(count):
            for _ in range(count):
                await limiter.acquire()

        # Run 5 coroutines trying to acquire 3 requests each (15 total)
        # With limit of 10, some should block
        tasks = [acquire_multiple(3) for _ in range(5)]
        start = time.time()
        await asyncio.gather(*tasks)
        elapsed = time.time() - start

        # Should have taken some time due to blocking
        assert elapsed > 0.5  # Some requests had to wait

    async def test_default_limits(self):
        """Test default rate limiter configuration."""
        limiter = RateLimiter()

        # Default should be 10000 requests per hour
        assert limiter.max_requests == 10000
        assert limiter.time_window == 3600.0
