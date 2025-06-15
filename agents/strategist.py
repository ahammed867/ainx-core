import os
from dotenv import load_dotenv
load_dotenv()


from openai import OpenAI
from core.ainx_message import AINXMessage

client = OpenAI()

class StrategistAgent:
    def handle(self, ainx_message: AINXMessage) -> AINXMessage:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a strategist agent who breaks down complex problems into manageable steps."},
                {"role": "user", "content": ainx_message.content}
            ]
        )

        reply_content = response.choices[0].message.content.strip()

        return AINXMessage(
            role="strategist",
            sender="StrategistAgent",
            content=reply_content
        )
