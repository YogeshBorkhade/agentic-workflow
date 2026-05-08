"""
Semantic Memory - Layer 2

Stores information as vector embeddings for semantic search.
Like "Have I seen this actor before?" - searches by meaning, not exact words.

Example:
    Query: "Tesla earnings"
    Finds: "Tesla quarterly revenue report" ✅ (similar meaning!)
    
vs Layer 1 (Conversational):
    Query: "Tesla earnings"
    Finds: Only if exact words "Tesla earnings" in recent messages ❌
"""

from typing import List, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime


class SemanticMemory:
    """
    Vector-based memory for semantic search.
    
    Components:
    - memories: List of all stored texts
    - embeddings: Vector representations of texts
    - model: Converts text to vectors
    
    Workflow:
    Add memory → model.encode(text) → Store vector →
    Search query → model.encode(query) → 
    Compare with all vectors → Return most similar
    
    Example:
        memory = SemanticMemory()
        memory.add("Tesla reported $96B revenue in 2023")
        memory.add("SpaceX launched 100 rockets this year")
        
        results = memory.search("Tesla earnings")
        # Finds the Tesla revenue memory! (semantic match)
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize semantic memory.
        
        Args:
            model_name: Sentence transformer model
                       (all-MiniLM-L6-v2 is fast and good)
        """
        print(f"🧠 Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.memories: List[str] = []
        self.embeddings: Optional[np.ndarray] = None
        self.timestamps: List[datetime] = []
        print("✅ Model loaded!")
    
    def add(self, text: str) -> None:
        """
        Add memory and compute embedding.
        
        Args:
            text: Text to remember
        """
        # Store text
        self.memories.append(text)
        self.timestamps.append(datetime.now())
        
        # Compute vector embedding
        embedding = self.model.encode([text])
        
        # Add to embeddings array
        if self.embeddings is None:
            self.embeddings = embedding
        else:
            self.embeddings = np.vstack([self.embeddings, embedding])
        
        print(f"💾 Saved: {text[:60]}...")
    
    def search(
        self, 
        query: str, 
        top_k: int = 3,
        threshold: float = 0.0
    ) -> List[Tuple[str, float]]:
        """
        Search for semantically similar memories.
        
        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity score (0-1)
        
        Returns:
            List of (text, similarity_score) tuples
        """
        if not self.memories:
            return []
        
        # Encode query to vector
        query_embedding = self.model.encode([query])
        
        # Compute cosine similarities with all memories
        # (dot product since embeddings are normalized)
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()
        
        # Get top k most similar
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Filter by threshold and return
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= threshold:
                results.append((self.memories[idx], score))
        
        return results
    
    def search_with_details(
        self,
        query: str,
        top_k: int = 3
    ) -> List[dict]:
        """
        Search with additional metadata.
        
        Returns:
            List of dicts with text, score, and timestamp
        """
        if not self.memories:
            return []
        
        query_embedding = self.model.encode([query])
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                "text": self.memories[idx],
                "score": float(similarities[idx]),
                "timestamp": self.timestamps[idx],
                "index": int(idx)
            })
        
        return results
    
    def get_all_memories(self) -> List[str]:
        """Get all stored memories."""
        return self.memories.copy()
    
    def clear(self) -> None:
        """Clear all memories."""
        self.memories = []
        self.embeddings = None
        self.timestamps = []
        print("🧹 Semantic memory cleared")
    
    def get_stats(self) -> dict:
        """Get memory statistics."""
        return {
            "total_memories": len(self.memories),
            "embedding_dim": self.embeddings.shape[1] if self.embeddings is not None else 0,
            "model": self.model.get_sentence_embedding_dimension(),
            "oldest": self.timestamps[0] if self.timestamps else None,
            "newest": self.timestamps[-1] if self.timestamps else None
        }
    
    def __len__(self) -> int:
        """Return number of memories."""
        return len(self.memories)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"SemanticMemory({len(self.memories)} memories)"