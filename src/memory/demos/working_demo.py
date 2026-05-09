"""
Working Memory Demo

See how working memory tracks tasks and progress!
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.memory.working import WorkingMemory, TaskStatus
import time


def demo_basic_workflow():
    """Demo: Basic task workflow."""
    
    print("=" * 70)
    print("🎯 DEMO 1: Basic Task Workflow")
    print("=" * 70)
    print()
    
    memory = WorkingMemory()
    
    print("Step 1: Start a task")
    print("-" * 70)
    task_id = memory.start_task(
        name="Write blog post about AI",
        context={"topic": "AI", "target_words": 1000}
    )
    
    print("\nStep 2: Add sub-tasks")
    print("-" * 70)
    memory.add_subtask(task_id, "Research AI topics")
    memory.add_subtask(task_id, "Create outline")
    memory.add_subtask(task_id, "Write draft")
    memory.add_subtask(task_id, "Review and edit")
    memory.add_subtask(task_id, "Format and publish")
    
    print("\nStep 3: Work on tasks (update status)")
    print("-" * 70)
    memory.update_subtask_status(task_id, 0, "done")  # Research done
    memory.update_subtask_status(task_id, 1, "done")  # Outline done
    memory.update_subtask_status(task_id, 2, "in_progress")  # Drafting now
    
    print("\nStep 4: Check progress")
    print("-" * 70)
    progress = memory.get_progress(task_id)
    print(f"  Progress: {progress['done']}/{progress['total']} complete")
    print(f"  Percentage: {progress['percent_complete']}%")
    
    print("\nStep 5: Complete remaining tasks")
    print("-" * 70)
    memory.update_subtask_status(task_id, 2, "done")
    memory.update_subtask_status(task_id, 3, "done")
    memory.update_subtask_status(task_id, 4, "done")
    
    print("\nStep 6: Mark task complete (clears memory)")
    print("-" * 70)
    memory.complete_task(task_id)
    print(f"  Active tasks: {len(memory)}")
    print()


def demo_context_updates():
    """Demo: Updating task context."""
    
    print("=" * 70)
    print("📝 DEMO 2: Context Updates")
    print("=" * 70)
    print()
    
    memory = WorkingMemory()
    
    print("Starting data analysis task...")
    print("-" * 70)
    task_id = memory.start_task(
        name="Analyze sales data",
        context={"file": "sales.csv"}
    )
    
    memory.add_subtask(task_id, "Load data")
    memory.add_subtask(task_id, "Clean data")
    memory.add_subtask(task_id, "Generate insights")
    
    print("\nLoading data... (updating context)")
    print("-" * 70)
    memory.update_subtask_status(task_id, 0, "done")
    memory.update_context(task_id, {
        "rows_loaded": 10000,
        "columns": 15
    })
    
    print("\nCleaning data... (updating context)")
    print("-" * 70)
    memory.update_subtask_status(task_id, 1, "done")
    memory.update_context(task_id, {
        "rows_after_cleaning": 9500,
        "missing_values_removed": 500
    })
    
    print("\nFinal context:")
    print("-" * 70)
    task = memory.get_task(task_id)
    for key, value in task.context.items():
        print(f"  {key}: {value}")
    
    memory.complete_task(task_id)
    print()


def demo_multiple_tasks():
    """Demo: Managing multiple tasks."""
    
    print("=" * 70)
    print("🔀 DEMO 3: Multiple Tasks")
    print("=" * 70)
    print()
    
    memory = WorkingMemory()
    
    print("Starting multiple tasks...")
    print("-" * 70)
    
    task1 = memory.start_task("Write documentation")
    memory.add_subtask(task1, "API docs")
    memory.add_subtask(task1, "User guide")
    
    task2 = memory.start_task("Fix bugs")
    memory.add_subtask(task2, "Bug #123")
    memory.add_subtask(task2, "Bug #456")
    
    task3 = memory.start_task("Review PRs")
    memory.add_subtask(task3, "PR #789")
    
    print("\nActive tasks:")
    print("-" * 70)
    for task in memory.list_tasks():
        progress = memory.get_progress(task.id)
        print(f"  {task.name}: {progress['done']}/{progress['total']} done")
    
    print("\nGet current task (most recent):")
    print("-" * 70)
    current = memory.get_current_task()
    print(f"  {current}")
    
    print("\nComplete some tasks...")
    print("-" * 70)
    memory.complete_task(task1)
    memory.complete_task(task2)
    
    print(f"\n  Active tasks remaining: {len(memory)}")
    
    memory.complete_task(task3)
    print()


def demo_task_blocking():
    """Demo: Blocked tasks."""
    
    print("=" * 70)
    print("🚫 DEMO 4: Task Blocking")
    print("=" * 70)
    print()
    
    memory = WorkingMemory()
    
    print("Starting deployment task...")
    print("-" * 70)
    task_id = memory.start_task(
        name="Deploy to production",
        context={"env": "prod", "version": "1.2.0"}
    )
    
    memory.add_subtask(task_id, "Run tests")
    memory.add_subtask(task_id, "Get approval")
    memory.add_subtask(task_id, "Deploy")
    memory.add_subtask(task_id, "Verify")
    
    print("\nTests pass...")
    print("-" * 70)
    memory.update_subtask_status(task_id, 0, "done")
    
    print("\nWaiting for approval (blocked)...")
    print("-" * 70)
    memory.update_subtask_status(task_id, 1, "blocked")
    memory.update_context(task_id, {"blocked_reason": "Waiting for manager"})
    
    print("\nProgress check:")
    print("-" * 70)
    progress = memory.get_progress(task_id)
    print(f"  Done: {progress['done']}")
    print(f"  Blocked: {progress['blocked']}")
    print(f"  Completion: {progress['percent_complete']}%")
    
    print("\nApproval received! Continuing...")
    print("-" * 70)
    memory.update_subtask_status(task_id, 1, "done")
    memory.update_subtask_status(task_id, 2, "in_progress")
    
    # Finish deployment
    memory.update_subtask_status(task_id, 2, "done")
    memory.update_subtask_status(task_id, 3, "done")
    memory.complete_task(task_id)
    print()


def demo_task_cancellation():
    """Demo: Cancelling tasks."""
    
    print("=" * 70)
    print("❌ DEMO 5: Task Cancellation")
    print("=" * 70)
    print()
    
    memory = WorkingMemory()
    
    print("Starting research task...")
    print("-" * 70)
    task_id = memory.start_task(
        name="Research competitor products",
        context={"competitors": ["A", "B", "C"]}
    )
    
    memory.add_subtask(task_id, "Analyze competitor A")
    memory.add_subtask(task_id, "Analyze competitor B")
    memory.add_subtask(task_id, "Analyze competitor C")
    
    print("\nAnalyzing A...")
    print("-" * 70)
    memory.update_subtask_status(task_id, 0, "in_progress")
    
    print("\nOops! Task no longer needed (priorities changed)")
    print("-" * 70)
    memory.cancel_task(task_id)
    
    print(f"  Active tasks: {len(memory)}")
    print()


def demo_layer_comparison():
    """Demo: Compare working memory to other layers."""
    
    print("=" * 70)
    print("🎬 DEMO 6: Working Memory vs Other Layers")
    print("=" * 70)
    print()
    
    from src.memory.conversational import ConversationalMemory
    from src.memory.semantic import SemanticMemory
    from src.memory.episodic import EpisodicMemory
    
    layer1 = ConversationalMemory()
    layer2 = SemanticMemory()
    layer3 = EpisodicMemory()
    layer4 = WorkingMemory()
    
    print("Scenario: Agent writing a blog post")
    print("-" * 70)
    
    # Layer 1: Recent conversation
    print("\nLayer 1 (Conversational):")
    layer1.add_message("user", "Write a blog post about AI")
    layer1.add_message("assistant", "I'll help with that")
    layer1.add_message("user", "Make it 1000 words")
    print(f"  Stores: Last {len(layer1)} messages")
    print("  Use: Recent context only")
    
    # Layer 2: Knowledge
    print("\nLayer 2 (Semantic):")
    layer2.add("AI is artificial intelligence")
    layer2.add("Machine learning is a subset of AI")
    print(f"  Stores: {len(layer2)} facts")
    print("  Use: Background knowledge")
    
    # Layer 3: Important events
    print("\nLayer 3 (Episodic):")
    layer3.record("User prefers technical writing", 0.8, ["preference"])
    print(f"  Stores: {len(layer3)} important events")
    print("  Use: User preferences")
    
    # Layer 4: Current task
    print("\nLayer 4 (Working Memory):")
    task_id = layer4.start_task(
        "Write blog post",
        context={"topic": "AI", "words": 1000}
    )
    layer4.add_subtask(task_id, "Research")
    layer4.add_subtask(task_id, "Outline")
    layer4.add_subtask(task_id, "Draft")
    print(f"  Stores: {len(layer4)} active task")
    print("  Use: Track current work")
    
    print("\n" + "=" * 70)
    print("All 4 layers work together!")
    print("=" * 70)
    print("  Layer 1: What just happened?")
    print("  Layer 2: What do I know?")
    print("  Layer 3: What's important about user?")
    print("  Layer 4: What am I working on?")
    print("=" * 70)
    print()


def main():
    """Run all demos."""
    
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "WORKING MEMORY DEMOS" + " " * 28 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    demo_basic_workflow()
    input("Press Enter for next demo...")
    print("\n")
    
    demo_context_updates()
    input("Press Enter for next demo...")
    print("\n")
    
    demo_multiple_tasks()
    input("Press Enter for next demo...")
    print("\n")
    
    demo_task_blocking()
    input("Press Enter for next demo...")
    print("\n")
    
    demo_task_cancellation()
    input("Press Enter for next demo...")
    print("\n")
    
    demo_layer_comparison()
    
    print("\n")
    print("=" * 70)
    print("✅ All demos complete!")
    print("=" * 70)
    print("\n💡 Key Takeaways:")
    print("  1. Working Memory = Current task focus")
    print("  2. Temporary (cleared when task done)")
    print("  3. Track sub-tasks and progress")
    print("  4. Update context as you work")
    print("  5. Different from Layers 1-3 (task-scoped)")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()