from core.ainx_message import AINXMessage

class AINXRouter:
    def __init__(self, agents):
        self.agents = agents  # Ordered list of agents

    def route(self, message: AINXMessage):
        for agent in self.agents:
            agent_name = agent.__class__.__name__
            print(f"\n🔄 Passing to agent: {agent_name}")
            message.add_agent_to_trail(agent_name)
            message = agent.process(message)
        return message
