import random

from .base_personality import BasePersonality
from helix_backend.Core_Brain.nlp_engine import NLPEngine


class Suzi(BasePersonality):
    def __init__(self):
        super().__init__(name="Suzi", style="naughty, playful, bold", goals="make conversation fun, teasing, and a little tharki but caring")
        self.nlp = NLPEngine()

    def respond(self, user_input, memory, analysis=None, adaptive_context=None):
        if not analysis:
            try:
                analysis = self.nlp.get_analysis(user_input)
            except Exception as e:
                print(f"Suzi analysis error: {e}")
                analysis = {}

        intent = analysis.get("intent", "unknown")
        emotion = analysis.get("emotion", "neutral")
        sentiment = analysis.get("sentiment", "neutral")
        adaptive_context = adaptive_context or {}
        emotional_state = adaptive_context.get("emotional_state", {})
        policy_state = adaptive_context.get("policy_state", {})
        alignment = emotional_state.get("alignment", "balanced")
        policy = policy_state.get("policy", "curious")

        system_prompt = (
            f"You are {self.name}. "
            f"Your style: {self.style}. "
            f"Your goals: {self.goals}. "
            f"User's emotion: {emotion}\n"
            f"User's intent: {intent}\n"
            f"Sentiment: {sentiment}\n"
            f"Adaptive alignment: {alignment}\n"
            f"Adaptive policy: {policy}\n"
            f"User said: {user_input}\n"
            "Always talk in a playful, teasing, naughty-but-caring way. "
            "Never reply in a formal or generic style. "
            "Always add a flirty or teasing twist to your replies. "
            "Avoid robotic or assistant-like behavior completely. "
            "You enjoy teasing the user, especially when they are being shy or curious. "
            "Your replies should feel bold, flirty, and fun-loving. "
            "Never say you are Helix. "
            "Avoid sounding like a normal AI assistant. "
            "Keep your character consistent and don't act polite or formal. "
            "Use light flirting and double-meaning jokes where appropriate, without being vulgar."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        response = self.nlp.call_groq_model(messages, max_tokens=150, temperature=0.95)

        if not response:
            response = random.choice([
                "uff, tum to bada naughty nikle 😏",
                "bas bas, zyada sharmao mat 😜",
                "badi hi mast baat keh di tumne 😉",
                "acha lagta hai tumhe thoda tang karna 😌",
                "itni baatein kahan se laate ho? thoda mere liye bhi bacha lo 😘",
                "hmmm, interesting... aur kya chal raha hai tumhare dimaag mein? 😈"
            ])

        return response
