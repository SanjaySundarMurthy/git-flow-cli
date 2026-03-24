"""Tests for local git scanner."""
import os

import pytest

from git_flow_cli.scanners.git_scanner import (
    is_git_repo,
    scan_local_repo,
)


class TestGitScanner:
    def test_is_git_repo_true(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        assert is_git_repo(str(tmp_path)) is True

    def test_is_git_repo_false(self, tmp_path):
        assert is_git_repo(str(tmp_path)) is False

    def test_scan_non_git_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Not a git"):
            scan_local_repo(str(tmp_path))

    def test_scan_real_repo(self):
        """Scan the git-flow-cli repo itself."""
        repo_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        if not os.path.isdir(os.path.join(repo_path, ".git")):
            pytest.skip("Not running inside a git repo")
        config = scan_local_repo(repo_path)
        assert config.name != ""
        assert len(config.branches) > 0
