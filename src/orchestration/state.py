"""
State definitions for the research agent workflow.
Defines the shared state that flows through all agents.
"""

from typing import TypedDict, Annotated, Sequence
from dataclasses import dataclass
from datetime import datetime


class ResearchState(TypedDict):
    """
    Shared state for the research workflow.
    
    This state flows through all agents automatically.
    Each agent reads what it needs and returns partial updates.
    LangGraph merges updates automatically.
    
    Think of this as a shared whiteboard that all agents can read/write.
    """
    
    # ============================================================================
    # INPUT (from user)
    # ============================================================================
    
    messages: list[dict]
    """
    Conversation history.
    Format: [{"role": "user", "content": "..."},
             {"role": "assistant", "content": "..."}, ...]
    """
    
    current_query: str
    """Current user query being processed."""
    
    user_id: str | None
    """Optional user ID for personalization."""
    
    # ============================================================================
    # CLARITY AGENT OUTPUT
    # ============================================================================
    
    company_name: str | None
    """Extracted company name from query (e.g., "Tesla")."""
    
    clarity_status: str
    """
    Status of query clarity.
    Values: "clear" | "unclear" | "needs_clarification"
    """
    
    entities: list[str]
    """Extracted entities from query (companies, people, products)."""
    
    intent: str
    """
    User intent classification.
    Examples: "company_info", "competitor_analysis", "financial_data"
    """
    
    # ============================================================================
    # RESEARCH AGENT OUTPUT
    # ============================================================================
    
    research_findings: dict
    """
    Research results with company data.
    Structure: {
        "company_name": "Tesla",
        "ceo": "Elon Musk",
        "revenue": "$96.8B",
        "competitors": ["BYD", "Ford"],
        ...
    }
    """
    
    data_sources: list[str]
    """List of data sources used (for transparency)."""
    
    confidence_score: float
    """
    Confidence in research quality (0-10 scale).
    < 5 = Low quality, triggers retry
    >= 5 = Acceptable
    >= 8 = High quality
    """
    
    research_strategy: str | None
    """Description of research approach used."""
    
    # ============================================================================
    # VALIDATOR AGENT OUTPUT
    # ============================================================================
    
    validation_result: str
    """
    Validation decision.
    Values: "sufficient" | "insufficient" | "needs_review"
    """
    
    validation_feedback: str | None
    """Feedback on what's missing or needs improvement."""
    
    validation_attempts: int
    """Number of validation attempts (for retry loop control)."""
    
    missing_info: list[str]
    """List of missing information items."""
    
    quality_score: float
    """Overall quality assessment (0-10 scale)."""
    
    # ============================================================================
    # SYNTHESIS AGENT OUTPUT
    # ============================================================================
    
    final_response: str | None
    """Final formatted response to user."""
    
    response_format: str
    """
    Format of response.
    Values: "text" | "markdown" | "json"
    """
    
    # ============================================================================
    # METADATA & CONTROL
    # ============================================================================
    
    request_id: str
    """Unique request ID for tracing."""
    
    started_at: datetime
    """Timestamp when request started."""
    
    agent_trace: list[str]
    """List of agents that processed this request (for debugging)."""
    
    error: str | None
    """Error message if something went wrong."""
    
    status: str
    """
    Overall workflow status.
    Values: "processing" | "completed" | "failed" | "needs_human"
    """


@dataclass
class StateUpdate:
    """
    Helper for creating partial state updates.
    
    Agents return this instead of full state.
    """
    updates: dict
    
    def to_dict(self) -> dict:
        """Convert to dict for LangGraph."""
        return self.updates


def create_initial_state(query: str, user_id: str | None = None) -> ResearchState:
    """
    Create initial state from user query.
    
    Args:
        query: User's question
        user_id: Optional user identifier
        
    Returns:
        Initial state with defaults
    """
    from uuid import uuid4
    from datetime import datetime
    
    return ResearchState(
        # Input
        messages=[{"role": "user", "content": query}],
        current_query=query,
        user_id=user_id,
        
        # Clarity outputs (to be filled)
        company_name=None,
        clarity_status="pending",
        entities=[],
        intent="unknown",
        
        # Research outputs (to be filled)
        research_findings={},
        data_sources=[],
        confidence_score=0.0,
        research_strategy=None,
        
        # Validator outputs (to be filled)
        validation_result="pending",
        validation_feedback=None,
        validation_attempts=0,
        missing_info=[],
        quality_score=0.0,
        
        # Synthesis outputs (to be filled)
        final_response=None,
        response_format="text",
        
        # Metadata
        request_id=str(uuid4())[:8],
        started_at=datetime.now(),
        agent_trace=[],
        error=None,
        status="processing",
    )


def add_agent_trace(state: ResearchState, agent_name: str) -> dict:
    """
    Add agent to trace (for tracking flow).
    
    Args:
        state: Current state
        agent_name: Name of agent to add
        
    Returns:
        Partial update with agent added to trace
    """
    trace = state.get("agent_trace", [])
    trace.append(agent_name)
    return {"agent_trace": trace}


# Example usage
if __name__ == "__main__":
    print("Testing ResearchState...\n")
    
    # Create initial state
    state = create_initial_state("Tell me about Tesla")
    
    print("✅ Initial state created:")
    print(f"   Query: {state['current_query']}")
    print(f"   Request ID: {state['request_id']}")
    print(f"   Status: {state['status']}\n")
    
    # Simulate agent updates
    print("Simulating agent updates...\n")
    
    # Clarity agent update
    clarity_update = {
        "company_name": "Tesla",
        "clarity_status": "clear",
        "entities": ["Tesla", "electric vehicles"],
        "intent": "company_info"
    }
    state.update(clarity_update)
    state.update(add_agent_trace(state, "clarity"))
    print(f"✅ After Clarity: company_name = {state['company_name']}")
    
    # Research agent update
    research_update = {
        "research_findings": {
            "ceo": "Elon Musk",
            "revenue": "$96.8B"
        },
        "confidence_score": 8.5,
        "data_sources": ["mock_data"]
    }
    state.update(research_update)
    state.update(add_agent_trace(state, "research"))
    print(f"✅ After Research: confidence = {state['confidence_score']}")
    
    # Validator agent update
    validator_update = {
        "validation_result": "sufficient",
        "quality_score": 9.0,
        "validation_attempts": 1
    }
    state.update(validator_update)
    state.update(add_agent_trace(state, "validator"))
    print(f"✅ After Validator: result = {state['validation_result']}")
    
    # Synthesis agent update
    synthesis_update = {
        "final_response": "Tesla is led by CEO Elon Musk...",
        "status": "completed"
    }
    state.update(synthesis_update)
    state.update(add_agent_trace(state, "synthesis"))
    print(f"✅ After Synthesis: status = {state['status']}")
    
    print(f"\n📊 Agent trace: {' → '.join(state['agent_trace'])}")
    print("\n✅ ResearchState working correctly!")