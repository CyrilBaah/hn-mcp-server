.PHONY: help install install-dev test lint type-check format clean build publish publish-test inspect

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

install-dev:  ## Install package with dev dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	pytest --cov=hn_mcp_server --cov-report=term --cov-report=html

lint:  ## Run linter (Ruff)
	ruff check .

lint-fix:  ## Run linter and fix issues
	ruff check --fix .

type-check:  ## Run type checker (mypy)
	mypy src/hn_mcp_server

format:  ## Format code with Ruff
	ruff format .

clean:  ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info htmlcov/ .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

build: clean  ## Build package
	python -m build

check-dist:  ## Check distribution files
	twine check dist/*

publish: build check-dist  ## Publish to PyPI
	@echo "⚠️  You are about to publish to PyPI. Are you sure? [y/N]" && read ans && [ $${ans:-N} = y ]
	twine upload dist/*

inspect:  ## Run MCP Inspector
	npx @modelcontextprotocol/inspector python -m hn_mcp_server

run:  ## Run the server
	python -m hn_mcp_server

verify:  ## Verify installation
	python -c "import hn_mcp_server; print(f'✓ hn_mcp_server version: {hn_mcp_server.__version__}')"
