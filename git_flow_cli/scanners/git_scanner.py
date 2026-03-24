"""Local git repository scanner."""
import os
import subprocess
from datetime import datetime, timezone

from ..models import Branch, BranchType, RepoConfig
from ..parser import classify_branch


def _run_git(args: list[str], cwd: str) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout.strip()


def is_git_repo(path: str) -> bool:
    """Check if path is inside a git repository."""
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir)


def scan_local_repo(path: str) -> RepoConfig:
    """Scan a local git repository and build a RepoConfig."""
    if not is_git_repo(path):
        raise ValueError(f"Not a git repository: {path}")

    repo_name = os.path.basename(os.path.abspath(path))
    default_branch = _get_default_branch(path)
    branches = _get_branches(path, default_branch)

    config = RepoConfig(
        name=repo_name,
        default_branch=default_branch,
        branches=branches,
    )
    return config


def _get_default_branch(cwd: str) -> str:
    """Detect the default branch (main or master)."""
    head = _run_git(
        ["symbolic-ref", "refs/remotes/origin/HEAD"],
        cwd,
    )
    if head:
        return head.split("/")[-1]
    # Fallback: check if main or master exists
    branches = _run_git(["branch", "-a"], cwd)
    if "main" in branches:
        return "main"
    if "master" in branches:
        return "master"
    return "main"


def _get_branches(
    cwd: str, default_branch: str
) -> list[Branch]:
    """List all branches with metadata."""
    raw = _run_git(
        ["branch", "-a", "--format",
         "%(refname:short)|%(committerdate:iso)"],
        cwd,
    )
    if not raw:
        return []

    branches: list[Branch] = []
    now = datetime.now(timezone.utc)

    for line in raw.strip().split("\n"):
        if not line or "->" in line:
            continue
        parts = line.split("|", 1)
        name = parts[0].strip()
        # Strip remote prefix
        if name.startswith("origin/"):
            name = name[7:]

        # Skip duplicates
        if any(b.name == name for b in branches):
            continue

        age_days = 0
        if len(parts) > 1 and parts[1].strip():
            try:
                date_str = parts[1].strip()
                commit_date = datetime.fromisoformat(date_str)
                age_days = (now - commit_date).days
            except (ValueError, TypeError):
                pass

        branch_type = classify_branch(name)
        is_protected = branch_type in (
            BranchType.MAIN, BranchType.DEVELOP
        )

        behind = _get_behind_count(cwd, name, default_branch)

        branches.append(Branch(
            name=name,
            branch_type=branch_type,
            is_protected=is_protected,
            last_commit_age_days=age_days,
            behind_main=behind,
        ))

    return branches


def _get_behind_count(
    cwd: str, branch: str, default_branch: str
) -> int:
    """Count how many commits a branch is behind default."""
    if branch == default_branch:
        return 0
    try:
        result = _run_git(
            ["rev-list", "--count",
             f"{branch}..{default_branch}"],
            cwd,
        )
        return int(result) if result else 0
    except (ValueError, subprocess.SubprocessError):
        return 0
