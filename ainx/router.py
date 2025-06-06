# ainx/router.py
from ainx.protocol import AINXMessage

class AINXRouterAgent:
    def __init__(self, name):
        self.name = name
        self.agents = []

    def register_agent(self, agent):
        self.agents.append(agent)

    def receive(self, message: AINXMessage):
        print(f"[{self.name}] received: {message}")
        for agent in self.agents:
            if message.intent in getattr(agent, "capabilities", []):
                print(f"[{self.name}] routing to {agent.name}")
                return agent.receive(message)

        return AINXMessage(
            sender=self.name,
            recipient=message.sender,
            command="ERROR",
            payload=f"No agent available to handle intent: {message.intent}"
        )
