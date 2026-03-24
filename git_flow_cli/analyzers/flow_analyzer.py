"""Git flow analyzer - applies GIT-001 to GIT-015 rules."""
import re

from ..models import (
    CONVENTIONAL_COMMIT_PATTERN,
    GIT_RULES,
    GITFLOW_TARGETS,
    BranchStrategy,
    BranchType,
    Finding,
    FlowReport,
    PRStatus,
    RepoConfig,
)


def analyze_flow(config: RepoConfig) -> FlowReport:
    """Analyze repository against git flow best practices."""
    report = FlowReport(
        strategy=config.strategy,
        repo_name=config.name,
        branches=config.branches,
        pull_requests=config.pull_requests,
    )
    _check_main_protection(config, report)
    _check_develop_protection(config, report)
    for branch in config.branches:
        _check_branch_naming(branch, config, report)
        _check_stale_branch(branch, report)
        _check_behind_main(branch, config, report)
        _check_linear_history(branch, config, report)
    for pr in config.pull_requests:
        if pr.status not in (PRStatus.OPEN, PRStatus.DRAFT):
            continue
        _check_pr_approvals(pr, config, report)
        _check_pr_size(pr, config, report)
        _check_pr_description(pr, report)
        _check_ci_passing(pr, report)
        _check_stale_pr(pr, config, report)
        _check_linked_issue(pr, report)
        _check_conventional_commits(pr, config, report)
        _check_pr_labels(pr, config, report)
        _check_branch_flow_target(pr, config, report)
    report.compute_summary()
    return report


def _make_finding(
    rule_id: str,
    resource_name: str,
    resource_type: str,
    **overrides,
) -> Finding:
    rule = GIT_RULES[rule_id]
    return Finding(
        rule_id=rule_id,
        title=overrides.get("title", rule["title"]),
        severity=overrides.get("severity", rule["severity"]),
        resource_name=resource_name,
        resource_type=resource_type,
        description=overrides.get(
            "description", rule["description"]
        ),
        recommendation=overrides.get(
            "recommendation", rule["recommendation"]
        ),
    )


def _check_main_protection(config: RepoConfig, report: FlowReport):
    """GIT-001: Main branch not protected."""
    main_branches = [
        b for b in config.branches
        if b.branch_type == BranchType.MAIN
    ]
    for branch in main_branches:
        if not branch.is_protected:
            report.findings.append(
                _make_finding("GIT-001", branch.name, "branch")
            )


def _check_branch_naming(
    branch, config: RepoConfig, report: FlowReport
):
    """GIT-002: Invalid branch naming convention."""
    if branch.branch_type in (BranchType.MAIN, BranchType.DEVELOP):
        return
    pattern = config.branch_naming_pattern
    if pattern and not re.match(pattern, branch.name):
        desc = (
            f"Branch '{branch.name}' does not match"
            f" pattern: {pattern}"
        )
        report.findings.append(
            _make_finding(
                "GIT-002", branch.name, "branch",
                description=desc,
            )
        )


def _check_stale_branch(branch, report: FlowReport):
    """GIT-003: Stale branch."""
    skip = (BranchType.MAIN, BranchType.DEVELOP)
    if branch.branch_type not in skip:
        if branch.last_commit_age_days > 30:
            days = branch.last_commit_age_days
            desc = (
                f"Branch '{branch.name}' last updated"
                f" {days} days ago"
            )
            report.findings.append(
                _make_finding(
                    "GIT-003", branch.name, "branch",
                    description=desc,
                )
            )


def _check_pr_approvals(
    pr, config: RepoConfig, report: FlowReport
):
    """GIT-004: Missing required approvals."""
    if pr.approvals < config.required_approvals:
        got = pr.approvals
        need = config.required_approvals
        desc = f"PR #{pr.number} has {got}/{need} approvals"
        report.findings.append(
            _make_finding(
                "GIT-004", f"PR #{pr.number}",
                "pull_request", description=desc,
            )
        )


def _check_pr_size(pr, config: RepoConfig, report: FlowReport):
    """GIT-005: Large pull request."""
    total_changes = pr.lines_added + pr.lines_deleted
    if total_changes > config.max_pr_size:
        desc = (
            f"PR #{pr.number} has {total_changes}"
            f" line changes (max: {config.max_pr_size})"
        )
        report.findings.append(
            _make_finding(
                "GIT-005", f"PR #{pr.number}",
                "pull_request", description=desc,
            )
        )


def _check_pr_description(pr, report: FlowReport):
    """GIT-006: Missing description."""
    if not pr.has_description:
        report.findings.append(
            _make_finding(
                "GIT-006", f"PR #{pr.number}", "pull_request"
            )
        )


def _check_ci_passing(pr, report: FlowReport):
    """GIT-007: CI not passing."""
    if not pr.has_ci_passed:
        report.findings.append(
            _make_finding(
                "GIT-007", f"PR #{pr.number}", "pull_request"
            )
        )


def _check_behind_main(
    branch, config: RepoConfig, report: FlowReport
):
    """GIT-008: Branch significantly behind main."""
    skip = (BranchType.MAIN, BranchType.DEVELOP)
    if branch.branch_type not in skip:
        if branch.behind_main > 50:
            desc = (
                f"Branch '{branch.name}' is"
                f" {branch.behind_main} commits behind"
                f" {config.default_branch}"
            )
            report.findings.append(
                _make_finding(
                    "GIT-008", branch.name, "branch",
                    description=desc,
                )
            )


def _check_stale_pr(pr, config: RepoConfig, report: FlowReport):
    """GIT-009: Stale pull request."""
    if pr.age_days > config.max_pr_age_days:
        desc = (
            f"PR #{pr.number} has been open"
            f" for {pr.age_days} days"
            f" (max: {config.max_pr_age_days})"
        )
        report.findings.append(
            _make_finding(
                "GIT-009", f"PR #{pr.number}",
                "pull_request", description=desc,
            )
        )


def _check_linked_issue(pr, report: FlowReport):
    """GIT-010: No linked issue."""
    if not pr.has_linked_issue:
        report.findings.append(
            _make_finding(
                "GIT-010", f"PR #{pr.number}", "pull_request"
            )
        )


def _check_linear_history(
    branch, config: RepoConfig, report: FlowReport
):
    """GIT-011: Non-linear history detected."""
    if config.enforce_linear_history:
        if not branch.has_linear_history:
            desc = (
                f"Branch '{branch.name}' contains merge"
                " commits breaking linear history"
            )
            report.findings.append(
                _make_finding(
                    "GIT-011", branch.name, "branch",
                    description=desc,
                )
            )


def _check_conventional_commits(
    pr, config: RepoConfig, report: FlowReport
):
    """GIT-012: Unconventional commit messages."""
    if not config.require_conventional_commits:
        return
    if not pr.commit_messages:
        return
    for msg in pr.commit_messages:
        if not re.match(CONVENTIONAL_COMMIT_PATTERN, msg):
            desc = (
                f"PR #{pr.number} has non-conventional"
                f" commit: '{msg[:50]}'"
            )
            report.findings.append(
                _make_finding(
                    "GIT-012", f"PR #{pr.number}",
                    "pull_request", description=desc,
                )
            )
            break


def _check_pr_labels(
    pr, config: RepoConfig, report: FlowReport
):
    """GIT-013: PR missing required labels."""
    if config.required_labels and not pr.labels:
        report.findings.append(
            _make_finding(
                "GIT-013", f"PR #{pr.number}", "pull_request"
            )
        )


def _check_branch_flow_target(
    pr, config: RepoConfig, report: FlowReport
):
    """GIT-014: Invalid branch flow target."""
    if config.strategy != BranchStrategy.GITFLOW:
        return
    src = pr.source_branch
    tgt = pr.target_branch
    for prefix, valid_targets in GITFLOW_TARGETS.items():
        if src.startswith(f"{prefix}/"):
            if tgt not in valid_targets:
                desc = (
                    f"PR #{pr.number}: {prefix}/ branch"
                    f" targets '{tgt}' instead of"
                    f" {valid_targets}"
                )
                report.findings.append(
                    _make_finding(
                        "GIT-014", f"PR #{pr.number}",
                        "pull_request", description=desc,
                    )
                )
            break


def _check_develop_protection(
    config: RepoConfig, report: FlowReport
):
    """GIT-015: Develop branch not protected."""
    if config.strategy != BranchStrategy.GITFLOW:
        return
    dev_branches = [
        b for b in config.branches
        if b.branch_type == BranchType.DEVELOP
    ]
    for branch in dev_branches:
        if not branch.is_protected:
            report.findings.append(
                _make_finding(
                    "GIT-015", branch.name, "branch"
                )
            )
