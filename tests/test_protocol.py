from ainx.protocol import AINXMessage

def test_parse():
    msg = AINXMessage("AGENT::REQUEST::TASK.type=sync.priority=high")
    assert msg.role == "AGENT"
    assert msg.intent == "REQUEST"
    assert msg.object == "TASK"
    assert msg.fields == {"type": "sync", "priority": "high"}
