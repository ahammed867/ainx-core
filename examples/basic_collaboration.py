#!/usr/bin/env python3
"""
AINX Basic Collaboration Example
Shows agents working together asynchronously
"""

import asyncio
from agents.researcher_agent import ResearcherAgent
# from agents.planner_agent import PlannerAgent  # When converted to async
# from agents.critic_agent import CriticAgent    # When converted to async

async def demo_collaboration():
    """Demo async agent collaboration"""
    
    print("🚀 Starting AINX Async Collaboration Demo")
    
    # Initialize agents
    researcher = ResearcherAgent("researcher")
    
    # Start research task
    research_task = asyncio.create_task(
        researcher.research("Python async programming best practices")
    )
    
    # You could start other agents simultaneously here
    # planner_task = asyncio.create_task(planner.plan())
    # critic_task = asyncio.create_task(critic.review())
    
    # Wait for completion
    research_result = await research_task
    
    print("✅ Demo completed!")
    print(f"Research result: {research_result[:100]}...")

if __name__ == "__main__":
    asyncio.run(demo_collaboration())