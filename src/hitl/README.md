# 🤝 Human-in-the-Loop (HITL) Layer

A production-ready approval system for agentic workflows with confidence-based routing.

## 📋 Overview

```
┌─────────────────────────────────────────────────────┐
│  HITL Layer - Human Approval Checkpoints            │
│                                                      │
│  Agent Output → Confidence Check → Route Decision   │
│                                                      │
│  High (>95%)   → Auto-approve (fast path)          │
│  Medium (30-95%) → Human review (queue)            │
│  Low (<30%)    → Auto-reject or escalate           │
└─────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

```python
from src.hitl import HITLSystem, HITLConfig

# Initialize
hitl = HITLSystem()

# Agent produces output
result = {"answer": "Paris is the capital of France"}

# Submit for approval
request_id = hitl.submit_for_approval(
    task_type="research_output",
    content=result,
    confidence=0.85,
    agent_name="ResearchAgent"
)

# Human reviews (or auto-approved if confidence > 95%)
hitl.approve(request_id, reviewer_id="user_123")

# Get approved content
approved = hitl.get_approved_content(request_id)
```

## 🏗️ Architecture

### Core Components

**1. Approval Queue**
- Holds tasks awaiting human review
- Priority-based ordering (critical → high → medium → low)
- Timeout: 30 minutes → escalate
- Storage: In-memory (dev), Redis (prod)

**2. Auto-Approval Engine**
- High confidence (>95%) → skip human review
- Instant processing, no wait time
- Logged with "auto_approved" status
- Can disable per task type

**3. Priority System**
- **Critical:** Contains keywords (delete, payment, confidential)
- **High:** Low confidence (<50%) or flagged by agent
- **Medium:** Normal review (50-70% confidence)
- **Low:** High confidence (70-95%), routine check

**4. Review Actions**
- **Approve:** Accept as-is, continue workflow
- **Reject:** Block output, return error
- **Edit:** Fix errors, then approve
- **Escalate:** Send to senior reviewer

## 📊 Workflow Integration

### Before HITL
```
User → Clarity → Research → Validator → Synthesis → User
       (fully automated, no oversight)
```

### After HITL
```
User → Clarity → Research → Validator → 🛑 HITL → Synthesis → User
                                         (checkpoint)
```

### Injection Points

**Option 1: After Validator (recommended)**
```python
workflow.add_edge("validator", "hitl_checkpoint")
workflow.add_edge("hitl_checkpoint", "synthesis")
```
- Reviews raw research quality
- Catches bad data before formatting
- Faster to review (less polished)

**Option 2: After Synthesis**
```python
workflow.add_edge("synthesis", "hitl_checkpoint")
workflow.add_edge("hitl_checkpoint", "output")
```
- Reviews final formatted response
- What user will actually see
- Easier to judge quality

**Option 3: Both (high-risk operations)**
```python
workflow.add_edge("validator", "hitl_checkpoint_1")
workflow.add_edge("synthesis", "hitl_checkpoint_2")
```
- Double checkpoint for critical tasks
- E.g., financial transactions, data deletion

## 🔄 LangGraph Integration

```python
from src.hitl import create_hitl_node, HITLSystem
from langgraph.graph import StateGraph

# Initialize
hitl = HITLSystem()

# Create graph
workflow = StateGraph(ResearchState)

# Add nodes
workflow.add_node("research", research_agent)
workflow.add_node("hitl_checkpoint", create_hitl_node(hitl))
workflow.add_node("synthesis", synthesis_agent)

# Connect with HITL checkpoint
workflow.add_edge("research", "hitl_checkpoint")
workflow.add_edge("hitl_checkpoint", "synthesis")

# Compile
app = workflow.compile()
```

The HITL node:
1. Submits output for approval
2. Checks confidence score
3. Auto-approves if > threshold
4. Otherwise pauses workflow
5. Resumes after human decision

## 📈 Confidence-Based Routing

```python
config = HITLConfig(
    auto_approve_threshold=0.95,  # Auto-approve if > 95%
    auto_reject_threshold=0.3      # Auto-reject if < 30%
)

hitl = HITLSystem(config)
```

**Routing Logic:**

| Confidence | Action | Wait Time | Use Case |
|------------|--------|-----------|----------|
| > 95% | Auto-approve | 0ms | Simple facts, verified data |
| 70-95% | Human review (low priority) | ~5min | Normal queries |
| 30-70% | Human review (high priority) | ~2min | Complex research |
| < 30% | Auto-reject or escalate | 0ms | Uncertain results |

## 🎯 Priority System

### Auto-Detection

```python
# Critical keywords trigger high priority
critical_keywords = [
    "delete", "remove", "payment", "transaction",
    "confidential", "sensitive", "cancel"
]

# Low confidence = higher priority
if confidence < 0.5:
    priority = TaskPriority.HIGH
```

### Manual Override

```python
hitl.submit_for_approval(
    task_type="data_modification",
    content={"action": "update_records"},
    confidence=0.85,
    priority=TaskPriority.CRITICAL  # Force critical
)
```

## 💾 Data Models

### ApprovalRequest
```python
@dataclass
class ApprovalRequest:
    id: str                              # Unique request ID
    task_type: str                       # "research_output", "final_response"
    content: Dict[str, Any]              # The output to review
    confidence_score: float              # 0.0 to 1.0
    priority: TaskPriority               # LOW/MEDIUM/HIGH/CRITICAL
    
    status: ApprovalStatus               # PENDING/APPROVED/REJECTED
    created_at: datetime
    reviewed_at: Optional[datetime]
    reviewer_id: Optional[str]
    
    decision_notes: str                  # Why approved/rejected
    edited_content: Optional[Dict]       # If human edited
```

### ApprovalStatus
```python
class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"
    AUTO_APPROVED = "auto_approved"
    ESCALATED = "escalated"
```

## 📊 Monitoring

### Key Metrics

```python
stats = hitl.get_stats()

# Returns:
{
    "total_requests": 150,
    "approved": 85,
    "rejected": 10,
    "auto_approved": 45,      # 30% auto-approved
    "edited": 10,
    "pending": 5,
    "approval_rate": 93.3      # High quality
}
```

### What to Track

**Approval Rate:** % approved vs rejected
- Target: >90%
- Low rate = agent quality issues

**Auto-Approval %:** How many skip human
- Target: 60-80%
- Too low = wasting human time
- Too high = missing errors

**Review Time:** Avg minutes to decision
- Target: <5 minutes
- High = need more reviewers

**Edit Rate:** How often humans fix errors
- Target: <15%
- High = agent needs retraining

## 🔧 Configuration

### Development (Fast, No Overhead)
```python
config = HITLConfig(
    auto_approve_threshold=0.90,  # Lenient
    timeout_minutes=5,             # Short timeout
    enable_escalation=False        # No escalation
)
```

### Production (Safe, Quality-Focused)
```python
config = HITLConfig(
    auto_approve_threshold=0.95,   # Strict
    timeout_minutes=30,            # Longer timeout
    enable_escalation=True,        # Enable escalation
    escalation_email="team@company.com",
    critical_keywords=[
        "delete", "payment", "confidential",
        "cancel", "refund", "terminate"
    ]
)
```

## 🎨 UI Dashboard (Future)

Build a review interface:

```
┌─────────────────────────────────────────┐
│  Approval Queue (5 pending)             │
├─────────────────────────────────────────┤
│  🔴 CRITICAL                            │
│  Delete customer records                 │
│  Confidence: 87% | Agent: DataAgent     │
│  [Approve] [Reject] [Edit]              │
├─────────────────────────────────────────┤
│  🟠 HIGH                                │
│  Research: Uncertain financial data      │
│  Confidence: 45% | Agent: ResearchAgent │
│  [Approve] [Reject] [Edit]              │
└─────────────────────────────────────────┘
```

Features needed:
- Real-time queue updates (WebSocket)
- Bulk approval for routine items
- Search/filter by agent, task type
- Historical review logs
- Performance analytics

## 🚨 Error Handling

### Timeout Handling
```python
# After 30 minutes, escalate
if time_elapsed > config.timeout_minutes:
    request.status = ApprovalStatus.ESCALATED
    notify_senior_reviewer(request)
```

### Escalation
```python
# Manual escalation
hitl.escalate(
    request_id,
    reason="Too complex for standard review",
    escalate_to="senior_reviewer@company.com"
)
```

### Fallback
```python
# If no response after escalation
if still_no_response:
    # Option 1: Auto-reject (safe)
    hitl.reject(request_id, notes="Timeout: no review")
    
    # Option 2: Auto-approve (risky)
    hitl.approve(request_id, notes="Timeout: auto-approved")
```

## 📝 Best Practices

### 1. Set Appropriate Thresholds
```python
# Too lenient (90%) = more errors slip through
# Too strict (99%) = everything needs review
# Sweet spot: 95-97%
```

### 2. Review Sample of Auto-Approved
```python
# Audit 5% of auto-approved items
# Ensure quality remains high
# Adjust threshold if errors found
```

### 3. Track Edit Patterns
```python
# If humans frequently edit same error type
# → Retrain agent on those cases
# → Update validation rules
```

### 4. Define Clear SLAs
```python
# Critical: 5 minutes
# High: 15 minutes  
# Medium: 30 minutes
# Low: 2 hours
```

### 5. Async Reviews
```python
# Don't block workflow for non-critical items
# Use webhooks or polling for async approval
# Show user: "Pending approval, we'll notify you"
```

## 🔮 Future Enhancements

- [ ] **Active Learning:** Train on approved edits
- [ ] **Confidence Calibration:** Improve scoring accuracy
- [ ] **Multi-Reviewer:** Require 2+ approvals for critical
- [ ] **Review Templates:** Pre-filled notes for common cases
- [ ] **Mobile App:** Approve on-the-go
- [ ] **Slack Integration:** Approve via Slack reactions
- [ ] **A/B Testing:** Compare auto vs human quality
- [ ] **Explainability:** Show why confidence is X%

## 📚 Examples

See `demos/hitl_demo.py` for comprehensive examples:

1. Basic approval workflow
2. Auto-approval (high confidence)
3. Auto-rejection (low confidence)
4. Edit and approve
5. Priority queue management
6. Statistics tracking
7. LangGraph integration

## 🐛 Troubleshooting

**Queue growing too large?**
- Lower auto-approve threshold (more auto-approvals)
- Add more reviewers
- Increase timeout (items escalate faster)

**Too many auto-rejections?**
- Review agent output quality
- Retrain agents
- Lower auto-reject threshold

**Humans editing too often?**
- Agent needs better training
- Validation rules too loose
- Add more validation checks

**Approval rate too low?**
- Agent quality issues
- Thresholds too strict
- Review criteria unclear

## 📄 License

Part of the Agentic AI Production System

---

**Version:** 1.0.0  
**Last Updated:** May 2026  
**Status:** Production Ready ✅