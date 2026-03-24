# 🌿 git-flow-cli

[![CI](https://github.com/SanjaySundarMurthy/git-flow-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/SanjaySundarMurthy/git-flow-cli/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/devops-git-flow-cli)](https://pypi.org/project/devops-git-flow-cli/)
[![PyPI](https://img.shields.io/pypi/v/devops-git-flow-cli)](https://pypi.org/project/devops-git-flow-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Branch strategy enforcer and PR health checker for Git workflows.**

Audits repositories against **15 best-practice rules** (GIT-001 to GIT-015) covering branch protection, naming conventions, PR health, CI status, conventional commits, linear history, and branch flow targets. Scan local repos, audit YAML configs, or query GitHub directly via API.

## ✨ Features

- **15 Validation Rules** — GIT-001 to GIT-015 covering branches and PRs
- **Live Git Scanning** — Scan local .git/ repositories directly
- **GitHub API Integration** — Audit remote repos via REST API
- **5 Output Formats** — Terminal (Rich), JSON, HTML, CSV, SARIF
- **CI/CD Integration** — --fail-on severity gates + SARIF for GitHub Code Scanning
- **Config Generator** — init command scaffolds starter configs
- **Schema Validation** — Strict mode catches malformed YAML configs
- **Docker Support** — Multi-stage build with non-root user
- **136 Tests** — 86% coverage with comprehensive rule testing

## 📦 Installation

`ash
pip install devops-git-flow-cli
`

Or with Docker:

`ash
docker pull ghcr.io/sanjaysundarmurthy/git-flow-cli:latest
`

## 🚀 Quick Start

`ash
# Generate a starter config
git-flow-cli init

# Audit the config
git-flow-cli audit repo-config.yaml

# Scan a local git repo (no config needed!)
git-flow-cli scan .

# Audit a GitHub repo via API
git-flow-cli github owner/repo --token $GITHUB_TOKEN

# Run the built-in demo
git-flow-cli demo
`

## 📖 Command Reference

### git-flow-cli audit

Audit a YAML configuration against branching best practices.

`ash
git-flow-cli audit <config-file> [OPTIONS]

Options:
  --format [terminal|json|html|csv|sarif]  Output format (default: terminal)
  --fail-on [critical|high|medium|low]     Exit code 1 if findings at level
  -o, --output PATH                        Save report to file
`

### git-flow-cli scan

Scan a local git repository — auto-detects branches, commit ages, and divergence.

`ash
git-flow-cli scan [PATH] [OPTIONS]

Options:
  --format [terminal|json|html|csv|sarif]  Output format
  --fail-on [critical|high|medium|low]     Exit code 1 if findings at level
  -o, --output PATH                        Save report to file
`

### git-flow-cli github

Audit a remote GitHub repository via the REST API.

`ash
git-flow-cli github <owner/repo> [OPTIONS]

Options:
  -t, --token TEXT                         GitHub personal access token
  --format [terminal|json|html|csv|sarif]  Output format
  --fail-on [critical|high|medium|low]     Exit code 1 if findings at level
  -o, --output PATH                        Save report to file
`

### git-flow-cli init

Generate a starter configuration file.

`ash
git-flow-cli init [OPTIONS]

Options:
  -o, --output PATH                        Output file (default: repo-config.yaml)
  --strategy [gitflow|github_flow|trunk_based|release_flow]  Branching strategy
`

### git-flow-cli validate

Validate a config file against the schema.

`ash
git-flow-cli validate <config-file>
`

### git-flow-cli demo

Run the built-in demo with sample data showcasing all 15 rules.

`ash
git-flow-cli demo [--format terminal|json|html|csv|sarif]
`

### git-flow-cli rules

Display all 15 validation rules in a formatted table.

`ash
git-flow-cli rules
`

### git-flow-cli --version

`ash
git-flow-cli --version
`

## 📏 Rules

| Rule | Severity | Title | Description |
|------|----------|-------|-------------|
| GIT-001 | 🔴 CRITICAL | Main Branch Not Protected | Main/master branch lacks branch protection |
| GIT-002 | 🟡 MEDIUM | Invalid Branch Naming | Branch does not follow naming pattern |
| GIT-003 | 🔵 LOW | Stale Branch Detected | Branch not updated in 30+ days |
| GIT-004 | 🟠 HIGH | PR Missing Approvals | PR lacks required number of approvals |
| GIT-005 | 🟡 MEDIUM | Large Pull Request | PR exceeds size limit |
| GIT-006 | 🟡 MEDIUM | PR Missing Description | PR has no description |
| GIT-007 | 🟠 HIGH | CI Checks Not Passing | PR has failing CI/CD checks |
| GIT-008 | 🟡 MEDIUM | Branch Behind Main | Branch 50+ commits behind main |
| GIT-009 | 🔵 LOW | Stale Pull Request | PR open for 14+ days |
| GIT-010 | 🔵 LOW | No Linked Issue | PR not linked to any issue |
| GIT-011 | 🟡 MEDIUM | Non-Linear History | Merge commits breaking linear history |
| GIT-012 | 🔵 LOW | Unconventional Commits | Commits not following Conventional Commits |
| GIT-013 | 🔵 LOW | PR Missing Labels | PR has no categorization labels |
| GIT-014 | 🟠 HIGH | Invalid Branch Flow | PR targets wrong branch per strategy |
| GIT-015 | 🟠 HIGH | Develop Not Protected | Develop branch lacks protection |

## 📐 Architecture

`
git_flow_cli/
├── __init__.py              # Package version (2.0.0)
├── cli.py                   # 7 Click commands (audit, scan, github, init, validate, demo, rules)
├── models.py                # Data models + 15 rule definitions
├── parser.py                # YAML config parser + schema validation
├── demo.py                  # Demo data generator
├── py.typed                 # PEP 561 type marker
├── analyzers/
│   └── flow_analyzer.py     # Rule engine (GIT-001 to GIT-015)
├── reporters/
│   ├── terminal_reporter.py # Rich terminal output with severity icons
│   └── export_reporter.py   # JSON, HTML, CSV, SARIF exporters
├── scanners/
│   ├── git_scanner.py       # Local .git/ repository scanner
│   └── github_scanner.py    # GitHub REST API scanner
└── validators/
    └── schema_validator.py  # Config file schema validation
`

## ⚙️ Configuration

See [examples/sample-config.yaml](examples/sample-config.yaml) for a fully documented config file.

`yaml
name: my-repository
default_branch: main
strategy: gitflow                # gitflow | github_flow | trunk_based | release_flow
required_approvals: 2
enforce_linear_history: false    # GIT-011: flag merge commits
require_conventional_commits: false  # GIT-012: enforce feat:, fix:, etc.
max_pr_size: 500                 # GIT-005: max lines changed
max_pr_age_days: 14              # GIT-009: max PR open days
branch_naming_pattern: "^(feature|bugfix|hotfix|release)/[a-z0-9-]+$"
required_labels:                 # GIT-013: require labels on PRs
  - bug
  - enhancement
`

## 🐳 Docker

`ash
# Build
docker build -t git-flow-cli .

# Run
docker run --rm git-flow-cli demo
docker run --rm -v ${PWD}:/workspace git-flow-cli audit /workspace/repo-config.yaml
`

## 🔗 CI/CD Integration

### GitHub Actions

`yaml
- name: Audit Git Flow
  run: |
    pip install devops-git-flow-cli
    git-flow-cli audit repo-config.yaml --fail-on high

# Or with SARIF upload for Code Scanning
- name: Git Flow SARIF
  run: |
    pip install devops-git-flow-cli
    git-flow-cli audit repo-config.yaml --format sarif -o results.sarif

- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
`

## 🧪 Development

`ash
# Install in dev mode
pip install -e ".[dev]"

# Run tests
pytest -v

# Run with coverage
pytest --cov=git_flow_cli --cov-report=term-missing

# Lint
ruff check .

# Auto-fix
ruff check . --fix
`

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Ensure tests pass: `pytest -v` and `ruff check .`
4. Commit with conventional format: `git commit -m 'feat: add amazing feature'`
5. Open a Pull Request

## 📝 License

MIT — see [LICENSE](LICENSE)

## 👤 Author

**Sanjay S** — [GitHub](https://github.com/SanjaySundarMurthy)

## 🔗 Links

- **PyPI**: [https://pypi.org/project/devops-git-flow-cli/](https://pypi.org/project/devops-git-flow-cli/)
- **GitHub**: [https://github.com/SanjaySundarMurthy/git-flow-cli](https://github.com/SanjaySundarMurthy/git-flow-cli)
- **Issues**: [https://github.com/SanjaySundarMurthy/git-flow-cli/issues](https://github.com/SanjaySundarMurthy/git-flow-cli/issues)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
