from __future__ import annotations

import httpx

from ...config import Settings
from .base import BasePlatformAdapter


class LinkedInAdapter(BasePlatformAdapter):
    platform = "linkedin"

    def __init__(self, settings: Settings):
        self.settings = settings

    def validate_credentials(self) -> tuple[bool, str]:
        if not self.settings.linkedin_access_token:
            return False, "Missing LinkedIn access token"
        if not self.settings.linkedin_author_urn:
            return False, "Missing LinkedIn author URN"
        return True, "ok"

    def format_payload(self, variant: dict[str, object]) -> dict[str, object]:
        text = str(variant.get("generated_text", "")).strip()
        return {
            "author": self.settings.linkedin_author_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }

    def send(self, payload: dict[str, object]) -> dict[str, object]:
        valid, message = self.validate_credentials()
        if not valid:
            return {"ok": False, "error": message}
        headers = {
            "Authorization": f"Bearer {self.settings.linkedin_access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        response = httpx.post("https://api.linkedin.com/rest/posts", headers=headers, json=payload, timeout=20)
        body = response.json() if response.content else {}
        return {
            "status_code": response.status_code,
            "body": body,
            "entity_id": response.headers.get("x-linkedin-id", "") or response.headers.get("x-restli-id", ""),
        }

    def dry_run(self, payload: dict[str, object]) -> dict[str, object]:
        return {"ok": True, "preview": payload, "mode": "dry_run"}

    def handle_response(self, response: dict[str, object]) -> dict[str, object]:
        if response.get("ok") is True:
            return {"success": True, "external_post_id": "", "normalized_status": "dry_run"}
        status_code = int(response.get("status_code", 0) or 0)
        if 200 <= status_code < 300:
            return {
                "success": True,
                "external_post_id": str(response.get("entity_id", "")),
                "normalized_status": "sent",
            }
        body = response.get("body", {})
        message = body.get("message", "LinkedIn request failed") if isinstance(body, dict) else "LinkedIn request failed"
        return {"success": False, "error": message, "normalized_status": "failed"}
