class BasePersonality:
    def __init__(self, name, style, goals):
        self.name = name
        self.style = style
        self.goals = goals

    def respond(self, user_input, memory, analysis=None, adaptive_context=None):
        """Default response if child personality doesn't override."""
        return f"{self.name} says: I am still learning how to respond."

    def respond_stream(self, user_input, memory, analysis=None, adaptive_context=None):
        """Default streaming response."""
        yield f"{self.name} is starting to think..."

