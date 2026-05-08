"""
Episodic Memory - Layer 3

Stores important events and decisions over time.
Like remembering key plot points in a movie, not every scene.

Example:
    memory = EpisodicMemory()
    
    # Important event!
    memory.record(
        event="User is allergic to peanuts",
        importance=0.9,
        tags=["health", "allergy"]
    )
    
    # Later retrieve
    allergies = memory.get_by_tag("health")
"""

from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Episode:
    """
    Single episodic memory.
    
    Components:
    - event: What happened (human-readable)
    - importance: How significant (0.0 to 1.0)
    - tags: Categories for filtering
    - context: Additional metadata
    - timestamp: When it occurred
    """
    event: str
    importance: float
    tags: List[str]
    context: Dict
    timestamp: datetime
    
    def __repr__(self):
        stars = "⭐" * int(self.importance * 5)
        return f"[{stars}] {self.event[:50]}..."


class EpisodicMemory:
    """
    Long-term memory of important events.
    
    Workflow:
    Event occurs → Assign importance → 
    If important (>0.7) → Record as Episode →
    Tag appropriately → Store with timestamp
    
    Later:
    Need specific info → Filter by tag/importance →
    Return relevant episodes
    
    Example:
        memory = EpisodicMemory()
        
        # Record important preference
        memory.record(
            event="User prefers morning meetings",
            importance=0.8,
            tags=["preference", "schedule"]
        )
        
        # Retrieve later
        prefs = memory.get_by_tag("preference")
    """
    
    def __init__(self, min_importance: float = 0.5):
        """
        Initialize episodic memory.
        
        Args:
            min_importance: Minimum importance to store (0.0-1.0)
                           Lower = store more, Higher = store less
        """
        self.episodes: List[Episode] = []
        self.min_importance = min_importance
    
    def record(
        self,
        event: str,
        importance: float,
        tags: List[str] = None,
        context: Dict = None
    ) -> Optional[Episode]:
        """
        Record an important event.
        
        Args:
            event: Description of what happened
            importance: Significance (0.0 = trivial, 1.0 = critical)
            tags: Categories (e.g., ["preference", "health"])
            context: Additional data
        
        Returns:
            Episode if stored, None if importance too low
        """
        # Filter by importance
        if importance < self.min_importance:
            print(f"⏭️  Skipped (importance {importance:.2f} < {self.min_importance})")
            return None
        
        episode = Episode(
            event=event,
            importance=importance,
            tags=tags or [],
            context=context or {},
            timestamp=datetime.now()
        )
        
        self.episodes.append(episode)
        
        stars = "⭐" * int(importance * 5)
        print(f"💾 Recorded [{stars}] {event[:50]}...")
        
        return episode
    
    def get_by_tag(self, tag: str) -> List[Episode]:
        """
        Retrieve episodes with specific tag.
        
        Args:
            tag: Tag to search for
        
        Returns:
            List of matching episodes (sorted by importance)
        """
        matches = [ep for ep in self.episodes if tag in ep.tags]
        return sorted(matches, key=lambda x: x.importance, reverse=True)
    
    def get_important(self, threshold: float = 0.7) -> List[Episode]:
        """
        Get high-importance episodes.
        
        Args:
            threshold: Minimum importance
        
        Returns:
            Episodes above threshold (sorted by recency)
        """
        important = [ep for ep in self.episodes if ep.importance >= threshold]
        return sorted(important, key=lambda x: x.timestamp, reverse=True)
    
    def get_recent(self, days: int = 7) -> List[Episode]:
        """
        Get recent episodes.
        
        Args:
            days: Number of days to look back
        
        Returns:
            Episodes from last N days
        """
        cutoff = datetime.now().timestamp() - (days * 86400)
        recent = [ep for ep in self.episodes if ep.timestamp.timestamp() > cutoff]
        return sorted(recent, key=lambda x: x.timestamp, reverse=True)
    
    def get_by_context(self, key: str, value: any) -> List[Episode]:
        """
        Search by context data.
        
        Args:
            key: Context key
            value: Context value
        
        Returns:
            Matching episodes
        """
        return [ep for ep in self.episodes if ep.context.get(key) == value]
    
    def get_all(self) -> List[Episode]:
        """Get all episodes (sorted by timestamp, newest first)."""
        return sorted(self.episodes, key=lambda x: x.timestamp, reverse=True)
    
    def clear(self) -> None:
        """Clear all episodes."""
        self.episodes = []
        print("🧹 Episodic memory cleared")
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        if not self.episodes:
            return {"total": 0}
        
        # Get all unique tags
        all_tags = set()
        for ep in self.episodes:
            all_tags.update(ep.tags)
        
        # Count by importance level
        critical = sum(1 for ep in self.episodes if ep.importance >= 0.8)
        important = sum(1 for ep in self.episodes if 0.5 <= ep.importance < 0.8)
        minor = sum(1 for ep in self.episodes if ep.importance < 0.5)
        
        return {
            "total_episodes": len(self.episodes),
            "unique_tags": len(all_tags),
            "tags": list(all_tags),
            "critical": critical,
            "important": important,
            "minor": minor,
            "oldest": self.episodes[0].timestamp if self.episodes else None,
            "newest": self.episodes[-1].timestamp if self.episodes else None,
            "avg_importance": sum(ep.importance for ep in self.episodes) / len(self.episodes)
        }
    
    def __len__(self) -> int:
        """Return number of episodes."""
        return len(self.episodes)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"EpisodicMemory({len(self.episodes)} episodes)"