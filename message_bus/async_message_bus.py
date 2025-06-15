"""
AINX Async Message Bus
Handles parallel message routing between agents
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from collections import defaultdict, deque

class AsyncMessageBus:
    """
    Async message bus for routing messages between agents in parallel
    Maintains AINX protocol while enabling concurrent message processing
    """
    
    def __init__(self, max_queue_size: int = 1000):
        self.message_queues = defaultdict(lambda: deque(maxlen=max_queue_size))
        self.message_history = deque(maxlen=10000)  # Keep last 10k messages
        self.subscribers = defaultdict(list)  # Agent callbacks
        self.routing_rules = {}
        self.logger = logging.getLogger("AINX.MessageBus")
        self.stats = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "failed_deliveries": 0
        }
        self._running = False
        self._delivery_tasks = set()
        
    async def start(self):
        """Start the async message bus"""
        self._running = True
        self.logger.info("Async message bus started")
        
    async def stop(self):
        """Stop the message bus gracefully"""
        self._running = False
        
        # Cancel all delivery tasks
        for task in self._delivery_tasks:
            task.cancel()
            
        if self._delivery_tasks:
            await asyncio.gather(*self._delivery_tasks, return_exceptions=True)
            
        self.logger.info("Async message bus stopped")
        
    async def send_message(self, message: Dict[str, Any]):
        """Send a message asynchronously"""
        if not self._running:
            raise RuntimeError("Message bus is not running")
            
        # Add message metadata
        message.setdefault("message_id", str(uuid.uuid4()))
        message.setdefault("timestamp", time.time())
        
        # Validate message format (AINX protocol)
        if not self._validate_message(message):
            raise ValueError(f"Invalid message format: {message}")
            
        # Log the message
        self.logger.info(
            f"Sending: {message['sender']} -> {message['recipient']} "
            f"({message['intent']})"
        )
        
        # Add to history
        self.message_history.append(message.copy())
        
        # Route the message
        await self._route_message(message)
        
        self.stats["messages_sent"] += 1
        
    async def _route_message(self, message: Dict[str, Any]):
        """Route message to appropriate recipients"""
        recipient = message.get("recipient")
        
        if recipient == "broadcast":
            # Broadcast to all agents
            await self._broadcast_message(message)
        elif recipient in self.routing_rules:
            # Custom routing rule
            await self._apply_routing_rule(message, recipient)
        else:
            # Direct delivery
            await self._deliver_message(message, recipient)
            
    async def _deliver_message(self, message: Dict[str, Any], recipient: str):
        """Deliver message to specific recipient"""
        try:
            # Add to recipient's queue
            self.message_queues[recipient].append(message)
            
            # Notify subscribers (for real-time updates)
            if recipient in self.subscribers:
                # Create delivery tasks for all subscribers
                tasks = []
                for callback in self.subscribers[recipient]:
                    task = asyncio.create_task(self._notify_subscriber(callback, message))
                    tasks.append(task)
                    self._delivery_tasks.add(task)
                    
                # Don't wait for notifications to complete (fire and forget)
                # Clean up completed tasks
                self._delivery_tasks = {task for task in self._delivery_tasks if not task.done()}
                    
            self.stats["messages_delivered"] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to deliver message to {recipient}: {e}")
            self.stats["failed_deliveries"] += 1
            
    async def _notify_subscriber(self, callback: Callable, message: Dict[str, Any]):
        """Notify a subscriber about a new message"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(message)
            else:
                callback(message)
        except Exception as e:
            self.logger.error(f"Subscriber notification failed: {e}")
            
    async def _broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all known agents"""
        agents = list(self.message_queues.keys())
        tasks = []
        
        for agent in agents:
            if agent != message.get("sender"):  # Don't send to sender
                task = asyncio.create_task(self._deliver_message(message, agent))
                tasks.append(task)
                
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def _apply_routing_rule(self, message: Dict[str, Any], recipient: str):
        """Apply custom routing rule"""
        rule = self.routing_rules[recipient]
        if asyncio.iscoroutinefunction(rule):
            await rule(message)
        else:
            rule(message)
            
    async def get_messages_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all pending messages for an agent"""
        messages = []
        queue = self.message_queues[agent_id]
        
        # Get all messages from queue
        while queue:
            messages.append(queue.popleft())
            
        return messages
        
    async def peek_messages_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """Peek at messages without removing them"""
        return list(self.message_queues[agent_id])
        
    def subscribe(self, agent_id: str, callback: Callable):
        """Subscribe to messages for an agent (for real-time notifications)"""
        self.subscribers[agent_id].append(callback)
        self.logger.info(f"Subscribed callback for agent: {agent_id}")
        
    def unsubscribe(self, agent_id: str, callback: Callable):
        """Unsubscribe from messages"""
        if callback in self.subscribers[agent_id]:
            self.subscribers[agent_id].remove(callback)
            
    def add_routing_rule(self, recipient: str, rule: Callable):
        """Add custom routing rule"""
        self.routing_rules[recipient] = rule
        self.logger.info(f"Added routing rule for: {recipient}")
        
    def _validate_message(self, message: Dict[str, Any]) -> bool:
        """Validate AINX message format"""
        required_fields = ["sender", "recipient", "role", "intent", "content"]
        return all(field in message for field in required_fields)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        return {
            **self.stats,
            "queue_sizes": {agent: len(queue) for agent, queue in self.message_queues.items()},
            "total_agents": len(self.message_queues),
            "subscribers": len(self.subscribers),
            "routing_rules": len(self.routing_rules),
            "running": self._running
        }
        
    def get_message_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent message history"""
        return list(self.message_history)[-limit:]
        
    async def clear_agent_queue(self, agent_id: str):
        """Clear all messages for an agent"""
        self.message_queues[agent_id].clear()
        self.logger.info(f"Cleared message queue for: {agent_id}")
        
    async def get_agent_queue_size(self, agent_id: str) -> int:
        """Get queue size for an agent"""
        return len(self.message_queues[agent_id])

# Utility functions for message bus management
class MessageBusManager:
    """Manages multiple message bus instances"""
    
    def __init__(self):
        self.buses = {}
        
    async def create_bus(self, bus_id: str = "default") -> AsyncMessageBus:
        """Create a new message bus"""
        bus = AsyncMessageBus()
        await bus.start()
        self.buses[bus_id] = bus
        return bus
        
    async def get_bus(self, bus_id: str = "default") -> Optional[AsyncMessageBus]:
        """Get existing message bus"""
        return self.buses.get(bus_id)
        
    async def stop_all_buses(self):
        """Stop all message buses"""
        for bus in self.buses.values():
            await bus.stop()
        self.buses.clear()

# Example usage and testing
async def test_async_message_bus():
    """Test the async message bus"""
    bus = AsyncMessageBus()
    await bus.start()
    
    # Test message sending
    test_message = {
        "sender": "human",
        "recipient": "researcher",
        "role": "user",
        "intent": "research",
        "content": {"topic": "async programming"}
    }
    
    await bus.send_message(test_message)
    
    # Get messages
    messages = await bus.get_messages_for_agent("researcher")
    print(f"Messages for researcher: {len(messages)}")
    
    # Test broadcast
    broadcast_message = {
        "sender": "system",
        "recipient": "broadcast",
        "role": "system",
        "intent": "shutdown",
        "content": {"reason": "maintenance"}
    }
    
    await bus.send_message(broadcast_message)
    
    # Check stats
    stats = bus.get_stats()
    print(f"Message bus stats: {stats}")
    
    await bus.stop()

if __name__ == "__main__":
    asyncio.run(test_async_message_bus())