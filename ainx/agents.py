from ainx.protocol import AINXMessage

class BaseAgent:
    def __init__(self, name):
        self.name = name

    def receive(self, message: AINXMessage):
        print(f"[{self.name}] received: {message}")
        return self.respond(message)

    def respond(self, message: AINXMessage):
        return AINXMessage(
            f"{self.name}::{message.sender}::{message.role}::ack::{self.name} received intent: {message.intent} with content: {message.content}"
        )


class ResearcherAgent(BaseAgent):
    def respond(self, message: AINXMessage):
        # Simulate a knowledge lookup
        return AINXMessage(
            f"{self.name}::{message.sender}::RESEARCHER::response::Found info about '{message.content}'"
        )


class PlannerAgent(BaseAgent):
    def respond(self, message: AINXMessage):
        return AINXMessage(
            f"{self.name}::{message.sender}::PLANNER::response::Created a step-by-step plan for '{message.content}'"
        )


class CriticAgent(BaseAgent):
    def respond(self, message: AINXMessage):
        return AINXMessage(
            f"{self.name}::{message.sender}::CRITIC::response::Critique of '{message.content}': looks solid, but consider edge cases."
        )
