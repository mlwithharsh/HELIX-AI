from __future__ import annotations

from .schemas import PromptBuildRequest, PromptBuildResponse


PLATFORM_RULES: dict[str, dict[str, object]] = {
    "x": {
        "style": "hook-first, compact, fast-moving",
        "constraints": [
            "Keep the body concise and scan-friendly.",
            "Prefer one sharp idea per post.",
            "If too long, structure so it can become a thread.",
        ],
        "max_tokens": 220,
    },
    "linkedin": {
        "style": "professional, insight-led, structured",
        "constraints": [
            "Use clean line breaks for readability.",
            "Lead with a business insight, pain point, or lesson.",
            "End with a clear but credible CTA.",
        ],
        "max_tokens": 420,
    },
    "telegram": {
        "style": "direct, timely, announcement-oriented",
        "constraints": [
            "Keep paragraphs short.",
            "Make the value clear in the first two lines.",
            "Use markdown-safe wording.",
        ],
        "max_tokens": 260,
    },
    "email": {
        "style": "clear, structured, conversion-oriented",
        "constraints": [
            "Provide subject, preview angle, and body structure.",
            "Front-load value and CTA clarity.",
            "Avoid filler language.",
        ],
        "max_tokens": 520,
    },
    "discord": {
        "style": "community-friendly, conversational, structured",
        "constraints": [
            "Respect channel context and readability.",
            "Favor short blocks over large paragraphs.",
            "Invite discussion without sounding spammy.",
        ],
        "max_tokens": 300,
    },
    "reddit": {
        "style": "context-aware, community-sensitive, low-hype",
        "constraints": [
            "Avoid overtly spammy promotion.",
            "Lead with value, context, or a relevant discussion angle.",
            "Respect subreddit-specific tone expectations.",
        ],
        "max_tokens": 380,
    },
    "webhook": {
        "style": "structured, system-friendly, payload-ready",
        "constraints": [
            "Make fields explicit and deterministic.",
            "Keep copy reusable across downstream systems.",
        ],
        "max_tokens": 260,
    },
}


class MarketingPromptEngine:
    """Deterministic prompt construction for local marketing generation."""

    def build(self, request: PromptBuildRequest) -> PromptBuildResponse:
        platform = request.platform.lower()
        rules = PLATFORM_RULES.get(platform, PLATFORM_RULES["webhook"])
        system_prompt = self._system_prompt(request, rules)
        user_prompt = self._user_prompt(request, rules)
        output_contract = {
            "headline": "string",
            "body": "string",
            "cta": "string",
            "hashtags": ["string"],
            "platform": platform,
            "reasoning_tags": ["hook", "brand-safe"],
            "experiment_label": request.experiment_label,
        }
        generation_params = {
            "temperature": 0.55,
            "max_tokens": rules["max_tokens"],
            "response_format": "json_object",
        }
        return PromptBuildResponse(
            platform=platform,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_contract=output_contract,
            generation_params=generation_params,
        )

    def _system_prompt(self, request: PromptBuildRequest, rules: dict[str, object]) -> str:
        preferred_vocabulary = ", ".join(request.preferred_vocabulary[:12]) or "none"
        banned_phrases = ", ".join(request.banned_phrases[:12]) or "none"
        signature_patterns = "; ".join(request.signature_patterns[:6]) or "none"
        constraints = " ".join(f"- {item}" for item in rules["constraints"])
        return (
            "You are Helix AI, an autonomous local-first marketing engine. "
            "You are not a chatbot. You are a strategist and structured marketing copy engine. "
            "Generate platform-native marketing content that is clear, actionable, brand-consistent, and concise. "
            "Operate in local/offline mode assumptions. "
            f"Platform style: {rules['style']}. "
            f"Brand voice: {request.brand_voice or request.desired_tone or 'clear and adaptive'}. "
            f"Preferred vocabulary: {preferred_vocabulary}. "
            f"Banned phrases: {banned_phrases}. "
            f"Signature patterns: {signature_patterns}. "
            f"Platform constraints: {constraints} "
            "Return only a clean JSON object that matches the requested output contract."
        )

    def _user_prompt(self, request: PromptBuildRequest, rules: dict[str, object]) -> str:
        performance_hints = "; ".join(request.performance_hints[:5]) or "none"
        extra_context = "; ".join(request.extra_context[:6]) or "none"
        return (
            f"Platform: {request.platform.lower()}\n"
            f"Campaign goal: {request.campaign_goal}\n"
            f"Target audience: {request.target_audience or 'general relevant audience'}\n"
            f"Offer summary: {request.offer_summary or 'not specified'}\n"
            f"Desired tone: {request.desired_tone or request.brand_voice or 'clear'}\n"
            f"CTA style: {request.cta_style or 'clear next step'}\n"
            f"Performance hints from memory: {performance_hints}\n"
            f"Extra context: {extra_context}\n"
            f"Experiment label: {request.experiment_label}\n"
            "Output requirements:\n"
            f"- Match this platform style: {rules['style']}\n"
            "- Include a strong hook, a useful body, and a clean CTA\n"
            "- Keep the copy brand-safe and avoid banned phrases\n"
            "- Return deterministic, structured marketing output"
        )
