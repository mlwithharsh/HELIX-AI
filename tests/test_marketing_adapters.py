from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path

from helix_backend.fullstack.config import Settings
from helix_backend.fullstack.marketing.adapters.discord import DiscordAdapter
from helix_backend.fullstack.marketing.adapters.linkedin import LinkedInAdapter
from helix_backend.fullstack.marketing.adapters.reddit import RedditAdapter
from helix_backend.fullstack.marketing.adapters.x import XAdapter
from helix_backend.fullstack.marketing.delivery_service import MarketingDeliveryService
from helix_backend.fullstack.marketing.repository import LocalMarketingRepository
from helix_backend.fullstack.marketing.schemas import CreateCampaignRequest


def build_settings(**updates) -> Settings:
    base = Settings()
    return base.model_copy(update={"root_dir": str(Path.cwd()), **updates})


class MarketingAdapterTests(unittest.TestCase):
    def test_x_adapter_threads_long_posts(self):
        settings = build_settings()
        adapter = XAdapter(settings)
        payload = adapter.format_payload({"generated_text": "word " * 120})

        self.assertTrue(payload["is_thread"])
        self.assertGreater(len(payload["segments"]), 1)
        self.assertLessEqual(len(payload["segments"][0]), 280)

    def test_linkedin_adapter_requires_access_token_and_author(self):
        missing = LinkedInAdapter(build_settings())
        valid, message = missing.validate_credentials()
        self.assertFalse(valid)
        self.assertIn("Missing LinkedIn", message)

        ready = LinkedInAdapter(build_settings(linkedin_access_token="token", linkedin_author_urn="urn:li:person:123"))
        valid, message = ready.validate_credentials()
        self.assertTrue(valid)
        self.assertEqual(message, "ok")

    def test_discord_adapter_prefers_webhook_or_bot_credentials(self):
        adapter = DiscordAdapter(build_settings(discord_webhook_url="https://discord.test/webhook"))
        valid, _ = adapter.validate_credentials()
        self.assertTrue(valid)

        bot_adapter = DiscordAdapter(build_settings(discord_bot_token="bot-token", discord_channel_id="123"))
        valid, _ = bot_adapter.validate_credentials()
        self.assertTrue(valid)

    def test_reddit_adapter_formats_reddit_safe_title(self):
        adapter = RedditAdapter(
            build_settings(
                reddit_client_id="id",
                reddit_client_secret="secret",
                reddit_username="user",
                reddit_password="pass",
                reddit_default_subreddit="helix",
            )
        )
        payload = adapter.format_payload(
            {
                "variant_name": "launch-a",
                "generated_text": "# Title line\n\nDetailed launch message for the Helix community.",
            }
        )
        self.assertEqual(payload["sr"], "helix")
        self.assertFalse(str(payload["title"]).startswith("#"))
        self.assertIn("Detailed launch message", payload["text"])


class MarketingDeliveryServiceTests(unittest.TestCase):
    def setUp(self):
        self.settings = build_settings(marketing_db_path="memory/test_marketing_adapters.db")
        self.repository = LocalMarketingRepository(self.settings)
        self.service = MarketingDeliveryService(self.repository, self.settings)
        self.campaign = self.repository.create_campaign(
            CreateCampaignRequest(name="Adapter Test", goal="Validate dispatch", target_audience="operators")
        )

    def _create_job(self, platform: str):
        variant = self.repository.create_variant(
            campaign_id=self.campaign.id,
            platform=platform,
            variant_name=f"{platform}-a",
            prompt_snapshot="snapshot",
            generated_text="Helix launch update with one clear CTA for the audience.",
            cta="Reply for rollout details.",
            hashtags=["#helix", "#launch"],
            score=0,
            experiment_group="A",
            approval_status="approved",
        )
        return self.repository.create_scheduled_job(
            campaign_id=self.campaign.id,
            variant_id=variant.id,
            platform=platform,
            run_at=datetime.now(timezone.utc),
            timezone_name="UTC",
            status="queued",
        )

    def test_platform_statuses_report_new_adapters(self):
        statuses = {item.platform: item for item in self.service.platform_statuses()}
        for platform in ["x", "linkedin", "discord", "reddit", "telegram", "webhook"]:
            self.assertIn(platform, statuses)
        self.assertFalse(statuses["x"].configured)

    def test_dry_run_dispatch_supports_new_platforms(self):
        for platform in ["x", "linkedin", "discord", "reddit"]:
            job = self._create_job(platform)
            log = self.service.dispatch_job(job.id, execution_mode="dry_run")
            self.assertIsNotNone(log)
            self.assertEqual(log.platform, platform)
            self.assertEqual(log.status, "dry_run")

    def test_live_dispatch_fails_fast_when_credentials_are_missing(self):
        job = self._create_job("x")
        log = self.service.dispatch_job(job.id, execution_mode="live")
        self.assertIsNotNone(log)
        self.assertEqual(log.status, "failed")
        self.assertEqual(log.execution_mode, "live")
        self.assertIn("Missing X access token", str(log.response_payload.get("error", "")))


if __name__ == "__main__":
    unittest.main()
