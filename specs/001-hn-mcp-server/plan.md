# Implementation Plan: HackerNews MCP Server

**Branch**: `001-hn-mcp-server` | **Date**: 2025-01-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-hn-mcp-server/spec.md`

## Summary

Create a Model Context Protocol (MCP) server that provides comprehensive access to the HackerNews API (https://hn.algolia.com/api). The server will expose MCP tools for searching posts, retrieving items, fetching user profiles, and filtering by various criteria (front page, latest, by author, date ranges, etc.). Built with Python 3.11+, TypeScript SDK support, and strict adherence to MCP protocol specifications.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: 
- `mcp` (Model Context Protocol SDK)
- `httpx` (async HTTP client)
- `pydantic` (data validation and serialization)
- `pytest` + `pytest-asyncio` (testing)

**Storage**: N/A (stateless API proxy)  
**Testing**: pytest with async support, contract tests for MCP protocol compliance  
**Target Platform**: Cross-platform (Linux, macOS, Windows) - runs as MCP server process  
**Project Type**: Single project (Python package with MCP server)  
**Performance Goals**: 
- API response time < 2s p95 (depends on HN API)
- Handle 10,000 requests/hour (within HN API rate limit)
- Memory footprint < 50MB

**Constraints**: 
- HN API rate limit: 10,000 requests/hour per IP
- Read-only operations (HN API doesn't support writes)
- MCP protocol compliance required

**Scale/Scope**: 
- 10+ MCP tools covering all HN API endpoints
- Support for all search parameters and filters
- Comprehensive error handling and validation

## Constitution Check

✅ **Code Quality First**: Using established packages (httpx, pydantic, MCP SDK)  
✅ **Test-First Development**: TDD with pytest, contract tests for MCP compliance  
✅ **Documentation via Context7**: API docs, usage examples, integration guides  
✅ **Latest Packages**: All dependencies at latest stable versions  
✅ **Python Standards**: Ruff for linting/formatting, mypy strict mode, type hints  
✅ **Sample Code**: Based on official MCP Python SDK examples  

*GATE PASSED: Proceed to Phase 0 research*

## Project Structure

### Documentation (this feature)

```text
specs/001-hn-mcp-server/
├── plan.md              # This file
├── research.md          # Phase 0: MCP protocol research, HN API analysis
├── data-model.md        # Phase 1: Pydantic models, tool schemas
├── quickstart.md        # Phase 1: Installation, configuration, usage
├── contracts/           # Phase 1: MCP protocol contracts
│   ├── search-tools.json
│   ├── item-tools.json
│   └── user-tools.json
└── tasks.md             # Phase 2: Implementation task breakdown
```

### Source Code (repository root)

```text
hn-mcp-server/
├── pyproject.toml           # Project config, dependencies, Ruff settings
├── README.md                # Quick start, installation
├── .python-version          # Python 3.11
├── src/
│   └── hn_mcp_server/
│       ├── __init__.py
│       ├── server.py        # MCP server setup and tool registration
│       ├── models/          # Pydantic data models
│       │   ├── __init__.py
│       │   ├── search.py    # Search request/response models
│       │   ├── item.py      # Item (story/comment) models
│       │   └── user.py      # User profile models
│       ├── services/        # Business logic
│       │   ├── __init__.py
│       │   ├── hn_client.py # HTTP client for HN API
│       │   └── rate_limit.py# Rate limiting logic
│       └── tools/           # MCP tool implementations
│           ├── __init__.py
│           ├── search.py    # Search tools
│           ├── items.py     # Item retrieval tools
│           └── users.py     # User profile tools
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── contract/            # MCP protocol compliance tests
│   │   ├── test_search_tools.py
│   │   ├── test_item_tools.py
│   │   └── test_user_tools.py
│   ├── integration/         # Integration tests with HN API
│   │   ├── test_hn_client.py
│   │   └── test_end_to_end.py
│   └── unit/                # Unit tests
│       ├── test_models.py
│       ├── test_tools.py
│       └── test_rate_limit.py
└── examples/
    ├── basic_search.py
    └── mcp_config.json      # Example MCP client configuration
```

**Structure Decision**: Single Python project structure chosen because:
- MCP server is a single executable process
- No frontend/backend separation needed
- Simple package structure for pip installation
- Clear separation: models (data), services (API interaction), tools (MCP interface)

## Complexity Tracking

No constitutional violations. All choices align with principles:
- Using official MCP SDK (not custom protocol implementation)
- Leveraging httpx (not writing HTTP client)
- Pydantic for validation (industry standard)
- Standard pytest setup
