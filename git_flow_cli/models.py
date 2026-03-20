"""Data models for git flow analysis."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class BranchStrategy(str, Enum):
    GITFLOW = "gitflow"
    GITHUB_FLOW = "github_flow"
    TRUNK_BASED = "trunk_based"
    RELEASE_FLOW = "release_flow"


class BranchType(str, Enum):
    MAIN = "main"
    DEVELOP = "develop"
    FEATURE = "feature"
    RELEASE = "release"
    HOTFIX = "hotfix"
    BUGFIX = "bugfix"
    SUPPORT = "support"
    UNKNOWN = "unknown"


class PRStatus(str, Enum):
    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"
    DRAFT = "draft"


class MergeStrategy(str, Enum):
    MERGE_COMMIT = "merge_commit"
    SQUASH = "squash"
    REBASE = "rebase"
    FAST_FORWARD = "fast_forward"


@dataclass
class Branch:
    name: str = ""
    branch_type: BranchType = BranchType.UNKNOWN
    is_protected: bool = False
    last_commit_age_days: int = 0
    ahead_of_main: int = 0
    behind_main: int = 0
    author: str = ""
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class PullRequest:
    number: int = 0
    title: str = ""
    source_branch: str = ""
    target_branch: str = ""
    status: PRStatus = PRStatus.OPEN
    author: str = ""
    reviewers: list[str] = field(default_factory=list)
    approvals: int = 0
    required_approvals: int = 1
    has_ci_passed: bool = True
    has_description: bool = True
    files_changed: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    age_days: int = 0
    has_linked_issue: bool = False
    merge_strategy: MergeStrategy = MergeStrategy.SQUASH
    labels: list[str] = field(default_factory=list)


@dataclass
class RepoConfig:
    name: str = ""
    default_branch: str = "main"
    strategy: BranchStrategy = BranchStrategy.GITFLOW
    branches: list[Branch] = field(default_factory=list)
    pull_requests: list[PullRequest] = field(default_factory=list)
    required_approvals: int = 1
    enforce_linear_history: bool = False
    branch_naming_pattern: str = r"^(feature|bugfix|hotfix|release)/[a-z0-9-]+$"
    max_pr_size: int = 500
    max_pr_age_days: int = 14
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class Finding:
    rule_id: str = ""
    title: str = ""
    severity: Severity = Severity.INFO
    resource_name: str = ""
    resource_type: str = ""
    description: str = ""
    recommendation: str = ""


@dataclass
class FlowReport:
    strategy: BranchStrategy = BranchStrategy.GITFLOW
    repo_name: str = ""
    branches: list[Branch] = field(default_factory=list)
    pull_requests: list[PullRequest] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    total_branches: int = 0
    total_prs: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    health_score: float = 100.0
    grade: str = "A"

    def compute_summary(self):
        self.total_branches = len(self.branches)
        self.total_prs = len(self.pull_requests)
        self.critical_count = sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
        self.high_count = sum(1 for f in self.findings if f.severity == Severity.HIGH)
        self.medium_count = sum(1 for f in self.findings if f.severity == Severity.MEDIUM)
        self.low_count = sum(1 for f in self.findings if f.severity == Severity.LOW)
        self.info_count = sum(1 for f in self.findings if f.severity == Severity.INFO)
        penalty = (self.critical_count * 15) + (self.high_count * 10) + (self.medium_count * 5) + (self.low_count * 2)
        self.health_score = max(0.0, 100.0 - penalty)
        if self.health_score >= 90:
            self.grade = "A"
        elif self.health_score >= 80:
            self.grade = "B"
        elif self.health_score >= 70:
            self.grade = "C"
        elif self.health_score >= 60:
            self.grade = "D"
        else:
            self.grade = "F"


GIT_RULES = {
    "GIT-001": {
        "title": "Main Branch Not Protected",
        "severity": Severity.CRITICAL,
        "description": "Main/master branch lacks branch protection rules",
        "recommendation": "Enable branch protection with required reviews and status checks",
    },
    "GIT-002": {
        "title": "Invalid Branch Naming Convention",
        "severity": Severity.MEDIUM,
        "description": "Branch name does not follow the configured naming pattern",
        "recommendation": "Rename branch to follow pattern: feature/, bugfix/, hotfix/, release/",
    },
    "GIT-003": {
        "title": "Stale Branch Detected",
        "severity": Severity.LOW,
        "description": "Branch has not been updated in over 30 days",
        "recommendation": "Delete or update stale branches to keep repository clean",
    },
    "GIT-004": {
        "title": "PR Missing Required Approvals",
        "severity": Severity.HIGH,
        "description": "Pull request does not have the required number of approvals",
        "recommendation": "Request additional reviews before merging",
    },
    "GIT-005": {
        "title": "Large Pull Request",
        "severity": Severity.MEDIUM,
        "description": "PR changes exceed recommended size limit",
        "recommendation": "Break large PRs into smaller, focused changes",
    },
    "GIT-006": {
        "title": "PR Missing Description",
        "severity": Severity.MEDIUM,
        "description": "Pull request has no description or context",
        "recommendation": "Add a clear description explaining the changes and motivation",
    },
    "GIT-007": {
        "title": "CI Checks Not Passing",
        "severity": Severity.HIGH,
        "description": "Pull request has failing CI/CD pipeline checks",
        "recommendation": "Fix CI failures before merging",
    },
    "GIT-008": {
        "title": "Branch Significantly Behind Main",
        "severity": Severity.MEDIUM,
        "description": "Feature branch is more than 50 commits behind main",
        "recommendation": "Rebase or merge main into feature branch to reduce conflicts",
    },
    "GIT-009": {
        "title": "Stale Pull Request",
        "severity": Severity.LOW,
        "description": "Pull request has been open for more than 14 days",
        "recommendation": "Review, update, or close stale pull requests",
    },
    "GIT-010": {
        "title": "No Linked Issue",
        "severity": Severity.LOW,
        "description": "Pull request has no linked issue for tracking",
        "recommendation": "Link a related issue for better traceability",
    },
}
