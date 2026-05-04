"""
Base agent class with common patterns.
All agents inherit from this to get logging, error handling, etc.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from src.orchestration.state import ResearchState, add_agent_trace
from src.data import DataSource
from src.utils import logger, add_context


class BaseAgent(ABC):
    """
    Base class for all agents.
    
    Provides:
    - Common logging patterns
    - State update helpers
    - Error handling
    - Agent name tracking
    """
    
    def __init__(self, data_source: DataSource):
        """
        Initialize agent.
        
        Args:
            data_source: Data source for LLM calls
        """
        self.data_source = data_source
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def process(self, state: ResearchState) -> Dict[str, Any]:
        """
        Process the state and return updates.
        
        Args:
            state: Current workflow state
            
        Returns:
            Dict with partial state updates (only changed fields)
        """
        pass
    
    async def __call__(self, state: ResearchState) -> Dict[str, Any]:
        """
        Execute agent with logging and error handling.
        
        This is called by LangGraph.
        """
        logger.bind(**add_context(agent=self.name)).info(
            f"{self.name} starting",
            request_id=state.get("request_id")
        )
        
        try:
            # Process state
            updates = await self.process(state)
            
            # Add this agent to trace
            trace_update = add_agent_trace(state, self.name)
            updates.update(trace_update)
            
            logger.bind(**add_context(agent=self.name)).info(
                f"{self.name} completed",
                updates=list(updates.keys())
            )
            
            return updates
            
        except Exception as e:
            logger.bind(**add_context(agent=self.name)).error(
                f"{self.name} failed",
                error=str(e)
            )
            
            # Return error state
            return {
                "error": f"{self.name} failed: {str(e)}",
                "status": "failed",
                **add_agent_trace(state, f"{self.name}:error")
            }
    
    def _get_query(self, state: ResearchState) -> str:
        """Extract current query from state."""
        return state.get("current_query", "")
    
    def _get_company_name(self, state: ResearchState) -> str | None:
        """Extract company name from state."""
        return state.get("company_name")
    
    def _get_findings(self, state: ResearchState) -> Dict[str, Any]:
        """Extract research findings from state."""
        return state.get("research_findings", {})


# Example usage
if __name__ == "__main__":
    import asyncio
    from src.orchestration import create_initial_state
    from src.data import get_data_source
    
    # Example agent implementation
    class ExampleAgent(BaseAgent):
        async def process(self, state: ResearchState) -> Dict[str, Any]:
            """Simple example agent."""
            query = self._get_query(state)
            
            # Simulate some work
            return {
                "company_name": "TestCorp",
                "clarity_status": "clear"
            }
    
    async def test():
        print("Testing BaseAgent...\n")
        
        # Create data source and agent
        data_source = await get_data_source()
        agent = ExampleAgent(data_source)
        
        # Create initial state
        state = create_initial_state("Tell me about Tesla")
        
        print(f"✅ Agent name: {agent.name}")
        print(f"   Query: {agent._get_query(state)}\n")
        
        # Process state
        updates = await agent(state)
        
        print(f"✅ Updates returned: {updates}")
        print(f"   Trace: {updates.get('agent_trace')}\n")
        
        print("✅ BaseAgent working!")
    
    asyncio.run(test())