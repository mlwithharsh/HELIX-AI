from __future__ import annotations

import httpx

from ...config import Settings
from .base import BasePlatformAdapter


class TelegramAdapter(BasePlatformAdapter):
    platform = "telegram"

    def __init__(self, settings: Settings):
        self.settings = settings

    def validate_credentials(self) -> tuple[bool, str]:
        if not self.settings.telegram_bot_token:
            return False, "Missing Telegram bot token"
        if not self.settings.telegram_chat_id:
            return False, "Missing Telegram chat id"
        return True, "ok"

    def format_payload(self, variant: dict[str, str]) -> dict[str, str]:
        text = variant.get("generated_text", "").strip()
        return {
            "chat_id": self.settings.telegram_chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }

    def send(self, payload: dict[str, str]) -> dict[str, object]:
        valid, message = self.validate_credentials()
        if not valid:
            return {"ok": False, "error": message}
        response = httpx.post(
            f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage",
            json=payload,
            timeout=15,
        )
        return {"status_code": response.status_code, "body": response.json() if response.content else {}}

    def dry_run(self, payload: dict[str, str]) -> dict[str, object]:
        return {"ok": True, "preview": payload, "mode": "dry_run"}

    def handle_response(self, response: dict[str, object]) -> dict[str, object]:
        if response.get("ok") is True:
            return {"success": True, "external_post_id": "", "normalized_status": "dry_run"}
        status_code = response.get("status_code", 0)
        body = response.get("body", {})
        if isinstance(body, dict) and body.get("ok"):
            result = body.get("result", {})
            external_id = str(result.get("message_id", "")) if isinstance(result, dict) else ""
            return {"success": True, "external_post_id": external_id, "normalized_status": "sent"}
        description = body.get("description", "Telegram request failed") if isinstance(body, dict) else "Telegram request failed"
        return {"success": False, "error": description, "normalized_status": "failed"}
