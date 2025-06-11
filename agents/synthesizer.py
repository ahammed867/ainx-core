# agents/synthesizer.py
from core.ainx_message import AINXMessage

class SynthesizerAgent:
    def __init__(self):
        self.name = "SynthesizerAgent"

    def handle(self, message: AINXMessage) -> AINXMessage:
        # Basic simulated logic synthesis
        synthesized = f"[Synthesized by {self.name}]: Interpreted strategy and building a cohesive response."

        return AINXMessage(
            role="synthesizer",
            sender=self.name,
            content=f"{message.content}\n\n---\n{synthesized}"
        )
