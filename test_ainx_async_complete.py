#!/usr/bin/env python3
"""
AINX Async MVP - Comprehensive Test Suite
Tests all components working together in parallel
"""

import asyncio
import logging
import time
import json
import sys
from typing import Dict, Any

# Configure colorful logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

def print_header(title: str):
    """Print a nice header"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {message}")

async def test_imports():
    """Test 1: Check all imports work"""
    print_header("TEST 1: Import All Components")
    
    try:
        from agents.async_agent_base import AsyncAgentBase, AsyncAgentManager
        print_success("AsyncAgentBase imported")
    except Exception as e:
        print_error(f"AsyncAgentBase import failed: {e}")
        return False
    
    try:
        from agents.researcher_agent import AsyncResearcherAgent
        print_success("AsyncResearcherAgent imported")
    except Exception as e:
        print_error(f"AsyncResearcherAgent import failed: {e}")
        return False
    
    try:
        from message_bus.async_message_bus import AsyncMessageBus
        print_success("AsyncMessageBus imported")
    except Exception as e:
        print_error(f"AsyncMessageBus import failed: {e}")
        return False
    
    try:
        from workspace.async_workspace import AsyncWorkspace
        print_success("AsyncWorkspace imported")
    except Exception as e:
        print_error(f"AsyncWorkspace import failed: {e}")
        return False
    
    try:
        import aiohttp
        import websockets
        print_success("All dependencies (aiohttp, websockets) imported")
    except Exception as e:
        print_error(f"Dependencies import failed: {e}")
        return False
    
    return True

async def test_workspace():
    """Test 2: Async Workspace functionality"""
    print_header("TEST 2: Async Workspace")
    
    from workspace.async_workspace import AsyncWorkspace
    
    workspace = AsyncWorkspace()
    
    # Test basic operations
    await workspace.set("test_key", "hello_world", "test_agent")
    value = await workspace.get("test_key")
    assert value == "hello_world", f"Expected 'hello_world', got {value}"
    print_success("Basic set/get operations work")
    
    # Test agent status
    await workspace.update_agent_status("agent1", "working", {"task": "testing"})
    status = await workspace.get_agent_status("agent1")
    assert status["status"] == "working", f"Status should be 'working', got {status}"
    print_success("Agent status tracking works")
    
    # Test parallel operations
    tasks = []
    for i in range(10):
        task = asyncio.create_task(workspace.set(f"parallel_key_{i}", f"value_{i}", f"agent_{i}"))
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    
    # Verify all keys were set
    keys = await workspace.keys()
    parallel_keys = [k for k in keys if k.startswith("parallel_key_")]
    assert len(parallel_keys) == 10, f"Expected 10 parallel keys, got {len(parallel_keys)}"
    print_success("Parallel workspace operations work")
    
    # Test stats
    stats = workspace.get_stats()
    print_info(f"Workspace stats: {stats}")
    
    return True

async def test_message_bus():
    """Test 3: Async Message Bus functionality"""
    print_header("TEST 3: Async Message Bus")
    
    from message_bus.async_message_bus import AsyncMessageBus
    
    bus = AsyncMessageBus()
    await bus.start()
    
    # Test message sending
    test_message = {
        "sender": "human",
        "recipient": "researcher",
        "role": "user", 
        "intent": "test",
        "content": {"message": "Hello from test"}
    }
    
    await bus.send_message(test_message)
    print_success("Message sent successfully")
    
    # Test message retrieval
    messages = await bus.get_messages_for_agent("researcher")
    assert len(messages) == 1, f"Expected 1 message, got {len(messages)}"
    assert messages[0]["content"]["message"] == "Hello from test"
    print_success("Message retrieval works")
    
    # Test parallel message sending
    tasks = []
    for i in range(5):
        message = {
            "sender": f"agent_{i}",
            "recipient": "target_agent",
            "role": "agent",
            "intent": "parallel_test",
            "content": {"id": i}
        }
        task = asyncio.create_task(bus.send_message(message))
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    
    target_messages = await bus.get_messages_for_agent("target_agent")
    assert len(target_messages) == 5, f"Expected 5 messages, got {len(target_messages)}"
    print_success("Parallel message sending works")
    
    # Test stats
    stats = bus.get_stats()
    print_info(f"Message bus stats: {stats}")
    
    await bus.stop()
    return True

async def test_researcher_agent():
    """Test 4: Async Researcher Agent"""
    print_header("TEST 4: Async Researcher Agent")
    
    from agents.researcher_agent import AsyncResearcherAgent
    from message_bus.async_message_bus import AsyncMessageBus
    from workspace.async_workspace import AsyncWorkspace
    
    # Setup environment
    workspace = AsyncWorkspace()
    message_bus = AsyncMessageBus()
    await message_bus.start()
    
    # Create and initialize agent
    researcher = AsyncResearcherAgent()
    await researcher.initialize(workspace, message_bus)
    print_success("Researcher agent initialized")
    
    # Test research request
    research_message = {
        "sender": "human",
        "recipient": "researcher",
        "role": "user",
        "intent": "research",
        "content": {
            "topic": "async programming",
            "sources": ["web", "knowledge"],
            "depth": "medium"
        }
    }
    
    print_info("Starting research request...")
    start_time = time.time()
    result = await researcher.process_message(research_message)
    end_time = time.time()
    
    assert "topic" in result, "Research result should contain topic"
    assert result["topic"] == "async programming"
    print_success(f"Research completed in {end_time - start_time:.2f}s")
    print_info(f"Research found {result.get('total_results', 0)} results from {len(result.get('sources_used', []))} sources")
    
    # Test search request
    search_message = {
        "sender": "human",
        "recipient": "researcher", 
        "role": "user",
        "intent": "search",
        "content": {
            "query": "machine learning",
            "source": "web"
        }
    }
    
    search_result = await researcher.process_message(search_message)
    assert "query" in search_result, "Search result should contain query"
    print_success("Search request works")
    
    await message_bus.stop()
    return True

async def test_parallel_agents():
    """Test 5: Multiple Agents Working in Parallel"""
    print_header("TEST 5: Parallel Agent Execution")
    
    from agents.async_agent_base import AsyncAgentBase
    from message_bus.async_message_bus import AsyncMessageBus
    from workspace.async_workspace import AsyncWorkspace
    
    # Setup environment
    workspace = AsyncWorkspace()
    message_bus = AsyncMessageBus()
    await message_bus.start()
    
    # Create test agent class
    class TestAgent(AsyncAgentBase):
        async def process_message(self, message: Dict[str, Any]):
            work_time = message.get("content", {}).get("work_time", 1)
            await asyncio.sleep(work_time)
            return {
                "agent_id": self.agent_id,
                "work_time": work_time,
                "completed": True
            }
    
    # Create multiple agents
    agents = []
    for i in range(3):
        agent = TestAgent(f"test_agent_{i}", "test")
        await agent.initialize(workspace, message_bus)
        agents.append(agent)
    
    print_success(f"Created {len(agents)} test agents")
    
    # Send work to all agents simultaneously
    tasks = []
    start_time = time.time()
    
    for i, agent in enumerate(agents):
        message = {
            "sender": "human",
            "recipient": f"test_agent_{i}",
            "role": "user",
            "intent": "work",
            "content": {"work_time": 1}  # 1 second of work each
        }
        
        task = asyncio.create_task(agent.process_message(message))
        tasks.append((f"test_agent_{i}", task))
    
    # Wait for all agents to complete
    results = []
    for agent_id, task in tasks:
        result = await task
        results.append((agent_id, result))
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print_success(f"All {len(agents)} agents completed work in {total_time:.2f}s")
    
    # Verify parallel execution (should be ~1s, not 3s)
    if total_time < 1.5:  # Allow some overhead
        print_success("✨ PARALLEL EXECUTION CONFIRMED! (Time < 1.5s)")
    else:
        print_error(f"Agents may be running sequentially (Time: {total_time:.2f}s)")
    
    # Check results
    for agent_id, result in results:
        assert result["completed"] == True, f"Agent {agent_id} should have completed"
        print_info(f"{agent_id}: ✅ Completed in {result['work_time']}s")
    
    await message_bus.stop()
    return True

async def test_full_system_integration():
    """Test 6: Full System Integration"""
    print_header("TEST 6: Full System Integration")
    
    from agents.researcher_agent import AsyncResearcherAgent
    from agents.async_agent_base import AsyncAgentManager
    from message_bus.async_message_bus import AsyncMessageBus
    from workspace.async_workspace import AsyncWorkspace
    
    # Setup full system
    workspace = AsyncWorkspace()
    message_bus = AsyncMessageBus()
    agent_manager = AsyncAgentManager()
    
    await message_bus.start()
    
    # Create researcher agent
    researcher = AsyncResearcherAgent()
    await researcher.initialize(workspace, message_bus)
    await agent_manager.add_agent(researcher)
    
    print_success("Full system initialized")
    
    # Simulate complex workflow
    print_info("Simulating complex research workflow...")
    
    # 1. Start research
    research_task = asyncio.create_task(researcher.process_message({
        "sender": "human",
        "recipient": "researcher",
        "role": "user",
        "intent": "research",
        "content": {
            "topic": "artificial intelligence trends 2025",
            "sources": ["web", "knowledge", "data"],
            "depth": "deep"
        }
    }))
    
    # 2. While research is running, check workspace
    await asyncio.sleep(0.1)  # Let research start
    
    agent_statuses = await workspace.get_all_agent_statuses()
    print_info(f"Found {len(agent_statuses)} active agents")
    
    # 3. Complete research
    research_result = await research_task
    print_success("Complex research workflow completed")
    
    # 4. Verify final state
    final_stats = {
        "workspace": workspace.get_stats(),
        "message_bus": message_bus.get_stats(),
        "agents": agent_manager.get_all_status()
    }
    
    print_info("System Statistics:")
    print_info(f"  Workspace: {final_stats['workspace']['total_keys']} keys, {final_stats['workspace']['reads']} reads, {final_stats['workspace']['writes']} writes")
    print_info(f"  Message Bus: {final_stats['message_bus']['messages_sent']} sent, {final_stats['message_bus']['messages_delivered']} delivered")
    print_info(f"  Agents: {len(final_stats['agents'])} active")
    
    await message_bus.stop()
    return True

async def run_all_tests():
    """Run all tests in sequence"""
    print_header("AINX ASYNC MVP - COMPREHENSIVE TEST SUITE")
    print_info("Testing all components built so far...\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Workspace Tests", test_workspace), 
        ("Message Bus Tests", test_message_bus),
        ("Researcher Agent Tests", test_researcher_agent),
        ("Parallel Execution Tests", test_parallel_agents),
        ("Full System Integration", test_full_system_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print_info(f"Running {test_name}...")
            result = await test_func()
            if result:
                passed += 1
                print_success(f"{test_name} PASSED")
            else:
                failed += 1
                print_error(f"{test_name} FAILED")
        except Exception as e:
            failed += 1
            print_error(f"{test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    # Final results
    print_header("TEST RESULTS")
    print_success(f"PASSED: {passed}/{len(tests)} tests")
    if failed > 0:
        print_error(f"FAILED: {failed}/{len(tests)} tests")
    else:
        print_success("🎉 ALL TESTS PASSED!")
        print_info("\n✨ AINX Async Foundation is working perfectly!")
        print_info("Ready for next phase: WebSocket Server for real-time monitoring")
    
    return failed == 0

if __name__ == "__main__":
    print("🚀 Starting AINX Async MVP Test Suite...")
    
    try:
        result = asyncio.run(run_all_tests())
        if result:
            print("\n🎯 SUCCESS: Ready to build WebSocket Server!")
            sys.exit(0)
        else:
            print("\n❌ FAILURE: Please fix issues before proceeding")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)