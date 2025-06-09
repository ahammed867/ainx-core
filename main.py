import sys
import os

# Ensure ainx-core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.ainx_message import AINXMessage
from core.router import AINXRouter
from agents.strategist import StrategistAgent
from agents.synthesizer import SynthesizerAgent

def run_ainx_pipeline(prompt: str):
    message = AINXMessage(task=prompt)
    agents = [
        StrategistAgent(),
        SynthesizerAgent()
    ]
    router = AINXRouter(agents)
    final_message = router.route(message)

    print("\n✅ Final Synthesized Output:\n")
    print(final_message.task)
    print("\n📜 Agent Trail:", " -> ".join(final_message.agent_trail))

if __name__ == "__main__":
    run_ainx_pipeline("Solve the integral of x^2 * sin(x)")

