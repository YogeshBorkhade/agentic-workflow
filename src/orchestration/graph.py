"""
LangGraph orchestration for multi-agent workflow.
Wires agents together into a coordinated flow.
"""

from langgraph.graph import StateGraph, END
from typing import Literal

from src.orchestration.state import ResearchState
from src.agents import ClarityAgent
from src.data import get_data_source
from src.utils import logger


async def create_research_graph():
    """
    Create the research agent workflow graph.
    
    Flow:
    START → Clarity → (more agents later) → END
    
    Returns:
        Compiled LangGraph workflow
    """
    logger.info("Creating research graph")
    
    # Get data source (mock or real)
    data_source = await get_data_source()
    
    # Initialize agents
    clarity_agent = ClarityAgent(data_source)
    
    # Create graph
    workflow = StateGraph(ResearchState)
    
    # Add nodes (agents)
    workflow.add_node("clarity", clarity_agent)
    
    # Define edges (flow)
    workflow.set_entry_point("clarity")
    
    # For now, just end after clarity
    # Later we'll add: clarity → research → validator → synthesis
    workflow.add_edge("clarity", END)
    
    # Compile graph
    graph = workflow.compile()
    
    logger.info("Research graph created")
    return graph


async def run_research(query: str, user_id: str | None = None) -> ResearchState:
    """
    Run the complete research workflow.
    
    Args:
        query: User's question
        user_id: Optional user identifier
        
    Returns:
        Final state after all agents complete
    """
    from src.orchestration.state import create_initial_state
    
    logger.info(f"Starting research workflow", query=query)
    
    # Create initial state
    initial_state = create_initial_state(query, user_id)
    
    # Create and run graph
    graph = await create_research_graph()
    final_state = await graph.ainvoke(initial_state)
    
    logger.info(
        f"Research workflow completed",
        request_id=final_state.get("request_id"),
        status=final_state.get("status"),
        agent_trace=final_state.get("agent_trace")
    )
    
    return final_state


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("Testing LangGraph Orchestration...\n")
        
        # Test query
        query = "Tell me about Tesla"
        
        print(f"Query: {query}\n")
        print("Running workflow...")
        print("-" * 50)
        
        # Run workflow
        result = await run_research(query)
        
        print("-" * 50)
        print("\n✅ Workflow Complete!\n")
        
        # Show results
        print("Results:")
        print(f"  Request ID: {result['request_id']}")
        print(f"  Company: {result['company_name']}")
        print(f"  Status: {result['clarity_status']}")
        print(f"  Intent: {result['intent']}")
        print(f"  Agent Trace: {' → '.join(result['agent_trace'])}")
        print(f"  Overall Status: {result['status']}\n")
        
        print("✅ LangGraph working!")
    
    asyncio.run(test())