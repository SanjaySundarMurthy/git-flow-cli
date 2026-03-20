"""Git flow analyzer — applies GIT-001 to GIT-010 rules."""
import re
from ..models import (
    RepoConfig, FlowReport, Finding, Severity, BranchType,
    PRStatus, GIT_RULES,
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
    for branch in config.branches:
        _check_branch_naming(branch, config, report)
        _check_stale_branch(branch, report)
        _check_behind_main(branch, config, report)
    for pr in config.pull_requests:
        if pr.status not in (PRStatus.OPEN, PRStatus.DRAFT):
            continue
        _check_pr_approvals(pr, config, report)
        _check_pr_size(pr, config, report)
        _check_pr_description(pr, report)
        _check_ci_passing(pr, report)
        _check_stale_pr(pr, config, report)
        _check_linked_issue(pr, report)
    report.compute_summary()
    return report


def _make_finding(rule_id: str, resource_name: str, resource_type: str, **overrides) -> Finding:
    rule = GIT_RULES[rule_id]
    return Finding(
        rule_id=rule_id,
        title=overrides.get("title", rule["title"]),
        severity=overrides.get("severity", rule["severity"]),
        resource_name=resource_name,
        resource_type=resource_type,
        description=overrides.get("description", rule["description"]),
        recommendation=overrides.get("recommendation", rule["recommendation"]),
    )


def _check_main_protection(config: RepoConfig, report: FlowReport):
    """GIT-001: Main branch not protected."""
    main_branches = [b for b in config.branches if b.branch_type == BranchType.MAIN]
    for branch in main_branches:
        if not branch.is_protected:
            report.findings.append(_make_finding("GIT-001", branch.name, "branch"))


def _check_branch_naming(branch, config: RepoConfig, report: FlowReport):
    """GIT-002: Invalid branch naming convention."""
    if branch.branch_type in (BranchType.MAIN, BranchType.DEVELOP):
        return
    pattern = config.branch_naming_pattern
    if pattern and not re.match(pattern, branch.name):
        report.findings.append(_make_finding("GIT-002", branch.name, "branch",
            description=f"Branch '{branch.name}' does not match pattern: {pattern}"))


def _check_stale_branch(branch, report: FlowReport):
    """GIT-003: Stale branch."""
    if branch.branch_type not in (BranchType.MAIN, BranchType.DEVELOP):
        if branch.last_commit_age_days > 30:
            report.findings.append(_make_finding("GIT-003", branch.name, "branch",
                description=f"Branch '{branch.name}' last updated {branch.last_commit_age_days} days ago"))


def _check_pr_approvals(pr, config: RepoConfig, report: FlowReport):
    """GIT-004: Missing required approvals."""
    if pr.approvals < config.required_approvals:
        report.findings.append(_make_finding("GIT-004", f"PR #{pr.number}", "pull_request",
            description=f"PR #{pr.number} has {pr.approvals}/{config.required_approvals} approvals"))


def _check_pr_size(pr, config: RepoConfig, report: FlowReport):
    """GIT-005: Large pull request."""
    total_changes = pr.lines_added + pr.lines_deleted
    if total_changes > config.max_pr_size:
        report.findings.append(_make_finding("GIT-005", f"PR #{pr.number}", "pull_request",
            description=f"PR #{pr.number} has {total_changes} line changes (max: {config.max_pr_size})"))


def _check_pr_description(pr, report: FlowReport):
    """GIT-006: Missing description."""
    if not pr.has_description:
        report.findings.append(_make_finding("GIT-006", f"PR #{pr.number}", "pull_request"))


def _check_ci_passing(pr, report: FlowReport):
    """GIT-007: CI not passing."""
    if not pr.has_ci_passed:
        report.findings.append(_make_finding("GIT-007", f"PR #{pr.number}", "pull_request"))


def _check_behind_main(branch, config: RepoConfig, report: FlowReport):
    """GIT-008: Branch significantly behind main."""
    if branch.branch_type not in (BranchType.MAIN, BranchType.DEVELOP):
        if branch.behind_main > 50:
            report.findings.append(_make_finding("GIT-008", branch.name, "branch",
                description=f"Branch '{branch.name}' is {branch.behind_main} commits behind {config.default_branch}"))


def _check_stale_pr(pr, config: RepoConfig, report: FlowReport):
    """GIT-009: Stale pull request."""
    if pr.age_days > config.max_pr_age_days:
        report.findings.append(_make_finding("GIT-009", f"PR #{pr.number}", "pull_request",
            description=f"PR #{pr.number} has been open for {pr.age_days} days (max: {config.max_pr_age_days})"))


def _check_linked_issue(pr, report: FlowReport):
    """GIT-010: No linked issue."""
    if not pr.has_linked_issue:
        report.findings.append(_make_finding("GIT-010", f"PR #{pr.number}", "pull_request"))
