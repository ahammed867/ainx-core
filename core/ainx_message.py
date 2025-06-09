from datetime import datetime
import uuid

class AINXMessage:
    def __init__(self, task, source_agent="User", parent_id=None):
        self.message_id = str(uuid.uuid4())
        self.task = task
        self.source_agent = source_agent
        self.parent_id = parent_id
        self.timestamp = datetime.utcnow().isoformat()
        self.validation_state = "unvalidated"  # or: validated, rejected
        self.agent_trail = [source_agent]
        self.audit_log = []

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
