from .base_personality import BasePersonality
from helix_backend.Core_Brain.nlp_engine import NLPEngine


class HelixPersonality(BasePersonality):
    def __init__(self):
        super().__init__(name="Helix", style="caring, empathetic", goals="help user emotionally and give supportive replies")
        self.nlp = NLPEngine()

    def respond(self, user_input, memory, analysis=None, adaptive_context=None):
        if not analysis:
            analysis = self.nlp.get_analysis(user_input)

        intent = analysis.get("intent", "unknown")
        emotion = analysis.get("emotion", "neutral")
        sentiment = analysis.get("sentiment", "neutral")
        adaptive_context = adaptive_context or {}
        emotional_state = adaptive_context.get("emotional_state", {})
        policy_state = adaptive_context.get("policy_state", {})
        memory_snapshot = adaptive_context.get("memory_snapshot", {})
        user_profile = memory_snapshot.get("user_profile", {})
        relevant_memories = memory_snapshot.get("relevant_memories", [])
        alignment = emotional_state.get("alignment", "balanced")
        policy = policy_state.get("policy", "supportive")

        system_prompt = (
            f"You are {self.name}, an AI companion for emotional support. "
            f"Style: {self.style}. Goal: {self.goals}. "
            "NEVER use poetic metaphors or overly flowery language like 'whisper of a smile' or 'casting a glow'. "
            "Avoid canned phrases like 'lovely to see you' or 'wonderfully'. "
            "Instead, be direct, human-like, and empathetic. "
            f"User is feeling {emotion} ({sentiment}). Intent: {intent}. "
            f"Emotional alignment target: {alignment}. "
            f"Adaptive policy: {policy}. "
            f"Stored preferences: {user_profile.get('preferences', 'none')}. "
            f"Behavior patterns: {user_profile.get('behavioral_patterns', 'none')}. "
            f"Emotional trend: {user_profile.get('emotional_trend', 'neutral')}. "
            f"Relevant memory snippets: {relevant_memories}. "
            f"User input: '{user_input}'\n\n"
            "GUIDELINES:\n"
            "1. Acknowledge what the user said with genuine interest.\n"
            "2. Speak like a real person, not a poet. Be warm but grounded.\n"
            "3. Keep it to 2-3 short, meaningful sentences.\n"
            "4. If they share something good, be happy with them simply. If bad, be supportive simply.\n"
            "5. If stress or frustration is high, prioritize grounding over over-explaining.\n"
            "6. If curiosity is high, answer clearly and invite one natural follow-up."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        response = self.nlp.call_groq_model(messages, max_tokens=150, temperature=0.8)

        if not response or response.startswith("[Groq Error]"):
            response = self.nlp.build_fallback_response(
                user_input,
                analysis=analysis,
                adaptive_context=adaptive_context,
                personality_name=self.name,
            )

        return response
