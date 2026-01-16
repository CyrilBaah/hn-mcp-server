# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-16

### Added
- **HTTP/SSE Transport Support** - Server now supports both stdio and HTTP/SSE transports (#1)
  - Command line arguments: `--transport [stdio|http]`, `--host`, `--port`
  - Optional dependencies via `pip install hn-mcp-server[http]`
  - Health check endpoint at `/health` for HTTP mode
  - SSE endpoint at `/sse` for MCP communication
- Dual transport mode enables both local (stdio) and cloud (HTTP) deployment
- Support for cloud platforms: Railway, fly.io, Render, AWS Lambda, Google Cloud Run
- Better observability and metrics for HTTP deployments
- Ready for submission to official MCP servers registry

### Changed
- Default transport remains stdio for backward compatibility
- HTTP dependencies (starlette, uvicorn, sse-starlette) are now optional

### Technical Details
- Added graceful fallback when HTTP dependencies are not installed
- Added CLI argument parsing with argparse
- Refactored server initialization to support multiple transports
- HTTP mode runs on `0.0.0.0:8000` by default

## [1.0.1] - 2026-01-16

### Added
- CHANGELOG.md for tracking version history
- LICENSE file with MIT license text

### Changed
- Improved documentation and examples
- Enhanced error handling and logging

### Fixed
- Minor bug fixes and performance improvements

## [1.0.0] - 2025-12-XX

### Added
- Initial release of HackerNews MCP Server
- Full HackerNews Algolia API integration
- Search by relevance and date
- Item retrieval (stories, comments, polls)
- User profile and activity access
- Async/await architecture with connection pooling
- Comprehensive type safety with Pydantic
- MCP protocol compatibility
- Rate limiting and retry logic
- Full test coverage (unit, integration, contract)
- Examples and documentation

### Features
- `search_hn` - Search by relevance with advanced filtering
- `search_hn_by_date` - Search by date with time range support
- `search_by_metrics` - Search with minimum points/comments thresholds
- `search_by_time_range` - Search within specific Unix timestamp range
- `get_front_page` - Retrieve current front page stories
- `get_latest_stories` - Get newest stories
- `get_latest_comments` - Get newest comments
- `get_item` - Retrieve any item by ID
- `get_item_with_comments` - Get item with full comment tree
- `get_user` - Get user profile
- `get_user_stories` - Get all stories by user
- `get_user_comments` - Get all comments by user

[1.1.0]: https://github.com/CyrilBaah/hn-mcp-server/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/CyrilBaah/hn-mcp-server/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/CyrilBaah/hn-mcp-server/releases/tag/v1.0.0
