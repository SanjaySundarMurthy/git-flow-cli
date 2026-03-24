"""Shared test fixtures for git-flow-cli."""
import pytest

from git_flow_cli.models import (
    Branch,
    BranchStrategy,
    BranchType,
    PRStatus,
    PullRequest,
    RepoConfig,
)


@pytest.fixture
def main_unprotected():
    return Branch(
        name="main", branch_type=BranchType.MAIN,
        is_protected=False,
    )


@pytest.fixture
def main_protected():
    return Branch(
        name="main", branch_type=BranchType.MAIN,
        is_protected=True,
    )


@pytest.fixture
def develop_unprotected():
    return Branch(
        name="develop", branch_type=BranchType.DEVELOP,
        is_protected=False,
    )


@pytest.fixture
def develop_protected():
    return Branch(
        name="develop", branch_type=BranchType.DEVELOP,
        is_protected=True,
    )


@pytest.fixture
def stale_branch():
    return Branch(
        name="feature/old-stuff",
        branch_type=BranchType.FEATURE,
        last_commit_age_days=45,
    )


@pytest.fixture
def fresh_branch():
    return Branch(
        name="feature/new-work",
        branch_type=BranchType.FEATURE,
        last_commit_age_days=2,
    )


@pytest.fixture
def bad_name_branch():
    return Branch(
        name="my-experiment",
        branch_type=BranchType.UNKNOWN,
        last_commit_age_days=5,
    )


@pytest.fixture
def behind_branch():
    return Branch(
        name="feature/behind-work",
        branch_type=BranchType.FEATURE,
        behind_main=75,
    )


@pytest.fixture
def nonlinear_branch():
    return Branch(
        name="feature/nonlinear",
        branch_type=BranchType.FEATURE,
        has_linear_history=False,
    )


@pytest.fixture
def good_pr():
    return PullRequest(
        number=1, title="Add feature",
        source_branch="feature/auth",
        target_branch="develop", status=PRStatus.OPEN,
        approvals=2, required_approvals=2,
        has_ci_passed=True, has_description=True,
        files_changed=10, lines_added=100,
        lines_deleted=20, age_days=3,
        has_linked_issue=True,
        labels=["enhancement"],
        commit_messages=["feat(auth): add login"],
    )


@pytest.fixture
def bad_pr():
    return PullRequest(
        number=2, title="Big change",
        source_branch="feature/payment",
        target_branch="develop", status=PRStatus.OPEN,
        approvals=0, required_approvals=2,
        has_ci_passed=False, has_description=False,
        files_changed=50, lines_added=800,
        lines_deleted=200, age_days=20,
        has_linked_issue=False, labels=[],
        commit_messages=["wip stuff", "fix things"],
    )


@pytest.fixture
def bad_target_pr():
    return PullRequest(
        number=3, title="Feature to main",
        source_branch="feature/wrong-target",
        target_branch="main", status=PRStatus.OPEN,
        approvals=2, has_ci_passed=True,
        has_description=True, has_linked_issue=True,
        labels=["enhancement"],
    )


@pytest.fixture
def basic_config(
    main_unprotected, stale_branch, bad_name_branch,
    good_pr, bad_pr,
):
    return RepoConfig(
        name="test-repo",
        strategy=BranchStrategy.GITFLOW,
        branches=[
            main_unprotected, stale_branch, bad_name_branch,
        ],
        pull_requests=[good_pr, bad_pr],
        required_approvals=2,
        max_pr_size=500,
        max_pr_age_days=14,
    )


@pytest.fixture
def healthy_config(main_protected, fresh_branch, good_pr):
    return RepoConfig(
        name="healthy-repo",
        strategy=BranchStrategy.GITHUB_FLOW,
        branches=[main_protected, fresh_branch],
        pull_requests=[good_pr],
        required_approvals=2,
    )


@pytest.fixture
def full_gitflow_config(
    main_protected, develop_protected,
    fresh_branch, good_pr,
):
    return RepoConfig(
        name="full-gitflow",
        strategy=BranchStrategy.GITFLOW,
        branches=[
            main_protected, develop_protected, fresh_branch,
        ],
        pull_requests=[good_pr],
        required_approvals=2,
        enforce_linear_history=True,
        require_conventional_commits=True,
        required_labels=["bug", "enhancement"],
    )


@pytest.fixture
def sample_yaml():
    return """name: acme-platform
default_branch: main
strategy: gitflow
required_approvals: 2
enforce_linear_history: true
require_conventional_commits: true
max_pr_size: 500
max_pr_age_days: 14
required_labels:
  - bug
  - enhancement
branches:
  - name: main
    is_protected: true
    last_commit_age_days: 0
    has_linear_history: true
  - name: feature/auth
    is_protected: false
    last_commit_age_days: 3
    behind_main: 10
pull_requests:
  - number: 42
    title: Add auth
    source_branch: feature/auth
    target_branch: develop
    status: open
    approvals: 2
    has_ci_passed: true
    has_description: true
    lines_added: 100
    lines_deleted: 20
    has_linked_issue: true
    labels:
      - enhancement
    commit_messages:
      - "feat(auth): add login"
"""


@pytest.fixture
def invalid_yaml():
    return """name: test
strategy: invalid_strategy
required_approvals: -1
max_pr_size: 0
branches: not-a-list
"""


@pytest.fixture
def empty_yaml():
    return ""
