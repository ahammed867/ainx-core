from ainx.protocol import AINXMessage

class AINXAgent:
    def __init__(self, name):
        self.name = name

    def receive(self, message: AINXMessage):
        print(f"[{self.name}] received: {message}")
        response = self.respond(message)
        if response:
            return response

    def respond(self, message: AINXMessage):
        if message.command == "QUERY":
            return AINXMessage(
                sender=self.name.upper(),
                recipient=message.sender,
                command="ACK",
                payload=f"RESPONSE.to={message.sender}"
            )
        # Do not respond to ACK messages
        return None
