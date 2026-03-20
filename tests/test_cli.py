"""Tests for CLI commands."""
from click.testing import CliRunner
from git_flow_cli.cli import cli


class TestCLI:
    def test_demo_terminal(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["demo"])
        assert result.exit_code == 0
        assert "Git Flow" in result.output or "GIT-" in result.output or "acme-platform" in result.output

    def test_demo_json(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["demo", "--format", "json"])
        assert result.exit_code == 0
        assert "health_score" in result.output
        assert "findings" in result.output

    def test_demo_html(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["demo", "--format", "html"])
        assert result.exit_code == 0
        assert "<html>" in result.output

    def test_rules_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["rules"])
        assert result.exit_code == 0
        assert "Main Branch Not Protected" in result.output

    def test_audit_file(self, tmp_path, sample_yaml):
        cfg = tmp_path / "repo.yaml"
        cfg.write_text(sample_yaml)
        runner = CliRunner()
        result = runner.invoke(cli, ["audit", str(cfg)])
        assert result.exit_code == 0

    def test_audit_json(self, tmp_path, sample_yaml):
        cfg = tmp_path / "repo.yaml"
        cfg.write_text(sample_yaml)
        runner = CliRunner()
        result = runner.invoke(cli, ["audit", str(cfg), "--format", "json"])
        assert result.exit_code == 0
        assert "health_score" in result.output

    def test_audit_output_file(self, tmp_path, sample_yaml):
        cfg = tmp_path / "repo.yaml"
        cfg.write_text(sample_yaml)
        out = tmp_path / "report.json"
        runner = CliRunner()
        result = runner.invoke(cli, ["audit", str(cfg), "--format", "json", "-o", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "git-flow-cli" in result.output
