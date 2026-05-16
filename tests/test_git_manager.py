from pathlib import Path

from src.git_manager import GitManager


def test_git_manager_initialization(tmp_path):
    manager = GitManager(
        repo_url="https://example.com/repo.git",
        local_path=tmp_path,
        branch="main"
    )

    assert manager.branch == "main"