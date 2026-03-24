"""Tests for data models."""
from git_flow_cli.models import (
    CONVENTIONAL_COMMIT_PATTERN,
    GIT_RULES,
    GITFLOW_TARGETS,
    Branch,
    BranchStrategy,
    BranchType,
    Finding,
    FlowReport,
    MergeStrategy,
    PRStatus,
    PullRequest,
    RepoConfig,
    Severity,
)


class TestBranchModel:
    def test_defaults(self):
        b = Branch()
        assert b.branch_type == BranchType.UNKNOWN
        assert not b.is_protected
        assert b.has_linear_history is True

    def test_custom_values(self):
        b = Branch(
            name="feature/test",
            branch_type=BranchType.FEATURE,
            is_protected=True,
            behind_main=10,
        )
        assert b.name == "feature/test"
        assert b.is_protected

    def test_labels_default_empty(self):
        b = Branch()
        assert b.labels == {}


class TestPRModel:
    def test_defaults(self):
        pr = PullRequest()
        assert pr.status == PRStatus.OPEN
        assert pr.approvals == 0
        assert pr.commit_messages == []
        assert pr.labels == []

    def test_custom_values(self):
        pr = PullRequest(
            number=42, title="Test",
            labels=["bug"],
            commit_messages=["fix: resolve bug"],
        )
        assert pr.number == 42
        assert pr.labels == ["bug"]


class TestRepoConfig:
    def test_defaults(self):
        config = RepoConfig()
        assert config.strategy == BranchStrategy.GITFLOW
        assert config.required_approvals == 1
        assert not config.enforce_linear_history
        assert not config.require_conventional_commits
        assert config.required_labels == []

    def test_custom_config(self):
        config = RepoConfig(
            name="test",
            enforce_linear_history=True,
            require_conventional_commits=True,
            required_labels=["bug"],
        )
        assert config.enforce_linear_history
        assert config.required_labels == ["bug"]


class TestFlowReport:
    def test_compute_summary_empty(self):
        report = FlowReport()
        report.compute_summary()
        assert report.health_score == 100.0
        assert report.grade == "A"

    def test_compute_summary_with_findings(self):
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

    def test_grade_a(self):
        report = FlowReport()
        report.compute_summary()
        assert report.grade == "A"

    def test_grade_b(self):
        report = FlowReport(
            findings=[Finding(severity=Severity.MEDIUM)] * 3,
        )
        report.compute_summary()
        assert report.grade == "B"

    def test_grade_c(self):
        report = FlowReport(
            findings=[Finding(severity=Severity.HIGH)] * 3,
        )
        report.compute_summary()
        assert report.grade == "C"

    def test_grade_d(self):
        report = FlowReport(
            findings=[Finding(severity=Severity.HIGH)] * 4,
        )
        report.compute_summary()
        assert report.grade == "D"

    def test_grade_f(self):
        report = FlowReport(
            findings=[
                Finding(severity=Severity.CRITICAL)
            ] * 7,
        )
        report.compute_summary()
        assert report.grade == "F"

    def test_score_floor_zero(self):
        report = FlowReport(
            findings=[
                Finding(severity=Severity.CRITICAL)
            ] * 20,
        )
        report.compute_summary()
        assert report.health_score == 0.0

    def test_info_no_penalty(self):
        report = FlowReport(
            findings=[Finding(severity=Severity.INFO)] * 5,
        )
        report.compute_summary()
        assert report.health_score == 100.0
        assert report.info_count == 5


class TestRules:
    def test_rules_count(self):
        assert len(GIT_RULES) == 15

    def test_rules_sequential_ids(self):
        for i in range(1, 16):
            assert f"GIT-{i:03d}" in GIT_RULES

    def test_all_severities_in_rules(self):
        severities = {
            r["severity"] for r in GIT_RULES.values()
        }
        assert Severity.CRITICAL in severities
        assert Severity.HIGH in severities
        assert Severity.MEDIUM in severities
        assert Severity.LOW in severities

    def test_all_rules_have_required_keys(self):
        for rule_id, rule in GIT_RULES.items():
            assert "title" in rule, f"{rule_id} missing title"
            assert "severity" in rule
            assert "description" in rule
            assert "recommendation" in rule


class TestEnums:
    def test_severity_values(self):
        assert Severity.CRITICAL.value == "critical"
        assert Severity.INFO.value == "info"

    def test_branch_strategy_values(self):
        assert BranchStrategy.GITFLOW.value == "gitflow"
        assert BranchStrategy.TRUNK_BASED.value == "trunk_based"

    def test_pr_status_values(self):
        assert PRStatus.OPEN.value == "open"
        assert PRStatus.DRAFT.value == "draft"

    def test_merge_strategy_values(self):
        assert MergeStrategy.SQUASH.value == "squash"

    def test_branch_type_values(self):
        assert BranchType.MAIN.value == "main"
        assert BranchType.UNKNOWN.value == "unknown"


class TestConstants:
    def test_conventional_pattern_exists(self):
        import re
        assert re.match(
            CONVENTIONAL_COMMIT_PATTERN,
            "feat(auth): add login",
        )
        assert not re.match(
            CONVENTIONAL_COMMIT_PATTERN,
            "wip stuff",
        )

    def test_gitflow_targets(self):
        assert "feature" in GITFLOW_TARGETS
        assert "develop" in GITFLOW_TARGETS["feature"]
        assert "hotfix" in GITFLOW_TARGETS
        assert "main" in GITFLOW_TARGETS["hotfix"]
