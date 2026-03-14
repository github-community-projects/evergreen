# Copilot Instructions

This is a GitHub Action that given an organization, team, or specified repositories, opens an issue/PR if dependabot is not enabled, or there are more package ecosystems that could be added. It also enables [automated security updates](https://docs.github.com/en/code-security/dependabot/dependabot-security-updates/configuring-dependabot-security-updates#managing-dependabot-security-updates-for-your-repositories) for the repository. Please follow these guidelines when contributing:

## Code Standards

### Required Before Each Commit

- Run `make lint` before committing any changes to ensure proper code linting and formatting.

### Development Flow

- Lint: `make lint`
- Test: `make test`

## Repository Structure

- `Makefile`: Contains commands for linting, testing, and other tasks
- `pyproject.toml`: Python dependencies and project configuration
- `README.md`: Project documentation and setup instructions
- `test_*.py`: Python test files matching the naming convention for test discovery

## Key Guidelines

1. Follow Python best practices and idiomatic patterns
2. Maintain existing code structure and organization
3. Write unit tests for new functionality.
4. Document changes to environment variables in the `README.md` file.
