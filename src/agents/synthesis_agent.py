"""
Synthesis Agent - Creates final formatted response for user.

Responsibilities:
- Takes all research findings from state
- Formats into clear, readable response
- Adapts format based on user intent
- Includes relevant data based on query
- Returns final polished answer
"""

from typing import Dict, Any

from src.agents.base import BaseAgent
from src.orchestration.state import ResearchState
from src.utils import logger


class SynthesisAgent(BaseAgent):
    """
    Synthesis Agent creates final user-facing response.
    
    Inputs (from state):
    - research_findings: All gathered data
    - company_name: Company researched
    - current_query: Original query
    - intent: User's intent (from ClarityAgent)
    - quality_score: Validation score
    
    Outputs (to state):
    - final_response: Formatted answer for user
    - response_format: Format used (text/markdown)
    - status: "completed"
    """
    
    async def process(self, state: ResearchState) -> Dict[str, Any]:
        """
        Create final response.
        
        Args:
            state: Current research state with all data
            
        Returns:
            Partial state update with final response
        """
        findings = self._get_findings(state)
        company_name = self._get_company_name(state)
        query = self._get_query(state)
        intent = state.get("intent", "general_information")
        quality_score = state.get("quality_score", 0.0)
        
        logger.info(
            "SynthesisAgent processing",
            company_name=company_name,
            intent=intent,
            quality_score=quality_score
        )
        
        # Check if we have data to synthesize
        if not findings or not company_name:
            logger.warning("SynthesisAgent: No data to synthesize")
            return {
                "final_response": "I wasn't able to find sufficient information to answer your question.",
                "response_format": "text",
                "status": "completed"
            }
        
        # Generate response based on intent
        response = self._generate_response(
            findings=findings,
            company_name=company_name,
            query=query,
            intent=intent,
            quality_score=quality_score
        )
        
        logger.info(
            "SynthesisAgent completed",
            response_length=len(response),
            company_name=company_name
        )
        
        return {
            "final_response": response,
            "response_format": "text",
            "status": "completed"
        }
    
    def _generate_response(
        self,
        findings: Dict[str, Any],
        company_name: str,
        query: str,
        intent: str,
        quality_score: float
    ) -> str:
        """
        Generate formatted response based on intent.
        
        Args:
            findings: Research findings
            company_name: Company name
            query: Original query
            intent: User intent
            quality_score: Data quality
            
        Returns:
            Formatted response string
        """
        # Route to specific formatter
        if intent == "competitor_analysis":
            return self._format_competitor_analysis(findings, company_name)
        elif intent == "financial_data":
            return self._format_financial_info(findings, company_name)
        elif intent == "company_info" or intent == "general_information":
            return self._format_general_info(findings, company_name)
        else:
            # Default format
            return self._format_general_info(findings, company_name)
    
    def _format_general_info(
        self,
        findings: Dict[str, Any],
        company_name: str
    ) -> str:
        """Format general company information."""
        
        response_parts = []
        
        # Opening
        description = findings.get("description", "")
        if description:
            response_parts.append(f"{company_name} is {description}")
        else:
            response_parts.append(f"Here's what I found about {company_name}:")
        
        # Key facts
        facts = []
        
        if findings.get("ceo"):
            facts.append(f"**CEO:** {findings['ceo']}")
        
        if findings.get("founded"):
            facts.append(f"**Founded:** {findings['founded']}")
        
        if findings.get("headquarters"):
            facts.append(f"**Headquarters:** {findings['headquarters']}")
        
        if findings.get("industry"):
            facts.append(f"**Industry:** {findings['industry']}")
        
        if findings.get("revenue"):
            facts.append(f"**Revenue:** {findings['revenue']}")
        
        if findings.get("employees"):
            facts.append(f"**Employees:** {findings['employees']}")
        
        if facts:
            response_parts.append("\n\n" + "\n".join(facts))
        
        # Products
        products = findings.get("products", [])
        if products:
            products_str = ", ".join(products[:5])  # Limit to 5
            response_parts.append(f"\n\n**Products/Services:** {products_str}")
            if len(products) > 5:
                response_parts.append(f" (and {len(products) - 5} more)")
        
        # Competitors
        competitors = findings.get("competitors", [])
        if competitors:
            competitors_str = ", ".join(competitors[:5])
            response_parts.append(f"\n\n**Main Competitors:** {competitors_str}")
            if len(competitors) > 5:
                response_parts.append(f" (and {len(competitors) - 5} more)")
        
        return "".join(response_parts)
    
    def _format_competitor_analysis(
        self,
        findings: Dict[str, Any],
        company_name: str
    ) -> str:
        """Format competitor-focused response."""
        
        response_parts = []
        
        # Opening
        response_parts.append(f"**{company_name} Competitive Landscape:**\n")
        
        # Company position
        if findings.get("industry"):
            response_parts.append(f"\n{company_name} operates in the {findings['industry']} industry.")
        
        # Main competitors
        competitors = findings.get("competitors", [])
        if competitors:
            response_parts.append(f"\n\n**Main Competitors:**")
            for i, comp in enumerate(competitors[:5], 1):
                response_parts.append(f"\n{i}. {comp}")
        else:
            response_parts.append("\n\nCompetitor information is currently unavailable.")
        
        # Market position indicators
        if findings.get("revenue"):
            response_parts.append(f"\n\n**Market Position:**")
            response_parts.append(f"\n- Revenue: {findings['revenue']}")
        
        if findings.get("employees"):
            response_parts.append(f"\n- Employee count: {findings['employees']}")
        
        return "".join(response_parts)
    
    def _format_financial_info(
        self,
        findings: Dict[str, Any],
        company_name: str
    ) -> str:
        """Format financial-focused response."""
        
        response_parts = []
        
        response_parts.append(f"**{company_name} Financial Overview:**\n")
        
        # Revenue
        if findings.get("revenue"):
            response_parts.append(f"\n**Revenue:** {findings['revenue']}")
        else:
            response_parts.append(f"\nRevenue information is currently unavailable.")
        
        # Company scale indicators
        if findings.get("employees"):
            response_parts.append(f"\n\n**Company Scale:**")
            response_parts.append(f"\n- Employees: {findings['employees']}")
        
        if findings.get("headquarters"):
            response_parts.append(f"\n- Headquarters: {findings['headquarters']}")
        
        # Context
        if findings.get("industry"):
            response_parts.append(f"\n\n**Industry:** {findings['industry']}")
        
        if findings.get("founded"):
            response_parts.append(f"\n**Founded:** {findings['founded']}")
        
        return "".join(response_parts)


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from src.orchestration import create_initial_state
    from src.data import get_data_source
    from src.agents import ClarityAgent, ResearchAgent, ValidatorAgent
    
    async def test():
        print("Testing SynthesisAgent - Full Pipeline...\n")
        
        # Create data source
        data_source = await get_data_source()
        
        # Create all agents
        clarity = ClarityAgent(data_source)
        research = ResearchAgent(data_source)
        validator = ValidatorAgent(data_source)
        synthesis = SynthesisAgent(data_source)
        
        # Test query
        query = "Tell me about Tesla"
        state = create_initial_state(query)
        
        print(f"Query: {query}\n")
        print("=" * 60)
        
        # Run full pipeline
        print("\n1. ClarityAgent...")
        state.update(await clarity(state))
        print(f"   → Company: {state['company_name']}")
        
        print("\n2. ResearchAgent...")
        state.update(await research(state))
        print(f"   → Confidence: {state['confidence_score']}")
        
        print("\n3. ValidatorAgent...")
        state.update(await validator(state))
        print(f"   → Result: {state['validation_result']}")
        print(f"   → Quality: {state['quality_score']}")
        
        print("\n4. SynthesisAgent...")
        state.update(await synthesis(state))
        print(f"   → Status: {state['status']}")
        
        print("\n" + "=" * 60)
        print("\nFINAL RESPONSE:")
        print("=" * 60)
        print(state['final_response'])
        print("=" * 60)
        
        print(f"\n✅ Full pipeline working!")
        print(f"Agent trace: {' → '.join(state['agent_trace'])}")
    
    
        print(f"   → Company: {state['company_name']}")
        print(f"   → Confidence: {state['confidence_score']}")
        print(f"   → Result: {state['validation_result']}")
        print(f"   → Quality: {state['quality_score']}")
        print(f"   → Status: {state['status']}")
    asyncio.run(test())