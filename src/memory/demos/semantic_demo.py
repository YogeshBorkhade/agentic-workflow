"""
Semantic Memory Demo

See how semantic search finds related content by meaning!
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.memory.semantic import SemanticMemory


def demo_basic_semantic_search():
    """Demo: Search by meaning, not exact words."""
    
    print("=" * 70)
    print("🔍 DEMO 1: Semantic Search (Finding by Meaning)")
    print("=" * 70)
    print()
    
    memory = SemanticMemory()
    
    # Add some knowledge
    print("📚 Adding knowledge to memory...")
    print("-" * 70)
    memory.add("Tesla reported $96 billion in revenue for 2023")
    memory.add("SpaceX launched 98 successful missions this year")
    memory.add("Elon Musk is the CEO of both Tesla and SpaceX")
    memory.add("Tesla's Cybertruck production started in late 2023")
    memory.add("SpaceX Starship completed its third test flight")
    print()
    
    # Search with different queries
    queries = [
        "Tesla earnings",          # Finds revenue info!
        "SpaceX rockets",          # Finds launches!
        "Who runs Tesla",          # Finds CEO info!
        "Cybertruck",             # Finds production info!
    ]
    
    for query in queries:
        print(f"🔍 Query: '{query}'")
        print("-" * 70)
        results = memory.search(query, top_k=2)
        
        for i, (text, score) in enumerate(results, 1):
            print(f"  {i}. [{score:.3f}] {text}")
        print()


def demo_semantic_vs_keyword():
    """Demo: Why semantic is better than keyword matching."""
    
    print("=" * 70)
    print("🔍 DEMO 2: Semantic Search vs Keyword Matching")
    print("=" * 70)
    print()
    
    memory = SemanticMemory()
    
    # Add facts about companies
    facts = [
        "Apple's iPhone sales increased 15% in Q4",
        "Microsoft Azure cloud revenue grew by 30%",
        "Google's advertising income reached $200B annually",
        "Amazon's e-commerce platform serves 300M customers",
        "Tesla's electric vehicle production hit 1.8M units"
    ]
    
    print("📚 Knowledge base:")
    print("-" * 70)
    for fact in facts:
        memory.add(fact)
        print(f"  ✓ {fact}")
    print()
    
    # Semantic queries (no exact word match!)
    test_cases = [
        ("phone sales", "Should find iPhone sales"),
        ("cloud computing revenue", "Should find Azure"),
        ("ad money", "Should find advertising income"),
        ("online shopping users", "Should find e-commerce customers"),
        ("EV manufacturing", "Should find vehicle production")
    ]
    
    for query, expected in test_cases:
        print(f"🔍 Query: '{query}' ({expected})")
        print("-" * 70)
        results = memory.search(query, top_k=1)
        
        if results:
            text, score = results[0]
            print(f"  ✅ Found: {text}")
            print(f"  📊 Similarity: {score:.3f}")
        else:
            print("  ❌ No results")
        print()


def demo_conversation_knowledge_base():
    """Demo: Using semantic memory as knowledge base."""
    
    print("=" * 70)
    print("🔍 DEMO 3: Knowledge Base for Agents")
    print("=" * 70)
    print()
    
    memory = SemanticMemory()
    
    # Build knowledge base
    print("📚 Building knowledge base...")
    print("-" * 70)
    knowledge = [
        "Tesla was founded in 2003 by Martin Eberhard and Marc Tarpenning",
        "Elon Musk joined Tesla as chairman in 2004 and became CEO in 2008",
        "Tesla's first car was the Roadster, launched in 2008",
        "The Model S sedan was introduced in 2012",
        "Tesla Gigafactory in Nevada produces batteries and powertrains",
        "Tesla's Autopilot is an advanced driver assistance system",
        "Tesla stock (TSLA) went public in 2010 at $17 per share",
        "Tesla's market cap exceeded $1 trillion in 2021"
    ]
    
    for item in knowledge:
        memory.add(item)
    
    print(f"  ✓ Added {len(memory)} facts to knowledge base")
    print()
    
    # Agent queries
    questions = [
        "When was Tesla founded?",
        "Who is the CEO?",
        "What was their first car?",
        "Tell me about Tesla stock",
        "What is Autopilot?"
    ]
    
    print("❓ Agent answering questions using semantic memory:")
    print("-" * 70)
    for question in questions:
        print(f"\nQ: {question}")
        
        # Search knowledge base
        results = memory.search(question, top_k=1)
        
        if results:
            answer, score = results[0]
            print(f"A: {answer}")
            print(f"   (confidence: {score:.2f})")


def demo_similarity_scores():
    """Demo: Understanding similarity scores."""
    
    print("\n")
    print("=" * 70)
    print("🔍 DEMO 4: Understanding Similarity Scores")
    print("=" * 70)
    print()
    
    memory = SemanticMemory()
    
    # Add related and unrelated facts
    memory.add("Tesla manufactures electric vehicles in California")
    memory.add("SpaceX builds rockets for space exploration")
    memory.add("Python is a programming language used for AI")
    
    # Test different query relevance
    print("🔍 Testing similarity scores...")
    print("-" * 70)
    
    queries = [
        ("Tesla electric cars", "Very relevant"),
        ("SpaceX vehicles", "Somewhat relevant"),
        ("Python coding", "Different topic"),
        ("banana recipes", "Completely unrelated")
    ]
    
    for query, expected_relevance in queries:
        print(f"\nQuery: '{query}' (Expected: {expected_relevance})")
        results = memory.search(query, top_k=1)
        
        if results:
            text, score = results[0]
            print(f"  Best match: {text[:50]}...")
            print(f"  Score: {score:.3f}", end="")
            
            if score > 0.5:
                print(" → 🟢 Highly relevant")
            elif score > 0.3:
                print(" → 🟡 Somewhat relevant")
            else:
                print(" → 🔴 Not very relevant")


def demo_layer1_vs_layer2():
    """Demo: When to use Layer 1 vs Layer 2."""
    
    print("\n\n")
    print("=" * 70)
    print("🎬 DEMO 5: Layer 1 (Conversational) vs Layer 2 (Semantic)")
    print("=" * 70)
    print()
    
    # Import Layer 1
    from src.memory.conversational import ConversationalMemory
    
    layer1 = ConversationalMemory(max_messages=3)
    layer2 = SemanticMemory()
    
    # Simulate conversation
    print("Conversation happening...")
    print("-" * 70)
    
    messages = [
        ("user", "Tell me about Tesla's founding"),
        ("assistant", "Tesla was founded in 2003"),
        ("user", "What about SpaceX?"),
        ("assistant", "SpaceX was founded in 2002"),
        ("user", "Who founded both?"),
        ("assistant", "Elon Musk is associated with both companies"),
    ]
    
    for role, content in messages:
        layer1.add_message(role, content)
        layer2.add(content)
        print(f"  {role}: {content}")
    
    print()
    
    # Add more info (but Layer 1 will forget oldest!)
    layer1.add_message("user", "What's Tesla's stock symbol?")
    layer1.add_message("assistant", "TSLA")
    layer2.add("Tesla stock symbol is TSLA")
    
    print("\n🔍 Now searching for 'Tesla founding'...")
    print("-" * 70)
    
    print("\nLayer 1 (Recent messages only):")
    context = layer1.get_recent_context()
    found_in_layer1 = "founded" in context.lower()
    print(f"  Found 'founded'? {found_in_layer1} ❌")
    print(f"  (It's gone! Only has last 3 messages)")
    
    print("\nLayer 2 (All knowledge, semantic search):")
    results = layer2.search("Tesla founding", top_k=1)
    if results:
        text, score = results[0]
        print(f"  Found: '{text}' ✅")
        print(f"  (It remembers! Semantic search found it)")
    
    print()
    print("💡 Use Layer 1 for: Recent context in current conversation")
    print("💡 Use Layer 2 for: Long-term knowledge and semantic search")


def main():
    """Run all demos."""
    
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 18 + "SEMANTIC MEMORY DEMOS" + " " * 29 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    demo_basic_semantic_search()
    input("Press Enter for next demo...")
    
    demo_semantic_vs_keyword()
    input("Press Enter for next demo...")
    
    demo_conversation_knowledge_base()
    input("Press Enter for next demo...")
    
    demo_similarity_scores()
    input("Press Enter for next demo...")
    
    demo_layer1_vs_layer2()
    
    print("\n")
    print("=" * 70)
    print("✅ All demos complete!")
    print("=" * 70)
    print("\n💡 Key Takeaways:")
    print("  1. Semantic search finds by MEANING, not exact words")
    print("  2. Works on ALL stored knowledge (not just recent)")
    print("  3. Similarity scores show relevance (0-1)")
    print("  4. Perfect for knowledge bases and RAG systems")
    print("  5. Use with Layer 1 for complete memory system")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()