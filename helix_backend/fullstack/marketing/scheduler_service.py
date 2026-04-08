from __future__ import annotations

import logging
from datetime import datetime, timezone

from .repository import LocalMarketingRepository
from .schemas import ScheduleCampaignRequest, ScheduleCampaignResponse

logger = logging.getLogger(__name__)

try:
    from apscheduler.schedulers.background import BackgroundScheduler
except Exception:  # pragma: no cover
    BackgroundScheduler = None


class MarketingSchedulerService:
    """Promotes approved scheduled jobs into queued state when due."""

    def __init__(self, repository: LocalMarketingRepository):
        self.repository = repository
        self.scheduler = None

    def start(self) -> None:
        if BackgroundScheduler is None or self.scheduler is not None:
            return
        self.scheduler = BackgroundScheduler(timezone="UTC")
        self.scheduler.add_job(self.enqueue_due_jobs, "interval", seconds=20, id="helix_marketing_enqueue_due")
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler is not None:
            self.scheduler.shutdown(wait=False)
            self.scheduler = None

    def schedule_campaign(self, campaign_id: str, request: ScheduleCampaignRequest) -> ScheduleCampaignResponse:
        jobs = []
        rejected_variant_ids: list[str] = []
        for variant_id in request.variant_ids:
            variant = self.repository.get_variant(variant_id)
            if not variant or variant.campaign_id != campaign_id or variant.approval_status != "approved":
                rejected_variant_ids.append(variant_id)
                continue
            jobs.append(
                self.repository.create_scheduled_job(
                    campaign_id=campaign_id,
                    variant_id=variant_id,
                    platform=variant.platform,
                    run_at=request.run_at,
                    timezone_name=request.timezone,
                    status="pending",
                )
            )
        if jobs:
            self.repository.update_campaign(campaign_id, payload={"status": "scheduled"})  # type: ignore[arg-type]
        return ScheduleCampaignResponse(jobs=jobs, rejected_variant_ids=rejected_variant_ids)

    def enqueue_due_jobs(self) -> int:
        now = datetime.now(timezone.utc)
        count = self.repository.mark_due_jobs_queued(now)
        if count:
            logger.info("Queued %s due marketing jobs", count)
        return count
