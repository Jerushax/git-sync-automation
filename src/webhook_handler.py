import os

from dotenv import load_dotenv
from fastapi import HTTPException, Request

from src.logger import setup_logger

load_dotenv()

logger = setup_logger("logs/app.log")


class WebhookHandler:

    @staticmethod
    async def process_webhook(request: Request):
        """
        Validate GitLab webhook secret
        and return payload.
        """

        gitlab_token = request.headers.get("X-Gitlab-Token")
        expected_token = os.getenv("WEBHOOK_SECRET")

        logger.info("Received webhook token: %s", gitlab_token)
        logger.info("Expected webhook token: %s", expected_token)

        if not gitlab_token:
            logger.error("Missing webhook token")
            raise HTTPException(
                status_code=401,
                detail="Missing webhook token"
            )

        if gitlab_token.strip() != expected_token.strip():
            logger.error("Invalid webhook secret")

            raise HTTPException(
                status_code=401,
                detail="Unauthorized"
            )

        payload = await request.json()

        logger.info("Webhook validated successfully")

        return payload