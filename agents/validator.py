# agents/validator.py

from core.ainx_message import AINXMessage

class ValidatorAgent:
    def process(self, message: AINXMessage) -> AINXMessage:
        # Placeholder: in real use, you might call another LLM
        print(f"[ValidatorAgent] Validating strategy: {message.content}")
        
        # Simulate validation step
        if "invalid" in message.content.lower():
            message.content += "\n[Validator] Warning: Detected potential issue."
        else:
            message.content += "\n[Validator] Strategy looks valid."

        message.metadata["validated"] = True
        return message
