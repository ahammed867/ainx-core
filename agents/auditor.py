# agents/auditor.py
from core.ainx_message import AINXMessage

class AuditorAgent:
    def __init__(self):
        self.name = "AuditorAgent"

    def handle(self, message: AINXMessage) -> AINXMessage:
        # Example logic: confidence score check
        confidence = "high" if len(message.content) > 50 else "low"
        audit_notes = f"AUDIT COMPLETE | Confidence: {confidence} | Agent: {self.name}"

        return AINXMessage(
            role="auditor",
            sender=self.name,
            content=message.content + f"\n\n---\n{audit_notes}"
        )
