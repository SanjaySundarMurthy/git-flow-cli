"""Tests for CLI commands and reporters."""
import json
import os

from click.testing import CliRunner

from git_flow_cli.cli import cli
from git_flow_cli.models import Finding, FlowReport, Severity
from git_flow_cli.reporters.export_reporter import (
    to_csv,
    to_dict,
    to_html,
    to_json,
    to_sarif,
)
from git_flow_cli.reporters.terminal_reporter import (
    print_report,
)


class TestCLIAudit:
    def test_audit_terminal(self, tmp_path, sample_yaml):
        cfg = tmp_path / "repo.yaml"
        cfg.write_text(sample_yaml)
        runner = CliRunner()
        result = runner.invoke(cli, ["audit", str(cfg)])
        assert result.exit_code == 0

    def test_audit_json(self, tmp_path, sample_yaml):
        cfg = tmp_path / "repo.yaml"
        cfg.write_text(sample_yaml)
        runner = CliRunner()
        result = runner.invoke(
            cli, ["audit", str(cfg), "--format", "json"]
        )
        assert result.exit_code == 0
        assert "health_score" in result.output

    def test_audit_html(self, tmp_path, sample_yaml):
        cfg = tmp_path / "repo.yaml"
        cfg.write_text(sample_yaml)
        runner = CliRunner()
        result = runner.invoke(
            cli, ["audit", str(cfg), "--format", "html"]
        )
        assert result.exit_code == 0
        assert "<html>" in result.output

    def test_audit_csv(self, tmp_path, sample_yaml):
        cfg = tmp_path / "repo.yaml"
        cfg.write_text(sample_yaml)
        runner = CliRunner()
        result = runner.invoke(
            cli, ["audit", str(cfg), "--format", "csv"]
        )
        assert result.exit_code == 0
        assert "Rule ID" in result.output

    def test_audit_sarif(self, tmp_path, sample_yaml):
        cfg = tmp_path / "repo.yaml"
        cfg.write_text(sample_yaml)
        runner = CliRunner()
        result = runner.invoke(
            cli, ["audit", str(cfg), "--format", "sarif"]
        )
        assert result.exit_code == 0
        assert "2.1.0" in result.output

    def test_audit_output_file(self, tmp_path, sample_yaml):
        cfg = tmp_path / "repo.yaml"
        cfg.write_text(sample_yaml)
        out = tmp_path / "report.json"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "audit", str(cfg),
                "--format", "json",
                "-o", str(out),
            ],
        )
        assert result.exit_code == 0
        assert out.exists()

    def test_audit_fail_on(self, tmp_path):
        yaml_content = """name: test
branches:
  - name: main
    is_protected: false
"""
        cfg = tmp_path / "repo.yaml"
        cfg.write_text(yaml_content)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["audit", str(cfg), "--fail-on", "critical"],
        )
        assert result.exit_code == 1


class TestCLIDemo:
    def test_demo_terminal(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["demo"])
        assert result.exit_code == 0

    def test_demo_json(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["demo", "--format", "json"]
        )
        assert result.exit_code == 0
        assert "health_score" in result.output
        assert "findings" in result.output

    def test_demo_html(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["demo", "--format", "html"]
        )
        assert result.exit_code == 0
        assert "<html>" in result.output

    def test_demo_csv(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["demo", "--format", "csv"]
        )
        assert result.exit_code == 0

    def test_demo_sarif(self):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["demo", "--format", "sarif"]
        )
        assert result.exit_code == 0


class TestCLIRules:
    def test_rules_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["rules"])
        assert result.exit_code == 0
        assert "Main Branch Not Protected" in result.output

    def test_rules_contains_new_rules(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["rules"])
        assert "Develop Branch" in result.output
        assert "Non-Linear" in result.output


class TestCLIInit:
    def test_init_default(self, tmp_path):
        out = tmp_path / "repo-config.yaml"
        runner = CliRunner()
        result = runner.invoke(
            cli, ["init", "-o", str(out)]
        )
        assert result.exit_code == 0
        assert out.exists()
        content = out.read_text()
        assert "my-repository" in content

    def test_init_with_strategy(self, tmp_path):
        out = tmp_path / "config.yaml"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["init", "-o", str(out), "--strategy", "trunk_based"],
        )
        assert result.exit_code == 0
        assert "trunk_based" in out.read_text()


class TestCLIValidate:
    def test_validate_valid(self, tmp_path, sample_yaml):
        cfg = tmp_path / "repo.yaml"
        cfg.write_text(sample_yaml)
        runner = CliRunner()
        result = runner.invoke(
            cli, ["validate", str(cfg)]
        )
        assert result.exit_code == 0

    def test_validate_invalid(self, tmp_path):
        cfg = tmp_path / "bad.yaml"
        cfg.write_text("not: valid\nmax_pr_size: 0\n")
        runner = CliRunner()
        result = runner.invoke(
            cli, ["validate", str(cfg)]
        )
        assert result.exit_code == 1


class TestCLIVersion:
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "2.0.0" in result.output


class TestCLIHelp:
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "git-flow-cli" in result.output

    def test_audit_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["audit", "--help"])
        assert result.exit_code == 0

    def test_scan_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["scan", "--help"])
        assert result.exit_code == 0

    def test_github_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["github", "--help"])
        assert result.exit_code == 0


class TestExportReporters:
    def _make_report(self):
        return FlowReport(
            repo_name="test-repo",
            findings=[
                Finding(
                    rule_id="GIT-001",
                    title="Test",
                    severity=Severity.CRITICAL,
                    resource_name="main",
                    resource_type="branch",
                    description="Test finding",
                    recommendation="Fix it",
                ),
            ],
        )

    def test_to_dict(self):
        report = self._make_report()
        report.compute_summary()
        d = to_dict(report)
        assert d["repo_name"] == "test-repo"
        assert len(d["findings"]) == 1

    def test_to_json(self):
        report = self._make_report()
        report.compute_summary()
        result = to_json(report)
        data = json.loads(result)
        assert data["repo_name"] == "test-repo"

    def test_to_csv(self):
        report = self._make_report()
        report.compute_summary()
        result = to_csv(report)
        assert "Rule ID" in result
        assert "GIT-001" in result
        assert "CRITICAL" in result

    def test_to_csv_empty(self):
        report = FlowReport()
        report.compute_summary()
        result = to_csv(report)
        assert "Rule ID" in result
        lines = result.strip().split("\n")
        assert len(lines) == 1

    def test_to_sarif(self):
        report = self._make_report()
        report.compute_summary()
        result = to_sarif(report)
        data = json.loads(result)
        assert data["version"] == "2.1.0"
        runs = data["runs"]
        assert len(runs) == 1
        assert len(runs[0]["results"]) == 1

    def test_to_sarif_rule_dedup(self):
        report = FlowReport(
            findings=[
                Finding(
                    rule_id="GIT-001",
                    severity=Severity.CRITICAL,
                    resource_name="r1",
                    resource_type="branch",
                    title="T", description="D",
                    recommendation="R",
                ),
                Finding(
                    rule_id="GIT-001",
                    severity=Severity.CRITICAL,
                    resource_name="r2",
                    resource_type="branch",
                    title="T", description="D",
                    recommendation="R",
                ),
            ],
        )
        report.compute_summary()
        data = json.loads(to_sarif(report))
        rules = data["runs"][0]["tool"]["driver"]["rules"]
        assert len(rules) == 1
        results = data["runs"][0]["results"]
        assert len(results) == 2

    def test_to_html(self):
        report = self._make_report()
        report.compute_summary()
        result = to_html(report)
        assert "<html>" in result
        assert "GIT-001" in result
        assert "test-repo" in result

    def test_to_html_empty(self):
        report = FlowReport(repo_name="empty")
        report.compute_summary()
        result = to_html(report)
        assert "empty" in result


class TestTerminalReporter:
    def test_print_report_no_findings(self, capsys):
        report = FlowReport(repo_name="clean")
        report.compute_summary()
        from rich.console import Console
        console = Console(file=open(os.devnull, "w"))
        print_report(report, console)

    def test_print_report_with_findings(self, capsys):
        report = FlowReport(
            repo_name="test",
            findings=[
                Finding(
                    rule_id="GIT-001",
                    severity=Severity.CRITICAL,
                    resource_name="main",
                    resource_type="branch",
                    title="T", description="D",
                    recommendation="R",
                ),
            ],
        )
        report.compute_summary()
        from rich.console import Console
        console = Console(file=open(os.devnull, "w"))
        print_report(report, console)
