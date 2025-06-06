from ainx.agent import AINXAgent
from ainx.protocol import AINXMessage

def run_simulation():
    a1 = AINXAgent("alpha")
    a2 = AINXAgent("beta")

    msg = AINXMessage("ALPHA::QUERY::STATUS.system=up")
    response = a2.receive(msg)
    a1.receive(response)
