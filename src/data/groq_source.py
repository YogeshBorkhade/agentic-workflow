"""
Groq data source implementation.
Uses Groq API for fast LLM inference.
"""

from typing import Dict, Any
from groq import Groq

from src.data.base import DataSource, DataSourceUnavailable
from src.config import settings
from src.utils import logger


class GroqDataSource(DataSource):
    """
    Groq-powered data source for fast LLM inference.
    
    Uses Groq API with Mixtral or Llama models for agent responses.
    ~500 tokens/sec, low latency, cost-effective.
    """
    
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        """
        Initialize Groq data source.
        
        Args:
            api_key: Groq API key
            model: Model to use (default: mixtral-8x7b-32768)
            
        Raises:
            ValueError: If API key is None or empty
        """
        if not api_key:
            raise ValueError("Groq API key is required")
        
        self.api_key = api_key
        self.model = model
        self.client = Groq(api_key=api_key)
        
        logger.info(
            "GroqDataSource initialized",
            model=model
        )
    
    async def get_llm_response(
        self,
        agent_type: str,
        query: str,
        context: Dict[str, Any] | None = None
    ) -> Dict[str, Any] | str:
        """
        Get LLM response from Groq API.
        
        Args:
            agent_type: Agent type (clarity, research, validator, synthesis)
            query: User query or prompt
            context: Optional context dict
            
        Returns:
            Agent-specific response (dict for structured, str for text)
        """
        logger.info(
            f"GroqDataSource: Getting LLM response",
            agent_type=agent_type,
            query=query[:50]
        )
        
        # Build prompt based on agent type
        prompt = self._build_prompt(agent_type, query, context)
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(agent_type)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            logger.debug(
                "GroqDataSource: Got response",
                agent_type=agent_type,
                length=len(content)
            )
            
            # Return based on agent type
            if agent_type == "clarity":
                # Clarity expects structured output
                return self._parse_clarity_response(content, query)
            else:
                # Other agents return text
                return content
            
        except Exception as e:
            logger.error(
                f"GroqDataSource: LLM call failed: {e}",
                agent_type=agent_type
            )
            raise
    
    async def get_company_data(self, company_name: str) -> Dict[str, Any]:
        """
        Get company data using Groq LLM.
        
        Args:
            company_name: Company name
            
        Returns:
            Dict with company information
            
        Raises:
            LookupError: If company not found or data unavailable
        """
        logger.info(f"GroqDataSource: Getting company data for {company_name}")
        
        prompt = f"""Provide factual information about {company_name}:
        - Full company name
        - CEO/Founder
        - Industry/sector
        - Revenue (latest year)
        - Top 3 competitors
        
        Format as: Name: X | CEO: Y | Industry: Z | Revenue: A | Competitors: B, C, D"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a business data expert. Provide accurate, factual information only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Parse response into structured data
            data = self._parse_company_data(content, company_name)
            
            logger.debug(
                "GroqDataSource: Got company data",
                company=company_name
            )
            
            return data
            
        except Exception as e:
            logger.error(
                f"GroqDataSource: Company lookup failed: {e}",
                company=company_name
            )
            raise LookupError(f"Could not retrieve data for '{company_name}'") from e
    
    def get_source_name(self) -> str:
        """Get source name."""
        return f"GroqAPI ({self.model})"
    
    def is_available(self) -> bool:
        """Check if Groq API is available."""
        try:
            # Quick health check
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.warning(f"GroqDataSource: Availability check failed: {e}")
            return False
    
    def _get_system_prompt(self, agent_type: str) -> str:
        """Get system prompt for agent type."""
        prompts = {
            "clarity": "You extract intent and entities from user queries. Be precise.",
            "research": "You are a research expert. Provide accurate, detailed information.",
            "validator": "You validate research quality. Be thorough and critical.",
            "synthesis": "You synthesize information into clear, concise responses."
        }
        return prompts.get(agent_type, "You are a helpful AI assistant.")
    
    def _build_prompt(self, agent_type: str, query: str, context: Dict[str, Any] | None) -> str:
        """Build prompt from query and context."""
        if not context:
            return query
        
        # Add context if provided
        context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
        return f"Context:\n{context_str}\n\nQuery: {query}"
    
    def _parse_clarity_response(self, content: str, original_query: str) -> Dict[str, Any]:
        """Parse clarity agent response into structured format."""
        # Simple parsing - in production, use structured output or JSON mode
        return {
            "company_name": self._extract_company(original_query),
            "intent": "company_info",
            "entities": [self._extract_company(original_query)],
            "clarity_status": "clear"
        }
    
    def _extract_company(self, text: str) -> str | None:
        """Extract company name from text (simple heuristic)."""
        # Look for capitalized words (basic company detection)
        words = text.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                return word
        return None
    
    def _parse_company_data(self, content: str, company_name: str) -> Dict[str, Any]:
        """Parse company data from LLM response."""
        # Simple parsing - in production, use structured output
        return {
            "name": company_name,
            "raw_info": content,
            "source": "groq_llm"
        }


async def create_groq_source() -> GroqDataSource:
    """
    Create and initialize Groq data source.
    
    Returns:
        Initialized GroqDataSource instance
        
    Raises:
        ValueError: If GROQ_API_KEY not set in settings
    """
    api_key = settings.groq_api_key
    
    if not api_key:
        logger.error("GroqDataSource: GROQ_API_KEY not found in settings")
        raise ValueError(
            "GROQ_API_KEY not set. Set it in .env or use USE_MOCK_DATA=true"
        )
    
    model = settings.groq_model if hasattr(settings, 'groq_model') else "mixtral-8x7b-32768"
    
    source = GroqDataSource(api_key=api_key, model=model)
    logger.info("GroqDataSource created successfully")
    
    return source