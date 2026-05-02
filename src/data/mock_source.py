"""
Mock data source implementation.
Returns pre-defined responses without calling real LLM APIs.
"""

import httpx
from typing import Dict, Any

from src.data.base import DataSource, DataSourceUnavailable
from src.data.mock_responses import get_mock_company_data, get_mock_llm_response
from src.config import settings
from src.utils import logger


class MockDataSource(DataSource):
    """
    Mock data source that returns pre-defined responses.
    
    Uses mock_responses.py for data, or calls mock_server if running.
    Fast, free, predictable - perfect for development and testing.
    """
    
    def __init__(self):
        self.server_url = settings.mock_server_url
        self.use_server = False  # Try server first, fallback to local data
        
    async def get_llm_response(
        self,
        agent_type: str,
        query: str,
        context: Dict[str, Any] | None = None
    ) -> Dict[str, Any] | str:
        """Get mock LLM response."""
        logger.info(
            f"MockDataSource: Getting LLM response",
            agent_type=agent_type,
            query=query[:50]  # Log first 50 chars
        )
        
        # Try mock server first (if running)
        if self.use_server:
            try:
                response = await self._call_mock_server_llm(agent_type, query, context)
                logger.debug("MockDataSource: Response from mock server")
                return response
            except Exception as e:
                logger.warning(f"Mock server unavailable, using local data: {e}")
                self.use_server = False  # Fallback to local
        
        # Use local mock data
        response = get_mock_llm_response(agent_type, query)
        logger.debug("MockDataSource: Response from local mock data")
        return response
    
    async def get_company_data(self, company_name: str) -> Dict[str, Any]:
        """Get mock company data."""
        logger.info(f"MockDataSource: Getting company data for {company_name}")
        
        # Try mock server first
        if self.use_server:
            try:
                response = await self._call_mock_server_company(company_name)
                logger.debug("MockDataSource: Company data from mock server")
                return response
            except Exception as e:
                logger.warning(f"Mock server unavailable, using local data: {e}")
                self.use_server = False
        
        # Use local mock data
        data = get_mock_company_data(company_name)
        
        if not data:
            raise LookupError(f"Company '{company_name}' not found in mock data")
        
        logger.debug("MockDataSource: Company data from local mock data")
        return data
    
    async def _call_mock_server_llm(
        self,
        agent_type: str,
        query: str,
        context: Dict[str, Any] | None
    ) -> Dict[str, Any] | str:
        """Call mock server for LLM response."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.server_url}/llm",
                json={
                    "agent_type": agent_type,
                    "query": query,
                    "context": context
                },
                timeout=5.0
            )
            response.raise_for_status()
            return response.json()["response"]
    
    async def _call_mock_server_company(self, company_name: str) -> Dict[str, Any]:
        """Call mock server for company data."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.server_url}/company",
                json={"company_name": company_name},
                timeout=5.0
            )
            response.raise_for_status()
            return response.json()["data"]
    
    def get_source_name(self) -> str:
        """Get source name."""
        return "MockDataSource"
    
    def is_available(self) -> bool:
        """Check if mock source is available."""
        # Mock data is always available (local fallback)
        return True


# Convenience function
async def create_mock_source() -> MockDataSource:
    """
    Create and initialize mock data source.
    
    Returns:
        Initialized MockDataSource instance
    """
    source = MockDataSource()
    logger.info("MockDataSource initialized")
    return source