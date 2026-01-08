# Publishing Guide

This guide explains how to publish the HackerNews MCP Server to PyPI.

## Quick Reference

Using the Makefile (recommended):

```bash
# Publish to TestPyPI (for testing)
make publish-test

# Publish to PyPI (production)
make publish
```

## Manual Publishing Steps

### 1. Prerequisites

```bash
pip install build twine
```

### 2. Update Version

Edit `pyproject.toml` and `src/hn_mcp_server/__init__.py`:

```toml
# pyproject.toml
[project]
version = "1.0.1"
```

```python
# src/hn_mcp_server/__init__.py
__version__ = "1.0.1"
```

### 3. Run Tests

```bash
make test
make lint
make type-check
```

### 4. Build Package

```bash
make build
# or manually:
python -m build
```

### 5. Check Distribution

```bash
make check-dist
# or manually:
twine check dist/*
```

### 6. Test on TestPyPI (Optional)

```bash
make publish-test
# or manually:
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ hn-mcp-server
```

### 7. Publish to PyPI

```bash
make publish
# or manually:
twine upload dist/*
```

### 8. Create Git Tag

```bash
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin v1.0.1
```

### 9. Create GitHub Release

1. Go to [GitHub Releases](https://github.com/CyrilBaah/hn-mcp-server/releases)
2. Click "Draft a new release"
3. Select the tag `v1.0.1`
4. Add release notes
5. Publish release

This will automatically trigger the GitHub Action to publish to PyPI.

## Using API Tokens

### Setting Up PyPI Token

1. Go to [pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
2. Create a new API token
3. Set scope to "Entire account" or specific project
4. Copy the token (starts with `pypi-`)

### Configure `~/.pypirc`

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...

[testpypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...
```

### GitHub Secrets

For automated publishing via GitHub Actions:

1. Go to Settings → Secrets and variables → Actions
2. Add secrets:
   - `PYPI_API_TOKEN` - Your PyPI token
   - `TEST_PYPI_API_TOKEN` - Your TestPyPI token (optional)

## Automated Publishing via GitHub Actions

The workflow is triggered by:

1. **Creating a GitHub Release** (automatic to PyPI)
2. **Manual workflow dispatch** (choose testpypi or pypi)

To manually trigger:

1. Go to Actions → Publish to PyPI
2. Click "Run workflow"
3. Select environment (testpypi or pypi)
4. Click "Run workflow"

## Makefile Commands

```bash
make help           # Show all available commands
make install        # Install package
make install-dev    # Install with dev dependencies
make test           # Run tests
make lint           # Run linter
make type-check     # Run type checker
make format         # Format code
make clean          # Clean build artifacts
make build          # Build package
make check-dist     # Check distribution
make publish-test   # Publish to TestPyPI
make publish        # Publish to PyPI
make inspect        # Run MCP Inspector
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backwards compatible)
- **PATCH** version for backwards compatible bug fixes

Examples:
- `1.0.0` → `1.0.1` (bug fix)
- `1.0.0` → `1.1.0` (new feature)
- `1.0.0` → `2.0.0` (breaking change)

## Checklist Before Publishing

- [ ] Tests pass (`make test`)
- [ ] Linting passes (`make lint`)
- [ ] Type checking passes (`make type-check`)
- [ ] Version updated in `pyproject.toml` and `__init__.py`
- [ ] CHANGELOG updated (if you have one)
- [ ] README updated
- [ ] Built and checked distribution (`make build check-dist`)
- [ ] Tested on TestPyPI (optional but recommended)
- [ ] Git tag created
- [ ] GitHub release created

## Troubleshooting

### Upload failed: File already exists

You cannot re-upload the same version. Increment the version number.

### Authentication failed

- Check your API token is correct
- Ensure `~/.pypirc` has correct format
- Token should start with `pypi-`

### Import errors after installation

- Clear pip cache: `pip cache purge`
- Reinstall: `pip install --force-reinstall --no-cache-dir hn-mcp-server`

### Package not found on PyPI

- Wait 1-2 minutes for PyPI to index
- Check package name: [pypi.org/project/hn-mcp-server/](https://pypi.org/project/hn-mcp-server/)
