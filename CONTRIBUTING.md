# Contributing to git-flow-cli

Thank you for considering contributing to git-flow-cli! This guide will help you get started.

## Development Setup

```bash
# Clone the repo
git clone https://github.com/SanjaySundarMurthy/git-flow-cli.git
cd git-flow-cli

# Install in development mode
pip install -e ".[dev]"

# Verify installation
git-flow-cli --version
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=git_flow_cli --cov-report=term-missing

# Run a specific test file
pytest tests/test_analyzers.py -v
```

### Linting

```bash
# Check for lint issues
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .
```

### Using Make (optional)

```bash
make test       # Run tests
make lint       # Run linter
make fix        # Auto-fix lint issues
make coverage   # Run tests with coverage
make build      # Build package
make clean      # Clean build artifacts
```

## Project Structure

```
git_flow_cli/
├── __init__.py              # Package version
├── cli.py                   # Click CLI commands
├── models.py                # Data models + 15 rules
├── parser.py                # YAML config parser + validation
├── demo.py                  # Demo data generator
├── py.typed                 # PEP 561 marker
├── analyzers/
│   └── flow_analyzer.py     # Rule engine (GIT-001 to GIT-015)
├── reporters/
│   ├── terminal_reporter.py # Rich terminal output
│   └── export_reporter.py   # JSON, HTML, CSV, SARIF exports
├── scanners/
│   ├── git_scanner.py       # Local .git/ scanner
│   └── github_scanner.py    # GitHub REST API scanner
└── validators/
    └── schema_validator.py  # Config schema validation
```

## Coding Standards

- **Line length**: 100 characters max
- **Python version**: 3.9+
- **Linter**: Ruff (E, F, W, I rules)
- **Tests**: pytest with fixtures in `conftest.py`
- **Commits**: Conventional Commits format preferred

## Adding a New Rule

1. Add the rule definition to `GIT_RULES` in `models.py`
2. Add the check function in `analyzers/flow_analyzer.py`
3. Call the check function from `analyze_flow()`
4. Add tests in `tests/test_analyzers.py`
5. Update the README rules table

## Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Write tests for your changes
4. Ensure all tests pass: `pytest -v`
5. Ensure linting passes: `ruff check .`
6. Commit changes: `git commit -m 'feat: add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## Reporting Issues

Use [GitHub Issues](https://github.com/SanjaySundarMurthy/git-flow-cli/issues) with the provided templates.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
