from ainx.protocol import AINXMessage
from ainx.agents import ResearcherAgent, PlannerAgent, CriticAgent

class AINXRouterAgent:
    def __init__(self, name):
        self.name = name
        self.routes = {
            "search": ResearcherAgent("researcher"),
            "plan": PlannerAgent("planner"),
            "critique": CriticAgent("critic"),
        }

    def receive(self, message: AINXMessage):
        print(f"[{self.name}] received: {message}")

        # Route to agent based on intent
        intent = message.intent
        agent = self.routes.get(intent)

        if agent:
            return agent.receive(message)
        else:
            return AINXMessage(
                f"{self.name}::{message.sender}::ERROR::unknown_intent::{intent}"
            )
