from .emotional_layer import EmotionalIntelligenceLayer
from .rl_layer import ReinforcementLearningLayer
from .reflection_layer import ReflectionLayer


class AdaptiveOrchestrator:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.emotional_layer = EmotionalIntelligenceLayer()
        self.rl_layer = ReinforcementLearningLayer()
        self.reflection_layer = ReflectionLayer()
        self.last_sentiment = "neutral"

    def prepare(self, user_input, analysis):
        memory_snapshot = self.memory_manager.get_memory_snapshot(user_input)
        emotional_state = self.emotional_layer.build_state(user_input, analysis, memory_snapshot)
        policy_state = self.rl_layer.select_policy(emotional_state, analysis)
        execution_actions = ["analyze", "retrieve_memory", "adapt_policy", "generate"]
        self.memory_manager.log_execution(execution_actions)
        return {
            "memory_snapshot": memory_snapshot,
            "emotional_state": emotional_state,
            "policy_state": policy_state,
            "execution_actions": execution_actions,
        }

    def complete(self, user_input, analysis, response_text, policy_state, emotional_state):
        reward = self.rl_layer.compute_reward(
            user_input=user_input,
            analysis=analysis,
            response_text=response_text,
            previous_sentiment=self.last_sentiment,
        )
        learning_state = self.rl_layer.update(reward, policy_state.get("policy"))
        reflection = self.reflection_layer.evaluate(
            user_input=user_input,
            analysis=analysis,
            emotional_state=emotional_state,
            policy_state=policy_state,
            response_text=response_text,
            reward=reward,
        )
        self.last_sentiment = (analysis or {}).get("sentiment", "neutral")
        return {
            "reward": reward,
            "learning_state": learning_state,
            "reflection": reflection,
        }
