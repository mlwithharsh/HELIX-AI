from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ConversationSample:
    user_input: str
    emotional_state_vector: List[float]
    history: List[Dict[str, str]]
    profile: Dict[str, float]
    target_intent: str


def build_demo_dataset() -> List[ConversationSample]:
    return [
        ConversationSample(
            user_input="I am overwhelmed with tasks. Help me prioritize.",
            emotional_state_vector=[0.2, 0.3, 0.8, 0.1, 0.6],
            history=[{"role": "user", "content": "Work is piling up."}],
            profile={"support_preference": 0.8, "task_focus": 0.9},
            target_intent="task_support",
        ),
        ConversationSample(
            user_input="I finished my release today and it went well.",
            emotional_state_vector=[0.8, 0.4, 0.1, 0.9, 0.1],
            history=[{"role": "assistant", "content": "How did the deployment go?"}],
            profile={"engagement_preference": 0.7, "brevity_preference": 0.4},
            target_intent="celebrate",
        ),
        ConversationSample(
            user_input="Explain what changed in the training loop.",
            emotional_state_vector=[0.7, 0.8, 0.1, 0.2, 0.1],
            history=[],
            profile={"task_focus": 0.85, "brevity_preference": 0.5},
            target_intent="explain",
        ),
    ]
