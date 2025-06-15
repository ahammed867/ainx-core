from datetime import datetime
import uuid

# core/ainx_message.py

class AINXMessage:
    def __init__(self, role, sender, content, metadata=None):
        self.role = role  # "user", "strategist", etc.
        self.sender = sender  # Name of sender
        self.content = content  # The main text content
        self.metadata = metadata or {}  # Dict for extra info


    def to_dict(self):
        return {
            "message_id": self.message_id,
            "task": self.task,
            "source_agent": self.source_agent,
            "parent_id": self.parent_id,
            "timestamp": self.timestamp,
            "validation_state": self.validation_state,
            "agent_trail": self.agent_trail,
            "audit_log": self.audit_log
        }

    def add_agent_to_trail(self, agent_name):
        self.agent_trail.append(agent_name)

    def log_audit(self, comment, passed):
        self.audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "comment": comment,
            "passed": passed
        })
