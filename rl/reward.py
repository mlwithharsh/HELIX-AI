from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional


@dataclass
class RewardConfig:
    engagement_weight: float = 1.0
    sentiment_weight: float = 1.0
    task_success_weight: float = 1.0
    confusion_penalty_weight: float = 1.0
    repetition_penalty_weight: float = 1.0
    emotional_alignment_weight: float = 0.75
    clarity_weight: float = 0.5


@dataclass
class RewardBreakdown:
    total: float
    engagement_score: float
    sentiment_improvement: float
    task_success: float
    confusion_penalty: float
    repetition_penalty: float
    emotional_alignment: float
    response_clarity: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "total": self.total,
            "engagement_score": self.engagement_score,
            "sentiment_improvement": self.sentiment_improvement,
            "task_success": self.task_success,
            "confusion_penalty": self.confusion_penalty,
            "repetition_penalty": self.repetition_penalty,
            "emotional_alignment": self.emotional_alignment,
            "response_clarity": self.response_clarity,
        }


class RewardFunction:
    def __init__(self, config: RewardConfig | None = None):
        self.config = config or RewardConfig()

    def _response_clarity(self, response_text: str) -> float:
        words = response_text.split()
        if not words:
            return -1.0
        if len(words) > 120:
            return -0.5
        punctuation_bonus = 0.2 if response_text.strip().endswith((".", "!", "?")) else 0.0
        return min(1.0, 0.4 + punctuation_bonus + (0.3 if len(words) >= 8 else 0.0))

    def _repetition_penalty(self, response_text: str) -> float:
        words = [word.lower() for word in response_text.split()]
        if not words:
            return 1.0
        unique_ratio = len(set(words)) / len(words)
        return max(0.0, 1.0 - unique_ratio)

    def _confusion_penalty(self, response_text: str) -> float:
        lowered = response_text.lower()
        confusion_markers = ["i don't know", "not sure", "maybe maybe", "unclear", "confused"]
        penalty = sum(0.2 for marker in confusion_markers if marker in lowered)
        return min(1.0, penalty)

    def compute(
        self,
        response_text: str,
        metrics: Dict[str, float],
        feedback_provider: Optional[Callable[[Dict[str, float]], float]] = None,
    ) -> RewardBreakdown:
        engagement_score = float(metrics.get("engagement_score", 0.0))
        sentiment_improvement = float(metrics.get("sentiment_improvement", 0.0))
        task_success = float(metrics.get("task_success", 0.0))
        emotional_alignment = float(metrics.get("emotional_alignment", 0.0))
        response_clarity = float(metrics.get("response_clarity", self._response_clarity(response_text)))
        confusion_penalty = float(metrics.get("confusion_penalty", self._confusion_penalty(response_text)))
        repetition_penalty = float(metrics.get("repetition_penalty", self._repetition_penalty(response_text)))

        total = (
            self.config.engagement_weight * engagement_score
            + self.config.sentiment_weight * sentiment_improvement
            + self.config.task_success_weight * task_success
            - self.config.confusion_penalty_weight * confusion_penalty
            - self.config.repetition_penalty_weight * repetition_penalty
            + self.config.emotional_alignment_weight * emotional_alignment
            + self.config.clarity_weight * response_clarity
        )

        if feedback_provider is not None:
            total += float(feedback_provider(metrics))

        return RewardBreakdown(
            total=round(total, 4),
            engagement_score=engagement_score,
            sentiment_improvement=sentiment_improvement,
            task_success=task_success,
            confusion_penalty=confusion_penalty,
            repetition_penalty=repetition_penalty,
            emotional_alignment=emotional_alignment,
            response_clarity=response_clarity,
        )
