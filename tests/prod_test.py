"""
Test script for Groq API integration.
Run this to verify real LLM calls work correctly.

Usage:
    python tests/test_groq_live.py
    
Make sure:
    - .env has USE_MOCK_DATA=false
    - .env has GROQ_API_KEY=your_key
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration import run_research
from src.config import settings
from src.utils import logger


async def test_single_query():
    """Test a single query with real Groq API."""
    
    print("=" * 70)
    print("Testing Single Query with Real Groq API")
    print("=" * 70)
    
    query = "Tell me about OpenAI - their CEO, products, and main competitors in the AI space"
    print(f"\nQuery: {query}\n")
    
    try:
        # Run workflow
        result = await run_research(query)
        
        # Display results
        print("\n" + "=" * 70)
        print("📊 RESULTS")
        print("=" * 70)
        
        print(f"\n✅ Basic Info:")
        print(f"   Request ID: {result['request_id']}")
        print(f"   Company: {result['company_name']}")
        print(f"   Intent: {result['intent']}")
        print(f"   Status: {result['status']}")
        
        print(f"\n📈 Quality Metrics:")
        print(f"   Research Confidence: {result['confidence_score']}/10")
        print(f"   Validation Quality: {result['quality_score']}/10")
        print(f"   Validation Result: {result['validation_result']}")
        print(f"   Validation Attempts: {result['validation_attempts']}")
        
        print(f"\n🔀 Agent Flow:")
        print(f"   {' → '.join(result['agent_trace'])}")
        
        print(f"\n📝 Research Findings:")
        findings = result.get('research_findings', {})
        if findings:
            for key, value in list(findings.items())[:8]:  # Show first 8 fields
                if isinstance(value, list):
                    print(f"   {key}: {value[:3]}" + (" ..." if len(value) > 3 else ""))
                else:
                    value_str = str(value)[:60]
                    print(f"   {key}: {value_str}" + ("..." if len(str(value)) > 60 else ""))
        else:
            print("   No findings")
        
        print(f"\n💬 Final Response:")
        print("-" * 70)
        print(result['final_response'])
        print("-" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_queries():
    """Test multiple queries to verify consistency."""
    
    print("\n\n" + "=" * 70)
    print("Testing Multiple Queries")
    print("=" * 70)
    
    queries = [
        "Tell me about Anthropic - their CEO, main products, and competitors",
        "What are NVIDIA's main competitors in the AI chip market?",
        "SpaceX revenue, CEO, and key achievements",
    ]
    
    results_summary = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Query: {query}")
        print("-" * 70)
        
        try:
            result = await run_research(query)
            
            summary = {
                "query": query,
                "company": result['company_name'],
                "confidence": result['confidence_score'],
                "quality": result['quality_score'],
                "attempts": result['validation_attempts'],
                "status": result['validation_result']
            }
            
            results_summary.append(summary)
            
            print(f"   Company: {summary['company']}")
            print(f"   Confidence: {summary['confidence']}/10")
            print(f"   Quality: {summary['quality']}/10")
            print(f"   Status: {summary['status']} (attempts: {summary['attempts']})")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results_summary.append({
                "query": query,
                "error": str(e)
            })
    
    # Summary table
    print("\n\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    for i, summary in enumerate(results_summary, 1):
        if "error" in summary:
            print(f"{i}. ❌ {summary['query'][:40]}... - FAILED")
        else:
            print(f"{i}. ✅ {summary['company']:<15} | Conf: {summary['confidence']:<4} | Qual: {summary['quality']:<4} | {summary['status']}")


async def main():
    """Main test runner."""
    
    print("\n🚀 Groq API Live Test\n")
    
    # Check settings
    print("⚙️  Configuration:")
    print(f"   USE_MOCK_DATA: {settings.use_mock_data}")
    print(f"   GROQ_API_KEY: {'✅ Set' if settings.groq_api_key else '❌ Missing'}")
    print(f"   Model: {settings.groq_model}")
    
    if settings.use_mock_data:
        print("\n⚠️  WARNING: USE_MOCK_DATA=true")
        print("   This test expects USE_MOCK_DATA=false")
        print("   Update .env file to test real Groq API\n")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    if not settings.groq_api_key:
        print("\n❌ ERROR: GROQ_API_KEY not set in .env")
        print("   Add GROQ_API_KEY=your_key to .env file")
        return
    
    print("\n" + "=" * 70)
    
    # Run tests
    choice = input("\nTest type:\n  1. Single query (detailed)\n  2. Multiple queries (summary)\n  Choice (1/2): ")
    
    if choice == "1":
        success = await test_single_query()
        if success:
            print("\n✅ Single query test passed!")
        else:
            print("\n❌ Single query test failed!")
    
    elif choice == "2":
        await test_multiple_queries()
        print("\n✅ Multiple query test completed!")
    
    else:
        print("Invalid choice!")
        return
    
    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70)
    print("\n💡 Remember to set USE_MOCK_DATA=true in .env for development\n")


if __name__ == "__main__":
    asyncio.run(main())