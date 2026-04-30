"""
Mock data server for development and demo.
Serves pre-defined responses without requiring LLM API keys.

Run with: uvicorn src.data.mock_server:app --port 8001 --reload
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.data.mock_responses import (
    get_mock_company_data,
    get_mock_llm_response,
    AVAILABLE_COMPANIES,
)


app = FastAPI(
    title="Research Assistant Mock Server",
    description="Mock data server for development without LLM API calls",
    version="1.0.0"
)


# Request/Response Models
class CompanyRequest(BaseModel):
    company_name: str


class LLMRequest(BaseModel):
    agent_type: str  # clarity, research, validator, synthesis
    query: str
    context: Optional[dict] = None


class CompanyResponse(BaseModel):
    company_name: str
    data: dict
    source: str = "mock_server"


class LLMResponse(BaseModel):
    agent_type: str
    response: dict | str
    source: str = "mock_server"


# Health check
@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Mock server is running",
        "available_companies": AVAILABLE_COMPANIES
    }


# Company data endpoint
@app.post("/company", response_model=CompanyResponse)
def get_company(request: CompanyRequest):
    """
    Get mock company data.
    
    Args:
        request: Company name
        
    Returns:
        Company data or 404 if not found
    """
    data = get_mock_company_data(request.company_name)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{request.company_name}' not found. "
                   f"Available: {', '.join(AVAILABLE_COMPANIES)}"
        )
    
    return CompanyResponse(
        company_name=request.company_name,
        data=data
    )


# LLM response endpoint
@app.post("/llm", response_model=LLMResponse)
def get_llm_response(request: LLMRequest):
    """
    Get mock LLM response for an agent.
    
    Args:
        request: Agent type and query
        
    Returns:
        Mock LLM response
    """
    valid_agents = ["clarity", "research", "validator", "synthesis"]
    
    if request.agent_type not in valid_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent_type. Must be one of: {', '.join(valid_agents)}"
        )
    
    response = get_mock_llm_response(request.agent_type, request.query)
    
    return LLMResponse(
        agent_type=request.agent_type,
        response=response
    )


# List available companies
@app.get("/companies")
def list_companies():
    """List all available mock companies."""
    return {
        "companies": AVAILABLE_COMPANIES,
        "count": len(AVAILABLE_COMPANIES)
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Mock Server on http://localhost:8001")
    print(f"📦 Available companies: {', '.join(AVAILABLE_COMPANIES)}")
    print("📖 API docs: http://localhost:8001/docs")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")