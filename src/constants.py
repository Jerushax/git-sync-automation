from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "config.yaml"
LOG_DIR = BASE_DIR / "logs"
REPO_DIR = BASE_DIR / "repos"

SUPPORTED_EVENTS = [
    "Merge Request Hook",
    "Push Hook"
]