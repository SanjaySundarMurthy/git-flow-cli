"""Tests for flow analyzer and parser."""
from git_flow_cli.parser import parse_repo_config, classify_branch
from git_flow_cli.analyzers.flow_analyzer import analyze_flow
from git_flow_cli.models import BranchType, BranchStrategy, Branch, PullRequest, PRStatus, RepoConfig


class TestParser:
    def test_classify_main(self):
        assert classify_branch("main") == BranchType.MAIN
        assert classify_branch("master") == BranchType.MAIN

    def test_classify_develop(self):
        assert classify_branch("develop") == BranchType.DEVELOP

    def test_classify_feature(self):
        assert classify_branch("feature/auth") == BranchType.FEATURE

    def test_classify_hotfix(self):
        assert classify_branch("hotfix/fix") == BranchType.HOTFIX

    def test_classify_unknown(self):
        assert classify_branch("random-name") == BranchType.UNKNOWN

    def test_parse_repo_config(self, sample_yaml):
        config = parse_repo_config(sample_yaml)
        assert config.name == "acme-platform"
        assert config.strategy == BranchStrategy.GITFLOW
        assert len(config.branches) == 2
        assert len(config.pull_requests) == 1

    def test_parse_empty(self):
        config = parse_repo_config("")
        assert config.name == ""

    def test_parse_branches(self, sample_yaml):
        config = parse_repo_config(sample_yaml)
        main = [b for b in config.branches if b.name == "main"][0]
        assert main.is_protected is True
        assert main.branch_type == BranchType.MAIN


class TestFlowAnalyzer:
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
            branches=[Branch(name="feature/behind", branch_type=BranchType.FEATURE, behind_main=75)],
        )
        report = analyze_flow(config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-008" in rule_ids

    def test_git009_stale_pr(self, basic_config):
        report = analyze_flow(basic_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-009" in rule_ids

    def test_git010_no_linked_issue(self, basic_config):
        report = analyze_flow(basic_config)
        rule_ids = [f.rule_id for f in report.findings]
        assert "GIT-010" in rule_ids

    def test_healthy_repo_high_score(self, healthy_config):
        report = analyze_flow(healthy_config)
        assert report.health_score >= 80

    def test_merged_prs_skipped(self):
        config = RepoConfig(
            pull_requests=[PullRequest(number=1, status=PRStatus.MERGED, approvals=0)],
        )
        report = analyze_flow(config)
        # Merged PRs should be skipped
        pr_findings = [f for f in report.findings if "PR #1" in f.resource_name]
        assert len(pr_findings) == 0
