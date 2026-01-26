"""GitHub webhook endpoint for push event notifications."""

import hashlib
import hmac
import json
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request

from atlas.config import settings
from atlas.entrypoints.dependencies import Atlas

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_github_signature(
    payload: bytes, signature: Optional[str], secret: str
) -> bool:
    """
    Verify GitHub webhook signature (HMAC SHA-256).

    Args:
        payload: Raw request body bytes
        signature: X-Hub-Signature-256 header value
        secret: Configured webhook secret

    Returns:
        True if signature is valid, False otherwise
    """
    if not signature or not secret:
        return False
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/github")
async def github_webhook(
    request: Request,
    atlas: Atlas,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
) -> dict:
    """
    Handle GitHub webhook events.

    Verifies signature (if GITHUB_WEBHOOK_SECRET configured),
    refreshes catalog cache on push events.

    Only processes 'push' events - other events are acknowledged but ignored.
    """
    payload = await request.body()

    if settings.github_webhook_secret:
        if not verify_github_signature(
            payload, x_hub_signature_256, settings.github_webhook_secret
        ):
            raise HTTPException(status_code=401, detail="Invalid signature")

    if x_github_event != "push":
        return {"status": "ignored", "reason": f"Event type '{x_github_event}' not handled"}

    data = json.loads(payload)

    changed_paths: set[str] = set()
    for commit in data.get("commits", []):
        changed_paths.update(commit.get("added", []))
        changed_paths.update(commit.get("modified", []))
        changed_paths.update(commit.get("removed", []))

    catalog_paths = [
        p for p in changed_paths if p.startswith(("skills/", "mcps/", "tools/"))
    ]

    if not catalog_paths:
        return {"status": "ok", "refreshed": False, "reason": "No catalog paths changed"}

    await atlas.refresh_catalog_cache()

    return {
        "status": "ok",
        "refreshed": True,
        "paths_changed": len(catalog_paths),
    }
