#!/usr/bin/env python3
"""
Release helper script for hn-mcp-server.

This script automates the release process:
1. Checks for uncommitted changes
2. Updates version numbers
3. Runs tests
4. Creates git tag
5. Builds and publishes to PyPI
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def get_current_version() -> str:
    """Get current version from __init__.py."""
    init_file = Path("src/hn_mcp_server/__init__.py")
    content = init_file.read_text()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in __init__.py")


def update_version(new_version: str) -> None:
    """Update version in both pyproject.toml and __init__.py."""
    # Update pyproject.toml
    pyproject = Path("pyproject.toml")
    content = pyproject.read_text()
    content = re.sub(
        r'version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        content,
        count=1
    )
    pyproject.write_text(content)
    print(f"✓ Updated version in pyproject.toml to {new_version}")

    # Update __init__.py
    init_file = Path("src/hn_mcp_server/__init__.py")
    content = init_file.read_text()
    content = re.sub(
        r'__version__\s*=\s*["\'][^"\']+["\']',
        f'__version__ = "{new_version}"',
        content
    )
    init_file.write_text(content)
    print(f"✓ Updated version in __init__.py to {new_version}")


def check_git_status() -> bool:
    """Check if there are uncommitted changes."""
    result = run_command(["git", "status", "--porcelain"], check=False)
    return len(result.stdout.strip()) == 0


def run_tests() -> bool:
    """Run the test suite."""
    print("\n🧪 Running tests...")
    result = run_command(["pytest"], check=False)
    if result.returncode != 0:
        print("❌ Tests failed!")
        print(result.stdout)
        print(result.stderr)
        return False
    print("✓ Tests passed")
    return True


def run_lint() -> bool:
    """Run linting checks."""
    print("\n🔍 Running linter...")
    result = run_command(["ruff", "check", "."], check=False)
    if result.returncode != 0:
        print("❌ Linting failed!")
        print(result.stdout)
        return False
    print("✓ Linting passed")
    return True


def build_package() -> bool:
    """Build the package."""
    print("\n📦 Building package...")
    # Clean old builds
    run_command(["rm", "-rf", "dist/", "build/", "*.egg-info"], check=False)

    # Build
    result = run_command(["python", "-m", "build"], check=False)
    if result.returncode != 0:
        print("❌ Build failed!")
        print(result.stderr)
        return False

    # Check distribution
    result = run_command(["twine", "check", "dist/*"], check=False)
    if result.returncode != 0:
        print("❌ Distribution check failed!")
        print(result.stderr)
        return False

    print("✓ Package built successfully")
    return True


def create_git_tag(version: str) -> bool:
    """Create and push git tag."""
    print(f"\n🏷️  Creating git tag v{version}...")

    # Commit version changes
    run_command(["git", "add", "pyproject.toml", "src/hn_mcp_server/__init__.py"])
    run_command(["git", "commit", "-m", f"Bump version to {version}"])

    # Create tag
    result = run_command(["git", "tag", "-a", f"v{version}", "-m", f"Release version {version}"], check=False)
    if result.returncode != 0:
        print("❌ Failed to create tag (may already exist)")
        return False

    # Push
    run_command(["git", "push", "origin", "main"])
    run_command(["git", "push", "origin", f"v{version}"])

    print(f"✓ Created and pushed tag v{version}")
    return True


def publish_to_pypi(test: bool = False) -> bool:
    """Publish package to PyPI or TestPyPI."""
    repo = "testpypi" if test else "pypi"
    print(f"\n📤 Publishing to {repo.upper()}...")

    cmd = ["twine", "upload", "dist/*"]
    if test:
        cmd.insert(2, "--repository")
        cmd.insert(3, "testpypi")

    result = run_command(cmd, check=False)
    if result.returncode != 0:
        print(f"❌ Publishing to {repo} failed!")
        print(result.stderr)
        return False

    print(f"✓ Published to {repo.upper()}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Release helper for hn-mcp-server")
    parser.add_argument("version", help="New version number (e.g., 1.0.1)")
    parser.add_argument("--test", action="store_true", help="Publish to TestPyPI instead of PyPI")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-tag", action="store_true", help="Skip creating git tag")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually publish")

    args = parser.parse_args()

    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', args.version):
        print("❌ Version must be in format X.Y.Z (e.g., 1.0.1)")
        sys.exit(1)

    current_version = get_current_version()
    print(f"Current version: {current_version}")
    print(f"New version: {args.version}")

    # Check git status
    if not check_git_status() and not args.dry_run:
        response = input("⚠️  You have uncommitted changes. Continue? [y/N] ")
        if response.lower() != 'y':
            print("Aborted")
            sys.exit(1)

    # Update version
    update_version(args.version)

    # Run tests
    if not args.skip_tests:
        if not run_tests():
            sys.exit(1)
        if not run_lint():
            sys.exit(1)

    # Build package
    if not build_package():
        sys.exit(1)

    if args.dry_run:
        print("\n✓ Dry run completed successfully")
        print("  No changes were pushed or published")
        return

    # Create git tag
    if not args.skip_tag and not create_git_tag(args.version):
        response = input("Continue without tag? [y/N] ")
        if response.lower() != 'y':
            sys.exit(1)

    # Publish
    if not publish_to_pypi(test=args.test):
        sys.exit(1)

    print("\n✅ Release complete!")
    print("\nNext steps:")
    print("1. Go to https://github.com/CyrilBaah/hn-mcp-server/releases")
    print(f"2. Create a new release for tag v{args.version}")
    print("3. Add release notes")


if __name__ == "__main__":
    main()
