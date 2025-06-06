from ainx.protocol import AINXMessage

class AINXAgent:
    def __init__(self, name):
        self.name = name

    def receive(self, message: AINXMessage):
        print(f"[{self.name}] received: {message}")
        return self.respond(message)

    def respond(self, message: AINXMessage):
        return AINXMessage(f"{self.name.upper()}::ACK::RESPONSE.to={message.role}")
