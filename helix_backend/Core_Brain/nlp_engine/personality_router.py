from helix_backend.personalities.Suzi import Suzi
from helix_backend.personalities.HelixPersonality import HelixPersonality


class PersonalityRouter:
    def __init__(self):
        self.personalities = {
            "helix": HelixPersonality(),
            "suzi": Suzi(),
        }
        self.active = "helix"

    def set_personality(self, personality_name):
        name = personality_name.lower()
        if name in self.personalities:
            self.active = name
        elif "suzi" in name:
            self.active = "suzi"
        elif "helix" in name:
            self.active = "helix"
        else:
            self.active = "helix"

    def get_response(self, user_input, memory, analysis=None, adaptive_context=None):
        try:
            target = self.active if self.active in self.personalities else "helix"
            return self.personalities[target].respond(user_input, memory, analysis, adaptive_context)
        except Exception as e:
            return "I'm having trouble processing your request right now. Please try again."

    def get_response_stream(self, user_input, memory, analysis=None, adaptive_context=None):
        try:
            target = self.active if self.active in self.personalities else "helix"
            return self.personalities[target].respond_stream(user_input, memory, analysis, adaptive_context)
        except Exception as e:
            def error_gen():
                yield "I'm having trouble processing your request right now. Please try again."
            return error_gen()
