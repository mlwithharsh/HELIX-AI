class EmotionalIntelligenceLayer:
    EMOTION_TO_VECTOR = {
        "neutral": [0.8, 0.3, 0.1, 0.2, 0.1],
        "happy": [0.9, 0.5, 0.05, 0.8, 0.05],
        "sad": [0.4, 0.2, 0.7, 0.1, 0.5],
        "angry": [0.2, 0.2, 0.8, 0.2, 0.9],
        "fear": [0.3, 0.2, 0.85, 0.1, 0.6],
        "surprise": [0.5, 0.8, 0.4, 0.7, 0.2],
        "disgust": [0.2, 0.2, 0.6, 0.1, 0.7],
    }

    def __init__(self):
        self.last_vector = [0.6, 0.4, 0.2, 0.3, 0.1]

    def build_state(self, user_input, analysis, memory_snapshot=None):
        emotion = (analysis or {}).get("emotion", "neutral")
        sentiment = (analysis or {}).get("sentiment", "neutral")
        base_vector = self.EMOTION_TO_VECTOR.get(emotion, self.EMOTION_TO_VECTOR["neutral"])[:]

        lowered = (user_input or "").lower()
        if "?" in lowered:
            base_vector[1] = min(1.0, base_vector[1] + 0.15)
        if any(token in lowered for token in ["help", "urgent", "stuck", "anxious", "stress"]):
            base_vector[2] = min(1.0, base_vector[2] + 0.2)
        if any(token in lowered for token in ["wow", "great", "excited", "awesome"]):
            base_vector[3] = min(1.0, base_vector[3] + 0.2)
        if sentiment == "negative":
            base_vector[4] = min(1.0, base_vector[4] + 0.15)
        if sentiment == "positive":
            base_vector[0] = min(1.0, base_vector[0] + 0.1)

        if memory_snapshot:
            dominant = memory_snapshot.get("emotional_summary", {}).get("dominant_emotion", "neutral")
            if dominant in {"sad", "fear", "angry"}:
                base_vector[2] = min(1.0, base_vector[2] + 0.05)

        smoothed = []
        for previous, current in zip(self.last_vector, base_vector):
            smoothed.append(round((previous * 0.4) + (current * 0.6), 3))
        self.last_vector = smoothed

        alignment = self._pick_alignment(smoothed)
        return {
            "vector": {
                "calm": smoothed[0],
                "curiosity": smoothed[1],
                "stress": smoothed[2],
                "excitement": smoothed[3],
                "frustration": smoothed[4],
            },
            "emotion": emotion,
            "sentiment": sentiment,
            "alignment": alignment,
        }

    def _pick_alignment(self, vector):
        calm, curiosity, stress, excitement, frustration = vector
        if stress >= 0.65 or frustration >= 0.65:
            return "grounding"
        if excitement >= 0.65:
            return "energized"
        if curiosity >= 0.6:
            return "exploratory"
        if calm >= 0.7:
            return "steady"
        return "balanced"
