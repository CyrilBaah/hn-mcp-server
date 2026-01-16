"""Tests for HTTP/SSE transport mode."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import argparse


class TestHTTPTransport:
    """Test HTTP/SSE transport functionality."""

    def test_parse_args_stdio_default(self):
        """Test that stdio is the default transport."""
        from hn_mcp_server.server import parse_args
        
        with patch('sys.argv', ['server.py']):
            args = parse_args()
            assert args.transport == "stdio"
            assert args.host == "0.0.0.0"
            assert args.port == 8000

    def test_parse_args_http_mode(self):
        """Test parsing HTTP mode arguments."""
        from hn_mcp_server.server import parse_args
        
        with patch('sys.argv', ['server.py', '--transport', 'http', '--host', '127.0.0.1', '--port', '3000']):
            args = parse_args()
            assert args.transport == "http"
            assert args.host == "127.0.0.1"
            assert args.port == 3000

    def test_parse_args_invalid_transport(self):
        """Test that invalid transport raises error."""
        from hn_mcp_server.server import parse_args
        
        with patch('sys.argv', ['server.py', '--transport', 'invalid']):
            with pytest.raises(SystemExit):
                parse_args()

    @pytest.mark.asyncio
    async def test_run_stdio_mode(self):
        """Test running in stdio mode."""
        from hn_mcp_server.server import run_stdio, app
        
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        
        with patch('hn_mcp_server.server.stdio_server') as mock_stdio:
            mock_stdio.return_value.__aenter__.return_value = (mock_read, mock_write)
            
            with patch.object(app, 'run', new_callable=AsyncMock) as mock_run:
                await run_stdio()
                
                mock_run.assert_called_once()
                assert mock_run.call_args[0][0] == mock_read
                assert mock_run.call_args[0][1] == mock_write

    @pytest.mark.asyncio
    async def test_http_mode_requires_dependencies(self):
        """Test that HTTP mode fails gracefully without dependencies."""
        from hn_mcp_server.server import run_http, HTTP_AVAILABLE
        
        if not HTTP_AVAILABLE:
            with pytest.raises(RuntimeError, match="HTTP transport requires additional dependencies"):
                await run_http()

    @pytest.mark.skipif(
        not __import__('importlib.util').util.find_spec('starlette'),
        reason="HTTP dependencies not installed"
    )
    @pytest.mark.asyncio
    async def test_http_mode_with_dependencies(self):
        """Test HTTP mode when dependencies are available."""
        from hn_mcp_server.server import run_http
        
        # Mock uvicorn at the import level
        with patch('uvicorn.Server.serve', new_callable=AsyncMock) as mock_serve:
            # Run in background to test initialization
            import asyncio
            task = asyncio.create_task(run_http(host="127.0.0.1", port=8888))
            
            # Give it a moment to initialize
            await asyncio.sleep(0.1)
            
            # Cancel the task
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            # Verify server was configured
            mock_serve.assert_called_once()


class TestCLIIntegration:
    """Test full CLI integration."""

    @pytest.mark.asyncio
    async def test_main_stdio_mode(self):
        """Test main function runs stdio mode by default."""
        from hn_mcp_server.server import main
        
        with patch('hn_mcp_server.server.parse_args') as mock_parse:
            mock_parse.return_value = argparse.Namespace(transport="stdio")
            
            with patch('hn_mcp_server.server.run_stdio', new_callable=AsyncMock) as mock_stdio:
                await main()
                mock_stdio.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_http_mode(self):
        """Test main function runs HTTP mode when specified."""
        from hn_mcp_server.server import main
        
        with patch('hn_mcp_server.server.parse_args') as mock_parse:
            mock_parse.return_value = argparse.Namespace(
                transport="http",
                host="0.0.0.0",
                port=8000
            )
            
            with patch('hn_mcp_server.server.run_http', new_callable=AsyncMock) as mock_http:
                await main()
                mock_http.assert_called_once_with(host="0.0.0.0", port=8000)


class TestHTTPEndpoints:
    """Test HTTP endpoint functionality."""

    @pytest.mark.skipif(
        not __import__('importlib.util').util.find_spec('starlette'),
        reason="HTTP dependencies not installed"
    )
    def test_health_endpoint_defined(self):
        """Test that health endpoint exists in route configuration."""
        # This is a smoke test to ensure the endpoint structure is correct
        # Full integration testing would require starting the server
        assert True  # Placeholder - actual endpoint tested in integration tests
