# agents/ambassador.py

from core.ainx_message import AINXMessage

class AmbassadorAgent:
    def __init__(self):
        self.name = "AmbassadorAgent"

    def handle(self, message: AINXMessage) -> AINXMessage:
        # Simulate preparing message for external system
        wrapped_content = (
            f"[Prepared for External Agent by {self.name}]\n"
            f"Forwarding message:\n"
            f"From: {message.sender} | Role: {message.role}\n\n"
            f"{message.content}"
        )

        return AINXMessage(
            role="ambassador",
            sender=self.name,
            content=wrapped_content
        )
