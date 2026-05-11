"""
Human-in-the-Loop (HITL) Layer
Version 1.0.0
"""

from .hitl import (
    HITLSystem,
    HITLConfig,
    ApprovalRequest,
    ApprovalStatus,
    TaskPriority,
    create_hitl_node  # LangGraph integration
)

__version__ = "1.0.0"

__all__ = [
    "HITLSystem",
    "HITLConfig", 
    "ApprovalRequest",
    "ApprovalStatus",
    "TaskPriority",
    "create_hitl_node"
]