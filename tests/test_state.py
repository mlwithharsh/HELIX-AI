from rl.state import StatePreprocessor


def test_state_preprocessor_builds_expected_shape():
    preprocessor = StatePreprocessor(embedding_dim=16)
    state = preprocessor.preprocess(
        user_input="Help me debug the training loop.",
        emotional_state_vector=[0.2, 0.4, 0.7, 0.1, 0.5],
        conversation_history=[{"role": "user", "content": "The job failed."}],
        user_profile_features={"task_focus": 0.9},
    )
    assert len(state.user_input_embedding) == 16
    assert len(state.emotional_state_vector) == 5
    assert state.user_profile_features["task_focus"] == 0.9
