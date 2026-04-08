from __future__ import annotations

from .repository import LocalMarketingRepository
from .safety_service import MarketingSafetyService
from .schemas import ApprovalResultResponse


class MarketingApprovalService:
    def __init__(self, repository: LocalMarketingRepository, safety_service: MarketingSafetyService):
        self.repository = repository
        self.safety_service = safety_service

    def review_variant(self, variant_id: str, approved: bool) -> ApprovalResultResponse | None:
        variant = self.repository.get_variant(variant_id)
        if not variant:
            return None

        if not approved:
            updated = self.repository.update_variant_approval(variant_id, "rejected")
            return ApprovalResultResponse(
                variant=updated,
                safe_to_schedule=False,
                reasons=["Rejected during review"],
            )

        safe, reasons = self.safety_service.evaluate_variant(variant_id)
        approval_status = "approved" if safe else "rejected"
        updated = self.repository.update_variant_approval(variant_id, approval_status)
        return ApprovalResultResponse(
            variant=updated,
            safe_to_schedule=safe,
            reasons=reasons,
        )

