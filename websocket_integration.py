

import asyncio
import websockets
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Global WebSocket connection
_websocket_client = None
_websocket_uri = "ws://localhost:8765"

logger = logging.getLogger("AINX.WebSocket")

async def connect_to_websocket_server():
    """Connect to WebSocket server for real-time reporting"""
    global _websocket_client
    
    try:
        _websocket_client = await websockets.connect(_websocket_uri)
        logger.info(f"✅ Connected to WebSocket server at {_websocket_uri}")
        return True
    except Exception as e:
        logger.warning(f"⚠️  Could not connect to WebSocket server: {e}")
        _websocket_client = None
        return False

async def disconnect_from_websocket_server():
    """Disconnect from WebSocket server"""
    global _websocket_client
    
    if _websocket_client:
        try:
            await _websocket_client.close()
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error closing WebSocket: {e}")
        finally:
            _websocket_client = None

async def send_websocket_message(message_type: str, agent_id: str, data: Dict[str, Any]):
    """Send message to WebSocket server"""
    global _websocket_client
    
    if not _websocket_client:
        return  # Fail silently if not connected
    
    try:
        message = {
            "type": message_type,
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        await _websocket_client.send(json.dumps(message))
        
    except Exception as e:
        logger.error(f"Failed to send WebSocket message: {e}")
        # Try to reconnect
        await connect_to_websocket_server()

# WebSocket reporting functions for agents
async def ws_report_status(agent_id: str, status: str, details: Optional[Dict] = None):
    """Report agent status change"""
    await send_websocket_message("status", agent_id, {
        "status": status,
        "details": details or {}
    })

async def ws_report_thinking(agent_id: str, thought: str):
    """Report agent thinking process"""
    await send_websocket_message("thinking", agent_id, {
        "thought": thought
    })

async def ws_report_task(agent_id: str, task_name: str, task_status: str, summary: Optional[str] = None):
    """Report task progress"""
    await send_websocket_message("task", agent_id, {
        "task_name": task_name,
        "task_status": task_status,
        "summary": summary
    })

async def ws_report_message(sender: str, recipient: str, role: str, intent: str, content_preview: str, direction: str):
    """Report message sending/receiving"""
    await send_websocket_message("message", sender, {
        "recipient": recipient,
        "role": role,
        "intent": intent,
        "content_preview": content_preview,
        "direction": direction
    })

async def ws_report_error(agent_id: str, error_message: str):
    """Report agent error"""
    await send_websocket_message("error", agent_id, {
        "error": error_message
    })

async def ws_report_performance(agent_id: str, metrics: Dict[str, Any]):
    """Report performance metrics"""
    await send_websocket_message("performance", agent_id, metrics)

# Context manager for WebSocket connection
class WebSocketConnection:
    """Context manager for WebSocket connections"""
    
    async def __aenter__(self):
        await connect_to_websocket_server()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await disconnect_from_websocket_server()

# Initialize WebSocket connection when module is imported
async def initialize_websocket():
    """Initialize WebSocket connection on startup"""
    await connect_to_websocket_server()

# Test WebSocket integration
async def test_websocket_integration():
    """Test WebSocket integration with your server"""
    print("🧪 Testing WebSocket Integration...")
    
    # Test connection
    connected = await connect_to_websocket_server()
    if not connected:
        print("❌ Could not connect to WebSocket server")
        print("   Make sure to run: python websocket_server.py")
        return False
    
    print("✅ Connected to WebSocket server")
    
    # Test all reporting functions
    try:
        await ws_report_status("test_agent", "initializing")
        await asyncio.sleep(0.1)
        
        await ws_report_thinking("test_agent", "Testing WebSocket integration...")
        await asyncio.sleep(0.1)
        
        await ws_report_task("test_agent", "Integration Test", "started")
        await asyncio.sleep(0.1)
        
        await ws_report_message("test_agent", "human", "agent", "test", "Hello WebSocket!", "sent")
        await asyncio.sleep(0.1)
        
        await ws_report_performance("test_agent", {
            "cpu_usage": 0.15,
            "memory_usage": 45.2,
            "response_time": 0.123
        })
        await asyncio.sleep(0.1)
        
        await ws_report_task("test_agent", "Integration Test", "completed", "All functions tested")
        await asyncio.sleep(0.1)
        
        await ws_report_status("test_agent", "idle")
        
        print("✅ All WebSocket reporting functions tested")
        
    except Exception as e:
        print(f"❌ WebSocket testing failed: {e}")
        return False
    
    finally:
        await disconnect_from_websocket_server()
    
    print("🎉 WebSocket integration test completed!")
    return True

if __name__ == "__main__":
    # Run test
    asyncio.run(test_websocket_integration())