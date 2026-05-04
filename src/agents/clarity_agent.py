"""
Clarity Agent - Extracts company name and intent from user queries.

Responsibilities:
- Identify company/entity names
- Classify user intent
- Detect if query is clear or needs clarification
"""

from typing import Dict, Any

from src.agents.base import BaseAgent
from src.orchestration.state import ResearchState
from src.utils import logger


class ClarityAgent(BaseAgent):
    """
    Clarity Agent extracts structured information from user queries.
    
    Outputs:
    - company_name: Extracted company name
    - entities: List of all entities mentioned
    - intent: User's intention (company_info, competitor_analysis, etc.)
    - clarity_status: Whether query is clear enough to proceed
    """
    
    async def process(self, state: ResearchState) -> Dict[str, Any]:
        """
        Extract company name and intent from query.
        
        Args:
            state: Current research state
            
        Returns:
            Partial state update with clarity information
        """
        query = self._get_query(state)
        
        logger.info(
            "ClarityAgent processing",
            query=query[:100]  # Log first 100 chars
        )
        
        # Call LLM to extract information
        response = await self.data_source.get_llm_response(
            agent_type="clarity",
            query=query,
            context={"request_id": state.get("request_id")}
        )
        
        # Parse response
        if isinstance(response, dict):
            # Structured response from LLM
            company_name = response.get("company_name")
            clarity_status = response.get("clarity_status", "clear")
            entities = response.get("entities", [])
            intent = response.get("intent", "general_information")
        else:
            # Fallback if response is just text
            logger.warning("ClarityAgent: Received text response, expected dict")
            company_name = self._extract_company_from_text(query, str(response))
            clarity_status = "clear" if company_name else "unclear"
            entities = [company_name] if company_name else []
            intent = "general_information"
        
        logger.info(
            "ClarityAgent completed",
            company_name=company_name,
            clarity_status=clarity_status,
            intent=intent
        )
        
        return {
            "company_name": company_name,
            "clarity_status": clarity_status,
            "entities": entities,
            "intent": intent,
        }
    
    def _extract_company_from_text(self, query: str, response: str) -> str | None:
        """
        Fallback: Extract company name from query using simple heuristics.
        
        This is a backup if LLM doesn't return structured data.
        """
        # Simple heuristic: look for capitalized words
        # In production, you'd use NER or better LLM prompting
        query_lower = query.lower()
        
        # Common company keywords
        known_companies = [
            "tesla", "apple", "microsoft", "google", "amazon",
            "meta", "netflix", "nvidia", "intel", "amd"
        ]
        
        for company in known_companies:
            if company in query_lower:
                return company.capitalize()
        
        return None


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from src.orchestration import create_initial_state
    from src.data import get_data_source
    
    async def test():
        print("Testing ClarityAgent...\n")
        
        # Create data source
        data_source = await get_data_source()
        
        # Create agent
        agent = ClarityAgent(data_source)
        
        # Test queries
        test_queries = [
            "Tell me about Tesla",
            "What are Apple's competitors?",
            "Microsoft revenue",
        ]
        
        for query in test_queries:
            print(f"Query: {query}")
            
            # Create state
            state = create_initial_state(query)
            
            # Process
            updates = await agent(state)
            
            print(f"  Company: {updates.get('company_name')}")
            print(f"  Status: {updates.get('clarity_status')}")
            print(f"  Intent: {updates.get('intent')}\n")
        
        print("✅ ClarityAgent working!")
    
    asyncio.run(test())