# Quick Start Guide

This guide will help you get the HackerNews MCP Server up and running quickly.

## Installation

### Option 1: Using pip (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/hn-mcp-server.git
cd hn-mcp-server

# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Option 2: Using uv (Faster)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/yourusername/hn-mcp-server.git
cd hn-mcp-server

# Create venv and install
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Configuration

### For Claude Desktop

1. **Find your config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add the server:**

```json
{
  "mcpServers": {
    "hackernews": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["-m", "hn_mcp_server.server"]
    }
  }
}
```

3. **Get the absolute path to your Python:**

```bash
# macOS/Linux
which python

# Windows
where python
```

4. **Restart Claude Desktop**

## Testing the Installation

### Option 1: In Claude Desktop

Ask Claude:
```
Search HackerNews for recent Python stories
```

Claude should use the `search_hn` tool and return results.

### Option 2: Command Line

```bash
# Activate your virtual environment
source venv/bin/activate

# Run the example script
python examples/basic_usage.py
```

### Option 3: Test directly

```bash
# Activate virtual environment
source venv/bin/activate

# Run the server (it will wait for input via stdio)
python -m hn_mcp_server.server
```

## Quick Examples

Once configured with Claude, try these prompts:

### Search Examples

```
Search HackerNews for Python stories with more than 50 points
```

```
Show me the latest Show HN posts
```

```
Find Ask HN posts from the last week
```

### Item Examples

```
Get the story with ID 39251790 and show me the top comments
```

```
What are people saying about the top story on HN?
```

### User Examples

```
Tell me about the HackerNews user 'pg'
```

```
What has user 'pg' posted recently?
```

## Verification

To verify everything is working:

1. **Check installation:**
```bash
pip list | grep hn-mcp-server
```

2. **Run tests:**
```bash
pytest tests/ -v
```

3. **Check code quality:**
```bash
ruff check .
```

## Troubleshooting

### Server won't start

**Check Python version:**
```bash
python --version  # Should be 3.11+
```

**Reinstall:**
```bash
pip uninstall hn-mcp-server
pip install -e .
```

### Claude can't find the server

**Check the path in config:**
- Must be absolute path to Python executable
- Use forward slashes even on Windows in JSON

**Check logs:**
- Look in Claude's logs for error messages

### No results returned

**Test the HN API directly:**
```bash
curl "https://hn.algolia.com/api/v1/search?query=python&tags=story&hitsPerPage=1"
```

**Check your query:**
- Verify spelling
- Try simpler queries first
- Check if the item ID exists on news.ycombinator.com

## Next Steps

- Read the [full documentation](docs/DOCUMENTATION.md)
- Check out [examples](examples/)
- Run the test suite to understand the API
- Customize the server for your needs

## Getting Help

- Check the [troubleshooting guide](docs/DOCUMENTATION.md#troubleshooting)
- Open an issue on GitHub
- Read the MCP protocol docs: https://modelcontextprotocol.io/

## Development Setup

If you want to contribute or modify the server:

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .

# Format code
ruff format .

# Type checking
mypy src/
```

Happy hacking! 🚀
