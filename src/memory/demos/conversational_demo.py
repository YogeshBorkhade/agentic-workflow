"""
Conversational Memory Demo

Run this to see how conversational memory works.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.memory.conversational import ConversationalMemory


def demo_basic_usage():
    """Demo: Basic conversational memory usage."""
    
    print("=" * 70)
    print("🎬 DEMO 1: Basic Conversational Memory")
    print("=" * 70)
    print()
    
    # Create memory (remember last 4 messages)
    memory = ConversationalMemory(max_messages=4)
    
    print("Scene 1: Initial conversation about Tesla")
    print("-" * 70)
    memory.add_message("user", "Tell me about Tesla")
    memory.add_message("assistant", "Tesla is an electric vehicle company founded by Elon Musk")
    print(memory.get_recent_context())
    print(f"Memory: {memory}")
    print()
    
    print("Scene 2: Follow-up question (needs context!)")
    print("-" * 70)
    memory.add_message("user", "What's their revenue?")
    print("📝 Context that agent sees:")
    print(memory.get_recent_context())
    print()
    memory.add_message("assistant", "Tesla's annual revenue is around $96 billion")
    print()
    
    print("Scene 3: Memory fills up (4/4 messages)")
    print("-" * 70)
    print(f"Before: {memory}")
    memory.add_message("user", "Who is the CEO?")
    memory.add_message("assistant", "Elon Musk is the CEO")
    print(f"After: {memory}")
    print()
    
    print("Scene 4: Sliding window kicks in!")
    print("-" * 70)
    print(f"Before: {memory}")
    memory.add_message("user", "Where are they based?")
    # This will forget the oldest message!
    print(f"After: {memory}")
    print()
    
    print("📊 Memory Stats:")
    print("-" * 70)
    for key, value in memory.get_stats().items():
        print(f"  {key}: {value}")
    print()


def demo_context_retrieval():
    """Demo: Different ways to retrieve context."""
    
    print("=" * 70)
    print("🎬 DEMO 2: Context Retrieval Methods")
    print("=" * 70)
    print()
    
    memory = ConversationalMemory(max_messages=10)
    
    # Add some messages
    memory.add_message("user", "Tell me about Tesla")
    memory.add_message("assistant", "Tesla makes electric vehicles")
    memory.add_message("user", "What about SpaceX?")
    memory.add_message("assistant", "SpaceX builds rockets")
    memory.add_message("user", "Who owns both?")
    memory.add_message("assistant", "Elon Musk owns both companies")
    
    print("Method 1: Get all context")
    print("-" * 70)
    print(memory.get_recent_context())
    print()
    
    print("Method 2: Get last 2 messages only")
    print("-" * 70)
    print(memory.get_recent_context(last_n=2))
    print()
    
    print("Method 3: Get last user message")
    print("-" * 70)
    print(f"Last user said: '{memory.get_last_user_message()}'")
    print()
    
    print("Method 4: Get as list of dicts")
    print("-" * 70)
    messages = memory.get_messages_as_list()
    for msg in messages[-2:]:
        print(f"  {msg}")
    print()


def demo_real_conversation():
    """Demo: Simulate real multi-turn conversation."""
    
    print("=" * 70)
    print("🎬 DEMO 3: Real Conversation Simulation")
    print("=" * 70)
    print()
    
    memory = ConversationalMemory(max_messages=6)
    
    conversation = [
        ("user", "Tell me about Tesla's stock"),
        ("assistant", "Tesla (TSLA) is trading around $240"),
        ("user", "How has it performed this year?"),
        ("assistant", "Tesla stock is up about 35% year-to-date"),
        ("user", "What about their competition?"),
        ("assistant", "Main competitors include Rivian, Lucid, and traditional automakers"),
        ("user", "Which competitor is strongest?"),
        ("assistant", "Rivian has shown strong growth in the EV truck segment"),
    ]
    
    for i, (role, content) in enumerate(conversation, 1):
        print(f"Turn {i}: {role.upper()}")
        print("-" * 70)
        memory.add_message(role, content)
        
        if role == "user":
            print(f"User asks: {content}")
            print(f"\n📝 Agent sees this context:")
            print(memory.get_recent_context(last_n=4))
            print()
        else:
            print(f"Agent responds: {content}")
            print(f"Memory: {memory}")
            print()


def demo_memory_clearing():
    """Demo: Clearing and resetting memory."""
    
    print("=" * 70)
    print("🎬 DEMO 4: Memory Management")
    print("=" * 70)
    print()
    
    memory = ConversationalMemory(max_messages=10)
    
    # Add messages
    memory.add_message("user", "Tell me about Tesla")
    memory.add_message("assistant", "Tesla is an EV company")
    memory.add_message("user", "What's their revenue?")
    
    print(f"Before clear: {memory}")
    print(memory.get_recent_context())
    print()
    
    print("Clearing memory...")
    memory.clear()
    print(f"After clear: {memory}")
    print(f"Context: '{memory.get_recent_context()}'")
    print()
    
    print("Starting fresh conversation:")
    memory.add_message("user", "Tell me about SpaceX")
    memory.add_message("assistant", "SpaceX builds rockets")
    print(memory.get_recent_context())
    print()


def main():
    """Run all demos."""
    
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "CONVERSATIONAL MEMORY DEMOS" + " " * 26 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    demo_basic_usage()
    input("Press Enter for next demo...")
    print("\n")
    
    demo_context_retrieval()
    input("Press Enter for next demo...")
    print("\n")
    
    demo_real_conversation()
    input("Press Enter for next demo...")
    print("\n")
    
    demo_memory_clearing()
    
    print("\n")
    print("=" * 70)
    print("✅ All demos complete!")
    print("=" * 70)
    print("\n💡 Key Takeaways:")
    print("  1. Memory stores recent messages (sliding window)")
    print("  2. Oldest messages forgotten when capacity reached")
    print("  3. Context includes conversation history for LLM")
    print("  4. Use get_recent_context() to include in prompts")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()