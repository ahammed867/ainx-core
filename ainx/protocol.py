class AINXMessage:
    def __init__(self, raw: str):
        self.raw = raw
        self.role = None
        self.intent = None
        self.object = None
        self.fields = {}
        self.parse()

    def parse(self):
        try:
            parts = self.raw.split("::")
            if len(parts) < 3:
                raise ValueError("AINX message must have ROLE::INTENT::OBJECT")
            self.role, self.intent, obj = parts[:3]
            if '.' in obj:
                obj_main, *field_parts = obj.split('.')
                self.object = obj_main
                for part in field_parts:
                    if '=' in part:
                        k, v = part.split('=')
                        self.fields[k] = v
            else:
                self.object = obj
        except Exception as e:
            raise ValueError(f"Invalid AINX message: {self.raw}") from e

    def __str__(self):
        field_str = ''.join(f".{k}={v}" for k, v in self.fields.items())
        return f"{self.role}::{self.intent}::{self.object}{field_str}"
