"""Tests for schema validator."""

from git_flow_cli.validators.schema_validator import validate_file


class TestSchemaValidator:
    def test_valid_file(self, tmp_path, sample_yaml):
        cfg = tmp_path / "valid.yaml"
        cfg.write_text(sample_yaml)
        valid, errors = validate_file(str(cfg))
        assert valid is True
        assert len(errors) == 0

    def test_missing_file(self):
        valid, errors = validate_file("/nonexistent/path.yaml")
        assert valid is False
        assert any("not found" in e.lower() for e in errors)

    def test_empty_file(self, tmp_path):
        cfg = tmp_path / "empty.yaml"
        cfg.write_text("")
        valid, errors = validate_file(str(cfg))
        assert valid is False

    def test_invalid_yaml(self, tmp_path):
        cfg = tmp_path / "bad.yaml"
        cfg.write_text("{{invalid yaml::")
        valid, errors = validate_file(str(cfg))
        assert valid is False
        assert any("yaml" in e.lower() for e in errors)

    def test_missing_name(self, tmp_path):
        cfg = tmp_path / "no_name.yaml"
        cfg.write_text("default_branch: main\n")
        valid, errors = validate_file(str(cfg))
        assert valid is False
        assert any("name" in e for e in errors)

    def test_invalid_pr_size(self, tmp_path):
        cfg = tmp_path / "bad_size.yaml"
        cfg.write_text("name: test\nmax_pr_size: 0\n")
        valid, errors = validate_file(str(cfg))
        assert valid is False
