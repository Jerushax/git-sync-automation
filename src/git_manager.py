import shutil
from pathlib import Path
from typing import List, Tuple

from git import GitCommandError, Repo

from src.logger import setup_logger
from src.retry_handler import retry_operation

logger = setup_logger("logs/app.log")


class GitManager:
    def __init__(
        self,
        repo_url: str,
        local_path: Path,
        branch: str
    ):
        self.repo_url = repo_url
        self.local_path = local_path
        self.branch = branch

    def clone_or_pull(self) -> Repo:
        """
        Clone repository if not exists.
        Otherwise pull latest changes.
        """

        if self.local_path.exists():
            logger.info(
                "Pulling latest changes for %s",
                self.local_path
            )

            repo = Repo(self.local_path)

            repo.git.checkout(self.branch)
            repo.remotes.origin.pull()

            return repo

        logger.info("Cloning repository %s", self.repo_url)

        return Repo.clone_from(
            self.repo_url,
            self.local_path
        )

    def checkout_branch(self, branch_name: str) -> None:
        """
        Create and checkout sync branch.
        """

        repo = Repo(self.local_path)

        try:
            repo.git.checkout("-b", branch_name)

        except GitCommandError:
            repo.git.checkout(branch_name)

    def get_changed_files(
        self,
        previous_commit: str,
        current_commit: str
    ) -> List[Tuple[str, str]]:
        """
        Detect changed files between commits.
        """

        repo = Repo(self.local_path)

        diff_output = repo.git.diff(
            "--name-status",
            previous_commit,
            current_commit
        )

        changed_files = []

        for line in diff_output.splitlines():
            status, file_path = line.split("\t", 1)
            changed_files.append((status, file_path))

        return changed_files

    @retry_operation()
    def commit_and_push(
        self,
        branch_name: str,
        commit_message: str
    ) -> None:
        """
        Commit and push changes.
        """

        repo = Repo(self.local_path)

        repo.git.add(all=True)

        if repo.is_dirty(untracked_files=True):
            repo.index.commit(commit_message)

        logger.info(
            "Pushing branch %s",
            branch_name
        )

        repo.git.push(
            "origin",
            branch_name
        )

    def cleanup(self) -> None:
        """
        Remove local repository.
        """

        if self.local_path.exists():
            shutil.rmtree(self.local_path)