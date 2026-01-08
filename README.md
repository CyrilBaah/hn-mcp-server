# HackerNews MCP Server

![hn-mcp-server](https://socialify.git.ci/CyrilBaah/hn-mcp-server/image?description=1&font=Raleway&language=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2Frdimascio%2Ficons%2Frefs%2Fheads%2Fmaster%2Ficons%2Fcolor%2Fhackernews.svg&name=1&owner=1&theme=Light)

[![PyPI version](https://img.shields.io/pypi/v/hn-mcp-server.svg)](https://pypi.org/project/hn-mcp-server/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/CyrilBaah/hn-mcp-server/workflows/Tests/badge.svg)](https://github.com/CyrilBaah/hn-mcp-server/actions)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![MCP](https://img.shields.io/badge/MCP-1.0.0-green.svg)](https://modelcontextprotocol.io/)
[![Downloads](https://img.shields.io/pypi/dm/hn-mcp-server.svg)](https://pypi.org/project/hn-mcp-server/)

A Model Context Protocol (MCP) server that provides programmatic access to HackerNews content through the official [HN Algolia API](https://hn.algolia.com/api). This enables AI assistants and other MCP clients to search, retrieve, and analyze HackerNews stories, comments, and user profiles.

## Features

- 🔍 **Comprehensive Search**: Search HackerNews by relevance or date with advanced filtering
- 📰 **Content Access**: Retrieve stories, comments, and polls with full metadata
- 👤 **User Profiles**: Access user information, submissions, and comment history
- ⚡ **High Performance**: Async/await design with connection pooling and retry logic
- 🛡️ **Type Safe**: Full Pydantic validation and type hints throughout
- 🔧 **MCP Compatible**: Works with Claude Desktop, Continue, and other MCP clients

## Installation

### From PyPI (Recommended)

```bash
pip install hn-mcp-server
```

### From Source

```bash
git clone https://github.com/CyrilBaah/hn-mcp-server.git
cd hn-mcp-server
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

### Testing the Server

First, verify the server is working correctly:

```bash
# Test that the server responds to MCP protocol
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"1.0.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | python -m hn_mcp_server
```

You should see a JSON response indicating successful initialization.

### With MCP Inspector

The MCP Inspector provides a web-based interface for testing and debugging your server:

```bash
# Using npx (no installation required)
npx @modelcontextprotocol/inspector python -m hn_mcp_server

# Or install globally
npm install -g @modelcontextprotocol/inspector
mcp-inspector python -m hn_mcp_server
```

This will open a browser interface where you can:
- Test all available tools interactively
- Inspect requests and responses
- Debug tool parameters and outputs
- View server logs in real-time

### With VS Code MCP

[![Install in VS Code](https://img.shields.io/badge/VS_Code-HackerNews_MCP-0098FF?style=flat-square&logo=visualstudiocode&logoColor=ffffff)](vscode:mcp/install?%7B%22name%22%3A%22microsoft.docs.mcp%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22python%22%2C%22args%22%3A%5B%22python%20-m%20hn_mcp_server%22%5D%7D)

Using [vscodemcp.com](https://vscodemcp.com/), update your `.vscode/mcp.json`:

```json
{
  "servers": {
    "hackernews": {
      "command": "python",
      "args": ["-m", "hn_mcp_server"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Note**: If you installed in a virtual environment, use the full path to your Python executable:

```json
{
  "servers": {
    "hackernews": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["-m", "hn_mcp_server"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### With Cursor

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en-US/install-mcp?name=hn_mcp_server&config=eyJjb21tYW5kIjoibnB4IC15IGhuX21jcF9zZXJ2ZXIifQ%3D%3D)

Or manually update your `.cursor/mcp.json`:

```json
{
  "servers": {
    "hackernews": {
      "command": "python",
      "args": ["-m", "hn_mcp_server"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Note**: If you installed in a virtual environment, use the full path to your Python executable:

```json
{
  "servers": {
    "hackernews": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["-m", "hn_mcp_server"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### With Claude Desktop

<img src="https://claude.ai/images/claude_app_icon.png" width="20" height="20" /> **Claude Desktop**

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hackernews": {
      "command": "python",
      "args": ["-m", "hn_mcp_server"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Restart Claude Desktop, and the HackerNews tools will be available.

### Standalone Usage

The HN client can also be used directly without MCP:

```python
import asyncio
from hn_mcp_server.services import HNClient

async def main():
    async with HNClient() as client:
        # Search for Python stories
        result = await client.search(
            query="python",
            tags=["story"],
            hits_per_page=10
        )
        
        for hit in result.hits:
            print(f"{hit.title} - {hit.points} points")

asyncio.run(main())
```

See [`examples/direct_api_usage.py`](examples/direct_api_usage.py) for more examples.

## Available Tools

### Search Tools

#### `search_hn`
Search HackerNews content by relevance (sorted by relevance → points → comments).

```json
{
  "query": "artificial intelligence",
  "tags": ["story"],
  "hits_per_page": 20
}
```

#### `search_hn_by_date`
Search HackerNews content by date (most recent first).

```json
{
  "query": "python",
  "tags": ["story", "show_hn"],
  "hits_per_page": 10
}
```

#### `get_front_page`
Retrieve current HackerNews front page stories.

```json
{
  "page": 0,
  "hits_per_page": 30
}
```

#### `get_latest_stories`
Retrieve most recent HackerNews stories.

```json
{
  "hits_per_page": 20
}
```

#### `get_latest_comments`
Retrieve most recent HackerNews comments.

```json
{
  "hits_per_page": 20
}
```

#### `search_by_time_range`
Search items within a specific time range.

```json
{
  "start_timestamp": 1704067200,
  "end_timestamp": 1736078400,
  "query": "AI",
  "hits_per_page": 10
}
```

#### `search_by_metrics`
Search items with minimum points or comments.

```json
{
  "min_points": 100,
  "min_comments": 50,
  "tags": ["story"]
}
```

### Item Tools

#### `get_item`
Retrieve a specific item (story, comment, poll) by ID.

```json
{
  "item_id": 1
}
```

#### `get_story_comments`
Retrieve a story and all its comments (full tree).

```json
{
  "story_id": 39195605
}
```

### User Tools

#### `get_user`
Retrieve user profile information.

```json
{
  "username": "pg"
}
```

#### `get_user_stories`
Retrieve all stories submitted by a user.

```json
{
  "username": "pg",
  "hits_per_page": 20
}
```

#### `get_user_comments`
Retrieve all comments by a user.

```json
{
  "username": "pg",
  "hits_per_page": 20
}
```

## Configuration

Configure via environment variables:

```bash
# API Configuration
export HN_API_BASE_URL="https://hn.algolia.com/api/v1"  # Default
export HN_REQUEST_TIMEOUT="10"  # Seconds, default: 10
export HN_MAX_RETRIES="3"  # Default: 3

# Logging
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
```

## Search Tags

Available tags for filtering:

- **Type**: `story`, `comment`, `poll`, `pollopt`
- **Special**: `show_hn`, `ask_hn`, `front_page`
- **Author**: `author_USERNAME` (e.g., `author_pg`)
- **Story**: `story_ID` (e.g., `story_12345`)

## Numeric Filters

Filter by numeric fields:

- `created_at_i` - Unix timestamp
- `points` - Story points
- `num_comments` - Number of comments

Operators: `<`, `<=`, `=`, `>`, `>=`

Examples:
- `points>100` - Stories with more than 100 points
- `created_at_i>1704067200` - Items after Jan 1, 2024
- `num_comments>=50` - Items with 50+ comments

## Examples

See the [examples/](examples/) directory for usage examples:

- [`direct_api_usage.py`](examples/direct_api_usage.py) - Direct API client usage without MCP
- [`basic_usage.py`](examples/basic_usage.py) - MCP client usage (requires MCP client library)
- [`mcp_config.json`](examples/mcp_config.json) - Claude Desktop configuration

### Running Examples

```bash
# Run direct API example (no MCP client needed)
python examples/direct_api_usage.py

# Run MCP client example (requires mcp library)
python examples/basic_usage.py
```

The direct API example demonstrates using the HackerNews client library directly, while the basic usage example shows how to interact with the MCP server programmatically.

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/hn-mcp-server.git
cd hn-mcp-server

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Testing the Installation

```bash
# Test the MCP server starts correctly
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"1.0.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | python -m hn_mcp_server

# Run the direct API example
python examples/direct_api_usage.py
```

### Testing

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=hn_mcp_server --cov-report=html

# Run integration tests (requires internet)
pytest tests/integration/ -m integration
```

### Linting & Formatting

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy src/
```

## Architecture

```
hn-mcp-server/
├── src/hn_mcp_server/
│   ├── server.py          # MCP server setup
│   ├── models/            # Pydantic data models
│   ├── services/          # API client & rate limiting
│   └── tools/             # MCP tool implementations
├── tests/
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── contract/          # MCP protocol tests
└── examples/              # Usage examples
```

## API Rate Limits

The HackerNews API has a rate limit of **10,000 requests/hour per IP**. The client includes built-in rate limiting to stay within these bounds.

## Troubleshooting

### Server Not Starting

If the MCP server fails to start:

1. **Check Python version**: Ensure you're using Python 3.11 or higher
   ```bash
   python --version
   ```

2. **Verify installation**: Make sure the package is installed correctly
   ```bash
   pip list | grep hn-mcp-server
   ```

3. **Test server directly**: Try initializing the server manually
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"1.0.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | python -m hn_mcp_server
   ```

### Virtual Environment Issues

If using a virtual environment with VS Code or Claude Desktop:

1. **Use full path**: In your configuration file, use the full path to the Python executable:
   ```json
   {
     "command": "/full/path/to/.venv/bin/python",
     "args": ["-m", "hn_mcp_server"]
   }
   ```

2. **Find Python path**: To get the full path to your virtual environment's Python:
   ```bash
   which python  # On Unix/macOS
   where python  # On Windows
   ```

### MCP Client Examples Not Working

The MCP client examples ([`basic_usage.py`](examples/basic_usage.py)) require the server subprocess to communicate via stdio. If you encounter issues:

1. Use the **direct API examples** instead ([`direct_api_usage.py`](examples/direct_api_usage.py))
2. Ensure you're using `sys.executable` in the client configuration (already updated in the examples)

### API Errors

If you encounter API errors:

1. **Check network connectivity**: Ensure you can reach `hn.algolia.com`
2. **Rate limiting**: Wait if you've exceeded the 10,000 requests/hour limit
3. **Invalid item ID**: Ensure the item ID exists on HackerNews

## Publishing to PyPI

### Prerequisites

1. Install build tools:
   ```bash
   pip install build twine
   ```

2. Ensure you have PyPI credentials (create account at [pypi.org](https://pypi.org))

### Quick Publish (Automated)

Use the release script for automated publishing:

```bash
# Publish to PyPI (production)
python scripts/release.py 1.0.1

# Or using Make
make publish       # PyPI
```

The script will automatically:
- Update version numbers
- Run tests and linting
- Build the package
- Create git tag
- Publish to PyPI

See [docs/PUBLISHING.md](docs/PUBLISHING.md) for detailed instructions.

### Manual Build and Publish

1. **Update version** in [`pyproject.toml`](pyproject.toml):
   ```toml
   [project]
   version = "1.0.1"  # Increment appropriately
   ```

2. **Clean previous builds**:
   ```bash
   rm -rf dist/ build/ *.egg-info
   ```

3. **Build the package**:
   ```bash
   python -m build
   ```

4. **Check the distribution**:
   ```bash
   twine check dist/*
   ```

5. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

6. **Create a git tag**:
   ```bash
   git tag -a v1.0.1 -m "Release version 1.0.1"
   git push origin v1.0.1
   ```

### Using API Tokens (Recommended)

Instead of username/password, use API tokens:

1. Generate token at [pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
2. Create `~/.pypirc`:
   ```ini
   [pypi]
   username = __token__
   password = pypi-AgEIcHlwaS5vcmc...
   ```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [HackerNews](https://news.ycombinator.com/) for the API
- [Algolia](https://www.algolia.com/) for powering the HN search
- [Model Context Protocol](https://modelcontextprotocol.io/) specification

## Support

- 📖 [Documentation](docs/DOCUMENTATION.md)
- 🚀 [Quick Start Guide](docs/QUICKSTART.md)
- 🐛 [Issue Tracker](https://github.com/CyrilBaah/hn-mcp-server/issues)
- 💬 [Discussions](https://github.com/CyrilBaah/hn-mcp-server/discussions)

---

**Note**: This is an unofficial third-party client and is not affiliated with Y Combinator or HackerNews.
