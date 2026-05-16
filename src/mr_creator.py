from datetime import datetime
from typing import List

import requests

from src.logger import setup_logger
from src.retry_handler import retry_operation

logger = setup_logger("logs/app.log")


class GitLabMRCreator:
    def __init__(
        self,
        gitlab_url: str,
        project_id: str,
        token: str
    ):
        self.gitlab_url = gitlab_url.rstrip("/")
        self.project_id = project_id
        self.token = token

    @retry_operation()
    def create_merge_request(
        self,
        source_branch: str,
        target_branch: str,
        title: str,
        source_commit: str,
        synced_files: List[str]
    ) -> dict:
        endpoint = (
            f"{self.gitlab_url}/api/v4/projects/"
            f"{self.project_id}/merge_requests"
        )

        description = (
            f"## Automated Sync\n"
            f"Source Commit: {source_commit}\n"
            f"Timestamp: {datetime.utcnow()}\n\n"
            f"### Synced Files\n"
            + "\n".join(f"- {file}" for file in synced_files)
        )

        payload = {
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": title,
            "description": description
        }

        headers = {
            "PRIVATE-TOKEN": self.token
        }

        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        logger.info("Merge request created successfully")

        return response.json()