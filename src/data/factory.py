"""
Data source factory.
Creates the appropriate data source based on configuration.
"""

from src.data.base import DataSource, DataSourceUnavailable
from src.data.mock_source import MockDataSource, create_mock_source
from src.data.groq_source import GroqDataSource, create_groq_source
from src.config import settings
from src.utils import logger


class DataSourceFactory:
    """
    Factory for creating data sources.
    
    Chooses between mock and real data sources based on USE_MOCK_DATA flag.
    """
    
    _instance: DataSource | None = None
    
    @classmethod
    async def get_source(cls) -> DataSource:
        """
        Get the configured data source.
        
        Returns singleton instance based on USE_MOCK_DATA setting.
        
        Returns:
            DataSource instance (MockDataSource or GroqDataSource)
            
        Raises:
            DataSourceUnavailable: If selected source is not available
        """
        # Return cached instance if exists
        if cls._instance is not None:
            return cls._instance
        
        # Create new instance based on settings
        if settings.use_mock_data:
            logger.info("DataSourceFactory: Creating MockDataSource")
            cls._instance = await create_mock_source()
        else:
            logger.info("DataSourceFactory: Creating GroqDataSource")
            try:
                cls._instance = await create_groq_source()
            except ValueError as e:
                logger.error(f"Failed to create GroqDataSource: {e}")
                raise DataSourceUnavailable(
                    "Groq API not available. Set GROQ_API_KEY or use USE_MOCK_DATA=true"
                ) from e
        
        # Verify source is available
        if not cls._instance.is_available():
            source_name = cls._instance.get_source_name()
            raise DataSourceUnavailable(f"{source_name} is not available")
        
        logger.info(
            f"DataSourceFactory: Using {cls._instance.get_source_name()}",
            use_mock_data=settings.use_mock_data
        )
        
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """
        Reset the factory (clear cached instance).
        
        Useful for testing or switching sources at runtime.
        """
        logger.debug("DataSourceFactory: Resetting instance")
        cls._instance = None
    
    @classmethod
    async def create_mock(cls) -> MockDataSource:
        """
        Create mock source explicitly (ignores USE_MOCK_DATA flag).
        
        Useful for testing.
        """
        logger.info("DataSourceFactory: Creating explicit MockDataSource")
        return await create_mock_source()
    
    @classmethod
    async def create_groq(cls) -> GroqDataSource:
        """
        Create Groq source explicitly (ignores USE_MOCK_DATA flag).
        
        Useful for testing.
        """
        logger.info("DataSourceFactory: Creating explicit GroqDataSource")
        return await create_groq_source()


# Convenience function for common use case
async def get_data_source() -> DataSource:
    """
    Get the configured data source.
    
    Shorthand for DataSourceFactory.get_source().
    
    Returns:
        DataSource instance
    """
    return await DataSourceFactory.get_source()


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("Testing Data Source Factory...\n")
        
        # Get configured source
        source = await get_data_source()
        print(f"✅ Data source: {source.get_source_name()}")
        print(f"   Available: {source.is_available()}")
        print(f"   Use mock: {settings.use_mock_data}\n")
        
        # Test LLM response
        print("Testing LLM response...")
        response = await source.get_llm_response(
            agent_type="clarity",
            query="Tell me about Tesla"
        )
        print(f"✅ Response type: {type(response)}")
        print(f"   Preview: {str(response)[:100]}...\n")
        
        # Test company data
        print("Testing company data...")
        try:
            company_data = await source.get_company_data("tesla")
            print(f"✅ Company: {company_data.get('name', 'N/A')}")
            print(f"   CEO: {company_data.get('ceo', 'N/A')}\n")
        except LookupError as e:
            print(f"❌ {e}\n")
        
        print("✅ Data source factory working!")
    
    asyncio.run(main())