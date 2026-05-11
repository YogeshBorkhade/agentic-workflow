"""
LangGraph orchestration for multi-agent workflow.
Wires agents together into a coordinated flow with retry logic.
"""

from langgraph.graph import StateGraph, END
from typing import Literal

from src.orchestration.state import ResearchState
from src.agents import ClarityAgent, ResearchAgent, ValidatorAgent, SynthesisAgent
from src.hitl import create_hitl_node, HITLSystem

from src.data import get_data_source
from src.utils import logger


def should_retry_research(state: ResearchState) -> Literal["research", "synthesis"]:
    """
    Decide whether to retry research or proceed to synthesis.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node: "research" for retry, "synthesis" to finish
    """
    validation_result = state.get("validation_result", "insufficient")
    attempts = state.get("validation_attempts", 0)
    max_attempts = 2
    
    # If validation passed OR we've tried enough times, go to synthesis
    if validation_result == "sufficient" or attempts >= max_attempts:
        logger.info(
            "Routing to synthesis",
            validation_result=validation_result,
            attempts=attempts
        )
        return "synthesis"
    
    # Otherwise, retry research
    logger.info(
        "Routing to research (retry)",
        validation_result=validation_result,
        attempts=attempts
    )
    return "research"


async def create_research_graph():
    """
    Create the complete research agent workflow graph.
    
    Flow:
    START → Clarity → Research → Validator → Decision
                         ↑           ↓
                         └─(retry)───┘
                                     ↓
                                 Synthesis → END
    
    Returns:
        Compiled LangGraph workflow
    """
    logger.info("Creating research graph with all agents")
    
    # Get data source (mock or real)
    data_source = await get_data_source()
    
    # Initialize all agents
    clarity_agent = ClarityAgent(data_source)
    research_agent = ResearchAgent(data_source)
    validator_agent = ValidatorAgent(data_source)
    synthesis_agent = SynthesisAgent(data_source)
    
    #initialize HITL system (for potential human intervention in validation)
    hitl = HITLSystem()
    
     
    # Wrap agents with evaluation
    clarity_with_eval = wrap_with_evaluation(clarity_agent, evaluation_pipeline, metrics_tracker)
    research_with_eval = wrap_with_evaluation(research_agent, evaluation_pipeline, metrics_tracker)
    validator_with_eval = wrap_with_evaluation(validator_agent, evaluation_pipeline, metrics_tracker)
    synthesis_with_eval = wrap_with_evaluation(synthesis_agent, evaluation_pipeline, metrics_tracker)
   

    # Create graph
    workflow = StateGraph(ResearchState)
    
    # Add nodes (agents)
    workflow.add_node("clarity", clarity_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("validator", validator_agent)
    workflow.add_node("hitl_checkpoint", create_hitl_node(hitl)) 
    workflow.add_node("synthesis", synthesis_agent)
    
    # Define edges (flow)
    workflow.set_entry_point("clarity")
    workflow.add_edge("clarity", "research")
    workflow.add_edge("research", "validator")
    
    # Conditional edge: validator decides whether to retry or finish
    workflow.add_conditional_edges(
        "validator",
        should_retry_research,
        {
            "research": "research",  # Retry research
            "synthesis": "hitl_checkpoint"  # go to HITL checkpoint before synthesis for final validation
        }
    )
    
    # HITL -> synthesis
    workflow.add_edge("hitl_checkpoint", "synthesis")
    
    # End after synthesis
    workflow.add_edge("synthesis", END)
    
    # Compile graph
    graph = workflow.compile()
    
    logger.info("Research graph created with conditional retry loop")
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
        validation_attempts=final_state.get("validation_attempts"),
        agent_trace=final_state.get("agent_trace")
    )
    
    return final_state


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("Testing Complete LangGraph Workflow...\n")
        
        # Test queries
        test_queries = [
            "Tell me about Tesla",
            "What are Apple's main competitors?",
        ]
        
        for query in test_queries:
            print("=" * 70)
            print(f"Query: {query}")
            print("=" * 70)
            
            # Run workflow
            result = await run_research(query)
            
            # Show results
            print(f"\n📊 Results:")
            print(f"   Company: {result['company_name']}")
            print(f"   Confidence: {result['confidence_score']}")
            print(f"   Quality: {result['quality_score']}")
            print(f"   Validation: {result['validation_result']}")
            print(f"   Attempts: {result['validation_attempts']}")
            print(f"   Status: {result['status']}")
            print(f"\n🔀 Agent Flow: {' → '.join(result['agent_trace'])}")
            
            print(f"\n💬 Final Response:")
            print("-" * 70)
            print(result['final_response'])
            print("-" * 70)
            print()
        
        print("\n✅ Complete workflow working!")
    
    asyncio.run(test())