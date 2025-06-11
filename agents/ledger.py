# agents/ledger.py
import hashlib
from core.ainx_message import AINXMessage

class LedgerAgent:
    def __init__(self):
        self.name = "LedgerAgent"
        self.ledger = []

    def handle(self, message: AINXMessage) -> AINXMessage:
        # Simulate writing to blockchain by hashing message
        content_hash = hashlib.sha256(message.content.encode()).hexdigest()
        entry = {
            "sender": message.sender,
            "role": message.role,
            "content": message.content,
            "hash": content_hash
        }

        self.ledger.append(entry)

        response_content = (
            f"[Ledger Entry Recorded by {self.name}]\n"
            f"Hash: {content_hash[:10]}... ✅\n"
            f"Total Entries: {len(self.ledger)}"
        )

        return AINXMessage(
            role="ledger",
            sender=self.name,
            content=response_content
        )
