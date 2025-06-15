import os
from dotenv import load_dotenv
load_dotenv()


from openai import OpenAI
from core.ainx_message import AINXMessage

client = OpenAI()

class SynthesizerAgent:
    def handle(self, ainx_message: AINXMessage) -> AINXMessage:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a synthesizer agent that converts structured steps into a single solution or insight."},
                {"role": "user", "content": ainx_message.content}
            ]
        )

        reply_content = response.choices[0].message.content.strip()

        return AINXMessage(
            role="synthesizer",
            sender="SynthesizerAgent",
            content=reply_content
        )
