# 📊 Evaluation & Metrics Layer

Measure agent quality, track performance, enable continuous improvement.

## 🚀 Quick Start

```python
from src.evaluation import EvaluationPipeline

pipeline = EvaluationPipeline()

# Evaluate agent output
result = pipeline.evaluate_request(
    request_id="req_123",
    agent_outputs={"research": "Tesla is..."},
    original_query="Tell me about Tesla"
)

# result contains LLM judge + self-assessment scores
```

## 🏗️ Components

### 1. LLM as Judge
Evaluates output quality using another LLM:
```python
from src.evaluation import LLMJudge

judge = LLMJudge()
result = judge.evaluate(
    agent_name="ResearchAgent",
    agent_output="Paris is the capital...",
    original_query="What is the capital of France?",
    criteria=["accuracy", "completeness", "relevance"]
)

print(f"Score: {result.overall_score}/10")
print(f"Passes: {result.passes_threshold}")
```

### 2. Self-Assessment
Agent evaluates own confidence:
```python
from src.evaluation import SelfAssessment

assessor = SelfAssessment()
result = assessor.assess(
    agent_name="ResearchAgent",
    agent_output="Tesla reported $96B revenue...",
    sources=["tesla.com", "sec.gov"]
)

if result.needs_review:
    print("⚠️ Low confidence - send to human review")
```

### 3. Metrics Tracking
Track performance and cost:
```python
from src.evaluation import MetricsTracker

tracker = MetricsTracker()

tracker.start_request("req_001")
tracker.track_agent("req_001", "ResearchAgent", latency_ms=850, tokens=500)
metrics = tracker.end_request("req_001", success=True)

print(f"Latency: {metrics.total_latency_ms}ms")
print(f"Cost: ${metrics.estimated_cost}")
```

## 📈 Key Metrics

| Metric | Target | How to Track |
|--------|--------|--------------|
| Accuracy | >95% | LLM Judge |
| Completeness | >90% | LLM Judge |
| Hallucination Rate | <2% | LLM Judge + Human Spot Check |
| Latency | <5s | MetricsTracker |
| Success Rate | >99% | MetricsTracker |
| Cost per Query | <$0.10 | MetricsTracker |

## 🔗 Integration

Add to your workflow:
```python
# In graph.py after each agent completes

# Track performance
tracker.track_agent(state["request_id"], "ResearchAgent", latency, tokens)

# Evaluate quality
result = judge.evaluate(
    agent_name="ResearchAgent",
    agent_output=state["research_findings"],
    original_query=state["current_query"]
)

# Flag low quality for HITL
if result.overall_score < 5.0:
    state["needs_review"] = True
```

## 📊 Evaluation Strategy

**Continuous (100%):** LLM judge + self-assessment on every request  
**Periodic (5-10%):** Human evaluation weekly  
**Pre-deploy:** Automated regression tests  

## 🎯 Best Practices

1. **Combine methods:** Use LLM judge + self-assessment together
2. **Track over time:** Monitor trends, not just individual scores
3. **Set thresholds:** Auto-flag outputs below quality threshold for HITL
4. **A/B test:** Compare evaluation methods to find best approach
5. **Calibrate:** Use human evals to validate automated scores

---

**Version:** 1.0.0  
**Status:** Production Ready ✅