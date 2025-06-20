import asyncio
from websocket_server import AINXWebSocketServer, set_websocket_server
# ... your other imports

async def main():
    """Main entry point with WebSocket server"""
    
    # Initialize WebSocket server
    ws_server = AINXWebSocketServer()
    set_websocket_server(ws_server)
    
    # Start WebSocket server in background
    ws_task = asyncio.create_task(ws_server.start_server())
    
    # Initialize your existing components
    # ... your existing main logic here
    
    # Keep running
    try:
        await asyncio.gather(ws_task)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    asyncio.run(main())


