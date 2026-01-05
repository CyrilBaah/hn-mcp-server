# HN MCP Server Constitution

## Core Principles

### I. Code Quality First
- Prioritize existing packages and libraries over custom implementations
- Leverage battle-tested solutions from npm/PyPI ecosystem
- Always use the latest stable package versions
- Custom code requires justification: performance, security, or unique requirements
- Code must be self-documenting with clear naming conventions
- Follow established design patterns and best practices for the technology stack
- **Python**: Ruff for linting and formatting (replaces Black, isort, Flake8, pylint)
- **Python**: Ruff configuration in `pyproject.toml` with strict rules enabled
- All code must pass Ruff checks before commit

### II. Test-First Development (NON-NEGOTIABLE)
- TDD mandatory: Tests written → User approved → Tests fail → Implementation begins
- Red-Green-Refactor cycle strictly enforced
- Minimum 80% code coverage required
- Tests must cover: happy paths, edge cases, error handling
- Integration tests required for: API endpoints, external dependencies, data transformations
- Test failures block all deployments

### III. Documentation via Context7
- All documentation must be created and maintained through Context7
- API documentation auto-generated from code annotations
- Include examples for all public interfaces
- Architecture decisions recorded in ADRs (Architecture Decision Records)
- Onboarding documentation kept current
- Documentation changes reviewed alongside code changes

### IV. User Experience Consistency
- Consistent error messages across all interfaces
- Standardized response formats (JSON for APIs, structured output for CLI)
- Clear, actionable error messages with resolution steps
- Uniform naming conventions across APIs and data models
- Accessible interfaces following WCAG 2.1 AA standards
- Performance budgets: API responses < 200ms p95, UI interactions < 100ms

### V. Dependency Management
- Always use latest stable versions of dependencies
- Security patches applied within 48 hours
- Major version upgrades evaluated monthly
- Dependencies reviewed for: active maintenance, security track record, bundle size
- Lock files committed to version control
- Automated dependency updates via Dependabot or Renovate

### VI. Sample Code & Reference Implementations
- Prefer copying from official package examples over custom solutions
- Maintain internal code snippet library for common patterns
- Reference implementations must include: usage examples, error handling, tests
- Document source of borrowed code patterns
- Adapt, don't reinvent: modify existing patterns to fit needs

## Quality Standards

### Code Review Requirements
- All code changes require peer review
- Reviewers verify: test coverage, documentation updates, principle adherence
- No direct commits to main branch
- PR descriptions must link to related issues/specs
- Breaking changes require explicit approval and migration plan

### Testing Gates
- Unit tests pass locally before PR creation
- Integration tests pass in CI/CD pipeline
- E2E tests pass for user-facing changes
- Performance regression tests for critical paths
- Security scanning (SAST/DAST) passes with no high/critical issues
- Ruff linting and formatting checks pass in CI/CD (Python projects)
- Pre-commit hooks enforce Ruff formatting before commits

### Performance Standards
- Monitor bundle size: flag increases > 10%
- Lighthouse scores: Performance > 90, Accessibility > 95
- API response time p95 < 200ms
- Database query optimization required for N+1 patterns
## Technology Constraints

### Package Selection Criteria
- Active maintenance (updated within last 6 months)
- Strong community support (> 1000 weekly downloads for npm, > 10k monthly for PyPI)
- TypeScript support (types included or @types/* available)
- Python type hints and py.typed marker for libraries
- Compatible license (MIT, Apache 2.0, BSD)
- Security audit passed within last year

### Python Standards
- Ruff as the single tool for linting and formatting
- Target Python 3.11+ for new projects
- Type hints required for all function signatures
- mypy in strict mode for type checking
- pytest for testing framework
- Pre-commit hooks configured with Ruff@types/* available)
- Compatible license (MIT, Apache 2.0, BSD)
- Security audit passed within last year

### Version Control
- Semantic versioning (MAJOR.MINOR.PATCH)
- CHANGELOG.md updated for every release
- Git tags for all releases
- Breaking changes require major version bump
- Feature branches named: feature/description, fix/description, docs/description

## Governance

This constitution supersedes all other development practices. All code changes must demonstrate compliance with these principles. When complexity is unavoidable, it must be documented and justified.

Amendments to this constitution require:
1. Documented proposal with rationale
2. Team consensus approval
3. Migration plan for existing code (if applicable)
4. Version bump and changelog entry

All pull requests and code reviews must verify compliance with this constitution. Use Context7 for runtime development guidance and documentation standards.

**Version**: 1.0.0 | **Ratified**: 2025-01-05 | **Last Amended**: 2025-01-05
