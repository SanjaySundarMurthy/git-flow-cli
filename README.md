# 🌿 git-flow-cli

[![CI](https://github.com/SanjaySundarMurthy/git-flow-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/SanjaySundarMurthy/git-flow-cli/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/devops-git-flow-cli)](https://pypi.org/project/devops-git-flow-cli/)
[![PyPI](https://img.shields.io/pypi/v/devops-git-flow-cli)](https://pypi.org/project/devops-git-flow-cli/)

**Branch strategy enforcer and PR health checker for Git workflows.**

Audits repository branching patterns and PR health against 10 best-practice rules (GIT-001 to GIT-010) covering branch protection, naming conventions, PR size, approvals, CI status, and stale resources.

## Installation

```bash
pip install devops-git-flow-cli
```

## Usage

```bash
# Audit repository config
git-flow-cli audit repo-config.yaml

# Fail on critical findings
git-flow-cli audit repo-config.yaml --fail-on critical

# JSON output
git-flow-cli audit repo-config.yaml --format json

# Run demo
git-flow-cli demo

# List rules
git-flow-cli rules
```




## Command Reference

### `git-flow-cli audit`

Audit a repository against branching best practices.

```bash
git-flow-cli audit <config-file> [OPTIONS]

Options:
  --format [text|json]    Output format (default: text)
  --fail-on [SEVERITY]    Exit with code 1 if findings at this level or above
```

### `git-flow-cli demo`

Run a built-in demo with sample repository configuration.

```bash
git-flow-cli demo
```

### `git-flow-cli rules`

Display all validation rules.

```bash
git-flow-cli rules
```

## Sample Output

```
git-flow-cli v1.0.0 - Branch Strategy Enforcer

Auditing: repo-config.yaml

  GIT-001 [CRITICAL] No Branch Protection on Main
    â†’ main branch has no protection rules enabled
  GIT-004 [HIGH] Stale Feature Branches
    â†’ 5 feature branches older than 30 days detected
  GIT-007 [MEDIUM] Missing PR Template
    â†’ No pull request template found

Score: 62/100 (Grade: D)
Findings: 1 critical, 2 high, 3 medium
```

## Configuration File

```yaml
repository:
  default_branch: main
  branches:
    - name: main
      protected: true
      require_reviews: 2
    - name: develop
      protected: true
  merge_strategy: squash
  max_branch_age_days: 30
```## Rules

| Rule | Severity | Title |
|------|----------|-------|
| GIT-001 | CRITICAL | Main Branch Not Protected |
| GIT-002 | MEDIUM | Invalid Branch Naming Convention |
| GIT-003 | LOW | Stale Branch Detected |
| GIT-004 | HIGH | PR Missing Required Approvals |
| GIT-005 | MEDIUM | Large Pull Request |
| GIT-006 | MEDIUM | PR Missing Description |
| GIT-007 | HIGH | CI Checks Not Passing |
| GIT-008 | MEDIUM | Branch Significantly Behind Main |
| GIT-009 | LOW | Stale Pull Request |
| GIT-010 | LOW | No Linked Issue |

## License

MIT

---

## Author

**Sanjay S** — [GitHub](https://github.com/SanjaySundarMurthy)


## 🐳 Docker

Run without installing Python:

```bash
# Build the image
docker build -t git-flow-cli .

# Run
docker run --rm git-flow-cli --help

# Example with volume mount
docker run --rm -v ${PWD}:/workspace git-flow-cli [command] /workspace
```

Or pull from the container registry:

```bash
docker pull ghcr.io/SanjaySundarMurthy/git-flow-cli:latest
docker run --rm ghcr.io/SanjaySundarMurthy/git-flow-cli:latest --help
```

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please ensure tests pass before submitting:

```bash
pip install devops-git-flow-cli
pytest -v
ruff check .
```

## 🔗 Links

- **PyPI**: [https://pypi.org/project/devops-git-flow-cli/](https://pypi.org/project/devops-git-flow-cli/)
- **GitHub**: [https://github.com/SanjaySundarMurthy/git-flow-cli](https://github.com/SanjaySundarMurthy/git-flow-cli)
- **Issues**: [https://github.com/SanjaySundarMurthy/git-flow-cli/issues](https://github.com/SanjaySundarMurthy/git-flow-cli/issues)