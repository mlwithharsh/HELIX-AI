from rl.reward import RewardFunction


def test_reward_prefers_clear_and_successful_response():
    reward_function = RewardFunction()
    reward = reward_function.compute(
        response_text="Here is a clear plan. First, list tasks. Next, rank them by urgency.",
        metrics={
            "engagement_score": 0.8,
            "sentiment_improvement": 0.6,
            "task_success": 0.9,
            "emotional_alignment": 0.7,
        },
    )
    assert reward.total > 1.5
    assert reward.response_clarity > 0


def test_reward_penalizes_repetition():
    reward_function = RewardFunction()
    reward = reward_function.compute(
        response_text="repeat repeat repeat repeat",
        metrics={
            "engagement_score": 0.1,
            "sentiment_improvement": 0.0,
            "task_success": 0.0,
            "emotional_alignment": 0.0,
        },
    )
    assert reward.repetition_penalty > 0.5
