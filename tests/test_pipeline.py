from rl.dataset import build_demo_dataset
from rl.reward import RewardFunction
from rl.state import StatePreprocessor


def test_pipeline_flow_generates_rewardable_state():
    sample = build_demo_dataset()[0]
    preprocessor = StatePreprocessor()
    reward_function = RewardFunction()

    state = preprocessor.preprocess(
        user_input=sample.user_input,
        emotional_state_vector=sample.emotional_state_vector,
        conversation_history=sample.history,
        user_profile_features=sample.profile,
    )
    response = "Let us break the work into three clear steps and handle the highest-risk task first."
    reward = reward_function.compute(
        response_text=response,
        metrics={
            "engagement_score": 0.7,
            "sentiment_improvement": 0.5,
            "task_success": 0.9,
            "emotional_alignment": 0.8,
        },
    )

    assert state.user_input
    assert reward.total > 0
