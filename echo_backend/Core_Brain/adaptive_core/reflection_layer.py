class ReflectionLayer:
    def evaluate(self, user_input, analysis, emotional_state, policy_state, response_text, reward):
        improvements = []
        if emotional_state["vector"]["stress"] > 0.65 and len((response_text or "").split()) > 70:
            improvements.append("Use shorter grounding responses when user stress is high.")
        if policy_state.get("policy") == "direct" and emotional_state["vector"]["calm"] < 0.45:
            improvements.append("Blend more empathy before direct problem-solving.")
        if not improvements:
            improvements.append("Current strategy was stable; continue monitoring sentiment shifts.")

        effective = reward >= 0.35
        return {
            "effective": effective,
            "reward": reward,
            "policy": policy_state.get("policy"),
            "summary": "Response improved trust signals." if effective else "Response should adjust tone or clarity next turn.",
            "improvements": improvements,
        }
