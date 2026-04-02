from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean


def evaluate(log_dir: str) -> dict:
    debug_path = Path(log_dir) / "debug.jsonl"
    if not debug_path.exists():
        return {"average_reward": 0.0, "response_quality": 0.0, "training_stability": 0.0, "samples": 0}

    rewards = []
    clarity_scores = []
    with debug_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = json.loads(line)
            rewards.append(payload["reward"]["total"])
            clarity_scores.append(payload["reward"]["response_clarity"])

    reward_deltas = [abs(rewards[index] - rewards[index - 1]) for index in range(1, len(rewards))]
    stability = 1.0 / (1.0 + mean(reward_deltas)) if reward_deltas else 1.0
    return {
        "average_reward": round(mean(rewards), 4) if rewards else 0.0,
        "response_quality": round(mean(clarity_scores), 4) if clarity_scores else 0.0,
        "training_stability": round(stability, 4),
        "samples": len(rewards),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RL training logs.")
    parser.add_argument("--log-dir", default="logs")
    args = parser.parse_args()
    results = evaluate(args.log_dir)
    print(json.dumps(results, indent=2))
