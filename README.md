# 🌿 git-flow-cli

**Branch strategy enforcer and PR health checker for Git workflows.**

Audits repository branching patterns and PR health against 10 best-practice rules (GIT-001 to GIT-010) covering branch protection, naming conventions, PR size, approvals, CI status, and stale resources.

## Installation

```bash
pip install -e .
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

## Rules

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
