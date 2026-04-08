from __future__ import annotations

from collections import defaultdict

from .repository import LocalMarketingRepository
from .schemas import (
    PerformanceEventResponse,
    RecordPerformanceEventRequest,
    AnalyticsSummaryResponse,
)


class MarketingAnalyticsService:
    """Stores performance feedback and derives lightweight local insights."""

    def __init__(self, repository: LocalMarketingRepository):
        self.repository = repository

    def record_event(self, payload: RecordPerformanceEventRequest) -> PerformanceEventResponse:
        return self.repository.create_performance_event(
            campaign_id=payload.campaign_id,
            variant_id=payload.variant_id,
            platform=payload.platform,
            metric_type=payload.metric_type,
            metric_value=payload.metric_value,
            source=payload.source,
            note=payload.note,
        )

    def summary(self, campaign_id: str | None = None) -> AnalyticsSummaryResponse:
        events = self.repository.list_performance_events(campaign_id=campaign_id)
        total_events = len(events)
        platform_totals: dict[str, float] = defaultdict(float)
        metric_totals: dict[str, float] = defaultdict(float)
        metric_counts: dict[str, int] = defaultdict(int)

        for event in events:
            platform_totals[event.platform] += event.metric_value
            metric_totals[event.metric_type] += event.metric_value
            metric_counts[event.metric_type] += 1

        platform_averages = {
            platform: round(value, 2) for platform, value in sorted(platform_totals.items(), key=lambda item: item[1], reverse=True)
        }
        top_metrics = {
            metric: round(metric_totals[metric] / max(metric_counts[metric], 1), 2)
            for metric in metric_totals
        }

        memory_hints = self.repository.build_performance_hints(campaign_id=campaign_id)

        return AnalyticsSummaryResponse(
            campaign_id=campaign_id,
            total_events=total_events,
            platform_scores=platform_averages,
            metric_averages=top_metrics,
            memory_hints=memory_hints,
        )
