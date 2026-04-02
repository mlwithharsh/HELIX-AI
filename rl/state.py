from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List

import numpy as np


@dataclass
class ConversationState:
    user_input: str
    user_input_embedding: List[float]
    emotional_state_vector: List[float]
    conversation_history: List[Dict[str, str]]
    user_profile_features: Dict[str, float]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class StatePreprocessor:
    embedding_dim: int = 64
    max_history_turns: int = 6

    def _hash_embedding(self, text: str) -> List[float]:
        vector = np.zeros(self.embedding_dim, dtype=np.float32)
        for index, byte in enumerate(text.encode("utf-8", errors="ignore")):
            vector[index % self.embedding_dim] += float((byte % 31) / 30.0)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector /= norm
        return vector.round(4).tolist()

    def _normalize_profile(self, profile: Dict[str, float] | None) -> Dict[str, float]:
        profile = profile or {}
        normalized = {
            "engagement_preference": float(profile.get("engagement_preference", 0.5)),
            "brevity_preference": float(profile.get("brevity_preference", 0.5)),
            "support_preference": float(profile.get("support_preference", 0.5)),
            "task_focus": float(profile.get("task_focus", 0.5)),
        }
        return normalized

    def _normalize_emotion(self, emotion_vector: List[float] | None) -> List[float]:
        if not emotion_vector:
            return [0.5, 0.5, 0.0, 0.0, 0.0]
        values = list(emotion_vector[:5])
        while len(values) < 5:
            values.append(0.0)
        return [round(float(value), 4) for value in values]

    def preprocess(
        self,
        user_input: str,
        emotional_state_vector: List[float] | None,
        conversation_history: List[Dict[str, str]] | None,
        user_profile_features: Dict[str, float] | None,
    ) -> ConversationState:
        history = (conversation_history or [])[-self.max_history_turns :]
        return ConversationState(
            user_input=user_input,
            user_input_embedding=self._hash_embedding(user_input),
            emotional_state_vector=self._normalize_emotion(emotional_state_vector),
            conversation_history=history,
            user_profile_features=self._normalize_profile(user_profile_features),
        )
