# 🧠 Memory System - 4 Layer Architecture

A production-ready memory system for AI agents with 4 specialized layers.

## 📋 Overview

```
┌─────────────────────────────────────────────────────┐
│  Layer 1: Conversational Memory                     │
│  → Recent messages (sliding window)                 │
│  → Use: What just happened?                         │
├─────────────────────────────────────────────────────┤
│  Layer 2: Semantic Memory                           │
│  → Knowledge base (vector search)                   │
│  → Use: What do I know?                             │
├─────────────────────────────────────────────────────┤
│  Layer 3: Episodic Memory                           │
│  → Important events (importance filtered)           │
│  → Use: What's important about the user?            │
├─────────────────────────────────────────────────────┤
│  Layer 4: Working Memory                            │
│  → Current tasks (temporary)                        │
│  → Use: What am I working on right now?             │
└─────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

```python
from src.memory import (
    ConversationalMemory,
    SemanticMemory,
    EpisodicMemory,
    WorkingMemory
)

# Layer 1: Recent context
conv_memory = ConversationalMemory(max_messages=10)
conv_memory.add_message("user", "Hello!")

# Layer 2: Knowledge base
semantic_memory = SemanticMemory()
semantic_memory.add("Paris is the capital of France")
results = semantic_memory.search("France capital", top_k=3)

# Layer 3: Important events
episodic_memory = EpisodicMemory(min_importance=0.5)
episodic_memory.record(
    "User is allergic to peanuts",
    importance=0.95,
    tags=["health", "allergy"]
)

# Layer 4: Current task
working_memory = WorkingMemory()
task_id = working_memory.start_task("Write blog post")
working_memory.add_subtask(task_id, "Research")
```

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run demos
python src/memory/demos/conversational_demo.py
python src/memory/demos/semantic_demo.py
python src/memory/demos/episodic_demo.py
python src/memory/demos/working_demo.py
```

## 🏗️ Architecture

### Layer 1: Conversational Memory

**Purpose:** Short-term context for active conversations

**Storage:**
- Dev: Python list (RAM)
- Prod: In-memory cache (RAM)

**Capacity:** Last 10 messages

**Lifecycle:**
1. Created when conversation starts
2. Updated on every message
3. Oldest dropped when limit reached (FIFO)
4. Destroyed when session ends

**Use Cases:**
- Maintaining conversation context
- Understanding current topic
- Providing coherent responses

---

### Layer 2: Semantic Memory

**Purpose:** Long-term knowledge base with semantic search

**Storage:**
- Dev: Python dict + NumPy (RAM)
- Prod: Vector DB (Pinecone, Weaviate, Qdrant)

**Capacity:** Unlimited (1M+ items)

**Lifecycle:**
1. Created at system startup
2. Updated when knowledge added
3. Text → embeddings → stored
4. Persists forever (prod) or session (dev)

**Use Cases:**
- Answering factual questions
- Finding related information
- Building knowledge base

---

### Layer 3: Episodic Memory

**Purpose:** Important events and user preferences over time

**Storage:**
- Dev: Python list + dataclass (RAM)
- Prod: Vector DB + metadata

**Capacity:** 10K+ episodes

**Lifecycle:**
1. Created at system startup
2. Event → scored (0.0-1.0)
3. If > threshold → stored with tags
4. Persists forever across sessions

**Use Cases:**
- User preferences
- Critical information
- Important decisions
- Building user profiles

---

### Layer 4: Working Memory

**Purpose:** Task-specific context and progress tracking

**Storage:**
- Dev: Python dict (RAM)
- Prod: Redis / In-memory

**Capacity:** Current task only

**Lifecycle:**
1. Created when task starts
2. Updated during task execution
3. Cleared when task completes/cancels
4. Temporary (task-scoped)

**Use Cases:**
- Multi-step task execution
- Progress tracking
- Context switching between tasks
- Resume after interruption

## 🔄 Integration Pattern

```python
class Agent:
    def __init__(self):
        # Initialize all 4 layers
        self.conv = ConversationalMemory()
        self.semantic = SemanticMemory()
        self.episodic = EpisodicMemory()
        self.working = WorkingMemory()
    
    def process_message(self, user_message: str):
        # Layer 1: Add to conversation
        self.conv.add_message("user", user_message)
        
        # Layer 2: Search knowledge
        knowledge = self.semantic.search(user_message, top_k=5)
        
        # Layer 3: Check important user info
        user_prefs = self.episodic.get_by_tag("preference")
        
        # Layer 4: Track task progress
        current_task = self.working.get_current_task()
        
        # Generate response using all layers
        response = self.generate_response(
            recent_context=self.conv.get_recent_context(),
            knowledge=knowledge,
            user_info=user_prefs,
            task_state=current_task
        )
        
        return response
```

## 📊 Storage Comparison

| Layer | Dev Storage | Prod Storage | Persistent | Capacity |
|-------|-------------|--------------|------------|----------|
| 1. Conversational | Python list | In-memory | No | 10 msgs |
| 2. Semantic | NumPy array | Vector DB | Yes | Unlimited |
| 3. Episodic | Python list | Vector DB | Yes | 10K+ |
| 4. Working | Python dict | Redis | No | 1 task |

## 💰 Cost Analysis

**Development (In-Memory):**
- Cost: $0/month
- Setup: Zero
- Capacity: Limited by RAM
- Best for: Learning, prototyping, testing

**Production (Database):**
- Cost: $50-100/month (Vector DB + Redis)
- Setup: Moderate (API keys, configuration)
- Capacity: Millions of items
- Best for: Production apps, multiple users

## 🎯 When to Use Each Layer

```
Query: "What did I say 2 messages ago?"
→ Layer 1 (Conversational)

Query: "Tell me about artificial intelligence"
→ Layer 2 (Semantic)

Query: "What are my dietary restrictions?"
→ Layer 3 (Episodic)

Query: "What step am I on for my current task?"
→ Layer 4 (Working)
```

## 🧪 Running Tests

```bash
# Run all demos
python src/memory/demos/conversational_demo.py
python src/memory/demos/semantic_demo.py
python src/memory/demos/episodic_demo.py
python src/memory/demos/working_demo.py
```

## 📚 Design Rationale

**Why 4 layers?**

Each layer solves a specific problem that others can't:

1. **Layer 1** - Recent context without overwhelming with history
2. **Layer 2** - Find knowledge semantically, not just keywords
3. **Layer 3** - Filter important from trivial automatically
4. **Layer 4** - Track progress without polluting long-term memory

**Why not just one big database?**

Different access patterns need different optimizations:
- Layer 1: O(1) append, recent retrieval
- Layer 2: O(log n) semantic search
- Layer 3: O(n) tag filtering, importance sorting
- Layer 4: O(1) current task access

## 🔮 Future Enhancements

- [ ] Vector DB integration (Pinecone, Weaviate)
- [ ] Redis cache for Layer 4
- [ ] Cross-layer search
- [ ] Memory compression
- [ ] Importance auto-scoring (ML model)
- [ ] Multi-user isolation
- [ ] Memory consolidation (move important Layer 1 → Layer 3)

## 📖 Additional Resources

- [Semantic Search Tutorial](https://www.sbert.net/)
- [Vector Databases Comparison](https://www.pinecone.io/)
- [Memory Systems in AI](https://arxiv.org/)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit pull request

## 📄 License

MIT License - feel free to use in your projects!

## 👥 Authors

Built as part of the Agentic AI Research Project.

---

**Version:** 4.0.0  
**Last Updated:** May 2025  
**Status:** Production Ready ✅