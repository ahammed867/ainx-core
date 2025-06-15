"""
AINX Async Researcher Agent
Researches information while other agents work in parallel
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from async_agent_base import AsyncAgentBase

class AsyncResearcherAgent(AsyncAgentBase):
    """
    Async researcher agent that can gather information while other agents work
    """
    
    def __init__(self):
        super().__init__("researcher", "researcher")
        self.search_engines = {
            "web": self._web_search,
            "knowledge": self._knowledge_search,
            "data": self._data_search
        }
        
    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process research requests asynchronously"""
        intent = message.get("intent")
        content = message.get("content", {})
        
        if intent == "research":
            return await self._handle_research_request(content)
        elif intent == "search":
            return await self._handle_search_request(content)
        elif intent == "analyze":
            return await self._handle_analysis_request(content)
        else:
            return {"error": f"Unknown intent: {intent}"}
            
    async def _handle_research_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle comprehensive research requests"""
        topic = content.get("topic")
        sources = content.get("sources", ["web", "knowledge"])
        depth = content.get("depth", "medium")
        
        if not topic:
            return {"error": "No research topic provided"}
            
        self.logger.info(f"Starting research on: {topic}")
        
        # Update workspace with research status
        await self.update_workspace(f"research_status_{topic}", {
            "status": "in_progress",
            "topic": topic,
            "sources": sources,
            "started": asyncio.get_event_loop().time()
        })
        
        # Research from multiple sources in parallel
        research_tasks = []
        for source in sources:
            if source in self.search_engines:
                task = asyncio.create_task(
                    self.search_engines[source](topic, depth)
                )
                research_tasks.append((source, task))
                
        # Wait for all research to complete
        results = {}
        for source, task in research_tasks:
            try:
                results[source] = await task
            except Exception as e:
                results[source] = {"error": str(e)}
                self.logger.error(f"Research failed for {source}: {e}")
                
        # Combine and analyze results
        final_result = await self._synthesize_research(topic, results)
        
        # Update workspace with final results
        await self.update_workspace(f"research_results_{topic}", final_result)
        
        self.logger.info(f"Research completed for: {topic}")
        return final_result
        
    async def _handle_search_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle quick search requests"""
        query = content.get("query")
        source = content.get("source", "web")
        
        if not query:
            return {"error": "No search query provided"}
            
        if source not in self.search_engines:
            return {"error": f"Unknown search source: {source}"}
            
        result = await self.search_engines[source](query, "quick")
        return {"query": query, "source": source, "result": result}
        
    async def _handle_analysis_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data analysis requests"""
        data = content.get("data")
        analysis_type = content.get("type", "summary")
        
        if not data:
            return {"error": "No data provided for analysis"}
            
        # Simulate async analysis processing
        await asyncio.sleep(0.5)  # Simulate processing time
        
        if analysis_type == "summary":
            return await self._summarize_data(data)
        elif analysis_type == "trends":
            return await self._analyze_trends(data)
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}
            
    async def _web_search(self, query: str, depth: str) -> Dict[str, Any]:
        """Simulate web search (replace with real implementation)"""
        await asyncio.sleep(1)  # Simulate network delay
        
        # In real implementation, use aiohttp to call search APIs
        return {
            "query": query,
            "results": [
                {
                    "title": f"Search Result 1 for {query}",
                    "url": "https://example.com/1",
                    "snippet": f"This is a search result about {query}...",
                    "relevance": 0.9
                },
                {
                    "title": f"Search Result 2 for {query}",
                    "url": "https://example.com/2", 
                    "snippet": f"Another relevant result for {query}...",
                    "relevance": 0.8
                }
            ],
            "total_results": 2,
            "search_time": 1.0,
            "source": "web"
        }
        
    async def _knowledge_search(self, query: str, depth: str) -> Dict[str, Any]:
        """Search internal knowledge base"""
        await asyncio.sleep(0.5)  # Simulate processing time
        
        return {
            "query": query,
            "knowledge_results": [
                {
                    "topic": query,
                    "summary": f"Knowledge base information about {query}",
                    "confidence": 0.85,
                    "sources": ["internal_kb", "previous_research"]
                }
            ],
            "source": "knowledge"
        }
        
    async def _data_search(self, query: str, depth: str) -> Dict[str, Any]:
        """Search structured data sources"""
        await asyncio.sleep(0.3)  # Simulate database query
        
        return {
            "query": query,
            "data_results": [
                {
                    "dataset": "research_data",
                    "matches": 5,
                    "relevance": 0.7,
                    "sample": f"Data sample related to {query}"
                }
            ],
            "source": "data"
        }
        
    async def _synthesize_research(self, topic: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize research results from multiple sources"""
        await asyncio.sleep(0.5)  # Simulate analysis time
        
        # Count total results
        total_results = 0
        sources_used = []
        
        for source, result in results.items():
            if "error" not in result:
                sources_used.append(source)
                if "results" in result:
                    total_results += len(result["results"])
                elif "knowledge_results" in result:
                    total_results += len(result["knowledge_results"])
                elif "data_results" in result:
                    total_results += len(result["data_results"])
                    
        return {
            "topic": topic,
            "summary": f"Research synthesis for {topic}",
            "sources_used": sources_used,
            "total_results": total_results,
            "detailed_results": results,
            "confidence": 0.8,
            "recommendations": [
                f"Based on research, {topic} shows promising results",
                f"Further investigation recommended in {sources_used[0] if sources_used else 'web'}"
            ]
        }
        
    async def _summarize_data(self, data: Any) -> Dict[str, Any]:
        """Summarize provided data"""
        await asyncio.sleep(0.2)
        
        return {
            "summary": f"Data summary: {str(data)[:100]}...",
            "type": type(data).__name__,
            "analysis": "summary_complete"
        }
        
    async def _analyze_trends(self, data: Any) -> Dict[str, Any]:
        """Analyze trends in data"""
        await asyncio.sleep(0.3)
        
        return {
            "trends": ["trend_1", "trend_2"],
            "analysis": "trends_identified",
            "confidence": 0.75
        }

# Example usage and testing
async def test_researcher_agent():
    """Test the async researcher agent"""
    from async_message_bus import AsyncMessageBus
    from async_workspace import AsyncWorkspace
    
    # Create test environment
    workspace = AsyncWorkspace()
    message_bus = AsyncMessageBus()
    
    # Create and initialize agent
    researcher = AsyncResearcherAgent()
    await researcher.initialize(workspace, message_bus)
    
    # Test research request
    test_message = {
        "sender": "human",
        "recipient": "researcher",
        "role": "user",
        "intent": "research",
        "content": {
            "topic": "artificial intelligence trends",
            "sources": ["web", "knowledge"],
            "depth": "medium"
        }
    }
    
    # Process message
    result = await researcher.process_message(test_message)
    print("Research Result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    # Run test
    asyncio.run(test_researcher_agent())