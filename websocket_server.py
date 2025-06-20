#!/usr/bin/env python3
"""
AINX WebSocket Server - Real-time Agent Communication
Enables live monitoring of async agent collaboration
"""

import asyncio
import json
import logging
import websockets
from typing import Set, Dict, Any, Optional
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AINXWebSocketServer:
    """WebSocket server for real-time AINX agent communication"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.agent_status: Dict[str, Dict[str, Any]] = {}
        self.message_history: list = []
        self.max_history = 1000  # Keep last 1000 messages
        
    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        """Register new WebSocket client"""
        self.clients.add(websocket)
        client_id = f"client_{len(self.clients)}"
        logger.info(f"Client {client_id} connected from {websocket.remote_address}")
        
        # Send current agent status and recent history to new client
        await self.send_to_client(websocket, {
            "type": "connection_established",
            "client_id": client_id,
            "agent_status": self.agent_status,
            "recent_messages": self.message_history[-10:]  # Last 10 messages
        })
    
    async def unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister WebSocket client"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected")
    
    async def send_to_client(self, websocket: websockets.WebSocketServerProtocol, message: Dict[str, Any]):
        """Send message to specific client"""
        try:
            await websocket.send(json.dumps(message, default=str))
        except websockets.exceptions.ConnectionClosed:
            await self.unregister_client(websocket)
        except Exception as e:
            logger.error(f"Error sending to client: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return
            
        # Add timestamp and message ID
        message.update({
            "timestamp": datetime.now().isoformat(),
            "message_id": str(uuid.uuid4())[:8]
        })
        
        # Store in history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
        
        # Send to all clients
        disconnected_clients = set()
        for client in self.clients:
            try:
                await client.send(json.dumps(message, default=str))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected_clients.add(client)
        
        # Clean up disconnected clients
        for client in disconnected_clients:
            await self.unregister_client(client)
    
    async def handle_client_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Handle message from WebSocket client"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "ping":
                await self.send_to_client(websocket, {"type": "pong"})
            
            elif message_type == "get_agent_status":
                await self.send_to_client(websocket, {
                    "type": "agent_status_response",
                    "agent_status": self.agent_status
                })
            
            elif message_type == "get_message_history":
                count = data.get("count", 50)
                await self.send_to_client(websocket, {
                    "type": "message_history_response",
                    "messages": self.message_history[-count:]
                })
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client: {message}")
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
    
    async def client_handler(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle WebSocket client connection"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                await self.handle_client_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
    
    # AINX Agent Communication Methods
    
    async def report_agent_status(self, agent_id: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Report agent status change"""
        self.agent_status[agent_id] = {
            "status": status,
            "last_update": datetime.now().isoformat(),
            "details": details or {}
        }
        
        await self.broadcast({
            "type": "agent_status_update",
            "agent_id": agent_id,
            "status": status,
            "details": details
        })
    
    async def report_message_sent(self, sender: str, recipient: str, role: str, intent: str, content: str):
        """Report AINX message sent"""
        await self.broadcast({
            "type": "ainx_message",
            "direction": "sent",
            "sender": sender,
            "recipient": recipient,
            "role": role,
            "intent": intent,
            "content": content
        })
    
    async def report_message_received(self, sender: str, recipient: str, role: str, intent: str, content: str):
        """Report AINX message received"""
        await self.broadcast({
            "type": "ainx_message",
            "direction": "received",
            "sender": sender,
            "recipient": recipient,
            "role": role,
            "intent": intent,
            "content": content
        })
    
    async def report_agent_thinking(self, agent_id: str, thought: str):
        """Report agent internal thinking/processing"""
        await self.broadcast({
            "type": "agent_thinking",
            "agent_id": agent_id,
            "thought": thought
        })
        
    
    async def report_task_started(self, agent_id: str, task: str):
        """Report agent started working on task"""
        await self.broadcast({
            "type": "task_started",
            "agent_id": agent_id,
            "task": task
        })
        
        await self.report_agent_status(agent_id, "working", {"current_task": task})
    
    async def report_task_completed(self, agent_id: str, task: str, result: str):
        """Report agent completed task"""
        await self.broadcast({
            "type": "task_completed",
            "agent_id": agent_id,
            "task": task,
            "result": result
        })
        
        await self.report_agent_status(agent_id, "idle", {"last_completed": task})
    
    async def report_error(self, agent_id: str, error: str, details: Optional[Dict[str, Any]] = None):
        """Report agent error"""
        await self.broadcast({
            "type": "agent_error",
            "agent_id": agent_id,
            "error": error,
            "details": details
        })
        
        await self.report_agent_status(agent_id, "error", {"error": error, "details": details})
    
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting AINX WebSocket server on {self.host}:{self.port}")
        
        async with websockets.serve(self.client_handler, self.host, self.port):
            logger.info(f"AINX WebSocket server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever
    
    def run(self):
        """Run the server (blocking)"""
        try:
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")

# Global server instance for agents to use
_server_instance: Optional[AINXWebSocketServer] = None

def get_websocket_server() -> Optional[AINXWebSocketServer]:
    """Get the global WebSocket server instance"""
    return _server_instance

def set_websocket_server(server: AINXWebSocketServer):
    """Set the global WebSocket server instance"""
    global _server_instance
    _server_instance = server

# Convenience functions for agents to use
async def ws_report_status(agent_id: str, status: str, details: Optional[Dict[str, Any]] = None):
    """Report agent status to WebSocket clients"""
    server = get_websocket_server()
    if server:
        await server.report_agent_status(agent_id, status, details)

async def ws_report_message(sender: str, recipient: str, role: str, intent: str, content: str, direction: str = "sent"):
    """Report AINX message to WebSocket clients"""
    server = get_websocket_server()
    if server:
        if direction == "sent":
            await server.report_message_sent(sender, recipient, role, intent, content)
        else:
            await server.report_message_received(sender, recipient, role, intent, content)

async def ws_report_thinking(agent_id: str, thought: str):
    """Report agent thinking to WebSocket clients"""
    server = get_websocket_server()
    if server:
        await server.report_agent_thinking(agent_id, thought)

async def ws_report_task(agent_id: str, task: str, status: str = "started", result: str = None):
    """Report agent task to WebSocket clients"""
    server = get_websocket_server()
    if server:
        if status == "started":
            await server.report_task_started(agent_id, task)
        elif status == "completed":
            await server.report_task_completed(agent_id, task, result)

async def ws_report_error(agent_id: str, error: str, details: Optional[Dict[str, Any]] = None):
    """Report agent error to WebSocket clients"""
    server = get_websocket_server()
    if server:
        await server.report_error(agent_id, error, details)

if __name__ == "__main__":
    # Run server standalone
    server = AINXWebSocketServer()
    server.run()


  
