# core/router.py

class AINXRouter:
    def __init__(self, agents):
        self.agents = agents

    def route(self, agent_name, message):
        agent = self.agents.get(agent_name)
        if agent:
            return agent.handle(message)
        raise ValueError(f"Agent '{agent_name}' not found.")
