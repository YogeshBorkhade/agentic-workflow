"""
Memory Module - Complete 4-Layer System

Contains all memory implementations for the agent system.

Memory Layers:
1. Conversational: Recent message history (sliding window)
2. Semantic: Vector-based knowledge retrieval  
3. Episodic: Long-term important events
4. Working: Task-specific context

Each layer solves a specific problem:
- Layer 1: What just happened?
- Layer 2: What do I know?
- Layer 3: What's important about the user?
- Layer 4: What am I working on right now?
"""

from .conversational import ConversationalMemory, Message
from .semantic import SemanticMemory
from .episodic import EpisodicMemory, Episode
from .working import WorkingMemory, Task, SubTask, TaskStatus

__all__ = [
    # Layer 1
    'ConversationalMemory',
    'Message',
    # Layer 2
    'SemanticMemory',
    # Layer 3
    'EpisodicMemory',
    'Episode',
    # Layer 4
    'WorkingMemory',
    'Task',
    'SubTask',
    'TaskStatus'
]

__version__ = '4.0.0'