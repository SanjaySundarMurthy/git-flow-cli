"""Parse repository configuration YAML into model objects."""
import yaml

from .models import (
    Branch,
    BranchStrategy,
    BranchType,
    MergeStrategy,
    PRStatus,
    PullRequest,
    RepoConfig,
)

STRATEGY_MAP = {
    "gitflow": BranchStrategy.GITFLOW,
    "github_flow": BranchStrategy.GITHUB_FLOW,
    "trunk_based": BranchStrategy.TRUNK_BASED,
    "release_flow": BranchStrategy.RELEASE_FLOW,
}

PR_STATUS_MAP = {
    "open": PRStatus.OPEN,
    "merged": PRStatus.MERGED,
    "closed": PRStatus.CLOSED,
    "draft": PRStatus.DRAFT,
}

MERGE_MAP = {
    "merge_commit": MergeStrategy.MERGE_COMMIT,
    "squash": MergeStrategy.SQUASH,
    "rebase": MergeStrategy.REBASE,
    "fast_forward": MergeStrategy.FAST_FORWARD,
}

REQUIRED_FIELDS = ["name", "default_branch"]


class ConfigValidationError(Exception):
    """Raised when YAML config has invalid structure."""


def classify_branch(name: str) -> BranchType:
    """Classify a branch name into a BranchType."""
    if name in ("main", "master"):
        return BranchType.MAIN
    elif name in ("develop", "dev", "development"):
        return BranchType.DEVELOP
    elif name.startswith("feature/"):
        return BranchType.FEATURE
    elif name.startswith("release/"):
        return BranchType.RELEASE
    elif name.startswith("hotfix/"):
        return BranchType.HOTFIX
    elif name.startswith("bugfix/"):
        return BranchType.BUGFIX
    elif name.startswith("support/"):
        return BranchType.SUPPORT
    return BranchType.UNKNOWN


def validate_config(data: dict) -> list[str]:
    """Validate config structure and return list of errors."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Config must be a YAML mapping"]
    if "name" not in data:
        errors.append("Missing required field: 'name'")
    strategy = data.get("strategy", "gitflow")
    if strategy.lower() not in STRATEGY_MAP:
        valid = ", ".join(STRATEGY_MAP.keys())
        errors.append(
            f"Invalid strategy '{strategy}'."
            f" Valid: {valid}"
        )
    approvals = data.get("required_approvals", 1)
    if not isinstance(approvals, int) or approvals < 0:
        errors.append(
            "required_approvals must be a non-negative integer"
        )
    max_size = data.get("max_pr_size", 500)
    if not isinstance(max_size, int) or max_size < 1:
        errors.append("max_pr_size must be a positive integer")
    branches = data.get("branches", [])
    if not isinstance(branches, list):
        errors.append("'branches' must be a list")
    prs = data.get("pull_requests", [])
    if not isinstance(prs, list):
        errors.append("'pull_requests' must be a list")
    return errors


def parse_repo_config(
    yaml_content: str, strict: bool = False
) -> RepoConfig:
    """Parse repository configuration from YAML."""
    data = yaml.safe_load(yaml_content)
    if not data:
        if strict:
            raise ConfigValidationError("Empty config")
        return RepoConfig()
    if strict:
        errors = validate_config(data)
        if errors:
            raise ConfigValidationError(
                "; ".join(errors)
            )
    strategy_str = data.get("strategy", "gitflow").lower()
    naming = data.get(
        "branch_naming_pattern",
        r"^(feature|bugfix|hotfix|release)/[a-z0-9-]+$",
    )
    config = RepoConfig(
        name=data.get("name", ""),
        default_branch=data.get("default_branch", "main"),
        strategy=STRATEGY_MAP.get(
            strategy_str, BranchStrategy.GITFLOW
        ),
        required_approvals=data.get("required_approvals", 1),
        enforce_linear_history=data.get(
            "enforce_linear_history", False
        ),
        branch_naming_pattern=naming,
        max_pr_size=data.get("max_pr_size", 500),
        max_pr_age_days=data.get("max_pr_age_days", 14),
        require_conventional_commits=data.get(
            "require_conventional_commits", False
        ),
        required_labels=data.get("required_labels", []),
    )
    for b_data in data.get("branches", []):
        name = b_data.get("name", "")
        branch = Branch(
            name=name,
            branch_type=classify_branch(name),
            is_protected=b_data.get("is_protected", False),
            last_commit_age_days=b_data.get(
                "last_commit_age_days", 0
            ),
            ahead_of_main=b_data.get("ahead_of_main", 0),
            behind_main=b_data.get("behind_main", 0),
            author=b_data.get("author", ""),
            has_linear_history=b_data.get(
                "has_linear_history", True
            ),
        )
        config.branches.append(branch)
    for pr_data in data.get("pull_requests", []):
        status_str = pr_data.get("status", "open").lower()
        merge_str = pr_data.get(
            "merge_strategy", "squash"
        ).lower()
        pr = PullRequest(
            number=pr_data.get("number", 0),
            title=pr_data.get("title", ""),
            source_branch=pr_data.get("source_branch", ""),
            target_branch=pr_data.get(
                "target_branch", "main"
            ),
            status=PR_STATUS_MAP.get(
                status_str, PRStatus.OPEN
            ),
            author=pr_data.get("author", ""),
            reviewers=pr_data.get("reviewers", []),
            approvals=pr_data.get("approvals", 0),
            required_approvals=data.get(
                "required_approvals", 1
            ),
            has_ci_passed=pr_data.get("has_ci_passed", True),
            has_description=pr_data.get(
                "has_description", True
            ),
            files_changed=pr_data.get("files_changed", 0),
            lines_added=pr_data.get("lines_added", 0),
            lines_deleted=pr_data.get("lines_deleted", 0),
            age_days=pr_data.get("age_days", 0),
            has_linked_issue=pr_data.get(
                "has_linked_issue", False
            ),
            merge_strategy=MERGE_MAP.get(
                merge_str, MergeStrategy.SQUASH
            ),
            labels=pr_data.get("labels", []),
            commit_messages=pr_data.get(
                "commit_messages", []
            ),
        )
        config.pull_requests.append(pr)
    return config
