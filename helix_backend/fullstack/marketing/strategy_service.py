from __future__ import annotations

from .schemas import StrategyRequest, StrategyResponse


class MarketingStrategyService:
    """Deterministic strategy inference with low-latency keyword heuristics."""

    PLATFORM_PRIORITY = {
        "awareness": ["linkedin", "x", "telegram"],
        "launch": ["x", "linkedin", "telegram"],
        "engagement": ["telegram", "x", "discord"],
        "conversion": ["email", "linkedin", "x"],
        "retention": ["email", "telegram", "discord"],
        "community": ["discord", "telegram", "reddit"],
    }

    CONTENT_MIX = {
        "awareness": {"educational": 0.5, "promotional": 0.2, "engagement": 0.3},
        "launch": {"educational": 0.2, "promotional": 0.6, "engagement": 0.2},
        "engagement": {"educational": 0.2, "promotional": 0.1, "engagement": 0.7},
        "conversion": {"educational": 0.2, "promotional": 0.65, "engagement": 0.15},
        "retention": {"educational": 0.4, "promotional": 0.15, "engagement": 0.45},
        "community": {"educational": 0.25, "promotional": 0.1, "engagement": 0.65},
    }

    POSTING_FREQUENCY = {
        "awareness": "1-2 posts per day",
        "launch": "2-3 posts per day during launch window",
        "engagement": "2 posts per day plus 1 discussion prompt",
        "conversion": "1 post per day plus 2 email touches per week",
        "retention": "3-4 touches per week",
        "community": "1-2 community prompts per day",
    }

    TIMING = {
        "linkedin": "weekday mornings and lunch hours",
        "x": "weekday mornings and early evenings",
        "telegram": "late mornings and evening update windows",
        "discord": "afternoons and evenings",
        "email": "weekday mornings",
        "reddit": "community-specific peak hours after rule review",
    }

    def infer_strategy(self, request: StrategyRequest) -> StrategyResponse:
        intent = self._infer_intent(request.goal, request.offer_summary)
        primary_platforms = request.preferred_platforms or self.PLATFORM_PRIORITY[intent]
        content_mix = self.CONTENT_MIX[intent]
        posting_frequency = self.POSTING_FREQUENCY[intent]
        tone_direction = self._infer_tone(request.brand_voice, request.target_audience, intent)
        cta_direction = self._infer_cta_direction(intent)
        timing_hypothesis = self._build_timing_hypothesis(primary_platforms)
        experiment_ideas = self._experiment_ideas(intent, primary_platforms)
        strategy_summary = self._summary(
            intent=intent,
            platforms=primary_platforms,
            posting_frequency=posting_frequency,
            tone_direction=tone_direction,
            cta_direction=cta_direction,
        )
        return StrategyResponse(
            campaign_goal=request.goal,
            inferred_intent=intent,
            primary_platforms=primary_platforms,
            content_mix=content_mix,
            posting_frequency=posting_frequency,
            timing_hypothesis=timing_hypothesis,
            tone_direction=tone_direction,
            cta_direction=cta_direction,
            experiment_ideas=experiment_ideas,
            strategy_summary=strategy_summary,
        )

    def _infer_intent(self, goal: str, offer_summary: str) -> str:
        text = f"{goal} {offer_summary}".lower()
        if any(token in text for token in ("launch", "announce", "release", "new product", "new feature")):
            return "launch"
        if any(token in text for token in ("convert", "sales", "revenue", "buyers", "signup", "sign up", "purchase")):
            return "conversion"
        if any(token in text for token in ("retain", "retention", "loyal", "reactivate", "reactivation")):
            return "retention"
        if any(token in text for token in ("community", "members", "server", "group", "subreddit")):
            return "community"
        if any(token in text for token in ("engage", "engagement", "reply", "comments", "discussion")):
            return "engagement"
        return "awareness"

    def _infer_tone(self, brand_voice: str, audience: str, intent: str) -> str:
        audience_text = audience.lower()
        brand_text = brand_voice.lower()
        if "developer" in audience_text or "technical" in audience_text:
            return "clear, credible, insight-led"
        if "founder" in audience_text or "b2b" in audience_text:
            return "professional, sharp, outcome-driven"
        if "creator" in audience_text or "community" in audience_text:
            return "conversational, energetic, trust-building"
        if brand_text:
            return brand_voice
        if intent == "conversion":
            return "direct, high-clarity, benefit-led"
        return "warm, clear, audience-aware"

    def _infer_cta_direction(self, intent: str) -> str:
        mapping = {
            "awareness": "invite follows, shares, and curiosity clicks",
            "launch": "drive announcement traffic and signups",
            "engagement": "invite replies, votes, and discussion",
            "conversion": "push demo, trial, or purchase action",
            "retention": "encourage return usage and reactivation",
            "community": "invite participation and membership growth",
        }
        return mapping[intent]

    def _build_timing_hypothesis(self, platforms: list[str]) -> str:
        hints = []
        for platform in platforms[:3]:
            if platform in self.TIMING:
                hints.append(f"{platform}: {self.TIMING[platform]}")
        return "; ".join(hints)

    def _experiment_ideas(self, intent: str, platforms: list[str]) -> list[str]:
        ideas = [
            "test problem-first hook vs outcome-first hook",
            "compare direct CTA vs curiosity CTA",
        ]
        if "linkedin" in platforms:
            ideas.append("compare founder-story opening vs data-point opening on LinkedIn")
        if intent == "conversion":
            ideas.append("test urgency framing vs proof framing for conversion posts")
        return ideas

    def _summary(
        self,
        *,
        intent: str,
        platforms: list[str],
        posting_frequency: str,
        tone_direction: str,
        cta_direction: str,
    ) -> str:
        return (
            f"Focus on {intent} with primary distribution on {', '.join(platforms[:3])}. "
            f"Use a {tone_direction} voice, publish at {posting_frequency}, "
            f"and keep CTAs aligned to {cta_direction}."
        )
