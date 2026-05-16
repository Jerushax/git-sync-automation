import hashlib
import hmac
import os
from datetime import datetime
from pathlib import Path
from typing import List


def generate_branch_name(prefix: str) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{prefix}/{timestamp}"


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def is_excluded(file_path: str, excluded_paths: List[str]) -> bool:
    return any(file_path.startswith(path) for path in excluded_paths)


def validate_signature(secret: str, payload: bytes, signature: str) -> bool:
    digest = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    expected_signature = f"sha256={digest}"
    return hmac.compare_digest(expected_signature, signature)


def get_env_variable(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise EnvironmentError(f"Missing required environment variable: {name}")

    return value