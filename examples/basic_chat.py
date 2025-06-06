# basic_chat.py
from ainx.protocol import AINXMessage
from ainx.agent import AINXBaseAgent
from ainx.roles.researcher import ResearcherAgent
from ainx.router import AINXRouterAgent

# Create router and agents
router = AINXRouterAgent("router")
researcher = ResearcherAgent("r1")
planner = AINXBaseAgent("p1", capabilities=["plan"])

# Register agents
router.register_agent(researcher)
router.register_agent(planner)

# Simulate message with a search intent
message1 = AINXMessage(
    sender="alpha",
    recipient="router",
    command="QUERY",
    intent="search",
    payload="Find trends in agent communication."
)

# Simulate message with a plan intent
message2 = AINXMessage(
    sender="alpha",
    recipient="router",
    command="QUERY",
    intent="plan",
    payload="Create a workflow from A to Z."
)

# Simulate message with an unknown intent
message3 = AINXMessage(
    sender="alpha",
    recipient="router",
    command="QUERY",
    intent="cook",
    payload="Make a sandwich."
)

# Run simulation
print(router.receive(message1))
print(router.receive(message2))
print(router.receive(message3))
