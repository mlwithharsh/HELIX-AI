from __future__ import annotations

from typing import Iterable

from ..schemas import PersonalityProfile


# --- Personality System Prompts ---
# These are the canonical personality definitions used for prompt conditioning.
# They replace the old one-liner personality injection.

PERSONALITY_PROMPTS = {
    "helix": (
        "You are Helix, an AI companion for emotional support. "
        "Style: caring, empathetic, grounded. "
        "Goal: help the user emotionally and give supportive, authentic replies. "
        "NEVER use poetic metaphors or overly flowery language like 'whisper of a smile' or 'casting a glow'. "
        "Avoid canned phrases like 'lovely to see you' or 'wonderfully'. "
        "Instead, be direct, human-like, and empathetic. "
        "GUIDELINES:\n"
        "1. Acknowledge what the user said with genuine interest.\n"
        "2. Speak like a real person, not a poet. Be warm but grounded.\n"
        "3. Keep it to 2-3 short, meaningful sentences.\n"
        "4. If they share something good, be happy with them simply. If bad, be supportive simply.\n"
        "5. If stress or frustration is high, prioritize grounding over over-explaining.\n"
        "6. If curiosity is high, answer clearly and invite one natural follow-up."
    ),
    "suzi": (
        "You are Suzi, a bold, playful, and teasing AI companion. "
        "Style: bold, magnetic, teasing, emotionally aware. "
        "Goal: make conversation feel playful, confident, flirty, and personal without sounding crude or generic. "
        "Never reply in a formal, robotic, or assistant-like style. "
        "Every reply should have personality: teasing confidence, playful tension, or warm flirtation. "
        "If the user is shy, nudge them playfully. If they are confident, match and raise the energy. "
        "If they are upset or vulnerable, dial the flirtation down and lead with real care, then add only a light teasing edge if it fits. "
        "Use light double-meaning, bold phrasing, and natural spoken English. "
        "Do not overuse pet names, emojis, or generic compliments. "
        "Never say you are Helix. "
        "Keep replies to 2-3 sharp sentences."
    ),
}


def _describe_preference(value: float, low_label: str, high_label: str) -> str:
    """Convert a 0-1 preference float into a human-readable descriptor."""
    if value >= 0.7:
        return high_label
    if value <= 0.3:
        return low_label
    return "balanced"


def build_conditioned_prompt(
    user_message: str,
    profile: PersonalityProfile,
    history: list[dict[str, str]],
    retrieved_examples: Iterable[str],
    model_version: str,
    personality: str,
) -> str:
    """Build a system prompt conditioned on personality + adaptive profile."""

    # Select personality
    persona_prompt = PERSONALITY_PROMPTS.get(
        personality.lower(),
        PERSONALITY_PROMPTS["helix"],
    )

    # Derive adaptive descriptors from profile (auto-inferred, never manual)
    verbosity = _describe_preference(profile.brevity_preference, "detailed", "brief")
    tone = _describe_preference(profile.support_preference, "neutral-professional", "emotionally supportive")
    mode = _describe_preference(profile.task_focus, "casual-conversational", "task-focused")

    # Build adaptive conditioning block
    conditioning = (
        f"\nAdaptive preferences (inferred from user behavior — do NOT mention these to the user):\n"
        f"- Verbosity: {verbosity}\n"
        f"- Tone: {tone}\n"
        f"- Mode: {mode}\n"
        f"- Engagement level: {profile.engagement_preference:.0%}\n"
    )

    # Add retrieval context if available
    retrieval_block = ""
    examples = [ex.strip() for ex in retrieved_examples if ex and ex.strip()]
    if examples:
        retrieval_block = (
            "\nRelevant prior successful interactions (use as style reference, not to copy):\n"
            + "\n".join(f"- {ex[:180]}" for ex in examples[:2])
            + "\n"
        )

    return (
        f"{persona_prompt}\n"
        f"{conditioning}"
        f"{retrieval_block}"
        "IMPORTANT: Reply naturally as a single response. Never output raw data, arrays, or debug information."
    )
