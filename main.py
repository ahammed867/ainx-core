from core.ainx_message import AINXMessage
from core.router import AINXRouter
from agents.strategist import StrategistAgent
from agents.synthesizer import SynthesizerAgent
from agents.auditor import AuditorAgent
from agents.ledger import LedgerAgent
from agents.ambassador import AmbassadorAgent


# Initialize agents
strategist = StrategistAgent()
synthesizer = SynthesizerAgent()
auditor = AuditorAgent()
ledger = LedgerAgent()
ambassador = AmbassadorAgent()


# Register agents into a dictionary
agent_registry = {
    "strategist": strategist.handle,
    "synthesizer": synthesizer.handle,
    "auditor": auditor.handle,
    "ledger": ledger.handle,
    "ambassador": ambassador.handle
}

# Initialize router with agent registry
router = AINXRouter(agents=agent_registry)

def ainx_loop(user_input: str):
    initial_message = AINXMessage(
        role="user",
        sender="User",
        content=user_input
    )

    strategist_response = router.route("strategist", initial_message)
    print("\n[Strategist Response]:\n", strategist_response.content)

    synth_response = router.route("synthesizer", strategist_response)
    print("\n[Synthesizer Response]:\n", synth_response.content)

    audit_response = router.route("auditor", synth_response)
    print("\n[Auditor Response]:\n", audit_response.content)

    ledger_response = router.route("ledger", audit_response)
    print("\n[Ledger Response]:\n", ledger_response.content)

    ambassador_response = router.route("ambassador", ledger_response)
    print("\n[Ambassador Response]:\n", ambassador_response.content)

    return ambassador_response

e


if __name__ == "__main__":
    user_input = input("Enter a complex prompt for AINX to solve:\n> ")
    final_output = ainx_loop(user_input)
    print("\n✅ Final AINX Output:\n", final_output.content)



