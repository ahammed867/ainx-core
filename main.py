# main.py

from core.ainx_message import AINXMessage
from agents.strategist import StrategistAgent
from agents.validator import ValidatorAgent
from agents.synthesizer import SynthesizerAgent

def main():
    input_prompt = "Create a strategy to solve a complex logic problem."

    strategist = StrategistAgent()
    validator = ValidatorAgent()
    synthesizer = SynthesizerAgent()

    # Step 1: Strategize
    message = AINXMessage(sender="user", content=input_prompt)
    message = strategist.process(message)

    # Step 2: Validate
    message = validator.process(message)

    # Step 3: Synthesize
    message = synthesizer.process(message)

    # Final output
    print("\n[AINX Final Output]")
    print(message.content)

if __name__ == "__main__":
    main()


