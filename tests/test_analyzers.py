"""Tests for flow analyzer, parser, and validators."""

import pytest

from git_flow_cli.analyzers.flow_analyzer import analyze_flow
from git_flow_cli.models import (
    Branch,
    BranchStrategy,
    BranchType,
    PRStatus,
    PullRequest,
    RepoConfig,
)
from git_flow_cli.parser import (
    ConfigValidationError,
    classify_branch,
    parse_repo_config,
    validate_config,
)


class TestClassifyBranch:
    def test_main(self):
        assert classify_branch("main") == BranchType.MAIN

    def test_master(self):
        assert classify_branch("master") == BranchType.MAIN

    def test_develop(self):
        assert classify_branch("develop") == BranchType.DEVELOP

    def test_dev(self):
        assert classify_branch("dev") == BranchType.DEVELOP

    def test_development(self):
        assert classify_branch("development") == BranchType.DEVELOP

    def test_feature(self):
        assert classify_branch("feature/auth") == BranchType.FEATURE

    def test_hotfix(self):
        assert classify_branch("hotfix/fix") == BranchType.HOTFIX

    def test_bugfix(self):
        assert classify_branch("bugfix/fix") == BranchType.BUGFIX

    def test_release(self):
        assert classify_branch("release/1.0") == BranchType.RELEASE

    def test_support(self):
        assert classify_branch("support/lts") == BranchType.SUPPORT

    def test_unknown(self):
        assert classify_branch("random-name") == BranchType.UNKNOWN


class TestParser:
    def test_parse_repo_config(self, sample_yaml):
        config = parse_repo_config(sample_yaml)
        assert config.name == "acme-platform"
        assert config.strategy == BranchStrategy.GITFLOW
        assert len(config.branches) == 2
        assert len(config.pull_requests) == 1

    def test_parse_empty(self):
        config = parse_repo_config("")
        assert config.name == ""

    def test_parse_empty_strict_raises(self):
        with pytest.raises(ConfigValidationError):
            parse_repo_config("", strict=True)

    def test_parse_branches(self, sample_yaml):
        config = parse_repo_config(sample_yaml)
        main = [
            b for b in config.branches if b.name == "main"
        ][0]
        assert main.is_protected is True
        assert main.branch_type == BranchType.MAIN

    def test_parse_new_fields(self, sample_yaml):
        config = parse_repo_config(sample_yaml)
        assert config.enforce_linear_history is True
        assert config.require_conventional_commits is True
        assert config.required_labels == ["bug", "enhancement"]

    def test_parse_pr_commit_messages(self, sample_yaml):
        config = parse_repo_config(sample_yaml)
        pr = config.pull_requests[0]
        assert len(pr.commit_messages) == 1
        assert "feat(auth)" in pr.commit_messages[0]

    def test_parse_pr_labels(self, sample_yaml):
        config = parse_repo_config(sample_yaml)
        pr = config.pull_requests[0]
        assert "enhancement" in pr.labels

    def test_parse_has_linear_history(self, sample_yaml):
        config = parse_repo_config(sample_yaml)
        main = [
            b for b in config.branches if b.name == "main"
        ][0]
        assert main.has_linear_history is True

    def test_default_strategy_fallback(self):
        yaml_content = "name: test\n"
        config = parse_repo_config(yaml_content)
        assert config.strategy == BranchStrategy.GITFLOW

    def test_parse_all_strategies(self):
        for s in ["gitflow", "github_flow", "trunk_based", "release_flow"]:
            yaml_content = f"name: test\nstrategy: {s}\n"
            config = parse_repo_config(yaml_content)
            assert config.strategy.value == s


class TestValidateConfig:
    def test_valid_config(self):
        data = {
            "name": "test",
            "default_branch": "main",
            "strategy": "gitflow",
        }
        errors = validate_config(data)
        assert len(errors) == 0

    def test_missing_name(self):
        data = {"default_branch": "main"}
        errors = validate_config(data)
        assert any("name" in e for e in errors)

    def test_invalid_strategy(self):
        data = {
            "name": "test",
            "strategy": "invalid_strategy",
        }
        errors = validate_config(data)
        assert any("strategy" in e.lower() for e in errors)

    def test_negative_approvals(self):
        data = {
            "name": "test",
            "required_approvals": -1,
        }
        errors = validate_config(data)
        assert any("approvals" in e for e in errors)

    def test_zero_pr_size(self):
        data = {"name": "test", "max_pr_size": 0}
        errors = validate_config(data)
        assert any("max_pr_size" in e for e in errors)

    def test_branches_not_list(self):
        data = {
            "name": "test",
            "branches": "not-a-list",
        }
        errors = validate_config(data)
        assert any("list" in e for e in errors)

    def test_not_a_dict(self):
        errors = validate_config("string")
        assert any("mapping" in e for e in errors)


class TestAnalyzerOriginalRules:
    def test_git001_main_unprotected(self, basic_config):
        report = analyze_flow(basic_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-001" in rule_ids

    def test_git001_main_protected(self, healthy_config):
        report = analyze_flow(healthy_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-001" not in rule_ids

    def test_git002_bad_naming(self, basic_config):
        report = analyze_flow(basic_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-002" in rule_ids

    def test_git002_main_skipped(self):
        config = RepoConfig(
            branches=[Branch(
                name="main",
                branch_type=BranchType.MAIN,
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-002"
            for f in report.findings
        )

    def test_git003_stale_branch(self, basic_config):
        report = analyze_flow(basic_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-003" in rule_ids

    def test_git003_fresh_branch(self, healthy_config):
        report = analyze_flow(healthy_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-003" not in rule_ids

    def test_git004_missing_approvals(self, basic_config):
        report = analyze_flow(basic_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-004" in rule_ids

    def test_git004_sufficient_approvals(self, healthy_config):
        report = analyze_flow(healthy_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-004" not in rule_ids

    def test_git005_large_pr(self, basic_config):
        report = analyze_flow(basic_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-005" in rule_ids

    def test_git006_missing_description(self, basic_config):
        report = analyze_flow(basic_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-006" in rule_ids

    def test_git007_ci_failing(self, basic_config):
        report = analyze_flow(basic_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-007" in rule_ids

    def test_git008_behind_main(self):
        config = RepoConfig(
            branches=[Branch(
                name="feature/behind",
                branch_type=BranchType.FEATURE,
                behind_main=75,
            )],
        )
        report = analyze_flow(config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-008" in rule_ids

    def test_git008_not_behind(self):
        config = RepoConfig(
            branches=[Branch(
                name="feature/close",
                branch_type=BranchType.FEATURE,
                behind_main=10,
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-008"
            for f in report.findings
        )

    def test_git009_stale_pr(self, basic_config):
        report = analyze_flow(basic_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-009" in rule_ids

    def test_git010_no_linked_issue(self, basic_config):
        report = analyze_flow(basic_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-010" in rule_ids


class TestAnalyzerNewRules:
    def test_git011_nonlinear_history(self):
        config = RepoConfig(
            enforce_linear_history=True,
            branches=[Branch(
                name="feature/nl",
                branch_type=BranchType.FEATURE,
                has_linear_history=False,
            )],
        )
        report = analyze_flow(config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-011" in rule_ids

    def test_git011_linear_history_ok(self):
        config = RepoConfig(
            enforce_linear_history=True,
            branches=[Branch(
                name="feature/lin",
                branch_type=BranchType.FEATURE,
                has_linear_history=True,
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-011"
            for f in report.findings
        )

    def test_git011_disabled(self):
        config = RepoConfig(
            enforce_linear_history=False,
            branches=[Branch(
                name="feature/nl",
                branch_type=BranchType.FEATURE,
                has_linear_history=False,
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-011"
            for f in report.findings
        )

    def test_git012_unconventional_commit(self):
        config = RepoConfig(
            require_conventional_commits=True,
            pull_requests=[PullRequest(
                number=1, status=PRStatus.OPEN,
                commit_messages=["wip stuff"],
            )],
        )
        report = analyze_flow(config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-012" in rule_ids

    def test_git012_conventional_commit_ok(self):
        config = RepoConfig(
            require_conventional_commits=True,
            pull_requests=[PullRequest(
                number=1, status=PRStatus.OPEN,
                commit_messages=["feat(auth): add login"],
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-012"
            for f in report.findings
        )

    def test_git012_disabled(self):
        config = RepoConfig(
            require_conventional_commits=False,
            pull_requests=[PullRequest(
                number=1, status=PRStatus.OPEN,
                commit_messages=["wip stuff"],
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-012"
            for f in report.findings
        )

    def test_git012_empty_commits(self):
        config = RepoConfig(
            require_conventional_commits=True,
            pull_requests=[PullRequest(
                number=1, status=PRStatus.OPEN,
                commit_messages=[],
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-012"
            for f in report.findings
        )

    def test_git013_missing_labels(self):
        config = RepoConfig(
            required_labels=["bug", "enhancement"],
            pull_requests=[PullRequest(
                number=1, status=PRStatus.OPEN,
                labels=[],
            )],
        )
        report = analyze_flow(config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-013" in rule_ids

    def test_git013_has_labels(self):
        config = RepoConfig(
            required_labels=["bug"],
            pull_requests=[PullRequest(
                number=1, status=PRStatus.OPEN,
                labels=["bug"],
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-013"
            for f in report.findings
        )

    def test_git013_no_requirement(self):
        config = RepoConfig(
            required_labels=[],
            pull_requests=[PullRequest(
                number=1, status=PRStatus.OPEN,
                labels=[],
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-013"
            for f in report.findings
        )

    def test_git014_invalid_flow_target(self):
        config = RepoConfig(
            strategy=BranchStrategy.GITFLOW,
            pull_requests=[PullRequest(
                number=1, status=PRStatus.OPEN,
                source_branch="feature/wrong",
                target_branch="main",
            )],
        )
        report = analyze_flow(config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-014" in rule_ids

    def test_git014_valid_flow_target(self):
        config = RepoConfig(
            strategy=BranchStrategy.GITFLOW,
            pull_requests=[PullRequest(
                number=1, status=PRStatus.OPEN,
                source_branch="feature/good",
                target_branch="develop",
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-014"
            for f in report.findings
        )

    def test_git014_hotfix_to_main_ok(self):
        config = RepoConfig(
            strategy=BranchStrategy.GITFLOW,
            pull_requests=[PullRequest(
                number=1, status=PRStatus.OPEN,
                source_branch="hotfix/fix",
                target_branch="main",
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-014"
            for f in report.findings
        )

    def test_git014_non_gitflow_skipped(self):
        config = RepoConfig(
            strategy=BranchStrategy.GITHUB_FLOW,
            pull_requests=[PullRequest(
                number=1, status=PRStatus.OPEN,
                source_branch="feature/wrong",
                target_branch="main",
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-014"
            for f in report.findings
        )

    def test_git015_develop_unprotected(self):
        config = RepoConfig(
            strategy=BranchStrategy.GITFLOW,
            branches=[Branch(
                name="develop",
                branch_type=BranchType.DEVELOP,
                is_protected=False,
            )],
        )
        report = analyze_flow(config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-015" in rule_ids

    def test_git015_develop_protected(self):
        config = RepoConfig(
            strategy=BranchStrategy.GITFLOW,
            branches=[Branch(
                name="develop",
                branch_type=BranchType.DEVELOP,
                is_protected=True,
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-015"
            for f in report.findings
        )

    def test_git015_non_gitflow_skipped(self):
        config = RepoConfig(
            strategy=BranchStrategy.GITHUB_FLOW,
            branches=[Branch(
                name="develop",
                branch_type=BranchType.DEVELOP,
                is_protected=False,
            )],
        )
        report = analyze_flow(config)
        assert all(
            f.rule_id != "GIT-015"
            for f in report.findings
        )


class TestAnalyzerEdgeCases:
    def test_healthy_repo_high_score(self, healthy_config):
        report = analyze_flow(healthy_config)
        assert report.health_score >= 80

    def test_merged_prs_skipped(self):
        config = RepoConfig(
            pull_requests=[PullRequest(
                number=1, status=PRStatus.MERGED,
                approvals=0,
            )],
        )
        report = analyze_flow(config)
        pr_findings = [
            f for f in report.findings
            if "PR #1" in f.resource_name
        ]
        assert len(pr_findings) == 0

    def test_closed_prs_skipped(self):
        config = RepoConfig(
            pull_requests=[PullRequest(
                number=1, status=PRStatus.CLOSED,
                approvals=0,
            )],
        )
        report = analyze_flow(config)
        pr_findings = [
            f for f in report.findings
            if "PR #1" in f.resource_name
        ]
        assert len(pr_findings) == 0

    def test_draft_prs_checked(self):
        config = RepoConfig(
            required_approvals=2,
            pull_requests=[PullRequest(
                number=1, status=PRStatus.DRAFT,
                approvals=0,
            )],
        )
        report = analyze_flow(config)
        pr_findings = [
            f for f in report.findings
            if "PR #1" in f.resource_name
        ]
        assert len(pr_findings) > 0

    def test_empty_repo(self):
        config = RepoConfig()
        report = analyze_flow(config)
        assert report.health_score == 100.0

    def test_full_gitflow_perfect(self, full_gitflow_config):
        report = analyze_flow(full_gitflow_config)
        assert report.health_score >= 80
