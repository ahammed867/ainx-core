from core.ainx_message import AINXMessage

class StrategistAgent:
    def process(self, message: AINXMessage) -> AINXMessage:
        task = message.task

        # 🔍 Simulated breakdown of task
        subtasks = [
            f"Understand the problem: {task}",
            f"Identify knowns/unknowns in: {task}",
            f"Propose steps to solve: {task}",
        ]
        message.task = "\n".join(subtasks)
        return message
