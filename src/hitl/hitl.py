"""
Human-in-the-Loop (HITL) Layer
Adds approval checkpoints in agentic workflows
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
import uuid


class ApprovalStatus(Enum):
    """Status of approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"
    AUTO_APPROVED = "auto_approved"
    ESCALATED = "escalated"


class TaskPriority(Enum):
    """Priority levels for human review"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ApprovalRequest:
    """Single approval request in the queue"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = ""  # "research_output", "final_response", "data_modification"
    content: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0  # 0.0 to 1.0
    priority: TaskPriority = TaskPriority.MEDIUM
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[str] = None
    
    # Status
    status: ApprovalStatus = ApprovalStatus.PENDING
    decision_notes: str = ""
    edited_content: Optional[Dict[str, Any]] = None
    
    # Context
    agent_name: str = ""
    original_query: str = ""
    execution_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HITLConfig:
    """Configuration for HITL system"""
    # Auto-approval thresholds
    auto_approve_threshold: float = 0.95  # Auto-approve if confidence > 95%
    auto_reject_threshold: float = 0.3    # Auto-reject if confidence < 30%
    
    # Queue settings
    max_queue_size: int = 100
    timeout_minutes: int = 30  # How long to wait before escalation
    
    # Priority rules
    critical_keywords: List[str] = field(default_factory=lambda: [
        "delete", "remove", "payment", "transaction", "confidential"
    ])
    
    # Escalation
    enable_escalation: bool = True
    escalation_email: Optional[str] = None


class HITLSystem:
    """
    Human-in-the-Loop approval system
    
    Usage:
        hitl = HITLSystem()
        
        # Agent generates output
        result = research_agent.run(query)
        
        # Submit for approval
        request_id = hitl.submit_for_approval(
            task_type="research_output",
            content={"results": result},
            confidence=0.85,
            agent_name="ResearchAgent"
        )
        
        # Wait for human decision
        approved_result = hitl.wait_for_approval(request_id)
    """
    
    def __init__(self, config: Optional[HITLConfig] = None):
        self.config = config or HITLConfig()
        self.approval_queue: Dict[str, ApprovalRequest] = {}
        self.history: List[ApprovalRequest] = []
    
    def submit_for_approval(
        self,
        task_type: str,
        content: Dict[str, Any],
        confidence: float,
        agent_name: str,
        original_query: str = "",
        priority: Optional[TaskPriority] = None
    ) -> str:
        """
        Submit task for human approval
        
        Returns:
            request_id: ID to track this approval request
        """
        # Determine priority
        if priority is None:
            priority = self._calculate_priority(content, confidence)
        
        request = ApprovalRequest(
            task_type=task_type,
            content=content,
            confidence_score=confidence,
            priority=priority,
            agent_name=agent_name,
            original_query=original_query
        )
        
        # Auto-approve/reject based on thresholds
        if confidence >= self.config.auto_approve_threshold:
            request.status = ApprovalStatus.AUTO_APPROVED
            request.reviewed_at = datetime.now()
            request.decision_notes = "Auto-approved: High confidence"
            self.history.append(request)
            return request.id
        
        if confidence <= self.config.auto_reject_threshold:
            request.status = ApprovalStatus.REJECTED
            request.reviewed_at = datetime.now()
            request.decision_notes = "Auto-rejected: Low confidence"
            self.history.append(request)
            return request.id
        
        # Add to queue
        self.approval_queue[request.id] = request
        print(f"✋ HITL: Waiting for approval - {request.id}")
        return request.id
    
    def get_pending_requests(
        self,
        priority: Optional[TaskPriority] = None
    ) -> List[ApprovalRequest]:
        """Get all pending approval requests"""
        requests = [
            req for req in self.approval_queue.values()
            if req.status == ApprovalStatus.PENDING
        ]
        
        if priority:
            requests = [r for r in requests if r.priority == priority]
        
        # Sort by priority (critical first) then by time
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        requests.sort(key=lambda r: (priority_order[r.priority], r.created_at))
        
        return requests
    
    def approve(
        self,
        request_id: str,
        reviewer_id: str = "human",
        notes: str = ""
    ) -> bool:
        """Approve a request"""
        if request_id not in self.approval_queue:
            return False
        
        request = self.approval_queue[request_id]
        request.status = ApprovalStatus.APPROVED
        request.reviewed_at = datetime.now()
        request.reviewer_id = reviewer_id
        request.decision_notes = notes
        
        # Move to history
        self.history.append(request)
        del self.approval_queue[request_id]
        
        print(f"✅ Approved: {request_id}")
        return True
    
    def reject(
        self,
        request_id: str,
        reviewer_id: str = "human",
        notes: str = ""
    ) -> bool:
        """Reject a request"""
        if request_id not in self.approval_queue:
            return False
        
        request = self.approval_queue[request_id]
        request.status = ApprovalStatus.REJECTED
        request.reviewed_at = datetime.now()
        request.reviewer_id = reviewer_id
        request.decision_notes = notes
        
        # Move to history
        self.history.append(request)
        del self.approval_queue[request_id]
        
        print(f"❌ Rejected: {request_id}")
        return True
    
    def edit_and_approve(
        self,
        request_id: str,
        edited_content: Dict[str, Any],
        reviewer_id: str = "human",
        notes: str = ""
    ) -> bool:
        """Edit content and approve"""
        if request_id not in self.approval_queue:
            return False
        
        request = self.approval_queue[request_id]
        request.status = ApprovalStatus.EDITED
        request.edited_content = edited_content
        request.reviewed_at = datetime.now()
        request.reviewer_id = reviewer_id
        request.decision_notes = notes
        
        # Move to history
        self.history.append(request)
        del self.approval_queue[request_id]
        
        print(f"✏️ Edited and approved: {request_id}")
        return True
    
    def get_approved_content(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get approved content (original or edited)"""
        # Check history
        for request in self.history:
            if request.id == request_id:
                if request.status == ApprovalStatus.APPROVED:
                    return request.content
                elif request.status == ApprovalStatus.EDITED:
                    return request.edited_content
                elif request.status == ApprovalStatus.AUTO_APPROVED:
                    return request.content
                else:
                    return None
        return None
    
    def is_approved(self, request_id: str) -> bool:
        """Check if request was approved"""
        for request in self.history:
            if request.id == request_id:
                return request.status in [
                    ApprovalStatus.APPROVED,
                    ApprovalStatus.EDITED,
                    ApprovalStatus.AUTO_APPROVED
                ]
        
        # Still in queue = not approved yet
        return False
    
    def _calculate_priority(
        self,
        content: Dict[str, Any],
        confidence: float
    ) -> TaskPriority:
        """Auto-calculate priority based on content and confidence"""
        # Check for critical keywords
        content_str = str(content).lower()
        for keyword in self.config.critical_keywords:
            if keyword in content_str:
                return TaskPriority.CRITICAL
        
        # Low confidence = higher priority for human review
        if confidence < 0.5:
            return TaskPriority.HIGH
        elif confidence < 0.7:
            return TaskPriority.MEDIUM
        else:
            return TaskPriority.LOW
    
    def get_stats(self) -> Dict[str, Any]:
        """Get approval statistics"""
        total = len(self.history)
        if total == 0:
            return {
                "total_requests": 0,
                "approved": 0,
                "rejected": 0,
                "auto_approved": 0,
                "pending": len(self.approval_queue)
            }
        
        approved = sum(1 for r in self.history if r.status == ApprovalStatus.APPROVED)
        rejected = sum(1 for r in self.history if r.status == ApprovalStatus.REJECTED)
        auto_approved = sum(1 for r in self.history if r.status == ApprovalStatus.AUTO_APPROVED)
        edited = sum(1 for r in self.history if r.status == ApprovalStatus.EDITED)
        
        return {
            "total_requests": total,
            "approved": approved,
            "rejected": rejected,
            "auto_approved": auto_approved,
            "edited": edited,
            "pending": len(self.approval_queue),
            "approval_rate": (approved + auto_approved + edited) / total * 100
        }


# ============================================================================
# Integration with LangGraph
# ============================================================================

def create_hitl_node(hitl_system: HITLSystem):
    """
    Create a LangGraph node that pauses for human approval
    
    Usage in LangGraph:
        from langgraph.graph import StateGraph
        
        hitl = HITLSystem()
        
        workflow = StateGraph(ResearchState)
        workflow.add_node("research", research_agent)
        workflow.add_node("hitl_checkpoint", create_hitl_node(hitl))
        workflow.add_node("synthesis", synthesis_agent)
        
        workflow.add_edge("research", "hitl_checkpoint")
        workflow.add_edge("hitl_checkpoint", "synthesis")
    """
    
    def hitl_checkpoint(state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node that pauses for approval"""
        
        # Submit for approval
        request_id = hitl_system.submit_for_approval(
            task_type="agent_output",
            content=state.get("results", {}),
            confidence=state.get("confidence", 0.5),
            agent_name=state.get("current_agent", "unknown"),
            original_query=state.get("query", "")
        )
        
        # In production: this would pause and wait for async approval
        # For demo: we'll simulate instant approval
        # Real implementation uses webhooks or polling
        
        # Check if auto-approved
        if hitl_system.is_approved(request_id):
            approved_content = hitl_system.get_approved_content(request_id)
            state["results"] = approved_content
            state["hitl_approved"] = True
        else:
            # Still pending - in production, this throws InterruptException
            # LangGraph would pause here and resume after approval
            state["hitl_pending"] = True
            state["hitl_request_id"] = request_id
        
        return state
    
    return hitl_checkpoint