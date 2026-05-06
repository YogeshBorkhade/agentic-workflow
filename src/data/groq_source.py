"""
Groq API data source implementation.
Calls real Groq API for LLM responses.
"""

from typing import Dict, Any
from groq import AsyncGroq

from src.data.base import DataSource, DataSourceUnavailable
from src.config import settings
from src.utils import (
    logger,
    retry_with_backoff,
    timeout,
    get_token_budget,
    LLMError,
    LLMTimeoutError,
)


class GroqDataSource(DataSource):
    """
    Groq API data source for real LLM calls.
    
    Uses Groq's Llama 3.3 70B model with:
    - Automatic retries on failure
    - Timeout protection
    - Token budget tracking
    - Error handling
    """
    
    def __init__(self):
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY not set in environment")
        
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        self.token_budget = get_token_budget("groq")
        
    @retry_with_backoff(max_attempts=settings.max_retries)
    @timeout(settings.timeout_seconds)
    async def get_llm_response(
        self,
        agent_type: str,
        query: str,
        context: Dict[str, Any] | None = None
    ) -> Dict[str, Any] | str:
        """
        Get LLM response from Groq API.
        
        Includes retry logic, timeout, and token tracking.
        """
        logger.info(
            f"GroqDataSource: Calling LLM",
            agent_type=agent_type,
            model=self.model,
            query_length=len(query)
        )
        
        try:
            # Build system prompt based on agent type
            system_prompt = self._get_system_prompt(agent_type)
            
            # Build user message
            user_message = self._build_user_message(query, context)
            
            # Call Groq API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000,
            )
            
            # Extract response
            content = response.choices[0].message.content
            
            # Track token usage
            tokens_used = response.usage.total_tokens
            self.token_budget.check_and_consume(tokens_used)
            
            logger.info(
                f"GroqDataSource: LLM response received",
                agent_type=agent_type,
                tokens=tokens_used,
                finish_reason=response.choices[0].finish_reason
            )
            
            # Parse response based on agent type
            return self._parse_response(agent_type, content)
            
        except Exception as e:
            logger.error(
                f"GroqDataSource: LLM call failed",
                agent_type=agent_type,
                error=str(e)
            )
            raise LLMError(f"Groq API call failed: {str(e)}") from e
    
    async def get_company_data(self, company_name: str) -> Dict[str, Any]:
        """
        Get company data using LLM.
        
        Note: For production, you'd use a real data API.
        This is a simplified implementation that uses LLM to generate data.
        """
        logger.info(f"GroqDataSource: Getting company data for {company_name}")
        
        query = f"Provide key information about {company_name} company"
        response = await self.get_llm_response("research", query)
        
        # In production, parse this into structured data
        return {"raw_response": response}
    
    def _get_system_prompt(self, agent_type: str) -> str:
        """Get system prompt for agent type."""
        prompts = {
            "clarity": (
                "You are a clarity extraction agent. Extract company information from user queries.\n\n"
                "CRITICAL: You MUST respond with ONLY a JSON object, no other text.\n\n"
                "Required JSON format:\n"
                "{\n"
                '  "company_name": "CompanyName",\n'
                '  "clarity_status": "clear",\n'
                '  "entities": ["company", "product", "person"],\n'
                '  "intent": "general_information"\n'
                "}\n\n"
                "Intent options: general_information, competitor_analysis, financial_data, company_info\n"
                "Clarity status: clear, unclear, needs_clarification"
            ),
            "research": (
                "You are a research agent. Provide comprehensive company information.\n\n"
                "CRITICAL: You MUST respond with ONLY a JSON object, no other text.\n\n"
                "Required JSON format:\n"
                "{\n"
                '  "company_name": "CompanyName",\n'
                '  "ceo": "Full Name",\n'
                '  "founded": "Year",\n'
                '  "headquarters": "City, Country",\n'
                '  "industry": "Industry Name",\n'
                '  "revenue": "$XXB (Year)",\n'
                '  "employees": "XXX,XXX",\n'
                '  "products": ["Product1", "Product2"],\n'
                '  "competitors": ["Company1", "Company2"],\n'
                '  "description": "Brief description"\n'
                "}\n\n"
                "Include as many fields as possible. Use actual data, not placeholders."
            ),
            "validator": (
                "You are a validation agent. Assess research quality.\n\n"
                "CRITICAL: You MUST respond with ONLY a JSON object, no other text.\n\n"
                "Required JSON format:\n"
                "{\n"
                '  "validation_result": "sufficient",\n'
                '  "feedback": "Quality assessment",\n'
                '  "quality_score": 8.5\n'
                "}\n\n"
                "validation_result options: sufficient, insufficient, needs_review"
            ),
            "synthesis": (
                "You are a synthesis agent. Create clear, comprehensive responses from research.\n"
                "Be factual, well-structured, and include specific details."
            )
        }
        return prompts.get(agent_type, "You are a helpful assistant.")
    
    def _build_user_message(self, query: str, context: Dict[str, Any] | None) -> str:
        """Build user message with context."""
        if context:
            return f"Query: {query}\n\nContext: {context}"
        return query
    
    def _parse_response(self, agent_type: str, content: str) -> Dict[str, Any] | str:
        """
        Parse LLM response based on agent type.
        
        For structured agents (clarity, validator), try to parse JSON.
        For text agents (research, synthesis), return raw text.
        """
        if agent_type in ["clarity", "research", "validator"]:
            # Try to parse JSON
            import json
            try:
                # Extract JSON from markdown code blocks if present
                if "```json" in content:
                    start = content.find("```json") + 7
                    end = content.find("```", start)
                    content = content[start:end].strip()
                elif "```" in content:
                    start = content.find("```") + 3
                    end = content.find("```", start)
                    content = content[start:end].strip()
                
                return json.loads(content)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON response for {agent_type}")
                # Return as dict with raw content
                return {"raw_response": content}
        
        # For research and synthesis, return text
        return content
    
    def get_source_name(self) -> str:
        """Get source name."""
        return f"GroqAPI ({self.model})"
    
    def is_available(self) -> bool:
        """Check if Groq API is available."""
        return bool(settings.groq_api_key)


# Convenience function
async def create_groq_source() -> GroqDataSource:
    """
    Create and initialize Groq data source.
    
    Returns:
        Initialized GroqDataSource instance
        
    Raises:
        ValueError: If GROQ_API_KEY not set
    """
    source = GroqDataSource()
    logger.info(f"GroqDataSource initialized with model: {source.model}")
    return source