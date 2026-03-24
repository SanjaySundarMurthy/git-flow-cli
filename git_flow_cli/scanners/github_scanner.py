"""GitHub API scanner — fetch repo data via REST API."""
import json
import os
import subprocess
from typing import Optional

from ..models import (
    Branch,
    PRStatus,
    PullRequest,
    RepoConfig,
)
from ..parser import classify_branch


def scan_github_repo(
    owner_repo: str,
    token: Optional[str] = None,
) -> RepoConfig:
    """Scan a GitHub repository via the REST API."""
    token = token or os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise ValueError(
            "GitHub token required. Set GITHUB_TOKEN env var"
            " or use --token flag"
        )

    owner, repo = _parse_owner_repo(owner_repo)
    repo_data = _gh_api(f"/repos/{owner}/{repo}", token)
    branches = _fetch_branches(owner, repo, token)
    prs = _fetch_pull_requests(owner, repo, token)

    default_branch = repo_data.get("default_branch", "main")

    config = RepoConfig(
        name=repo_data.get("full_name", owner_repo),
        default_branch=default_branch,
        branches=branches,
        pull_requests=prs,
    )
    return config


def _parse_owner_repo(owner_repo: str) -> tuple[str, str]:
    """Parse 'owner/repo' string."""
    parts = owner_repo.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError(
            f"Invalid format '{owner_repo}'."
            " Expected: owner/repo"
        )
    return parts[-2], parts[-1]


def _gh_api(endpoint: str, token: str) -> dict:
    """Call GitHub REST API."""
    headers = [
        "-H", "Accept: application/vnd.github+json",
        "-H", f"Authorization: Bearer {token}",
    ]
    result = subprocess.run(
        ["gh", "api", endpoint] + headers,
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"GitHub API error: {result.stderr.strip()}"
        )
    return json.loads(result.stdout)


def _gh_api_list(endpoint: str, token: str) -> list:
    """Call GitHub REST API expecting a list response."""
    data = _gh_api(endpoint, token)
    return data if isinstance(data, list) else []


def _fetch_branches(
    owner: str, repo: str, token: str
) -> list[Branch]:
    """Fetch branches from GitHub API."""
    data = _gh_api_list(
        f"/repos/{owner}/{repo}/branches?per_page=100",
        token,
    )
    branches: list[Branch] = []
    for b in data:
        name = b.get("name", "")
        branch_type = classify_branch(name)
        branches.append(Branch(
            name=name,
            branch_type=branch_type,
            is_protected=b.get("protected", False),
        ))
    return branches


def _fetch_pull_requests(
    owner: str, repo: str, token: str
) -> list[PullRequest]:
    """Fetch open pull requests from GitHub API."""
    data = _gh_api_list(
        f"/repos/{owner}/{repo}/pulls?state=open&per_page=100",
        token,
    )
    prs: list[PullRequest] = []
    for pr_data in data:
        labels = [
            lb.get("name", "")
            for lb in pr_data.get("labels", [])
        ]
        reviewers = [
            r.get("login", "")
            for r in pr_data.get("requested_reviewers", [])
        ]
        source = pr_data.get("head", {}).get("ref", "")
        target = pr_data.get("base", {}).get("ref", "")
        prs.append(PullRequest(
            number=pr_data.get("number", 0),
            title=pr_data.get("title", ""),
            source_branch=source,
            target_branch=target,
            status=PRStatus.OPEN,
            author=pr_data.get("user", {}).get("login", ""),
            reviewers=reviewers,
            has_description=bool(pr_data.get("body", "")),
            files_changed=0,
            labels=labels,
        ))
    return prs
