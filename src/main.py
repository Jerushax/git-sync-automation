import os
from pathlib import Path
from git import Repo
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

from src.config_loader import ConfigLoader
from src.git_manager import GitManager
from src.logger import setup_logger
from src.mr_creator import GitLabMRCreator
from src.sync_engine import SyncEngine
from src.utils import generate_branch_name
from src.webhook_handler import WebhookHandler

# Load environment variables
load_dotenv()

# Load config
config = ConfigLoader.load().data

# Logger
logger = setup_logger(config["logging"]["file"])

app = FastAPI(title="Repo Sync Automation")


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy"}


@app.post("/webhook")
async def webhook(request: Request):

    try:
        # Validate webhook
        payload = await WebhookHandler.process_webhook(request)
        logger.info("Webhook validated successfully")

        # Repo paths
        source_repo_path = Path("repos/source_repo")
        target_repo_path = Path("repos/target_repo")

        # Git managers
        source_manager = GitManager(
            repo_url=config["source_repo"]["url"],
            local_path=source_repo_path,
            branch=config["source_repo"]["branch"]
        )

        target_manager = GitManager(
            repo_url=config["target_repo"]["url"],
            local_path=target_repo_path,
            branch=config["target_repo"]["branch"]
        )

        # Clone / pull
        source_manager.clone_or_pull()
        target_manager.clone_or_pull()

        # Git repo object
        repo = Repo(source_repo_path)

        current_commit = repo.head.commit.hexsha

        if repo.head.commit.parents:
            previous_commit = repo.head.commit.parents[0].hexsha
        else:
            previous_commit = current_commit

        logger.info("Previous commit: %s", previous_commit)
        logger.info("Current commit: %s", current_commit)

        # Detect changes
        changed_files = source_manager.get_changed_files(
            previous_commit,
            current_commit
        )

        logger.info("Changed files detected: %s", changed_files)

        #  IMPORTANT: STOP EARLY IF NO CHANGES
        if not changed_files:
            logger.info("No changes detected. Skipping sync.")
            return {"message": "No changes detected"}

        # Generate branch ONLY when needed
        branch_name = generate_branch_name(
            config["sync"]["sync_branch_prefix"]
        )

        logger.info("Creating branch: %s", branch_name)

        # Checkout branch
        target_manager.checkout_branch(branch_name)

        # Sync engine
        sync_engine = SyncEngine(
            excluded_paths=config["sync"]["excluded_paths"]
        )

        synced_files = sync_engine.sync_files(
            source_repo_path=source_repo_path,
            target_repo_path=target_repo_path,
            changed_files=changed_files
        )

        logger.info("Synced files: %s", synced_files)

        # Commit & push
        target_manager.commit_and_push(
            branch_name=branch_name,
            commit_message="Automated sync from Repo A"
        )

        logger.info("Branch pushed successfully")

        # MR creation
        mr_creator = GitLabMRCreator(
            gitlab_url="https://gitlab.com",
            project_id="82195055",
            token=os.getenv("GITLAB_TOKEN")
        )

        mr_response = mr_creator.create_merge_request(
            source_branch=branch_name,
            target_branch=config["merge_request"]["target_branch"],
            title="Auto Sync: Changes from Repo A",
            source_commit=current_commit,
            synced_files=synced_files
        )

        logger.info("Merge request created successfully")

        return {
            "message": "Sync completed successfully",
            "merge_request_url": mr_response.get("web_url")
        }

    except Exception as exc:
        logger.exception("Sync failed")
        raise HTTPException(status_code=500, detail=str(exc))