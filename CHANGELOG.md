# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-03-24

### Added
- **5 new rules** (GIT-011 to GIT-015): non-linear history, conventional commits, PR labels, branch flow target, develop protection
- **`scan` command**: Scan local git repositories directly — no YAML needed
- **`github` command**: Audit remote GitHub repos via REST API
- **`init` command**: Generate starter configuration files
- **`validate` command**: Schema validation for config files
- **`--version` flag**: Display version information
- **SARIF export**: GitHub Code Scanning integration (`--format sarif`)
- **CSV export**: Spreadsheet-friendly output (`--format csv`)
- **Schema validation**: Strict mode catches malformed YAML configs
- **Local git scanner**: Auto-detect branches, commit ages, divergence from `.git/`
- **GitHub API scanner**: Fetch branches, PRs, protection status remotely
- Sample config files in `examples/` directory
- `py.typed` marker for PEP 561 compliance
- CONTRIBUTING.md with development guidelines
- GitHub issue templates (bug report + feature request)
- Pull request template
- Makefile with common development commands
- Pre-commit hook configuration
- Expanded test suite (90+ tests, 96%+ coverage)
- PyPI classifiers for better discoverability

### Changed
- Version bumped to 2.0.0
- All lint issues fixed (0 ruff warnings)
- CI pipeline: added coverage reporting, removed `continue-on-error` on lint
- CLI output helper refactored to support 5 formats
- Demo updated to showcase all 15 rules
- README completely rewritten with architecture docs

### Fixed
- Unused `re` import in parser.py
- Unused `Severity` import in flow_analyzer.py
- 26 line-too-long lint warnings
- 8 unsorted-import warnings
- 7 unused-import warnings

## [1.0.0] - 2026-03-20

### Added
- Initial release with 10 rules (GIT-001 to GIT-010)
- `audit` command for YAML config analysis
- `demo` command with sample data
- `rules` command to list validation rules
- Terminal, JSON, and HTML output formats
- `--fail-on` severity threshold for CI gates
- Docker multi-stage build with non-root user
- CI/CD pipeline with multi-version Python testing
- Automated PyPI publishing
- 38 tests with 96% coverage
