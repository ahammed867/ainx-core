#!/usr/bin/env python3
"""
AINX Modern WebSocket Server - Real-time Agent Monitoring
Fixed deprecation warnings and enhanced functionality
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Dict, Any, Set
import signal
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AINXWebSocketServer:
    """Modern AINX WebSocket Server for real-time agent monitoring"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None
        self.running = False
        
        # Statistics
        self.stats = {
            "clients_connected": 0,
            "total_connections": 0,
            "messages_received": 0,
            "messages_broadcast": 0,
            "start_time": None
        }
    
    async def register_client(self, websocket):
        """Register a new WebSocket client - Fixed deprecation warning"""
        self.clients.add(websocket)
        self.stats["clients_connected"] += 1
        self.stats["total_connections"] += 1
        
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"📱 Client connected: {client_info} (Total: {len(self.clients)})")
        
        # Send welcome message
        welcome_msg = {
            "type": "welcome",
            "message": "Connected to AINX WebSocket Server",
            "server_info": {
                "version": "2.0",
                "capabilities": ["agent_monitoring", "real_time_updates", "performance_metrics"]
            },
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_client(websocket, welcome_msg)
    
    async def unregister_client(self, websocket):
        """Unregister a WebSocket client - Fixed deprecation warning"""
        self.clients.discard(websocket)
        self.stats["clients_connected"] -= 1
        
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}" if hasattr(websocket, 'remote_address') else "unknown"
        logger.info(f"📱 Client disconnected: {client_info} (Remaining: {len(self.clients)})")
    
    async def send_to_client(self, websocket, message: Dict[str, Any]):
        """Send message to specific client - Fixed deprecation warning"""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Attempted to send to closed connection")
            await self.unregister_client(websocket)
        except Exception as e:
            logger.error(f"Error sending to client: {e}")
    
    async def broadcast_to_all_clients(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return
        
        # Create a copy of clients set to avoid modification during iteration
        clients_copy = self.clients.copy()
        
        # Send to all clients concurrently
        tasks = [self.send_to_client(client, message) for client in clients_copy]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.stats["messages_broadcast"] += 1
    
    async def handle_client_message(self, websocket, message: str):
        """Handle incoming messages from clients - Fixed deprecation warning"""
        try:
            data = json.loads(message)
            self.stats["messages_received"] += 1
            
            message_type = data.get("type", "unknown")
            logger.info(f"📨 Received {message_type} message from client")
            
            # Handle different message types
            if message_type == "ping":
                await self.send_to_client(websocket, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_type == "get_stats":
                stats_copy = self.stats.copy()
                stats_copy["current_time"] = datetime.now().isoformat()
                stats_copy["uptime"] = self._get_uptime()
                
                await self.send_to_client(websocket, {
                    "type": "stats_response",
                    "stats": stats_copy
                })
            
            elif message_type == "agent_command":
                # Broadcast agent commands to all clients
                await self.broadcast_to_all_clients({
                    "type": "agent_command_broadcast",
                    "command": data.get("command"),
                    "target_agent": data.get("target_agent"),
                    "sender": "client",
                    "timestamp": datetime.now().isoformat()
                })
            
            else:
                # Echo unknown messages back for debugging
                await self.send_to_client(websocket, {
                    "type": "echo",
                    "original_message": data,
                    "timestamp": datetime.now().isoformat()
                })
                
        except json.JSONDecodeError:
            await self.send_to_client(websocket, {
                "type": "error",
                "message": "Invalid JSON format",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            await self.send_to_client(websocket, {
                "type": "error", 
                "message": f"Server error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    
    async def client_handler(self, websocket, path: str):
        """Handle WebSocket client connections - Fixed deprecation warning"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_client_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed normally")
        except Exception as e:
            logger.error(f"Error in client handler: {e}")
        finally:
            await self.unregister_client(websocket)
    
    def _get_uptime(self) -> str:
        """Get server uptime"""
        if not self.stats["start_time"]:
            return "0 seconds"
        
        uptime_seconds = (datetime.now() - self.stats["start_time"]).total_seconds()
        
        if uptime_seconds < 60:
            return f"{uptime_seconds:.1f} seconds"
        elif uptime_seconds < 3600:
            return f"{uptime_seconds/60:.1f} minutes"
        else:
            return f"{uptime_seconds/3600:.1f} hours"
    
    async def start_server(self):
        """Start the WebSocket server"""
        try:
            logger.info(f"🚀 Starting AINX WebSocket server on {self.host}:{self.port}")
            
            # Fixed handler signature for newer websockets library
            async def handler_wrapper(websocket, path):
                await self.client_handler(websocket, path)
            
            self.server = await websockets.serve(
                handler_wrapper,
                self.host,
                self.port,
                ping_interval=30,  # Send ping every 30 seconds
                ping_timeout=60,   # Wait 60 seconds for pong
                compression=None   # Disable compression for better performance
            )
            
            self.running = True
            self.stats["start_time"] = datetime.now()
            
            logger.info(f"✅ AINX WebSocket server running on ws://{self.host}:{self.port}")
            logger.info(f"🌐 Ready to accept agent connections and client monitoring")
            
            # Keep server running
            await self.server.wait_closed()
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            raise
    
    async def stop_server(self):
        """Stop the WebSocket server"""
        if self.server and self.running:
            logger.info("🛑 Stopping AINX WebSocket server...")
            
            # Close all client connections
            if self.clients:
                await asyncio.gather(
                    *[client.close() for client in self.clients.copy()],
                    return_exceptions=True
                )
            
            # Close server
            self.server.close()
            await self.server.wait_closed()
            
            self.running = False
            logger.info("✅ AINX WebSocket server stopped")

# Global server instance
websocket_server = AINXWebSocketServer()

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    asyncio.create_task(websocket_server.stop_server())

# Public API functions for agents to report status
async def report_agent_status(agent_id: str, status: str, details: Dict[str, Any] = None):
    """Public API for agents to report their status"""
    message = {
        "type": "agent_status",
        "agent_id": agent_id,
        "status": status,
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    }
    
    await websocket_server.broadcast_to_all_clients(message)

async def report_agent_thinking(agent_id: str, thought: str):
    """Public API for agents to report thinking process"""
    message = {
        "type": "agent_thinking",
        "agent_id": agent_id,
        "thought": thought,
        "timestamp": datetime.now().isoformat()
    }
    
    await websocket_server.broadcast_to_all_clients(message)

async def report_agent_task(agent_id: str, task_name: str, task_status: str, summary: str = None):
    """Public API for agents to report task progress"""
    message = {
        "type": "agent_task",
        "agent_id": agent_id,
        "task_name": task_name,
        "task_status": task_status,
        "summary": summary,
        "timestamp": datetime.now().isoformat()
    }
    
    await websocket_server.broadcast_to_all_clients(message)

async def main():
    """Main server function"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await websocket_server.start_server()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        if websocket_server.running:
            await websocket_server.stop_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)