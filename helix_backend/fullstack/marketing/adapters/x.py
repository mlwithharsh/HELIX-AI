from __future__ import annotations

import httpx

from ...config import Settings
from .base import BasePlatformAdapter


class XAdapter(BasePlatformAdapter):
    platform = "x"

    def __init__(self, settings: Settings):
        self.settings = settings

    def validate_credentials(self) -> tuple[bool, str]:
        if not self.settings.x_access_token:
            return False, "Missing X access token"
        return True, "ok"

    def format_payload(self, variant: dict[str, object]) -> dict[str, object]:
        text = str(variant.get("generated_text", "")).strip()
        if len(text) <= 280:
            return {"text": text, "segments": [text], "is_thread": False}

        segments: list[str] = []
        words = text.split()
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(candidate) <= 275:
                current = candidate
                continue
            if current:
                segments.append(current)
            current = word
        if current:
            segments.append(current)
        numbered = [f"{segment} ({index + 1}/{len(segments)})" for index, segment in enumerate(segments)]
        return {"text": numbered[0], "segments": numbered, "is_thread": True}

    def send(self, payload: dict[str, object]) -> dict[str, object]:
        valid, message = self.validate_credentials()
        if not valid:
            return {"ok": False, "error": message}

        headers = {
            "Authorization": f"Bearer {self.settings.x_access_token}",
            "Content-Type": "application/json",
        }
        segments = payload.get("segments", [])
        if not isinstance(segments, list) or not segments:
            segments = [str(payload.get("text", "")).strip()]
        created_ids: list[str] = []
        previous_id = None

        with httpx.Client(timeout=20) as client:
            for segment in segments:
                body: dict[str, object] = {"text": segment}
                if previous_id:
                    body["reply"] = {"in_reply_to_tweet_id": previous_id}
                response = client.post("https://api.x.com/2/tweets", headers=headers, json=body)
                parsed = response.json() if response.content else {}
                if response.status_code >= 300:
                    return {"status_code": response.status_code, "body": parsed, "created_ids": created_ids}
                previous_id = str(parsed.get("data", {}).get("id", "")) if isinstance(parsed, dict) else ""
                if previous_id:
                    created_ids.append(previous_id)

        return {"status_code": 201, "body": {"data": {"id": created_ids[0] if created_ids else ""}}, "created_ids": created_ids}

    def dry_run(self, payload: dict[str, object]) -> dict[str, object]:
        return {"ok": True, "preview": payload, "mode": "dry_run"}

    def handle_response(self, response: dict[str, object]) -> dict[str, object]:
        if response.get("ok") is True:
            preview = response.get("preview", {})
            segments = preview.get("segments", []) if isinstance(preview, dict) else []
            return {
                "success": True,
                "external_post_id": "",
                "normalized_status": "dry_run",
                "thread_size": len(segments) if isinstance(segments, list) else 0,
            }
        status_code = int(response.get("status_code", 0) or 0)
        body = response.get("body", {})
        if 200 <= status_code < 300:
            data = body.get("data", {}) if isinstance(body, dict) else {}
            return {
                "success": True,
                "external_post_id": str(data.get("id", "")),
                "normalized_status": "sent",
                "thread_size": len(response.get("created_ids", [])),
            }
        detail = body.get("detail", "X request failed") if isinstance(body, dict) else "X request failed"
        return {"success": False, "error": detail, "normalized_status": "failed"}
