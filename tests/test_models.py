"""Tests for data models."""
from git_flow_cli.models import (
    Branch, PullRequest, RepoConfig, FlowReport, Finding,
    BranchType, BranchStrategy, PRStatus, Severity, GIT_RULES,
)


class TestModels:
    def test_branch_defaults(self):
        b = Branch()
        assert b.branch_type == BranchType.UNKNOWN
        assert not b.is_protected

    def test_pr_defaults(self):
        pr = PullRequest()
        assert pr.status == PRStatus.OPEN
        assert pr.approvals == 0

    def test_report_compute_summary_empty(self):
        report = FlowReport()
        report.compute_summary()
        assert report.health_score == 100.0
        assert report.grade == "A"

    def test_report_compute_summary_with_findings(self):
        report = FlowReport(
            branches=[Branch()],
            pull_requests=[PullRequest()],
            findings=[
                Finding(severity=Severity.CRITICAL),
                Finding(severity=Severity.HIGH),
            ],
        )
        report.compute_summary()
        assert report.critical_count == 1
        assert report.high_count == 1
        assert report.health_score == 75.0
        assert report.grade == "C"

    def test_grade_f(self):
        report = FlowReport(findings=[Finding(severity=Severity.CRITICAL)] * 7)
        report.compute_summary()
        assert report.grade == "F"

    def test_rules_exist(self):
        assert len(GIT_RULES) == 10
        for i in range(1, 11):
            assert f"GIT-{i:03d}" in GIT_RULES

    def test_all_severities_in_rules(self):
        severities = {r["severity"] for r in GIT_RULES.values()}
        assert Severity.CRITICAL in severities
        assert Severity.HIGH in severities
        assert Severity.MEDIUM in severities
        assert Severity.LOW in severities
