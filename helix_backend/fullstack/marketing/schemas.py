from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


CampaignStatus = Literal["draft", "ready", "scheduled", "running", "completed", "archived"]
ApprovalStatus = Literal["pending", "approved", "rejected"]
JobStatus = Literal["pending", "queued", "running", "completed", "failed", "paused", "cancelled"]
ExecutionMode = Literal["live", "dry_run"]


class BrandProfileBase(BaseModel):
    brand_name: str
    voice_style: str = ""
    preferred_vocabulary: list[str] = Field(default_factory=list)
    banned_phrases: list[str] = Field(default_factory=list)
    signature_patterns: list[str] = Field(default_factory=list)
    default_cta_style: str = ""
    audience_notes: str = ""
    positioning: str = ""


class CreateBrandProfileRequest(BrandProfileBase):
    pass


class UpdateBrandProfileRequest(BaseModel):
    brand_name: str | None = None
    voice_style: str | None = None
    preferred_vocabulary: list[str] | None = None
    banned_phrases: list[str] | None = None
    signature_patterns: list[str] | None = None
    default_cta_style: str | None = None
    audience_notes: str | None = None
    positioning: str | None = None


class BrandProfileResponse(BrandProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime


class CampaignBase(BaseModel):
    name: str
    goal: str
    target_audience: str = ""
    brand_profile_id: str | None = None
    brand_voice: str = ""
    offer_summary: str = ""
    strategy_summary: str = ""
    content_mix: dict[str, float] = Field(default_factory=dict)
    posting_frequency: str = ""
    status: CampaignStatus = "draft"


class CreateCampaignRequest(CampaignBase):
    pass


class CampaignResponse(CampaignBase):
    id: str
    created_at: datetime
    updated_at: datetime


class CampaignVariantResponse(BaseModel):
    id: str
    campaign_id: str
    platform: str
    variant_name: str
    prompt_snapshot: str = ""
    generated_text: str = ""
    cta: str = ""
    hashtags: list[str] = Field(default_factory=list)
    score: float = 0
    experiment_group: str = ""
    approval_status: ApprovalStatus = "pending"
    created_at: datetime


class TemplateResponse(BaseModel):
    id: str
    name: str
    category: str = ""
    platform: str = ""
    template_text: str
    tone: str = ""
    cta_style: str = ""
    score: float = 0
    created_at: datetime


class ScheduledJobResponse(BaseModel):
    id: str
    campaign_id: str
    variant_id: str
    platform: str
    run_at: datetime
    timezone: str
    status: JobStatus
    retry_count: int = 0
    last_error: str = ""
    created_at: datetime


class DeliveryLogResponse(BaseModel):
    id: str
    job_id: str
    platform: str
    request_payload: dict[str, Any] = Field(default_factory=dict)
    response_payload: dict[str, Any] = Field(default_factory=dict)
    status: str
    external_post_id: str = ""
    execution_mode: ExecutionMode = "dry_run"
    created_at: datetime


class PerformanceEventResponse(BaseModel):
    id: str
    campaign_id: str
    variant_id: str | None = None
    platform: str
    metric_type: str
    metric_value: float
    source: str = "manual"
    created_at: datetime


class ExperimentRunResponse(BaseModel):
    id: str
    campaign_id: str
    variant_a_id: str
    variant_b_id: str
    winner_variant_id: str | None = None
    decision_reason: str = ""
    created_at: datetime
