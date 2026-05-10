"""
LangGraph orchestration for multi-agent workflow.
Wires agents together into a coordinated flow with retry logic.
"""

from langgraph.graph import StateGraph, END
from typing import Literal

from src.orchestration.state import ResearchState
from src.agents import ClarityAgent, ResearchAgent, ValidatorAgent, SynthesisAgent
from src.hitl import create_hitl_node, HITLSystem

from src.evaluation import EvaluationPipeline, MetricsTracker

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


async def create_research_graph(metrics_tracker: MetricsTracker):
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
    
    evaluation_pipeline = EvaluationPipeline()
    
    # Wrap agents with evaluation
    clarity_with_eval = wrap_with_evaluation(clarity_agent, evaluation_pipeline, metrics_tracker)
    research_with_eval = wrap_with_evaluation(research_agent, evaluation_pipeline, metrics_tracker)
    validator_with_eval = wrap_with_evaluation(validator_agent, evaluation_pipeline, metrics_tracker)
    synthesis_with_eval = wrap_with_evaluation(synthesis_agent, evaluation_pipeline, metrics_tracker)
   

    # Create graph
    workflow = StateGraph(ResearchState)
    
    # Add nodes (agents)
    workflow.add_node("clarity", clarity_with_eval)
    workflow.add_node("research", research_with_eval)
    workflow.add_node("validator", validator_with_eval)
    workflow.add_node("hitl_checkpoint", create_hitl_node(hitl)) 
    workflow.add_node("synthesis", synthesis_with_eval)
    
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



def wrap_with_evaluation(agent, evaluation_pipeline, metrics_tracker):
    """
    Wrap agent with automatic evaluation & metrics tracking
    
    This decorator:
    1. Tracks performance (latency, tokens)
    2. Evaluates output quality (LLM judge + self-assessment)
    3. Flags low-quality outputs for review
    """
    import time
    from functools import wraps
    
    @wraps(agent)
    async def wrapper(state: ResearchState):
        request_id = state.get("request_id", "unknown")
        agent_name = agent.__class__.__name__
        
        # Start tracking
        start_time = time.time()
        
        # Run agent
        result = await agent(state)
        
        # Calculate metrics
        latency_ms = (time.time() - start_time) * 1000
        tokens = estimate_tokens(result)  # Simple estimation
        
        # Track performance
        metrics_tracker.track_agent(
            request_id=request_id,
            agent_name=agent_name,
            latency_ms=latency_ms,
            tokens=tokens
        )
        
        # Evaluate quality (only for research and synthesis)
        if agent_name in ["ResearchAgent", "SynthesisAgent"]:
            output = get_agent_output(result, agent_name)
            
            # LLM judge
            eval_result = evaluation_pipeline.llm_judge.evaluate(
                agent_name=agent_name,
                agent_output=output,
                original_query=state.get("current_query", ""),
                request_id=request_id
            )
            
            # Self-assessment
            self_result = evaluation_pipeline.self_assessor.assess(
                agent_name=agent_name,
                agent_output=output,
                sources=state.get("data_sources", []),
                request_id=request_id
            )
            
            # Flag if low quality
            if eval_result.overall_score < 5.0 or self_result.needs_review:
                result["needs_review"] = True
                result["eval_score"] = eval_result.overall_score
                logger.warning(
                    f"{agent_name} output flagged for review",
                    score=eval_result.overall_score,
                    confidence=self_result.overall_score
                )
        
        return result
    
    return wrapper


def estimate_tokens(state: dict) -> int:
    """Rough token estimation (4 chars ≈ 1 token)"""
    text = str(state)
    return len(text) // 4


def get_agent_output(state: dict, agent_name: str) -> str:
    """Extract relevant output from state based on agent"""
    if agent_name == "ResearchAgent":
        return str(state.get("research_findings", ""))
    elif agent_name == "SynthesisAgent":
        return state.get("final_response", "")
    return ""



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
    
    metrics_tracker = MetricsTracker()
    
    logger.info(f"Starting research workflow", query=query)
    
    # Create initial state
    initial_state = create_initial_state(query, user_id)
    request_id = initial_state["request_id"]
    
    metrics_tracker.start_request(request_id)
    
    # Create and run graph
    graph = await create_research_graph(metrics_tracker)
    
    # Start metrics tracking
    # graph.evaluation_pipeline.metrics_tracker.start_request(request_id)
    
    # Run workflow
    final_state = await graph.ainvoke(initial_state)
    
    # Complete metrics
    success = final_state.get("status") == "completed"
    retries = final_state.get("validation_attempts", 0)
    
    metrics = metrics_tracker.end_request(
        request_id=request_id,
        success=success,
        retry_count=retries
    )
    
    # Log final metrics
    logger.info(
        f"Research workflow completed",
        request_id=request_id,
        status=final_state.get("status"),
        validation_attempts=retries,
        agent_trace=final_state.get("agent_trace"),
        latency_ms=metrics.total_latency_ms,
        cost=metrics.estimated_cost,
        success=success
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