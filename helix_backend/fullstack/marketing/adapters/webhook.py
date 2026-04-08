from __future__ import annotations

import httpx

from ...config import Settings
from .base import BasePlatformAdapter


class WebhookAdapter(BasePlatformAdapter):
    platform = "webhook"

    def __init__(self, settings: Settings):
        self.settings = settings

    def validate_credentials(self) -> tuple[bool, str]:
        if not self.settings.marketing_webhook_url:
            return False, "Missing webhook URL"
        return True, "ok"

    def format_payload(self, variant: dict[str, str]) -> dict[str, object]:
        return {
            "platform": variant.get("platform", "webhook"),
            "campaign_id": variant.get("campaign_id", ""),
            "variant_id": variant.get("id", ""),
            "content": variant.get("generated_text", ""),
            "cta": variant.get("cta", ""),
            "hashtags": variant.get("hashtags", []),
        }

    def send(self, payload: dict[str, object]) -> dict[str, object]:
        valid, message = self.validate_credentials()
        if not valid:
            return {"ok": False, "error": message}
        response = httpx.post(self.settings.marketing_webhook_url, json=payload, timeout=15)
        body = response.json() if response.content else {}
        return {"status_code": response.status_code, "body": body}

    def dry_run(self, payload: dict[str, object]) -> dict[str, object]:
        return {"ok": True, "preview": payload, "mode": "dry_run"}

    def handle_response(self, response: dict[str, object]) -> dict[str, object]:
        if response.get("ok") is True:
            return {"success": True, "external_post_id": "", "normalized_status": "dry_run"}
        status_code = int(response.get("status_code", 0) or 0)
        body = response.get("body", {})
        if 200 <= status_code < 300:
            external_id = ""
            if isinstance(body, dict):
                external_id = str(body.get("id", "") or body.get("external_id", ""))
            return {"success": True, "external_post_id": external_id, "normalized_status": "sent"}
        return {"success": False, "error": "Webhook request failed", "normalized_status": "failed"}
