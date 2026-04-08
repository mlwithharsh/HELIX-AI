from __future__ import annotations

import httpx

from ...config import Settings
from .base import BasePlatformAdapter


class DiscordAdapter(BasePlatformAdapter):
    platform = "discord"

    def __init__(self, settings: Settings):
        self.settings = settings

    def validate_credentials(self) -> tuple[bool, str]:
        if self.settings.discord_webhook_url:
            return True, "ok"
        if self.settings.discord_bot_token and self.settings.discord_channel_id:
            return True, "ok"
        return False, "Missing Discord webhook URL or bot token/channel id"

    def format_payload(self, variant: dict[str, object]) -> dict[str, object]:
        text = str(variant.get("generated_text", "")).strip()
        cta = str(variant.get("cta", "")).strip()
        hashtags = variant.get("hashtags", [])
        footer = " ".join(hashtags) if isinstance(hashtags, list) else ""
        content = "\n\n".join(part for part in [text, cta, footer] if part)
        return {"content": content[:2000]}

    def send(self, payload: dict[str, object]) -> dict[str, object]:
        valid, message = self.validate_credentials()
        if not valid:
            return {"ok": False, "error": message}
        if self.settings.discord_webhook_url:
            response = httpx.post(self.settings.discord_webhook_url, json=payload, timeout=20)
            body = response.json() if response.content else {}
            return {"status_code": response.status_code, "body": body}

        headers = {
            "Authorization": f"Bot {self.settings.discord_bot_token}",
            "Content-Type": "application/json",
        }
        url = f"https://discord.com/api/v10/channels/{self.settings.discord_channel_id}/messages"
        response = httpx.post(url, headers=headers, json=payload, timeout=20)
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
            return {"success": True, "external_post_id": str(body.get("id", "")) if isinstance(body, dict) else "", "normalized_status": "sent"}
        message = body.get("message", "Discord request failed") if isinstance(body, dict) else "Discord request failed"
        return {"success": False, "error": message, "normalized_status": "failed"}
