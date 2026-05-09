"""
Working Memory - Layer 4

Task-specific context that's active while working on something.
Like your desk: everything you need for current task.

Example:
    memory = WorkingMemory()
    
    # Start task
    task_id = memory.start_task(
        name="Write blog post",
        context={"topic": "AI", "words": 1000}
    )
    
    # Track progress
    memory.add_subtask(task_id, "Research", status="done")
    memory.add_subtask(task_id, "Draft", status="in_progress")
    
    # Complete task (clears memory)
    memory.complete_task(task_id)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(Enum):
    """Task status options."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


@dataclass
class SubTask:
    """
    Individual step in a task.
    
    Components:
    - name: What to do
    - status: Current state
    - notes: Additional details
    - created_at: When added
    """
    name: str
    status: TaskStatus = TaskStatus.NOT_STARTED
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def __repr__(self):
        status_icons = {
            TaskStatus.NOT_STARTED: "⚪",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.BLOCKED: "🚫",
            TaskStatus.DONE: "✅",
            TaskStatus.CANCELLED: "❌"
        }
        icon = status_icons.get(self.status, "⚪")
        return f"{icon} {self.name}"


@dataclass
class Task:
    """
    Active task with context and sub-tasks.
    
    Components:
    - id: Unique identifier
    - name: Task description
    - context: Task-specific data
    - subtasks: List of steps
    - status: Current state
    - created_at: Start time
    - updated_at: Last modification
    """
    id: str
    name: str
    context: Dict[str, Any] = field(default_factory=dict)
    subtasks: List[SubTask] = field(default_factory=list)
    status: TaskStatus = TaskStatus.NOT_STARTED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __repr__(self):
        done = sum(1 for st in self.subtasks if st.status == TaskStatus.DONE)
        total = len(self.subtasks)
        progress = f"{done}/{total}" if total > 0 else "0/0"
        return f"Task({self.name}, progress={progress}, status={self.status.value})"


class WorkingMemory:
    """
    Task-specific context manager.
    
    Workflow:
    Start task → Add sub-tasks → Track progress →
    Update context → Complete/Cancel → Clear
    
    Unlike other layers:
    - Temporary (cleared when task done)
    - Task-scoped (one task at a time)
    - Mutable (constantly updated)
    
    Example:
        memory = WorkingMemory()
        
        # Start task
        task_id = memory.start_task(
            name="Analyze data",
            context={"file": "sales.csv"}
        )
        
        # Add steps
        memory.add_subtask(task_id, "Load data")
        memory.add_subtask(task_id, "Clean data")
        memory.add_subtask(task_id, "Generate report")
        
        # Update as you work
        memory.update_subtask_status(task_id, 0, "done")
        memory.update_context(task_id, {"rows": 1000})
        
        # Complete
        memory.complete_task(task_id)
    """
    
    def __init__(self):
        """Initialize empty working memory."""
        self.tasks: Dict[str, Task] = {}
        self._task_counter = 0
    
    def start_task(
        self,
        name: str,
        context: Dict[str, Any] = None
    ) -> str:
        """
        Start a new task.
        
        Args:
            name: Task description
            context: Task-specific data
        
        Returns:
            task_id: Unique identifier
        """
        self._task_counter += 1
        task_id = f"task_{self._task_counter}"
        
        task = Task(
            id=task_id,
            name=name,
            context=context or {},
            status=TaskStatus.IN_PROGRESS
        )
        
        self.tasks[task_id] = task
        
        print(f"🎯 Started task: {name}")
        print(f"   ID: {task_id}")
        
        return task_id
    
    def add_subtask(
        self,
        task_id: str,
        name: str,
        status: str = "not_started",
        notes: str = ""
    ) -> bool:
        """
        Add sub-task to existing task.
        
        Args:
            task_id: Parent task ID
            name: Sub-task name
            status: Initial status
            notes: Additional details
        
        Returns:
            True if added, False if task not found
        """
        task = self.tasks.get(task_id)
        if not task:
            print(f"❌ Task {task_id} not found")
            return False
        
        # Convert string to enum
        try:
            status_enum = TaskStatus(status)
        except ValueError:
            status_enum = TaskStatus.NOT_STARTED
        
        subtask = SubTask(
            name=name,
            status=status_enum,
            notes=notes
        )
        
        task.subtasks.append(subtask)
        task.updated_at = datetime.now()
        
        print(f"  ➕ Added: {subtask}")
        
        return True
    
    def update_subtask_status(
        self,
        task_id: str,
        subtask_index: int,
        status: str
    ) -> bool:
        """
        Update status of a sub-task.
        
        Args:
            task_id: Parent task ID
            subtask_index: Index in subtasks list
            status: New status
        
        Returns:
            True if updated, False otherwise
        """
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if subtask_index >= len(task.subtasks):
            return False
        
        try:
            status_enum = TaskStatus(status)
        except ValueError:
            return False
        
        task.subtasks[subtask_index].status = status_enum
        task.updated_at = datetime.now()
        
        print(f"  ✏️  Updated: {task.subtasks[subtask_index]}")
        
        return True
    
    def update_context(
        self,
        task_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update task context.
        
        Args:
            task_id: Task ID
            updates: New context data
        
        Returns:
            True if updated, False if task not found
        """
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        task.context.update(updates)
        task.updated_at = datetime.now()
        
        print(f"  📝 Context updated: {list(updates.keys())}")
        
        return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def get_current_task(self) -> Optional[Task]:
        """
        Get most recent active task.
        
        Returns:
            Latest in-progress task, or None
        """
        active = [
            t for t in self.tasks.values()
            if t.status == TaskStatus.IN_PROGRESS
        ]
        
        if not active:
            return None
        
        # Return most recently updated
        return sorted(active, key=lambda t: t.updated_at, reverse=True)[0]
    
    def complete_task(self, task_id: str) -> bool:
        """
        Mark task as complete and remove from working memory.
        
        Args:
            task_id: Task ID
        
        Returns:
            True if completed, False if not found
        """
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        task.status = TaskStatus.DONE
        
        print(f"✅ Completed: {task.name}")
        
        # Clear from working memory
        del self.tasks[task_id]
        
        return True
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel task and remove from working memory.
        
        Args:
            task_id: Task ID
        
        Returns:
            True if cancelled, False if not found
        """
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        task.status = TaskStatus.CANCELLED
        
        print(f"❌ Cancelled: {task.name}")
        
        # Clear from working memory
        del self.tasks[task_id]
        
        return True
    
    def get_progress(self, task_id: str) -> Optional[Dict]:
        """
        Get task progress summary.
        
        Args:
            task_id: Task ID
        
        Returns:
            Progress dict with counts and percentages
        """
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        total = len(task.subtasks)
        if total == 0:
            return {
                "total": 0,
                "done": 0,
                "in_progress": 0,
                "not_started": 0,
                "blocked": 0,
                "percent_complete": 0
            }
        
        done = sum(1 for st in task.subtasks if st.status == TaskStatus.DONE)
        in_progress = sum(1 for st in task.subtasks if st.status == TaskStatus.IN_PROGRESS)
        not_started = sum(1 for st in task.subtasks if st.status == TaskStatus.NOT_STARTED)
        blocked = sum(1 for st in task.subtasks if st.status == TaskStatus.BLOCKED)
        
        return {
            "total": total,
            "done": done,
            "in_progress": in_progress,
            "not_started": not_started,
            "blocked": blocked,
            "percent_complete": int((done / total) * 100)
        }
    
    def list_tasks(self) -> List[Task]:
        """Get all active tasks."""
        return list(self.tasks.values())
    
    def clear(self) -> None:
        """Clear all tasks (emergency reset)."""
        count = len(self.tasks)
        self.tasks.clear()
        self._task_counter = 0
        print(f"🧹 Cleared {count} tasks from working memory")
    
    def __len__(self) -> int:
        """Return number of active tasks."""
        return len(self.tasks)
    
    def __repr__(self) -> str:
        """String representation."""
        active = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        return f"WorkingMemory({active} active tasks)"