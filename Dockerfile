FROM python:3.11-slim

LABEL org.opencontainers.image.title="HackerNews MCP Server"
LABEL org.opencontainers.image.description="Model Context Protocol server for HackerNews API"
LABEL org.opencontainers.image.url="https://github.com/CyrilBaah/hn-mcp-server"
LABEL org.opencontainers.image.source="https://github.com/CyrilBaah/hn-mcp-server"
LABEL org.opencontainers.image.version="1.1.0"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir hn-mcp-server[http]

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run server
CMD ["python", "-m", "hn_mcp_server", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]
