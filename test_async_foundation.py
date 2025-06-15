"""
AINX Async Agent Base Class
Revolutionary async foundation for parallel agent execution
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import time
import uuid

class AsyncAgentBase(ABC):
    """
    Base class for all async AINX agents
    Maintains AINX protocol while enabling parallel execution
    """
    
    def __init__(self, agent_id: str, role: str):
        self.agent_id = agent_id
        self.role = role
        self.status = "idle"
        self.workspace = None
        self.message_bus = None
        self.logger = logging.getLogger(f"AINX.{agent_id}")
        self.active_tasks = set()
        
    async def initialize(self, workspace, message_bus):
        """Initialize agent with workspace and message bus"""
        self.workspace = workspace
        self.message_bus = message_bus
        self.logger.info(f"Agent {self.agent_id} initialized for async operation")
        
    async def start_listening(self):
        """Start listening for messages asynchronously"""
        self.status = "listening"
        self.logger.info(f"Agent {self.agent_id} started listening")
        
        while self.status == "listening":
            try:
                # Get messages for this agent
                messages = await self.message_bus.get_messages_for_agent(self.agent_id)
                
                # Process each message concurrently
                tasks = []
                for message in messages:
                    task = asyncio.create_task(self._process_message_async(message))
                    tasks.append(task)
                    self.active_tasks.add(task)
                    
                # Wait for all current tasks to complete
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
                # Clean up completed tasks
                self.active_tasks = {task for task in self.active_tasks if not task.done()}
                
                # Brief pause to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in message processing: {e}")
                await asyncio.sleep(1)
                
    async def _process_message_async(self, message: Dict[str, Any]):
        """Process a single message asynchronously"""
        task_id = str(uuid.uuid4())[:8]
        
        try:
            self.logger.info(f"[{task_id}] Processing: {message.get('intent', 'unknown')}")
            
            # Update workspace with processing status
            await self.workspace.update_agent_status(
                self.agent_id, 
                f"processing_{task_id}", 
                {"message": message, "started": time.time()}
            )
            
            # Call the agent's specific processing logic
            result = await self.process_message(message)
            
            # Send response if result is provided
            if result:
                await self.send_response(result, message)
                
            self.logger.info(f"[{task_id}] Completed successfully")
            
        except Exception as e:
            self.logger.error(f"[{task_id}] Failed: {e}")
            await self.send_error_response(str(e), message)
            
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a message and return a response
        Each agent implements this with their specific logic
        """
        pass
        
    async def send_response(self, response_data: Dict[str, Any], original_message: Dict[str, Any]):
        """Send a response using AINX protocol format"""
        response = {
            "sender": self.agent_id,
            "recipient": original_message.get("sender", "human"),
            "role": self.role,
            "intent": "response",
            "content": response_data,
            "timestamp": time.time(),
            "original_message_id": original_message.get("message_id")
        }
        
        await self.message_bus.send_message(response)
        self.logger.info(f"Response sent to {response['recipient']}")
        
    async def send_error_response(self, error: str, original_message: Dict[str, Any]):
        """Send an error response"""
        await self.send_response({
            "error": error,
            "status": "failed"
        }, original_message)
        
    async def send_message(self, recipient: str, intent: str, content: Dict[str, Any]):
        """Send a message to another agent"""
        message = {
            "sender": self.agent_id,
            "recipient": recipient,
            "role": self.role,
            "intent": intent,
            "content": content,
            "timestamp": time.time(),
            "message_id": str(uuid.uuid4())
        }
        
        await self.message_bus.send_message(message)
        self.logger.info(f"Message sent to {recipient}: {intent}")
        
    async def update_workspace(self, key: str, value: Any):
        """Update shared workspace"""
        await self.workspace.set(key, value, self.agent_id)
        
    async def read_workspace(self, key: str) -> Any:
        """Read from shared workspace"""
        return await self.workspace.get(key)
        
    async def stop(self):
        """Stop the agent gracefully"""
        self.status = "stopping"
        
        # Wait for active tasks to complete
        if self.active_tasks:
            self.logger.info(f"Waiting for {len(self.active_tasks)} active tasks to complete")
            await asyncio.gather(*self.active_tasks, return_exceptions=True)
            
        self.status = "stopped"
        self.logger.info(f"Agent {self.agent_id} stopped")
        
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "status": self.status,
            "active_tasks": len(self.active_tasks)
        }

class AsyncAgentManager:
    """Manages multiple async agents"""
    
    def __init__(self):
        self.agents = {}
        self.agent_tasks = {}
        
    async def add_agent(self, agent: AsyncAgentBase):
        """Add an agent to the manager"""
        self.agents[agent.agent_id] = agent
        
    async def start_all_agents(self):
        """Start all agents listening concurrently"""
        tasks = []
        for agent_id, agent in self.agents.items():
            task = asyncio.create_task(agent.start_listening())
            self.agent_tasks[agent_id] = task
            tasks.append(task)
            
        return tasks
        
    async def stop_all_agents(self):
        """Stop all agents gracefully"""
        # Signal all agents to stop
        for agent in self.agents.values():
            await agent.stop()
            
        # Cancel all agent tasks
        for task in self.agent_tasks.values():
            task.cancel()
            
        # Wait for tasks to complete
        await asyncio.gather(*self.agent_tasks.values(), return_exceptions=True)
        
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents"""
        return {agent_id: agent.get_status() for agent_id, agent in self.agents.items()}