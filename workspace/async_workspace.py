"""
AINX Async Workspace
Shared memory space for agents to collaborate in parallel
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, Optional, List, Set
from collections import defaultdict
import weakref

class AsyncWorkspace:
    """
    Async shared workspace for agent collaboration
    Thread-safe storage with real-time updates and change notifications
    """
    
    def __init__(self):
        self.data = {}
        self.metadata = {}  # Stores who wrote what and when
        self.change_history = []
        self.subscribers = defaultdict(list)  # Change notification callbacks
        self.locks = defaultdict(asyncio.Lock)  # Per-key locks for thread safety
        self.logger = logging.getLogger("AINX.Workspace")
        self.stats = {
            "reads": 0,
            "writes": 0,
            "updates": 0,
            "deletes": 0
        }
        
    async def set(self, key: str, value: Any, agent_id: str = None) -> bool:
        """Set a value in the workspace"""
        async with self.locks[key]:
            try:
                # Store the value
                old_value = self.data.get(key)
                self.data[key] = value
                
                # Store metadata
                self.metadata[key] = {
                    "agent_id": agent_id,
                    "timestamp": time.time(),
                    "operation": "set",
                    "previous_value": old_value
                }
                
                # Record change
                change_record = {
                    "key": key,
                    "operation": "set",
                    "agent_id": agent_id,
                    "timestamp": time.time(),
                    "old_value": old_value,
                    "new_value": value
                }
                self.change_history.append(change_record)
                
                # Update stats
                if old_value is None:
                    self.stats["writes"] += 1
                else:
                    self.stats["updates"] += 1
                    
                # Notify subscribers
                await self._notify_subscribers(key, change_record)
                
                self.logger.debug(f"Set {key} = {type(value).__name__} by {agent_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to set {key}: {e}")
                return False
                
    async def get(self, key: str) -> Any:
        """Get a value from the workspace"""
        async with self.locks[key]:
            self.stats["reads"] += 1
            value = self.data.get(key)
            self.logger.debug(f"Get {key} = {type(value).__name__ if value else 'None'}")
            return value
            
    async def get_with_metadata(self, key: str) -> Dict[str, Any]:
        """Get value with metadata"""
        async with self.locks[key]:
            return {
                "value": self.data.get(key),
                "metadata": self.metadata.get(key, {})
            }
            
    async def update(self, key: str, value: Any, agent_id: str = None) -> bool:
        """Update an existing value (alias for set)"""
        return await self.set(key, value, agent_id)
        
    async def delete(self, key: str, agent_id: str = None) -> bool:
        """Delete a key from the workspace"""
        async with self.locks[key]:
            try:
                if key in self.data:
                    old_value = self.data[key]
                    del self.data[key]
                    
                    # Clean up metadata
                    if key in self.metadata:
                        del self.metadata[key]
                        
                    # Record change
                    change_record = {
                        "key": key,
                        "operation": "delete",
                        "agent_id": agent_id,
                        "timestamp": time.time(),
                        "old_value": old_value,
                        "new_value": None
                    }
                    self.change_history.append(change_record)
                    
                    self.stats["deletes"] += 1
                    
                    # Notify subscribers
                    await self._notify_subscribers(key, change_record)
                    
                    self.logger.debug(f"Deleted {key} by {agent_id}")
                    return True
                else:
                    return False
                    
            except Exception as e:
                self.logger.error(f"Failed to delete {key}: {e}")
                return False
                
    async def exists(self, key: str) -> bool:
        """Check if a key exists"""
        return key in self.data
        
    async def keys(self) -> List[str]:
        """Get all keys in workspace"""
        return list(self.data.keys())
        
    async def values(self) -> List[Any]:
        """Get all values in workspace"""
        return list(self.data.values())
        
    async def items(self) -> List[tuple]:
        """Get all key-value pairs"""
        return list(self.data.items())
        
    async def size(self) -> int:
        """Get number of items in workspace"""
        return len(self.data)
        
    async def clear(self, agent_id: str = None) -> bool:
        """Clear all data from workspace"""
        try:
            old_keys = list(self.data.keys())
            self.data.clear()
            self.metadata.clear()
            
            # Record change
            change_record = {
                "key": "*",
                "operation": "clear",
                "agent_id": agent_id,
                "timestamp": time.time(),
                "old_value": old_keys,
                "new_value": None
            }
            self.change_history.append(change_record)
            
            # Notify subscribers for all keys
            for key in old_keys:
                await self._notify_subscribers(key, change_record)
                
            self.logger.info(f"Workspace cleared by {agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear workspace: {e}")
            return False
            
    async def get_by_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get all data written by specific agent"""
        result = {}
        for key, metadata in self.metadata.items():
            if metadata.get("agent_id") == agent_id:
                result[key] = self.data.get(key)
        return result
        
    async def get_keys_by_agent(self, agent_id: str) -> List[str]:
        """Get all keys written by specific agent"""
        return [
            key for key, metadata in self.metadata.items()
            if metadata.get("agent_id") == agent_id
        ]
        
    async def update_agent_status(self, agent_id: str, status: str, metadata: Dict = None):
        """Update agent status in workspace"""
        status_key = f"agent_status_{agent_id}"
        status_data = {
            "status": status,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        await self.set(status_key, status_data, agent_id)
        
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent status"""
        status_key = f"agent_status_{agent_id}"
        return await self.get(status_key)
        
    async def get_all_agent_statuses(self) -> Dict[str, Any]:
        """Get all agent statuses"""
        statuses = {}
        for key in self.data.keys():
            if key.startswith("agent_status_"):
                agent_id = key.replace("agent_status_", "")
                statuses[agent_id] = self.data[key]
        return statuses
        
    def subscribe(self, key: str, callback):
        """Subscribe to changes for a specific key"""
        self.subscribers[key].append(callback)
        self.logger.debug(f"Subscribed to changes for key: {key}")
        
    def subscribe_all(self, callback):
        """Subscribe to all changes"""
        self.subscribers["*"].append(callback)
        self.logger.debug("Subscribed to all workspace changes")
        
    def unsubscribe(self, key: str, callback):
        """Unsubscribe from changes"""
        if callback in self.subscribers[key]:
            self.subscribers[key].remove(callback)
            
    async def _notify_subscribers(self, key: str, change_record: Dict[str, Any]):
        """Notify subscribers of changes"""
        # Notify key-specific subscribers
        tasks = []
        for callback in self.subscribers[key]:
            task = asyncio.create_task(self._call_subscriber(callback, change_record))
            tasks.append(task)
            
        # Notify global subscribers
        for callback in self.subscribers["*"]:
            task = asyncio.create_task(self._call_subscriber(callback, change_record))
            tasks.append(task)
            
        # Fire and forget notifications
        if tasks:
            asyncio.create_task(asyncio.gather(*tasks, return_exceptions=True))
            
    async def _call_subscriber(self, callback, change_record: Dict[str, Any]):
        """Call a subscriber callback"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(change_record)
            else:
                callback(change_record)
        except Exception as e:
            self.logger.error(f"Subscriber callback failed: {e}")
            
    def get_stats(self) -> Dict[str, Any]:
        """Get workspace statistics"""
        return {
            **self.stats,
            "total_keys": len(self.data),
            "change_history_size": len(self.change_history),
            "active_locks": len(self.locks),
            "subscribers": sum(len(subs) for subs in self.subscribers.values())
        }
        
    def get_change_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent change history"""
        return self.change_history[-limit:]
        
    async def export_data(self) -> Dict[str, Any]:
        """Export all workspace data"""
        return {
            "data": self.data.copy(),
            "metadata": self.metadata.copy(),
            "stats": self.get_stats(),
            "export_timestamp": time.time()
        }
        
    async def import_data(self, data: Dict[str, Any], agent_id: str = None):
        """Import workspace data"""
        if "data" in data:
            for key, value in data["data"].items():
                await self.set(key, value, agent_id)
                
        self.logger.info(f"Imported {len(data.get('data', {}))} items by {agent_id}")

# Workspace manager for multiple workspaces
class WorkspaceManager:
    """Manages multiple workspaces"""
    
    def __init__(self):
        self.workspaces = {}
        
    async def create_workspace(self, workspace_id: str = "default") -> AsyncWorkspace:
        """Create a new workspace"""
        workspace = AsyncWorkspace()
        self.workspaces[workspace_id] = workspace
        return workspace
        
    async def get_workspace(self, workspace_id: str = "default") -> Optional[AsyncWorkspace]:
        """Get existing workspace"""
        return self.workspaces.get(workspace_id)
        
    async def delete_workspace(self, workspace_id: str):
        """Delete a workspace"""
        if workspace_id in self.workspaces:
            del self.workspaces[workspace_id]
            return True
        return False

# Example usage and testing
async def test_async_workspace():
    """Test the async workspace"""
    workspace = AsyncWorkspace()
    
    # Test basic operations
    await workspace.set("test_key", "test_value", "test_agent")
    value = await workspace.get("test_key")
    print(f"Retrieved value: {value}")
    
    # Test with metadata
    data_with_meta = await workspace.get_with_metadata("test_key")
    print(f"Value with metadata: {data_with_meta}")
    
    # Test agent status
    await workspace.update_agent_status("agent1", "working", {"task": "research"})
    status = await workspace.get_agent_status("agent1")
    print(f"Agent status: {status}")
    
    # Test stats
    stats = workspace.get_stats()
    print(f"Workspace stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_async_workspace())