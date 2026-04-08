from __future__ import annotations

import logging

from .adapters import DiscordAdapter, LinkedInAdapter, RedditAdapter, TelegramAdapter, WebhookAdapter, XAdapter
from .credential_service import MarketingCredentialService
from .repository import LocalMarketingRepository
from .schemas import DeliveryLogResponse, PlatformAdapterStatusResponse
from ..config import Settings

logger = logging.getLogger(__name__)

try:
    from apscheduler.schedulers.background import BackgroundScheduler
except Exception:  # pragma: no cover
    BackgroundScheduler = None


class MarketingDeliveryService:
    """Executes queued jobs through platform adapters and records delivery logs."""

    def __init__(self, repository: LocalMarketingRepository, settings: Settings, credential_service: MarketingCredentialService | None = None):
        self.repository = repository
        self.settings = settings
        self.credential_service = credential_service
        self.scheduler = None
        self.adapter_classes = {
            "discord": DiscordAdapter,
            "linkedin": LinkedInAdapter,
            "reddit": RedditAdapter,
            "telegram": TelegramAdapter,
            "webhook": WebhookAdapter,
            "x": XAdapter,
        }

    def start(self) -> None:
        if BackgroundScheduler is None or self.scheduler is not None:
            return
        self.scheduler = BackgroundScheduler(timezone="UTC")
        self.scheduler.add_job(self.process_queued_jobs, "interval", seconds=15, id="helix_marketing_delivery")
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler is not None:
            self.scheduler.shutdown(wait=False)
            self.scheduler = None

    def process_queued_jobs(self, execution_mode: str = "dry_run") -> int:
        jobs = self.repository.list_scheduled_jobs(status="queued")
        processed = 0
        for job in jobs:
            if self.dispatch_job(job.id, execution_mode=execution_mode):
                processed += 1
        if processed:
            logger.info("Processed %s queued marketing jobs", processed)
        return processed

    def platform_statuses(self) -> list[PlatformAdapterStatusResponse]:
        statuses: list[PlatformAdapterStatusResponse] = []
        for platform in sorted(self.adapter_classes):
            adapter = self._build_adapter(platform)
            valid, message = adapter.validate_credentials()
            statuses.append(
                PlatformAdapterStatusResponse(
                    platform=platform,
                    configured=bool(valid),
                    supports_live=True,
                    message=message,
                )
            )
        return statuses

    def dispatch_job(self, job_id: str, execution_mode: str = "dry_run") -> DeliveryLogResponse | None:
        job = self.repository.get_scheduled_job(job_id)
        if not job:
            return None
        variant = self.repository.get_variant(job.variant_id)
        if not variant:
            self.repository.update_scheduled_job_status(job_id, "failed", "Variant not found")
            return None
        platform = job.platform.lower()
        if platform not in self.adapter_classes:
            self.repository.update_scheduled_job_status(job_id, "failed", f"No adapter configured for {job.platform}")
            return None
        adapter = self._build_adapter(platform)
        if execution_mode == "live":
            valid, message = adapter.validate_credentials()
            if not valid:
                self.repository.update_scheduled_job_status(job_id, "failed", message)
                return self.repository.create_delivery_log(
                    job_id=job.id,
                    platform=job.platform,
                    request_payload={},
                    response_payload={"error": message},
                    status="failed",
                    external_post_id="",
                    execution_mode=execution_mode,
                )

        self.repository.update_scheduled_job_status(job_id, "running")
        variant_payload = variant.model_dump()
        payload = adapter.format_payload(variant_payload)

        if execution_mode == "live":
            raw_response = adapter.send(payload)
        else:
            raw_response = adapter.dry_run(payload)

        normalized = adapter.handle_response(raw_response)
        if normalized.get("success"):
            self.repository.update_scheduled_job_status(job_id, "completed")
            return self.repository.create_delivery_log(
                job_id=job.id,
                platform=job.platform,
                request_payload=payload,
                response_payload=raw_response,
                status=str(normalized.get("normalized_status", "completed")),
                external_post_id=str(normalized.get("external_post_id", "")),
                execution_mode=execution_mode,
            )

        error_message = str(normalized.get("error", "Delivery failed"))
        updated_job = self.repository.increment_scheduled_job_retry(job.id, error_message)
        final_status = "queued" if updated_job and updated_job.retry_count < self.settings.marketing_max_retries else "failed"
        self.repository.update_scheduled_job_status(job_id, final_status, error_message)
        return self.repository.create_delivery_log(
            job_id=job.id,
            platform=job.platform,
            request_payload=payload,
            response_payload=raw_response,
            status="failed",
            external_post_id="",
            execution_mode=execution_mode,
        )

    def _build_adapter(self, platform: str):
        adapter_cls = self.adapter_classes[platform]
        settings = self.credential_service.resolve_platform_settings(platform) if self.credential_service else self.settings
        return adapter_cls(settings)
