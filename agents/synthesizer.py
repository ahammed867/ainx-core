from core.ainx_message import AINXMessage

class SynthesizerAgent:
    def process(self, message: AINXMessage) -> AINXMessage:
        subtasks = message.task.split("\n")
        
        # Very basic simulated synthesis
        solution = "🔧 Synthesized Plan:\n"
        for i, step in enumerate(subtasks, 1):
            solution += f"{i}. {step} → [simulated solution step]\n"

        message.task = solution
        return message
