"""
Conversational Memory

Stores recent conversation history with sliding window.
Like remembering the last 10 minutes of a movie.
"""

from typing import List, Dict, Optional
from datetime import datetime


class Message:
    """Single message in conversation."""
    
    def __init__(self, role: str, content: str):
        self.role = role  # "user" or "assistant"
        self.content = content
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
    
    def __repr__(self):
        return f"{self.role}: {self.content[:50]}..."


class ConversationalMemory:
    """
    Stores recent conversation history with sliding window.
    
    Components:
    - messages: List of recent messages
    - max_messages: Window size (how many to remember)
    
    Workflow:
    User/Agent message → add_message() → Check size → 
    If > max: Remove oldest → Store new message →
    When needed: get_recent_context() → Format as string
    
    Example:
        memory = ConversationalMemory(max_messages=10)
        memory.add_message("user", "Tell me about Tesla")
        memory.add_message("assistant", "Tesla is...")
        
        context = memory.get_recent_context()  # Get history for LLM
    """
    
    def __init__(self, max_messages: int = 10):
        """
        Initialize conversational memory.
        
        Args:
            max_messages: Maximum messages to store (sliding window)
        """
        self.messages: List[Message] = []
        self.max_messages = max_messages
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add message to memory.
        
        Args:
            role: "user" or "assistant"
            content: Message content
        """
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        
        # Sliding window: keep only recent messages
        if len(self.messages) > self.max_messages:
            removed = self.messages.pop(0)
            print(f"🗑️  Forgot: {removed.role[:1].upper()}: {removed.content[:30]}...")
    
    def get_recent_context(self, last_n: Optional[int] = None) -> str:
        """
        Get recent conversation as formatted string.
        
        Args:
            last_n: Number of recent messages (None = all)
        
        Returns:
            Formatted conversation history
        """
        if last_n:
            relevant_messages = self.messages[-last_n:]
        else:
            relevant_messages = self.messages
        
        if not relevant_messages:
            return "No conversation history"
        
        return "\n".join([
            f"{msg.role.upper()}: {msg.content}"
            for msg in relevant_messages
        ])
    
    def get_last_user_message(self) -> str:
        """Get most recent user message."""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return ""
    
    def get_last_assistant_message(self) -> str:
        """Get most recent assistant message."""
        for msg in reversed(self.messages):
            if msg.role == "assistant":
                return msg.content
        return ""
    
    def get_messages_as_list(self) -> List[Dict]:
        """Get messages as list of dictionaries."""
        return [msg.to_dict() for msg in self.messages]
    
    def clear(self) -> None:
        """Clear all memory."""
        self.messages = []
        print("🧹 Memory cleared")
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        user_count = sum(1 for m in self.messages if m.role == "user")
        assistant_count = sum(1 for m in self.messages if m.role == "assistant")
        
        return {
            "total_messages": len(self.messages),
            "user_messages": user_count,
            "assistant_messages": assistant_count,
            "capacity": self.max_messages,
            "utilization": f"{len(self.messages)}/{self.max_messages}",
            "oldest_timestamp": self.messages[0].timestamp if self.messages else None,
            "newest_timestamp": self.messages[-1].timestamp if self.messages else None
        }
    
    def __len__(self) -> int:
        """Return number of messages."""
        return len(self.messages)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"ConversationalMemory({len(self.messages)}/{self.max_messages} messages)"