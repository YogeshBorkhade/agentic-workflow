from setuptools import setup, find_packages

setup(
    name="research-assistant",
    version="0.1.0",
    description="Production-ready multi-agent research assistant",
    author="yogesh.borkhade@gmail.com",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "groq>=0.4.0",
        "loguru>=0.7.2",
        "tenacity>=8.2.3",
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "langgraph>=0.0.20",
        "langchain-core>=0.1.23",
        "pytest>=7.4.3",
        "pytest-asyncio>=0.23.3",
    ],
)