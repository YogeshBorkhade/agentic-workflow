"""
Mock data responses for development and demo purposes.
Pre-defined responses for common queries.
"""

# Mock company data
MOCK_COMPANIES = {
    "tesla": {
        "name": "Tesla, Inc.",
        "ceo": "Elon Musk",
        "founded": "2003",
        "headquarters": "Austin, Texas",
        "industry": "Automotive, Clean Energy",
        "revenue": "$96.8 billion (2023)",
        "employees": "~140,000",
        "market_cap": "$800 billion (approx)",
        "competitors": ["BYD", "Ford", "General Motors", "Rivian"],
        "products": ["Model S", "Model 3", "Model X", "Model Y", "Cybertruck"],
        "key_facts": [
            "World's most valuable automaker",
            "Leader in electric vehicles",
            "Also produces solar panels and energy storage",
            "Operates Supercharger network",
        ]
    },
    "apple": {
        "name": "Apple Inc.",
        "ceo": "Tim Cook",
        "founded": "1976",
        "headquarters": "Cupertino, California",
        "industry": "Consumer Electronics, Software",
        "revenue": "$383.3 billion (2023)",
        "employees": "~161,000",
        "market_cap": "$3 trillion (approx)",
        "competitors": ["Samsung", "Microsoft", "Google", "Huawei"],
        "products": ["iPhone", "iPad", "Mac", "Apple Watch", "AirPods"],
        "key_facts": [
            "Most valuable company in the world",
            "Services revenue growing rapidly",
            "Strong ecosystem lock-in",
            "Premium brand positioning",
        ]
    },
    "microsoft": {
        "name": "Microsoft Corporation",
        "ceo": "Satya Nadella",
        "founded": "1975",
        "headquarters": "Redmond, Washington",
        "industry": "Software, Cloud Computing, AI",
        "revenue": "$211.9 billion (2023)",
        "employees": "~221,000",
        "market_cap": "$2.8 trillion (approx)",
        "competitors": ["Amazon", "Google", "Apple", "Oracle"],
        "products": ["Windows", "Office 365", "Azure", "Xbox", "LinkedIn"],
        "key_facts": [
            "Leader in cloud computing (Azure)",
            "Major investment in OpenAI",
            "Dominant in enterprise software",
            "Gaming division growing",
        ]
    },
    "google": {
        "name": "Alphabet Inc. (Google)",
        "ceo": "Sundar Pichai",
        "founded": "1998",
        "headquarters": "Mountain View, California",
        "industry": "Internet, AI, Advertising",
        "revenue": "$307.4 billion (2023)",
        "employees": "~182,000",
        "market_cap": "$1.8 trillion (approx)",
        "competitors": ["Microsoft", "Amazon", "Meta", "Apple"],
        "products": ["Search", "YouTube", "Android", "Google Cloud", "Gemini AI"],
        "key_facts": [
            "Dominant in search (~90% market share)",
            "YouTube is second-largest search engine",
            "Leading in AI research",
            "Advertising is 80% of revenue",
        ]
    },
    "amazon": {
        "name": "Amazon.com, Inc.",
        "ceo": "Andy Jassy",
        "founded": "1994",
        "headquarters": "Seattle, Washington",
        "industry": "E-commerce, Cloud Computing",
        "revenue": "$574.8 billion (2023)",
        "employees": "~1,500,000",
        "market_cap": "$1.5 trillion (approx)",
        "competitors": ["Walmart", "Microsoft", "Google", "Alibaba"],
        "products": ["Amazon.com", "AWS", "Prime Video", "Alexa", "Whole Foods"],
        "key_facts": [
            "Leader in cloud computing (AWS)",
            "Largest e-commerce platform in US",
            "Prime has 200M+ members",
            "Expanding into healthcare and logistics",
        ]
    }
}


# Mock LLM responses for different agent types
MOCK_LLM_RESPONSES = {
    "clarity": {
        "tesla": {
            "company_name": "Tesla",
            "clarity_status": "clear",
            "entities": ["Tesla", "electric vehicles", "Elon Musk"],
            "intent": "general_information"
        },
        "default": {
            "company_name": None,
            "clarity_status": "unclear",
            "entities": [],
            "intent": "unknown"
        }
    },
    "research": {
        "tesla": {
            "findings": MOCK_COMPANIES["tesla"],
            "sources": [
                "Company website",
                "SEC filings",
                "Financial reports"
            ],
            "confidence_score": 8.5,
            "data_quality": "high"
        },
        "default": {
            "findings": {},
            "sources": [],
            "confidence_score": 3.0,
            "data_quality": "low"
        }
    },
    "validator": {
        "sufficient": {
            "validation_result": "sufficient",
            "feedback": "Data is comprehensive and from reliable sources.",
            "missing_info": [],
            "quality_score": 9.0
        },
        "insufficient": {
            "validation_result": "insufficient",
            "feedback": "Missing key financial metrics and competitive analysis.",
            "missing_info": ["detailed financials", "market position", "growth trends"],
            "quality_score": 5.0
        }
    },
    "synthesis": {
        "tesla": (
            "Tesla, Inc. is the world's most valuable automaker, founded in 2003 and "
            "headquartered in Austin, Texas. Led by CEO Elon Musk, the company generated "
            "$96.8 billion in revenue in 2023 and employs approximately 140,000 people.\n\n"
            "Tesla is the leader in electric vehicles with popular models including Model S, "
            "Model 3, Model X, Model Y, and the upcoming Cybertruck. The company also produces "
            "solar panels and energy storage solutions. Its Supercharger network provides a "
            "competitive advantage in the EV market.\n\n"
            "Main competitors include BYD, Ford, General Motors, and Rivian. Tesla's market "
            "capitalization stands at approximately $800 billion."
        ),
        "default": (
            "I don't have enough information to provide a comprehensive response about "
            "this topic. Please provide more specific details or ask about a different subject."
        )
    }
}


def get_mock_company_data(company_name: str) -> dict:
    """
    Get mock company data by name.
    
    Args:
        company_name: Name of the company (case-insensitive)
        
    Returns:
        Dict with company data or empty dict if not found
    """
    company_key = company_name.lower()
    return MOCK_COMPANIES.get(company_key, {})


def get_mock_llm_response(agent_type: str, query: str) -> dict | str:
    """
    Get mock LLM response for a given agent type and query.
    
    Args:
        agent_type: Type of agent (clarity, research, validator, synthesis)
        query: User query
        
    Returns:
        Mock response appropriate for the agent type
    """
    # Extract company name from query (simple keyword matching)
    query_lower = query.lower()
    company_key = None
    
    for company in MOCK_COMPANIES.keys():
        if company in query_lower:
            company_key = company
            break
    
    # Get agent-specific responses
    if agent_type not in MOCK_LLM_RESPONSES:
        return {}
    
    agent_responses = MOCK_LLM_RESPONSES[agent_type]
    
    # Return company-specific or default response
    if company_key and company_key in agent_responses:
        return agent_responses[company_key]
    else:
        return agent_responses.get("default", {})


# Available mock companies (for listing)
AVAILABLE_COMPANIES = list(MOCK_COMPANIES.keys())


if __name__ == "__main__":
    print("Mock Data Examples:\n")
    
    print("1. Company Data:")
    tesla_data = get_mock_company_data("tesla")
    print(f"   Tesla CEO: {tesla_data['ceo']}")
    print(f"   Revenue: {tesla_data['revenue']}\n")
    
    print("2. LLM Responses:")
    clarity_response = get_mock_llm_response("clarity", "Tell me about Tesla")
    print(f"   Clarity: {clarity_response}\n")
    
    research_response = get_mock_llm_response("research", "Tell me about Tesla")
    print(f"   Research confidence: {research_response['confidence_score']}\n")
    
    print(f"3. Available companies: {', '.join(AVAILABLE_COMPANIES)}")
    print("\n✅ Mock data configured successfully!")