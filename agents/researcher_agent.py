"""
AINX Async Researcher Agent - Furnished with WebSocket Integration
Researches information while other agents work in parallel
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from async_agent_base import AsyncAgentBase

# WebSocket reporting imports
try:
    from websocket_server import (
        ws_report_status, 
        ws_report_thinking, 
        ws_report_task, 
        ws_report_message,
        ws_report_error
    )
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    # Create no-op functions if websocket server not available
    async def ws_report_status(*args, **kwargs): pass
    async def ws_report_thinking(*args, **kwargs): pass
    async def ws_report_task(*args, **kwargs): pass
    async def ws_report_message(*args, **kwargs): pass
    async def ws_report_error(*args, **kwargs): pass

class AsyncResearcherAgent(AsyncAgentBase):
    """
    Async researcher agent that can gather information while other agents work
    Enhanced with WebSocket real-time reporting
    """
    
    def __init__(self):
        super().__init__("researcher", "researcher")
        self.search_engines = {
            "web": self._web_search,
            "knowledge": self._knowledge_search,
            "data": self._data_search
        }
        
    async def initialize(self, workspace, message_bus):
        """Initialize agent with WebSocket reporting"""
        await super().initialize(workspace, message_bus)
        await ws_report_status("researcher", "initializing")
        await ws_report_thinking("researcher", "Researcher agent coming online...")
        self.logger.info("Researcher agent initialized")
        await ws_report_status("researcher", "idle")
        
    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process research requests asynchronously with WebSocket reporting"""
        intent = message.get("intent")
        content = message.get("content", {})
        sender = message.get("sender", "unknown")
        
        # Report message received
        await ws_report_message(sender, "researcher", message.get("role", ""), intent, str(content)[:100], "received")
        await ws_report_thinking("researcher", f"Processing {intent} request from {sender}")
        
        try:
            if intent == "research":
                result = await self._handle_research_request(content)
            elif intent == "search":
                result = await self._handle_search_request(content)
            elif intent == "analyze":
                result = await self._handle_analysis_request(content)
            else:
                error_msg = f"Unknown intent: {intent}"
                await ws_report_error("researcher", error_msg)
                return {"error": error_msg}
                
            # Report successful processing
            await ws_report_thinking("researcher", f"Successfully processed {intent} request")
            return result
            
        except Exception as e:
            error_msg = f"Error processing {intent}: {str(e)}"
            await ws_report_error("researcher", error_msg)
            self.logger.error(error_msg)
            return {"error": error_msg}
            
    async def _handle_research_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle comprehensive research requests with detailed reporting"""
        topic = content.get("topic")
        sources = content.get("sources", ["web", "knowledge"])
        depth = content.get("depth", "medium")
        
        if not topic:
            await ws_report_error("researcher", "No research topic provided")
            return {"error": "No research topic provided"}
            
        # Start research task reporting
        await ws_report_status("researcher", "researching")
        await ws_report_task("researcher", f"Research: {topic}", "started")
        await ws_report_thinking("researcher", f"Starting comprehensive research on: {topic}")
        
        self.logger.info(f"Starting research on: {topic}")
        
        # Update workspace with research status
        await self.update_workspace(f"research_status_{topic}", {
            "status": "in_progress",
            "topic": topic,
            "sources": sources,
            "started": asyncio.get_event_loop().time()
        })
        
        await ws_report_thinking("researcher", f"Will search {len(sources)} sources: {', '.join(sources)}")
        
        # Research from multiple sources in parallel
        research_tasks = []
        for source in sources:
            if source in self.search_engines:
                await ws_report_thinking("researcher", f"Starting {source} search...")
                task = asyncio.create_task(
                    self.search_engines[source](topic, depth)
                )
                research_tasks.append((source, task))
            else:
                await ws_report_thinking("researcher", f"Skipping unknown source: {source}")
                
        # Wait for all research to complete
        results = {}
        completed_sources = []
        
        for source, task in research_tasks:
            try:
                await ws_report_thinking("researcher", f"Waiting for {source} results...")
                results[source] = await task
                completed_sources.append(source)
                await ws_report_thinking("researcher", f"✓ {source} search completed")
            except Exception as e:
                results[source] = {"error": str(e)}
                await ws_report_thinking("researcher", f"✗ {source} search failed: {str(e)}")
                self.logger.error(f"Research failed for {source}: {e}")
                
        await ws_report_thinking("researcher", f"All searches complete. Synthesizing results from {len(completed_sources)} sources...")
        
        # Combine and analyze results
        final_result = await self._synthesize_research(topic, results)
        
        # Update workspace with final results
        await self.update_workspace(f"research_results_{topic}", final_result)
        
        # Complete task reporting
        summary = f"Found {final_result.get('total_results', 0)} results from {len(completed_sources)} sources"
        await ws_report_task("researcher", f"Research: {topic}", "completed", summary)
        await ws_report_status("researcher", "idle")
        
        self.logger.info(f"Research completed for: {topic}")
        return final_result
        
    async def _handle_search_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle quick search requests with reporting"""
        query = content.get("query")
        source = content.get("source", "web")
        
        if not query:
            await ws_report_error("researcher", "No search query provided")
            return {"error": "No search query provided"}
            
        if source not in self.search_engines:
            error_msg = f"Unknown search source: {source}"
            await ws_report_error("researcher", error_msg)
            return {"error": error_msg}
            
        # Report search activity
        await ws_report_status("researcher", "searching")
        await ws_report_task("researcher", f"Quick search: {query}", "started")
        await ws_report_thinking("researcher", f"Performing quick {source} search for: {query}")
        
        try:
            result = await self.search_engines[source](query, "quick")
            
            await ws_report_task("researcher", f"Quick search: {query}", "completed", f"Found results from {source}")
            await ws_report_status("researcher", "idle")
            
            return {"query": query, "source": source, "result": result}
            
        except Exception as e:
            await ws_report_error("researcher", f"Search failed: {str(e)}")
            await ws_report_status("researcher", "error")
            raise
        
    async def _handle_analysis_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data analysis requests with reporting"""
        data = content.get("data")
        analysis_type = content.get("type", "summary")
        
        if not data:
            await ws_report_error("researcher", "No data provided for analysis")
            return {"error": "No data provided for analysis"}
            
        # Report analysis activity
        await ws_report_status("researcher", "analyzing")
        await ws_report_task("researcher", f"Analysis: {analysis_type}", "started")
        await ws_report_thinking("researcher", f"Starting {analysis_type} analysis...")
        
        try:
            # Simulate async analysis processing
            await asyncio.sleep(0.5)  # Simulate processing time
            await ws_report_thinking("researcher", f"Processing data for {analysis_type} analysis...")
            
            if analysis_type == "summary":
                result = await self._summarize_data(data)
            elif analysis_type == "trends":
                result = await self._analyze_trends(data)
            else:
                error_msg = f"Unknown analysis type: {analysis_type}"
                await ws_report_error("researcher", error_msg)
                return {"error": error_msg}
                
            await ws_report_task("researcher", f"Analysis: {analysis_type}", "completed", "Analysis complete")
            await ws_report_status("researcher", "idle")
            
            return result
            
        except Exception as e:
            await ws_report_error("researcher", f"Analysis failed: {str(e)}")
            await ws_report_status("researcher", "error")
            raise
            
    async def _web_search(self, query: str, depth: str) -> Dict[str, Any]:
        """Simulate web search with realistic async behavior"""
        await ws_report_thinking("researcher", f"Connecting to web search APIs...")
        await asyncio.sleep(1.2)  # Simulate network delay
        
        await ws_report_thinking("researcher", f"Processing web search results for: {query}")
        await asyncio.sleep(0.5)  # Simulate processing
        
        # In real implementation, use aiohttp to call search APIs
        result_count = 3 if depth == "deep" else 2
        results = []
        
        for i in range(result_count):
            results.append({
                "title": f"Web Result {i+1} for {query}",
                "url": f"https://example.com/result/{i+1}",
                "snippet": f"This is web search result #{i+1} about {query}. Contains relevant information...",
                "relevance": 0.9 - (i * 0.1),
                "source": "web_api"
            })
        
        await ws_report_thinking("researcher", f"Found {len(results)} web results")
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "search_time": 1.7,
            "source": "web",
            "depth": depth
        }
        
    async def _knowledge_search(self, query: str, depth: str) -> Dict[str, Any]:
        """Search internal knowledge base with reporting"""
        await ws_report_thinking("researcher", f"Searching internal knowledge base...")
        await asyncio.sleep(0.6)  # Simulate knowledge base query
        
        await ws_report_thinking("researcher", f"Processing knowledge base results...")
        await asyncio.sleep(0.3)
        
        confidence = 0.9 if depth == "deep" else 0.8
        
        return {
            "query": query,
            "knowledge_results": [
                {
                    "topic": query,
                    "summary": f"Internal knowledge about {query}: This topic involves multiple aspects and considerations...",
                    "confidence": confidence,
                    "sources": ["internal_kb", "previous_research", "expert_annotations"],
                    "related_topics": [f"{query}_related_1", f"{query}_related_2"]
                }
            ],
            "source": "knowledge",
            "depth": depth
        }
        
    async def _data_search(self, query: str, depth: str) -> Dict[str, Any]:
        """Search structured data sources with reporting"""
        await ws_report_thinking("researcher", f"Querying structured data sources...")
        await asyncio.sleep(0.4)  # Simulate database query
        
        match_count = 8 if depth == "deep" else 5
        
        return {
            "query": query,
            "data_results": [
                {
                    "dataset": "research_database",
                    "matches": match_count,
                    "relevance": 0.75,
                    "sample_data": f"Structured data sample related to {query}",
                    "metadata": {
                        "last_updated": "2024-01-15",
                        "record_count": match_count * 100
                    }
                }
            ],
            "source": "data",
            "depth": depth
        }
        
    async def _synthesize_research(self, topic: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize research results from multiple sources with detailed reporting"""
        await ws_report_thinking("researcher", "Synthesizing research results...")
        await asyncio.sleep(0.8)  # Simulate analysis time
        
        # Count total results and analyze sources
        total_results = 0
        sources_used = []
        source_quality = {}
        
        for source, result in results.items():
            if "error" not in result:
                sources_used.append(source)
                
                # Count results from each source
                result_count = 0
                if "results" in result:
                    result_count = len(result["results"])
                elif "knowledge_results" in result:
                    result_count = len(result["knowledge_results"])
                elif "data_results" in result:
                    result_count = len(result["data_results"])
                
                total_results += result_count
                source_quality[source] = {
                    "result_count": result_count,
                    "quality": "high" if result_count > 2 else "medium"
                }
            else:
                await ws_report_thinking("researcher", f"Excluding {source} due to errors")
        
        await ws_report_thinking("researcher", f"Synthesis complete: {total_results} results from {len(sources_used)} sources")
        
        # Generate insights and recommendations
        insights = [
            f"Research on '{topic}' yielded {total_results} relevant results",
            f"Most reliable sources: {', '.join([s for s, q in source_quality.items() if q['quality'] == 'high'])}",
            f"Coverage across {len(sources_used)} different source types provides comprehensive view"
        ]
        
        recommendations = [
            f"Based on research, '{topic}' shows significant relevance across multiple sources",
            f"Recommend focusing on {sources_used[0] if sources_used else 'web'} source for deeper investigation",
            f"Consider expanding research to related topics for broader context"
        ]
        
        return {
            "topic": topic,
            "summary": f"Comprehensive research synthesis for '{topic}' across {len(sources_used)} sources",
            "sources_used": sources_used,
            "source_quality": source_quality,
            "total_results": total_results,
            "detailed_results": results,
            "confidence": min(0.9, 0.6 + (len(sources_used) * 0.1)),
            "insights": insights,
            "recommendations": recommendations,
            "research_metadata": {
                "sources_attempted": len(results),
                "sources_successful": len(sources_used),
                "synthesis_timestamp": asyncio.get_event_loop().time()
            }
        }
        
    async def _summarize_data(self, data: Any) -> Dict[str, Any]:
        """Summarize provided data with reporting"""
        await ws_report_thinking("researcher", "Analyzing data structure and content...")
        await asyncio.sleep(0.3)
        
        data_str = str(data)
        data_type = type(data).__name__
        
        return {
            "summary": f"Data summary ({data_type}): {data_str[:150]}{'...' if len(data_str) > 150 else ''}",
            "type": data_type,
            "length": len(data_str),
            "analysis": "summary_complete",
            "key_characteristics": [
                f"Data type: {data_type}",
                f"Content length: {len(data_str)} characters",
                f"Complexity: {'high' if len(data_str) > 500 else 'medium' if len(data_str) > 100 else 'low'}"
            ]
        }
        
    async def _analyze_trends(self, data: Any) -> Dict[str, Any]:
        """Analyze trends in data with reporting"""
        await ws_report_thinking("researcher", "Identifying patterns and trends...")
        await asyncio.sleep(0.4)
        
        # Simulate trend analysis
        trends = ["upward_trend", "seasonal_pattern", "anomaly_detected"]
        
        return {
            "trends": trends,
            "analysis": "trends_identified",
            "confidence": 0.78,
            "trend_details": {
                trend: f"Analysis details for {trend}" for trend in trends
            },
            "recommendations": [
                "Monitor upward trend continuation",
                "Investigate seasonal pattern causes",
                "Examine anomaly for significance"
            ]
        }

    async def send_message(self, recipient: str, role: str, intent: str, content: str):
        """Send message with WebSocket reporting"""
        # Report message being sent
        await ws_report_message("researcher", recipient, role, intent, str(content)[:100], "sent")
        await ws_report_thinking("researcher", f"Sending {intent} message to {recipient}")
        
        # Use parent class send logic
        return await super().send_message(recipient, role, intent, content)

    async def shutdown(self):
        """Shutdown agent with reporting"""
        await ws_report_thinking("researcher", "Shutting down researcher agent...")
        await ws_report_status("researcher", "offline")
        await super().shutdown()

# Example usage and testing
async def test_researcher_agent():
    """Test the async researcher agent with WebSocket integration"""
    print("🧪 Testing AINX Async Researcher Agent")
    
    try:
        from async_message_bus import AsyncMessageBus
        from async_workspace import AsyncWorkspace
        
        # Create test environment
        workspace = AsyncWorkspace()
        message_bus = AsyncMessageBus()
        
        # Create and initialize agent
        researcher = AsyncResearcherAgent()
        await researcher.initialize(workspace, message_bus)
        
        print("✅ Agent initialized successfully")
        
        # Test comprehensive research request
        test_message = {
            "sender": "human",
            "recipient": "researcher", 
            "role": "user",
            "intent": "research",
            "content": {
                "topic": "artificial intelligence trends 2024",
                "sources": ["web", "knowledge", "data"],
                "depth": "medium"
            }
        }
        
        print("🔍 Starting research test...")
        result = await researcher.process_message(test_message)
        
        print("📊 Research Result Summary:")
        print(f"  Topic: {result.get('topic', 'N/A')}")
        print(f"  Sources: {', '.join(result.get('sources_used', []))}")
        print(f"  Total Results: {result.get('total_results', 0)}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
        
        # Test quick search
        search_message = {
            "sender": "planner",
            "recipient": "researcher",
            "role": "agent", 
            "intent": "search",
            "content": {
                "query": "machine learning frameworks",
                "source": "web"
            }
        }
        
        print("\n🔎 Starting quick search test...")
        search_result = await researcher.process_message(search_message)
        print(f"  Query: {search_result.get('query', 'N/A')}")
        print(f"  Source: {search_result.get('source', 'N/A')}")
        
        await researcher.shutdown()
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run test
    asyncio.run(test_researcher_agent())