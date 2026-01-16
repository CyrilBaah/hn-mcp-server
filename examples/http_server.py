"""Example of running HackerNews MCP Server in HTTP mode."""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    """Start the server in HTTP mode."""
    from hn_mcp_server.server import run_http
    
    print("Starting HackerNews MCP Server in HTTP mode...")
    print("Endpoints:")
    print("  - SSE: http://localhost:8000/sse")
    print("  - Health: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop")
    
    try:
        await run_http(host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == "__main__":
    asyncio.run(main())
