from __future__ import annotations

from .prompt_engine import MarketingPromptEngine
from .repository import LocalMarketingRepository
from .schemas import (
    CampaignResponse,
    GeneratedVariantDraft,
    GenerateVariantsRequest,
    GenerateVariantsResponse,
    PromptBuildRequest,
    StrategyRequest,
    StrategyResponse,
    UpdateCampaignRequest,
)
from .strategy_service import MarketingStrategyService


class MarketingCampaignService:
    """Orchestrates campaign strategy generation and offline draft creation."""

    def __init__(
        self,
        repository: LocalMarketingRepository,
        strategy_service: MarketingStrategyService,
        prompt_engine: MarketingPromptEngine,
    ):
        self.repository = repository
        self.strategy_service = strategy_service
        self.prompt_engine = prompt_engine

    def generate_strategy_for_campaign(self, campaign_id: str) -> tuple[CampaignResponse, StrategyResponse] | None:
        campaign = self.repository.get_campaign(campaign_id)
        if not campaign:
            return None
        strategy = self.strategy_service.infer_strategy(
            StrategyRequest(
                goal=campaign.goal,
                target_audience=campaign.target_audience,
                offer_summary=campaign.offer_summary,
                brand_voice=campaign.brand_voice,
            )
        )
        updated = self.repository.update_campaign(
            campaign_id,
            UpdateCampaignRequest(
                strategy_summary=strategy.strategy_summary,
                content_mix=strategy.content_mix,
                posting_frequency=strategy.posting_frequency,
                status="ready",
            ),
        )
        return updated, strategy

    def generate_variants(self, campaign_id: str, request: GenerateVariantsRequest) -> GenerateVariantsResponse | None:
        strategy_bundle = self.generate_strategy_for_campaign(campaign_id)
        if not strategy_bundle:
            return None
        campaign, strategy = strategy_bundle
        brand_profile = self.repository.get_brand_profile(campaign.brand_profile_id) if campaign.brand_profile_id else None
        learned_hints = self.repository.build_performance_hints(campaign_id=campaign.id)

        platforms = request.platforms or strategy.primary_platforms
        experiment_labels = request.experiment_labels or ["A"]
        variants = []

        for platform in platforms:
            for experiment_label in experiment_labels:
                prompt = self.prompt_engine.build(
                    PromptBuildRequest(
                        platform=platform,
                        campaign_goal=campaign.goal,
                        target_audience=campaign.target_audience,
                        offer_summary=campaign.offer_summary,
                        brand_voice=(brand_profile.voice_style if brand_profile else campaign.brand_voice),
                        desired_tone=request.desired_tone or strategy.tone_direction,
                        cta_style=request.cta_style or (brand_profile.default_cta_style if brand_profile else strategy.cta_direction),
                        experiment_label=experiment_label,
                        performance_hints=request.performance_hints or learned_hints or strategy.experiment_ideas,
                        preferred_vocabulary=brand_profile.preferred_vocabulary if brand_profile else [],
                        banned_phrases=brand_profile.banned_phrases if brand_profile else [],
                        signature_patterns=brand_profile.signature_patterns if brand_profile else [],
                        extra_context=request.extra_context,
                    )
                )
                draft = self._draft_variant(campaign, strategy, platform, experiment_label)
                variants.append(
                    self.repository.create_variant(
                        campaign_id=campaign.id,
                        platform=draft.platform,
                        variant_name=draft.variant_name,
                        prompt_snapshot=f"{prompt.system_prompt}\n\n{prompt.user_prompt}",
                        generated_text=self._combine_copy(draft),
                        cta=draft.cta,
                        hashtags=draft.hashtags,
                        score=0,
                        experiment_group=draft.experiment_label,
                        approval_status="pending",
                    )
                )

        refreshed_campaign = self.repository.get_campaign(campaign.id) or campaign
        return GenerateVariantsResponse(campaign=refreshed_campaign, strategy=strategy, variants=variants)

    def _draft_variant(
        self,
        campaign: CampaignResponse,
        strategy: StrategyResponse,
        platform: str,
        experiment_label: str,
    ) -> GeneratedVariantDraft:
        audience = campaign.target_audience or "your audience"
        offer = campaign.offer_summary or campaign.name
        hook = self._hook_for(platform, strategy.inferred_intent, experiment_label, offer)
        body = self._body_for(platform, audience, offer, strategy)
        cta = self._cta_for(platform, strategy.cta_direction, offer)
        hashtags = self._hashtags_for(platform, campaign.name, strategy.inferred_intent)
        return GeneratedVariantDraft(
            platform=platform.lower(),
            variant_name=f"{platform.lower()}-{experiment_label.lower()}",
            headline=hook,
            body=body,
            cta=cta,
            hashtags=hashtags,
            reasoning_tags=[strategy.inferred_intent, "brand-safe", f"exp-{experiment_label.lower()}"],
            experiment_label=experiment_label,
        )

    def _hook_for(self, platform: str, intent: str, experiment_label: str, offer: str) -> str:
        if platform.lower() == "linkedin":
            if experiment_label == "A":
                return f"What usually slows adoption is not the product, but how {offer} is explained."
            return "Most launch campaigns underperform because the message is vague before the audience even clicks."
        if platform.lower() == "x":
            if experiment_label == "A":
                return f"If you're building around {offer}, clarity wins faster than noise."
            return f"The easiest way to lose attention in a {intent} campaign is to say too much."
        if platform.lower() == "telegram":
            if experiment_label == "A":
                return f"Quick update: we're sharpening the {intent} message for {offer}."
            return f"New angle for {offer}: a tighter {intent} message with a cleaner next step."
        if platform.lower() == "discord":
            if experiment_label == "A":
                return f"Quick idea for the community: a cleaner way to frame {offer}."
            return f"Different angle: what if the message around {offer} did less, but landed harder?"
        if platform.lower() == "email":
            if experiment_label == "A":
                return f"Subject: A clearer way to improve results with {offer}"
            return f"Subject: What usually blocks results before {offer} even gets a chance"
        return f"{offer}: a clearer way to move your {intent} campaign forward."

    def _body_for(self, platform: str, audience: str, offer: str, strategy: StrategyResponse) -> str:
        if platform.lower() == "email":
            return (
                f"We built this around a simple principle: make {offer} easier for {audience} to understand, trust, and act on. "
                f"This campaign is tuned for {strategy.inferred_intent} with a {strategy.tone_direction} voice."
            )
        if platform.lower() == "linkedin":
            return (
                f"For {audience}, the strongest campaigns combine a clear problem, a credible point of view, "
                f"and one obvious next step. This version is built around that pattern."
            )
        if platform.lower() == "x":
            return f"Strong campaigns for {audience} usually come down to one useful message and one clear next step."
        if platform.lower() == "telegram":
            return (
                f"This version is built for {audience} and keeps the message direct, timely, and easy to act on."
                if strategy.inferred_intent != "engagement"
                else f"This version is built for {audience} and leans into a direct prompt that invites a quick response."
            )
        return f"This content is aimed at {audience} and shaped around a {strategy.tone_direction} style."

    def _cta_for(self, platform: str, cta_direction: str, offer: str) -> str:
        if platform.lower() == "email":
            return f"Reply if you want the full breakdown for {offer}."
        if platform.lower() == "linkedin":
            return "If this is relevant, send a message and I will share the exact approach."
        if platform.lower() == "telegram":
            return "Message us if you want the next update."
        return "Follow for the next step."

    def _hashtags_for(self, platform: str, campaign_name: str, intent: str) -> list[str]:
        if platform.lower() not in {"x", "linkedin"}:
            return []
        normalized = campaign_name.lower().replace(" ", "")
        return [f"#{intent}", f"#{normalized[:20]}"]

    def _combine_copy(self, draft: GeneratedVariantDraft) -> str:
        parts = [part for part in [draft.headline, draft.body, draft.cta] if part]
        return "\n\n".join(parts)
