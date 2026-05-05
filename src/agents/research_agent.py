"""
Research Agent - Gathers comprehensive company information.

Responsibilities:
- Takes company name from state
- Calls data source for company data
- Extracts structured information (CEO, revenue, competitors, etc.)
- Returns research findings with confidence score
"""

from typing import Dict, Any

from src.agents.base import BaseAgent
from src.orchestration.state import ResearchState
from src.utils import logger


class ResearchAgent(BaseAgent):
    """
    Research Agent gathers company information.
    
    Inputs (from state):
    - company_name: Company to research
    - current_query: Original user query for context
    
    Outputs (to state):
    - research_findings: Structured company data
    - data_sources: List of sources used
    - confidence_score: Quality score (0-10)
    - research_strategy: Description of approach
    """
    
    async def process(self, state: ResearchState) -> Dict[str, Any]:
        """
        Gather company research data.
        
        Args:
            state: Current research state
            
        Returns:
            Partial state update with research findings
        """
        company_name = self._get_company_name(state)
        query = self._get_query(state)
        
        if not company_name:
            logger.warning("ResearchAgent: No company name in state")
            return {
                "research_findings": {},
                "confidence_score": 0.0,
                "data_sources": [],
                "research_strategy": "skipped - no company identified"
            }
        
        logger.info(
            "ResearchAgent processing",
            company_name=company_name,
            query=query[:50]
        )
        
        # Build research query
        research_query = self._build_research_query(company_name, query)
        
        # Call data source
        try:
            response = await self.data_source.get_llm_response(
                agent_type="research",
                query=research_query,
                context={
                    "company_name": company_name,
                    "original_query": query,
                    "request_id": state.get("request_id")
                }
            )
            
            # Parse response
            findings = self._parse_research_response(response, company_name)
            
            # Calculate confidence
            confidence = self._calculate_confidence(findings)
            
            logger.info(
                "ResearchAgent completed",
                company_name=company_name,
                confidence=confidence,
                fields_found=len(findings)
            )
            
            return {
                "research_findings": findings,
                "confidence_score": confidence,
                "data_sources": ["llm_research"],
                "research_strategy": f"Direct research for {company_name}"
            }
            
        except Exception as e:
            logger.error(
                "ResearchAgent failed",
                company_name=company_name,
                error=str(e)
            )
            
            return {
                "research_findings": {},
                "confidence_score": 0.0,
                "data_sources": [],
                "research_strategy": f"failed - {str(e)}",
                "error": f"Research failed: {str(e)}"
            }
    
    def _build_research_query(self, company_name: str, original_query: str) -> str:
        """
        Build focused research query.
        
        Args:
            company_name: Company to research
            original_query: User's original question
            
        Returns:
            Optimized research query
        """
        # Extract intent from original query
        query_lower = original_query.lower()
        
        if "competitor" in query_lower or "vs" in query_lower:
            focus = "competitors and market position"
        elif "revenue" in query_lower or "financial" in query_lower:
            focus = "financial information"
        elif "product" in query_lower:
            focus = "products and services"
        else:
            focus = "general information"
        
        return f"Provide comprehensive information about {company_name}, focusing on {focus}"
    
    def _parse_research_response(
        self, 
        response: Dict[str, Any] | str,
        company_name: str
    ) -> Dict[str, Any]:
        """
        Parse LLM response into structured findings.
        
        Args:
            response: LLM response (dict or text)
            company_name: Company being researched
            
        Returns:
            Structured research findings
        """
        # If response is already structured
        if isinstance(response, dict):
            # Check if response has 'findings' key (mock format)
            if "findings" in response:
                # Extract from nested findings
                data = response["findings"]
            else:
                # Direct format
                data = response
            
            # Extract relevant fields
            findings = {
                "company_name": data.get("company_name", company_name),
                "ceo": data.get("ceo"),
                "founded": data.get("founded"),
                "headquarters": data.get("headquarters"),
                "industry": data.get("industry"),
                "revenue": data.get("revenue"),
                "employees": data.get("employees"),
                "products": data.get("products", []),
                "competitors": data.get("competitors", []),
                "description": data.get("description"),
            }
            
            # Remove None values
            findings = {k: v for k, v in findings.items() if v is not None}
            
            return findings
        
        # If response is text, try to extract key information
        logger.warning("ResearchAgent: Received text response, attempting extraction")
        
        # Basic text parsing (fallback)
        # In production, you'd use more sophisticated extraction
        findings = {
            "company_name": company_name,
            "raw_text": str(response)[:500]  # First 500 chars
        }
        
        return findings
    
    def _calculate_confidence(self, findings: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on data completeness.
        
        Args:
            findings: Research findings
            
        Returns:
            Confidence score (0-10)
        """
        if not findings or "raw_text" in findings:
            # Only raw text, low confidence
            return 3.0
        
        # Key fields to check
        key_fields = ["ceo", "revenue", "industry", "description"]
        optional_fields = ["founded", "headquarters", "employees", "products", "competitors"]
        
        # Count present fields
        key_present = sum(1 for field in key_fields if findings.get(field))
        optional_present = sum(1 for field in optional_fields if findings.get(field))
        
        # Calculate score (0-10)
        key_score = (key_present / len(key_fields)) * 6  # Up to 6 points
        optional_score = (optional_present / len(optional_fields)) * 4  # Up to 4 points
        
        confidence = key_score + optional_score
        
        return round(confidence, 1)


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from src.orchestration import create_initial_state
    from src.data import get_data_source
    from src.agents import ClarityAgent
    
    async def test():
        print("Testing ResearchAgent...\n")
        
        # Create data source
        data_source = await get_data_source()
        
        # Create agents
        clarity = ClarityAgent(data_source)
        research = ResearchAgent(data_source)
        
        # Test query
        query = "Tell me about Tesla"
        state = create_initial_state(query)
        
        print(f"Query: {query}\n")
        
        # Step 1: Clarity
        print("Step 1: ClarityAgent...")
        clarity_updates = await clarity(state)
        state.update(clarity_updates)
        print(f"  Company: {state['company_name']}\n")
        
        # Step 2: Research
        print("Step 2: ResearchAgent...")
        research_updates = await research(state)
        state.update(research_updates)
        
        print(f"  Confidence: {state['confidence_score']}")
        print(f"  Findings: {len(state['research_findings'])} fields")
        print(f"  Fields: {list(state['research_findings'].keys())}")
        
        # Show some data
        findings = state['research_findings']
        if 'ceo' in findings:
            print(f"\n  CEO: {findings['ceo']}")
        if 'revenue' in findings:
            print(f"  Revenue: {findings['revenue']}")
        if 'competitors' in findings:
            print(f"  Competitors: {findings['competitors']}")
        
        print(f"\n✅ ResearchAgent working!")
    
    asyncio.run(test())