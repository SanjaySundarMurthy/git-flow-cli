---
title: "🌿 git-flow-cli v2.0: Branch Strategy Enforcer with Live Scanning & 15 Rules"
published: true
description: "A Python CLI that audits Git workflows with 15 rules, live repo scanning, GitHub API integration, SARIF export, and 5 output formats."
tags: git, devops, python, opensource
---

## What I Built

**git-flow-cli** — a comprehensive branch strategy enforcer and PR health checker.

### v2.0 Highlights

- **15 Validation Rules** — GIT-001 to GIT-015
- **Live Git Scanning** — `git-flow-cli scan .` reads your `.git/` directly
- **GitHub API Integration** — `git-flow-cli github owner/repo`
- **5 Output Formats** — Terminal, JSON, HTML, CSV, SARIF
- **CI/CD Ready** — `--fail-on` gates + SARIF for GitHub Code Scanning
- **Config Generator** — `git-flow-cli init` scaffolds configs
- **Schema Validation** — Catches malformed YAML before audit

### New Rules in v2.0

| Rule | What it catches |
|------|----------------|
| GIT-011 | Non-linear history (merge commits) |
| GIT-012 | Non-conventional commit messages |
| GIT-013 | PRs missing required labels |
| GIT-014 | PRs targeting wrong branches per strategy |
| GIT-015 | Unprotected develop branch |

### Architecture

`
7 CLI commands → Parser + Validator → Analyzer (15 rules) → 5 Reporters
                  ↑ YAML configs        ↑ Local git scanner
                                         ↑ GitHub API scanner
`

## Test Results

`
136 passed in 0.70s
Coverage: 86%
Lint: 0 errors (ruff)
`

## Quick Start

`ash
pip install devops-git-flow-cli

# Scan your repo
git-flow-cli scan .

# Or audit a config
git-flow-cli audit repo-config.yaml --format json

# Generate SARIF for GitHub Code Scanning
git-flow-cli audit config.yaml --format sarif -o results.sarif
`

## Links

- **GitHub**: [git-flow-cli](https://github.com/SanjaySundarMurthy/git-flow-cli)
- **PyPI**: [devops-git-flow-cli](https://pypi.org/project/devops-git-flow-cli/)
- **Part of**: DevOps CLI Tools Suite
