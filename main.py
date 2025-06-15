# main.py

from agents.strategist import StrategistAgent
from agents.synthesizer import SynthesizerAgent
from core.router import AINXRouter
from core.ainx_message import AINXMessage

# Initialize agents
strategist = StrategistAgent()
synthesizer = SynthesizerAgent()

router = AINXRouter(agents={
    "strategist": strategist,
    "synthesizer": synthesizer,
})

def ainx_loop(user_input: str):
    initial_message = AINXMessage(role="user", sender="User", content=user_input)

    strategist_response = router.route("strategist", initial_message)
    print("\n[Strategist Response]:", strategist_response.content)

    synth_response = router.route("synthesizer", strategist_response)
    print("\n[Synthesizer Response]:", synth_response.content)

if __name__ == "__main__":
    user_input = input("Enter a real-world task for AINX to solve: ")
    ainx_loop(user_input)




