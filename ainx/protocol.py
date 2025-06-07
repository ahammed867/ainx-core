class AINXMessage:
    def __init__(self, raw: str):
        self.raw = raw
        self.role = None
        self.intent = None
        self.object = None
        self.fields = {}
        self.sender = None
        self.recipient = None
        self.content = None
        self.parse()

    def parse(self):
        try:
            parts = self.raw.split("::")
            if len(parts) < 5:
                raise ValueError("AINX message must have 5 parts")

            self.sender, self.recipient, self.role, self.intent, self.content = parts

            self.fields = {
                "sender": self.sender,
                "recipient": self.recipient,
                "role": self.role,
                "intent": self.intent,
                "content": self.content
            }
        except Exception as e:
            raise ValueError(f"Failed to parse AINX message: {e}")

    def __str__(self):
        return f"{self.sender}::{self.recipient}::{self.role}::{self.intent}::{self.content}"
