import shutil
from pathlib import Path
from typing import List, Tuple

from src.conflict_handler import ConflictHandler
from src.logger import setup_logger
from src.utils import ensure_directory, is_excluded

logger = setup_logger("logs/app.log")


class SyncEngine:
    def __init__(self, excluded_paths: List[str]):
        self.excluded_paths = excluded_paths

    def sync_files(
        self,
        source_repo_path: Path,
        target_repo_path: Path,
        changed_files: List[Tuple[str, str]]
    ) -> List[str]:
        synced_files = []

        for status, relative_path in changed_files:
            if is_excluded(relative_path, self.excluded_paths):
                logger.info("Skipping excluded path: %s", relative_path)
                continue

            source_file = source_repo_path / relative_path
            target_file = target_repo_path / relative_path

            if status == "D":
                if target_file.exists():
                    logger.info("Deleting file: %s", target_file)
                    target_file.unlink()
                    synced_files.append(relative_path)
                continue

            ensure_directory(target_file.parent)

            if ConflictHandler.detect_conflict(source_file, target_file):
                raise Exception(f"Conflict detected for file: {relative_path}")

            shutil.copy2(source_file, target_file)
            logger.info("Synced file: %s", relative_path)
            synced_files.append(relative_path)

        return synced_files