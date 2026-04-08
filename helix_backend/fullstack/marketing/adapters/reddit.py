from __future__ import annotations

import httpx

from ...config import Settings
from .base import BasePlatformAdapter


class RedditAdapter(BasePlatformAdapter):
    platform = "reddit"

    def __init__(self, settings: Settings):
        self.settings = settings

    def validate_credentials(self) -> tuple[bool, str]:
        required = {
            "client_id": self.settings.reddit_client_id,
            "client_secret": self.settings.reddit_client_secret,
            "username": self.settings.reddit_username,
            "password": self.settings.reddit_password,
            "subreddit": self.settings.reddit_default_subreddit,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            return False, f"Missing Reddit settings: {', '.join(missing)}"
        return True, "ok"

    def format_payload(self, variant: dict[str, object]) -> dict[str, object]:
        text = str(variant.get("generated_text", "")).strip()
        title = self._extract_title(str(variant.get("variant_name", "Helix update")), text)
        return {
            "sr": self.settings.reddit_default_subreddit,
            "kind": "self",
            "title": title,
            "text": text[:40000],
        }

    def send(self, payload: dict[str, object]) -> dict[str, object]:
        valid, message = self.validate_credentials()
        if not valid:
            return {"ok": False, "error": message}
        token = self._access_token()
        if not token:
            return {"ok": False, "error": "Failed to acquire Reddit access token"}

        headers = {
            "Authorization": f"bearer {token}",
            "User-Agent": self.settings.reddit_user_agent,
        }
        response = httpx.post("https://oauth.reddit.com/api/submit", headers=headers, data=payload, timeout=20)
        body = response.json() if response.content else {}
        return {"status_code": response.status_code, "body": body, "permalink": self._extract_permalink(body)}

    def dry_run(self, payload: dict[str, object]) -> dict[str, object]:
        return {"ok": True, "preview": payload, "mode": "dry_run"}

    def handle_response(self, response: dict[str, object]) -> dict[str, object]:
        if response.get("ok") is True:
            return {"success": True, "external_post_id": "", "normalized_status": "dry_run"}
        status_code = int(response.get("status_code", 0) or 0)
        if 200 <= status_code < 300:
            return {
                "success": True,
                "external_post_id": str(response.get("permalink", "")),
                "normalized_status": "sent",
            }
        body = response.get("body", {})
        message = "Reddit request failed"
        if isinstance(body, dict):
            errors = body.get("json", {}).get("errors", [])
            if errors:
                message = ", ".join("/".join(str(part) for part in error if part) for error in errors)
        return {"success": False, "error": message, "normalized_status": "failed"}

    def _access_token(self) -> str:
        auth = (self.settings.reddit_client_id or "", self.settings.reddit_client_secret or "")
        data = {
            "grant_type": "password",
            "username": self.settings.reddit_username or "",
            "password": self.settings.reddit_password or "",
        }
        headers = {"User-Agent": self.settings.reddit_user_agent}
        response = httpx.post("https://www.reddit.com/api/v1/access_token", data=data, auth=auth, headers=headers, timeout=20)
        body = response.json() if response.content else {}
        return str(body.get("access_token", "")) if isinstance(body, dict) else ""

    @staticmethod
    def _extract_title(variant_name: str, text: str) -> str:
        first_line = text.splitlines()[0].strip() if text else variant_name
        first_line = first_line.replace("#", "").replace("*", "").strip()
        base = first_line or variant_name or "Helix update"
        return base[:300]

    @staticmethod
    def _extract_permalink(body: dict[str, object]) -> str:
        if not isinstance(body, dict):
            return ""
        json_block = body.get("json", {})
        data = json_block.get("data", {}) if isinstance(json_block, dict) else {}
        url = data.get("url", "") if isinstance(data, dict) else ""
        return str(url)
