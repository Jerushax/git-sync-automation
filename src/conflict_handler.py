from pathlib import Path


class ConflictHandler:
    @staticmethod
    def detect_conflict(source_file: Path, target_file: Path) -> bool:
        if not target_file.exists():
            return False

        source_content = source_file.read_text(encoding="utf-8")
        target_content = target_file.read_text(encoding="utf-8")

        return source_content != target_content