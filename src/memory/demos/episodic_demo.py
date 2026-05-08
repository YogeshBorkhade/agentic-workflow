"""
Episodic Memory Demo

See how episodic memory stores important events!
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.memory.episodic import EpisodicMemory
from datetime import datetime, timedelta


def demo_basic_usage():
    """Demo: Basic episodic memory."""
    
    print("=" * 70)
    print("📝 DEMO 1: Recording Important Events")
    print("=" * 70)
    print()
    
    memory = EpisodicMemory(min_importance=0.5)
    
    print("Recording various events...")
    print("-" * 70)
    
    # Critical events
    memory.record(
        event="User is allergic to peanuts",
        importance=0.95,
        tags=["health", "allergy", "critical"],
        context={"severity": "severe", "mentioned_count": 1}
    )
    
    memory.record(
        event="User's birthday is March 15th",
        importance=0.85,
        tags=["personal", "date", "important"],
        context={"month": 3, "day": 15}
    )
    
    # Important events
    memory.record(
        event="User prefers morning meetings",
        importance=0.75,
        tags=["preference", "schedule", "work"],
        context={"reason": "more productive in AM"}
    )
    
    # Medium importance
    memory.record(
        event="User completed onboarding tutorial",
        importance=0.6,
        tags=["milestone", "progress"],
        context={"duration_minutes": 5}
    )
    
    # Low importance (won't be stored!)
    memory.record(
        event="User asked about weather",
        importance=0.3,
        tags=["question", "casual"]
    )
    
    print()
    print(f"📊 Total episodes stored: {len(memory)}")
    print()


def demo_retrieval_methods():
    """Demo: Different ways to retrieve episodes."""
    
    print("=" * 70)
    print("🔍 DEMO 2: Retrieving Episodes")
    print("=" * 70)
    print()
    
    memory = EpisodicMemory()
    
    # Add diverse episodes
    memory.record("User is allergic to peanuts", 0.9, ["health", "allergy"])
    memory.record("User prefers morning meetings", 0.8, ["preference", "work"])
    memory.record("User's favorite color is blue", 0.6, ["preference", "personal"])
    memory.record("User completed Level 1", 0.5, ["milestone", "achievement"])
    memory.record("User set timezone to EST", 0.7, ["setting", "preference"])
    
    print("\nMethod 1: Get by tag")
    print("-" * 70)
    prefs = memory.get_by_tag("preference")
    for ep in prefs:
        print(f"  {ep}")
    
    print("\nMethod 2: Get high-importance only")
    print("-" * 70)
    important = memory.get_important(threshold=0.75)
    for ep in important:
        print(f"  {ep}")
    
    print("\nMethod 3: Get all episodes")
    print("-" * 70)
    all_eps = memory.get_all()
    print(f"  Total: {len(all_eps)} episodes")
    
    print()


def demo_user_profile():
    """Demo: Building user profile over time."""
    
    print("=" * 70)
    print("👤 DEMO 3: Building User Profile")
    print("=" * 70)
    print()
    
    memory = EpisodicMemory()
    
    print("📅 Day 1: User signup")
    print("-" * 70)
    memory.record(
        "User signed up",
        importance=0.8,
        tags=["milestone", "user_lifecycle"],
        context={"source": "website", "plan": "free"}
    )
    
    print("\n📅 Day 3: User preferences emerge")
    print("-" * 70)
    memory.record(
        "User set dark mode preference",
        importance=0.6,
        tags=["preference", "ui"],
        context={"theme": "dark"}
    )
    
    memory.record(
        "User is allergic to shellfish",
        importance=0.95,
        tags=["health", "allergy", "critical"],
        context={"severity": "severe"}
    )
    
    print("\n📅 Day 7: Important decision")
    print("-" * 70)
    memory.record(
        "User upgraded to Pro plan",
        importance=0.9,
        tags=["milestone", "business", "revenue"],
        context={"plan": "pro", "mrr": 29}
    )
    
    print("\n📅 Day 14: More preferences")
    print("-" * 70)
    memory.record(
        "User prefers email notifications",
        importance=0.7,
        tags=["preference", "notifications"],
        context={"channel": "email", "frequency": "daily"}
    )
    
    print("\n👤 User Profile Summary:")
    print("=" * 70)
    
    print("\n🚨 Critical Info:")
    critical = memory.get_important(threshold=0.9)
    for ep in critical:
        print(f"  • {ep.event}")
    
    print("\n⚙️  Preferences:")
    prefs = memory.get_by_tag("preference")
    for ep in prefs:
        print(f"  • {ep.event}")
    
    print("\n🎯 Milestones:")
    milestones = memory.get_by_tag("milestone")
    for ep in milestones:
        print(f"  • {ep.event}")
    
    print()


def demo_importance_filtering():
    """Demo: How importance filtering works."""
    
    print("=" * 70)
    print("⭐ DEMO 4: Importance Filtering")
    print("=" * 70)
    print()
    
    print("Scenario: User mentions various things in conversation")
    print("-" * 70)
    print()
    
    memory = EpisodicMemory(min_importance=0.6)
    
    events = [
        ("User is allergic to peanuts", 0.95, "Stored ✅"),
        ("User asked about weather", 0.2, "Skipped ❌"),
        ("User's birthday is July 4th", 0.85, "Stored ✅"),
        ("User said hello", 0.1, "Skipped ❌"),
        ("User prefers dark mode", 0.7, "Stored ✅"),
        ("User scrolled page", 0.05, "Skipped ❌"),
        ("User set notification preference", 0.75, "Stored ✅"),
    ]
    
    for event, importance, expected in events:
        print(f"\nEvent: '{event}'")
        print(f"Importance: {importance:.2f}")
        result = memory.record(event, importance, tags=["test"])
        print(f"Result: {expected}")
    
    print("\n" + "=" * 70)
    print(f"Final: {len(memory)} important events stored")
    print(f"Skipped: {len([e for e, i, _ in events if i < 0.6])} trivial events")
    print()


def demo_layer_comparison():
    """Demo: Compare all 3 layers."""
    
    print("=" * 70)
    print("🎬 DEMO 5: Layer 1 vs 2 vs 3")
    print("=" * 70)
    print()
    
    from src.memory.conversational import ConversationalMemory
    from src.memory.semantic import SemanticMemory
    
    layer1 = ConversationalMemory(max_messages=3)
    layer2 = SemanticMemory()
    layer3 = EpisodicMemory()
    
    print("Simulating conversation with important moments...")
    print("-" * 70)
    
    # Conversation flow
    interactions = [
        ("Tell me about Tesla", 0.3),
        ("I'm allergic to peanuts!", 0.95),  # IMPORTANT!
        ("What's the weather?", 0.2),
        ("My favorite color is blue", 0.7),  # IMPORTANT!
        ("Show me news", 0.2),
        ("I prefer morning meetings", 0.8),  # IMPORTANT!
    ]
    
    for msg, importance in interactions:
        # All layers get the message
        layer1.add_message("user", msg)
        layer2.add(msg)
        if importance >= 0.7:
            layer3.record(msg, importance, tags=["user_info"])
    
    print("\n🔍 Now searching: 'What are my preferences?'")
    print("=" * 70)
    
    print("\nLayer 1 (Conversational):")
    print("-" * 70)
    context = layer1.get_recent_context()
    print(f"  {context}")
    print(f"  ❌ Only last 3 messages, no 'peanuts' or 'blue'!")
    
    print("\nLayer 2 (Semantic):")
    print("-" * 70)
    results = layer2.search("preferences", top_k=6)
    print(f"  ✅ Found {len(results)} results, BUT includes everything:")
    for text, score in results:
        print(f"     • {text}")
    
    print("\nLayer 3 (Episodic):")
    print("-" * 70)
    important = layer3.get_important(threshold=0.7)
    print(f"  ✅ Found {len(important)} IMPORTANT preferences only:")
    for ep in important:
        print(f"     • {ep.event}")
    
    print("\n💡 Winner: Layer 3 returns only what matters!")
    print()


def main():
    """Run all demos."""
    
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "EPISODIC MEMORY DEMOS" + " " * 27 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    demo_basic_usage()
    input("Press Enter for next demo...")
    print("\n")
    
    demo_retrieval_methods()
    input("Press Enter for next demo...")
    print("\n")
    
    demo_user_profile()
    input("Press Enter for next demo...")
    print("\n")
    
    demo_importance_filtering()
    input("Press Enter for next demo...")
    print("\n")
    
    demo_layer_comparison()
    
    print("\n")
    print("=" * 70)
    print("✅ All demos complete!")
    print("=" * 70)
    print("\n💡 Key Takeaways:")
    print("  1. Episodic = Important events only")
    print("  2. Filter by importance (0.0-1.0)")
    print("  3. Tag for easy retrieval")
    print("  4. Perfect for user preferences/critical info")
    print("  5. Use with Layers 1 & 2 for complete memory")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()