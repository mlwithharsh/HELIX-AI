from echo_backend.personalities.Suzi import Suzi
from echo_backend.personalities.EchoPersonality import EchoPersonality


class PersonalityRouter:
    def __init__(self):
        self.personalities = {
            "echo": EchoPersonality(),
            "suzi": Suzi(),
        }
        self.active = "echo"

    def set_personality(self, personality_name):
        name = personality_name.lower()
        if name in self.personalities:
            self.active = name
        elif "suzi" in name:
            self.active = "suzi"
        elif "echo" in name:
            self.active = "echo"
        else:
            self.active = "echo"

    def get_response(self, user_input, memory, analysis=None, adaptive_context=None):
        try:
            if self.active in self.personalities:
                return self.personalities[self.active].respond(user_input, memory, analysis, adaptive_context)
            else:
                return self.personalities["echo"].respond(user_input, memory, analysis, adaptive_context)
        except Exception as e:
            return "I'm having trouble processing your request right now. Please try again."
