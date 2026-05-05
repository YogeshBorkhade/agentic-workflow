"""
Validator Agent - Checks quality and completeness of research.

Responsibilities:
- Validates research findings quality
- Checks for missing critical information
- Calculates quality score
- Determines if research is sufficient or needs retry
- Provides feedback on improvements needed
"""

from typing import Dict, Any, List

from src.agents.base import BaseAgent
from src.orchestration.state import ResearchState
from src.utils import logger


class ValidatorAgent(BaseAgent):
    """
    Validator Agent assesses research quality.
    
    Inputs (from state):
    - research_findings: Data to validate
    - company_name: Company being researched
    - current_query: Original query to check relevance
    - confidence_score: Research confidence
    
    Outputs (to state):
    - validation_result: "sufficient" | "insufficient" | "needs_review"
    - validation_feedback: What's missing or good
    - quality_score: Overall quality (0-10)
    - missing_info: List of missing items
    - validation_attempts: Counter for retry loop control
    """
    
    # Quality thresholds
    SUFFICIENT_THRESHOLD = 6.0  # Quality score needed to pass
    MAX_ATTEMPTS = 2  # Max validation attempts before giving up
    
    async def process(self, state: ResearchState) -> Dict[str, Any]:
        """
        Validate research quality.
        
        Args:
            state: Current research state
            
        Returns:
            Partial state update with validation results
        """
        findings = self._get_findings(state)
        company_name = self._get_company_name(state)
        query = self._get_query(state)
        confidence = state.get("confidence_score", 0.0)
        attempts = state.get("validation_attempts", 0)
        
        logger.info(
            "ValidatorAgent processing",
            company_name=company_name,
            confidence=confidence,
            attempts=attempts,
            fields_count=len(findings)
        )
        
        # Check if we have any findings
        if not findings:
            logger.warning("ValidatorAgent: No research findings to validate")
            return {
                "validation_result": "insufficient",
                "validation_feedback": "No research data found",
                "quality_score": 0.0,
                "missing_info": ["all data"],
                "validation_attempts": attempts + 1
            }
        
        # Assess quality
        quality_score = self._calculate_quality_score(findings, confidence)
        missing_info = self._identify_missing_info(findings, query)
        feedback = self._generate_feedback(findings, missing_info, quality_score)
        
        # Determine validation result
        if quality_score >= self.SUFFICIENT_THRESHOLD:
            result = "sufficient"
        elif attempts >= self.MAX_ATTEMPTS:
            # Too many attempts, accept what we have
            result = "sufficient"
            feedback += " (Max attempts reached, proceeding with available data)"
        else:
            result = "insufficient"
        
        logger.info(
            "ValidatorAgent completed",
            result=result,
            quality_score=quality_score,
            missing_count=len(missing_info)
        )
        
        return {
            "validation_result": result,
            "validation_feedback": feedback,
            "quality_score": quality_score,
            "missing_info": missing_info,
            "validation_attempts": attempts + 1
        }
    
    def _calculate_quality_score(
        self, 
        findings: Dict[str, Any],
        confidence: float
    ) -> float:
        """
        Calculate overall quality score.
        
        Combines:
        - Data completeness (fields present)
        - Research confidence
        - Data richness (list lengths, text lengths)
        
        Args:
            findings: Research findings
            confidence: Research confidence score
            
        Returns:
            Quality score (0-10)
        """
        # Critical fields
        critical_fields = ["company_name", "ceo", "industry", "description"]
        critical_present = sum(
            1 for field in critical_fields 
            if findings.get(field) and str(findings[field]).strip()
        )
        critical_score = (critical_present / len(critical_fields)) * 4  # 0-4 points
        
        # Optional fields
        optional_fields = ["revenue", "headquarters", "founded", "employees"]
        optional_present = sum(
            1 for field in optional_fields 
            if findings.get(field) and str(findings[field]).strip()
        )
        optional_score = (optional_present / len(optional_fields)) * 2  # 0-2 points
        
        # Rich data (lists)
        rich_data_score = 0
        if findings.get("products") and len(findings["products"]) > 0:
            rich_data_score += 1
        if findings.get("competitors") and len(findings["competitors"]) > 0:
            rich_data_score += 1
        # 0-2 points
        
        # Use confidence as a factor (0-2 points)
        confidence_factor = min(confidence / 10 * 2, 2)
        
        # Total: 4 + 2 + 2 + 2 = 10 points max
        quality = critical_score + optional_score + rich_data_score + confidence_factor
        
        return round(quality, 1)
    
    def _identify_missing_info(
        self, 
        findings: Dict[str, Any],
        query: str
    ) -> List[str]:
        """
        Identify what information is missing.
        
        Args:
            findings: Research findings
            query: Original user query
            
        Returns:
            List of missing information items
        """
        missing = []
        
        # Check critical fields
        if not findings.get("ceo"):
            missing.append("CEO/leadership information")
        
        if not findings.get("industry"):
            missing.append("industry classification")
        
        if not findings.get("description"):
            missing.append("company description")
        
        # Check query-specific needs
        query_lower = query.lower()
        
        if "competitor" in query_lower and not findings.get("competitors"):
            missing.append("competitor information")
        
        if ("revenue" in query_lower or "financial" in query_lower) and not findings.get("revenue"):
            missing.append("financial data")
        
        if "product" in query_lower and not findings.get("products"):
            missing.append("product information")
        
        return missing
    
    def _generate_feedback(
        self,
        findings: Dict[str, Any],
        missing_info: List[str],
        quality_score: float
    ) -> str:
        """
        Generate human-readable feedback.
        
        Args:
            findings: Research findings
            missing_info: List of missing items
            quality_score: Calculated quality score
            
        Returns:
            Feedback message
        """
        if quality_score >= 8.0:
            feedback = "Excellent research quality. Comprehensive data found."
        elif quality_score >= self.SUFFICIENT_THRESHOLD:
            feedback = "Good research quality. Sufficient data for response."
        else:
            feedback = "Research quality below threshold."
        
        if missing_info:
            feedback += f" Missing: {', '.join(missing_info)}."
        
        # Add positive notes
        strengths = []
        if findings.get("competitors") and len(findings["competitors"]) > 2:
            strengths.append("good competitor data")
        if findings.get("products") and len(findings["products"]) > 2:
            strengths.append("detailed product info")
        if findings.get("revenue"):
            strengths.append("financial metrics")
        
        if strengths:
            feedback += f" Strengths: {', '.join(strengths)}."
        
        return feedback


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from src.orchestration import create_initial_state
    from src.data import get_data_source
    from src.agents import ClarityAgent, ResearchAgent
    
    async def test():
        print("Testing ValidatorAgent...\n")
        
        # Create data source
        data_source = await get_data_source()
        
        # Create agents
        clarity = ClarityAgent(data_source)
        research = ResearchAgent(data_source)
        validator = ValidatorAgent(data_source)
        
        # Test query
        query = "Tell me about Tesla and its competitors"
        state = create_initial_state(query)
        
        print(f"Query: {query}\n")
        
        # Step 1: Clarity
        print("Step 1: ClarityAgent...")
        state.update(await clarity(state))
        print(f"  Company: {state['company_name']}\n")
        
        # Step 2: Research
        print("Step 2: ResearchAgent...")
        state.update(await research(state))
        print(f"  Confidence: {state['confidence_score']}")
        print(f"  Findings: {len(state['research_findings'])} fields\n")
        
        # Step 3: Validator
        print("Step 3: ValidatorAgent...")
        state.update(await validator(state))
        
        print(f"  Result: {state['validation_result']}")
        print(f"  Quality Score: {state['quality_score']}")
        print(f"  Missing: {state['missing_info']}")
        print(f"  Feedback: {state['validation_feedback']}\n")
        
        # Test with poor data
        print("Testing with poor data...")
        poor_state = create_initial_state("Tell me about XYZ Corp")
        poor_state.update({
            "company_name": "XYZ Corp",
            "research_findings": {"company_name": "XYZ Corp"},  # Minimal data
            "confidence_score": 2.0
        })
        
        poor_result = await validator(poor_state)
        print(f"  Result: {poor_result['validation_result']}")
        print(f"  Quality: {poor_result['quality_score']}")
        print(f"  Feedback: {poor_result['validation_feedback']}\n")
        
        print("✅ ValidatorAgent working!")
    
    asyncio.run(test())