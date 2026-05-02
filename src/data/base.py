"""
Abstract base class for data sources.
Defines the interface that all data sources must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class DataSource(ABC):
    """
    Abstract base class for data sources.
    
    All data sources (mock, Groq, OpenAI, etc.) must implement this interface.
    This allows agents to work with any data source without knowing the details.
    """
    
    @abstractmethod
    async def get_llm_response(
        self,
        agent_type: str,
        query: str,
        context: Dict[str, Any] | None = None
    ) -> Dict[str, Any] | str:
        """
        Get LLM response for a given agent type and query.
        
        Args:
            agent_type: Type of agent (clarity, research, validator, synthesis)
            query: User query or prompt
            context: Optional context dict with additional info
            
        Returns:
            Agent-specific response (dict or str depending on agent)
            
        Raises:
            LLMError: If LLM call fails
            RateLimitError: If rate limit exceeded
        """
        pass
    
    @abstractmethod
    async def get_company_data(self, company_name: str) -> Dict[str, Any]:
        """
        Get company data by name.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Dict with company information
            
        Raises:
            LookupError: If company not found
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """
        Get the name of this data source.
        
        Returns:
            Human-readable source name (e.g., "MockServer", "GroqAPI")
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this data source is currently available.
        
        Returns:
            True if source can be used, False otherwise
        """
        pass


class DataSourceError(Exception):
    """Base exception for data source errors."""
    pass


class DataSourceUnavailable(DataSourceError):
    """Raised when data source is not available."""
    pass