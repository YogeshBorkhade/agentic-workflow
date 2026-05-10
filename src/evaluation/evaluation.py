"""
Evaluation & Metrics Layer
Measures agent quality, tracks performance, enables continuous improvement
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
import json


class EvaluationMethod(Enum):
    """Evaluation approach"""
    LLM_JUDGE = "llm_judge"
    SELF_ASSESSMENT = "self_assessment"
    HUMAN_REVIEW = "human_review"
    AUTOMATED_TEST = "automated_test"


class QualityCriteria(Enum):
    """Quality dimensions to evaluate"""
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    CLARITY = "clarity"
    FACTUALITY = "factuality"


@dataclass
class EvaluationResult:
    """Single evaluation result"""
    id: str
    request_id: str
    agent_name: str
    
    # Scores (0-10 scale)
    overall_score: float
    criteria_scores: Dict[str, float]  # {criteria: score}
    
    # Analysis
    strengths: List[str]
    weaknesses: List[str]
    reasoning: str
    
    # Metadata
    method: EvaluationMethod
    evaluated_at: datetime = field(default_factory=datetime.now)
    evaluator: str = "system"  # "system" or human evaluator ID
    
    # Flags
    passes_threshold: bool = False
    needs_review: bool = False


@dataclass
class PerformanceMetrics:
    """Performance tracking"""
    request_id: str
    
    # Timing
    total_latency_ms: float
    agent_latencies: Dict[str, float]  # {agent: ms}
    
    # Cost
    total_tokens: int
    token_breakdown: Dict[str, int]  # {agent: tokens}
    estimated_cost: float
    
    # Success
    completed: bool
    retry_count: int
    error: Optional[str] = None


class LLMJudge:
    """
    LLM as Judge - Uses LLM to evaluate agent outputs
    
    Usage:
        judge = LLMJudge()
        result = judge.evaluate(
            agent_output="Paris is the capital of France",
            ground_truth="Paris",
            criteria=["accuracy", "completeness"]
        )
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client  # Groq, OpenAI, etc.
        self.evaluation_history: List[EvaluationResult] = []
    
    def evaluate(
        self,
        agent_name: str,
        agent_output: str,
        original_query: str,
        ground_truth: Optional[str] = None,
        criteria: Optional[List[str]] = None,
        request_id: str = ""
    ) -> EvaluationResult:
        """
        Evaluate agent output quality
        
        Args:
            agent_name: Which agent produced this
            agent_output: The output to evaluate
            original_query: User's original question
            ground_truth: Known correct answer (if available)
            criteria: What to evaluate (accuracy, completeness, etc.)
            request_id: Link to original request
            
        Returns:
            Evaluation with scores and reasoning
        """
        if criteria is None:
            criteria = ["accuracy", "completeness", "relevance"]
        
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(
            original_query=original_query,
            agent_output=agent_output,
            ground_truth=ground_truth,
            criteria=criteria
        )
        
        # Get LLM judgment (mock for now, replace with real LLM call)
        judgment = self._call_llm_judge(prompt)
        
        # Parse scores
        criteria_scores = {}
        for criterion in criteria:
            criteria_scores[criterion] = judgment.get(criterion, 7.0)
        
        overall_score = sum(criteria_scores.values()) / len(criteria_scores)
        
        # Create result
        result = EvaluationResult(
            id=f"eval_{datetime.now().timestamp()}",
            request_id=request_id,
            agent_name=agent_name,
            overall_score=overall_score,
            criteria_scores=criteria_scores,
            strengths=judgment.get("strengths", []),
            weaknesses=judgment.get("weaknesses", []),
            reasoning=judgment.get("reasoning", ""),
            method=EvaluationMethod.LLM_JUDGE,
            passes_threshold=overall_score >= 7.0,
            needs_review=overall_score < 5.0
        )
        
        self.evaluation_history.append(result)
        return result
    
    def _build_evaluation_prompt(
        self,
        original_query: str,
        agent_output: str,
        ground_truth: Optional[str],
        criteria: List[str]
    ) -> str:
        """Build prompt for LLM judge"""
        prompt = f"""You are an expert evaluator assessing AI agent outputs.

Original Query: {original_query}

Agent Output:
{agent_output}
"""
        
        if ground_truth:
            prompt += f"\nGround Truth Answer: {ground_truth}\n"
        
        prompt += f"""
Evaluate the agent output on these criteria (score 0-10 for each):
{', '.join(criteria)}

Provide your evaluation as JSON:
{{
    "accuracy": <score>,
    "completeness": <score>,
    "relevance": <score>,
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "reasoning": "explanation of scores"
}}
"""
        return prompt
    
    def _call_llm_judge(self, prompt: str) -> Dict[str, Any]:
        """Call LLM to get judgment (mock for demo)"""
        # In production, call actual LLM:
        # response = self.llm_client.chat.completions.create(...)
        # return json.loads(response)
        
        # Mock response for demo
        return {
            "accuracy": 8.5,
            "completeness": 7.0,
            "relevance": 9.0,
            "strengths": ["Directly answers question", "Clear language"],
            "weaknesses": ["Could provide more context"],
            "reasoning": "Answer is correct and relevant but lacks detail"
        }
    
    def get_average_score(self, agent_name: Optional[str] = None) -> float:
        """Get average score across evaluations"""
        evals = self.evaluation_history
        if agent_name:
            evals = [e for e in evals if e.agent_name == agent_name]
        
        if not evals:
            return 0.0
        
        return sum(e.overall_score for e in evals) / len(evals)


class SelfAssessment:
    """
    Agent self-evaluates its own output
    
    Usage:
        assessor = SelfAssessment()
        confidence = assessor.assess(
            agent_output="Tesla was founded in 2003",
            sources=["wikipedia.org"]
        )
    """
    
    def assess(
        self,
        agent_name: str,
        agent_output: str,
        sources: List[str],
        request_id: str = ""
    ) -> EvaluationResult:
        """
        Agent evaluates its own output confidence
        
        Returns:
            Evaluation with confidence score and identified gaps
        """
        # Calculate confidence based on heuristics
        confidence = self._calculate_confidence(agent_output, sources)
        
        # Identify potential gaps
        gaps = self._identify_gaps(agent_output)
        
        result = EvaluationResult(
            id=f"self_{datetime.now().timestamp()}",
            request_id=request_id,
            agent_name=agent_name,
            overall_score=confidence * 10,  # Convert to 0-10 scale
            criteria_scores={"confidence": confidence * 10},
            strengths=["Self-aware assessment"],
            weaknesses=gaps,
            reasoning=f"Confidence: {confidence:.2%}",
            method=EvaluationMethod.SELF_ASSESSMENT,
            passes_threshold=confidence >= 0.7,
            needs_review=confidence < 0.5
        )
        
        return result
    
    def _calculate_confidence(self, output: str, sources: List[str]) -> float:
        """Calculate confidence score (0-1)"""
        confidence = 0.5  # Base
        
        # More sources = higher confidence
        if len(sources) >= 3:
            confidence += 0.2
        elif len(sources) >= 2:
            confidence += 0.1
        
        # Longer, detailed output = higher confidence
        if len(output) > 200:
            confidence += 0.15
        
        # Contains numbers/specifics = higher confidence
        if any(char.isdigit() for char in output):
            confidence += 0.1
        
        # Hedging language = lower confidence
        hedges = ["maybe", "possibly", "unclear", "uncertain"]
        if any(hedge in output.lower() for hedge in hedges):
            confidence -= 0.2
        
        return min(max(confidence, 0.0), 1.0)
    
    def _identify_gaps(self, output: str) -> List[str]:
        """Identify potential information gaps"""
        gaps = []
        
        if len(output) < 100:
            gaps.append("Response is brief, may lack detail")
        
        if "I don't know" in output.lower():
            gaps.append("Agent expressed uncertainty")
        
        if not any(char.isdigit() for char in output):
            gaps.append("No specific data or numbers provided")
        
        return gaps


class MetricsTracker:
    """
    Track performance and cost metrics
    
    Usage:
        tracker = MetricsTracker()
        tracker.start_request("req_123")
        # ... agents run ...
        tracker.end_request("req_123", success=True)
    """
    
    def __init__(self):
        self.active_requests: Dict[str, Dict[str, Any]] = {}
        self.completed_metrics: List[PerformanceMetrics] = []
    
    def start_request(self, request_id: str):
        """Start tracking a request"""
        self.active_requests[request_id] = {
            "start_time": datetime.now(),
            "agent_times": {},
            "token_counts": {}
        }
    
    def track_agent(
        self,
        request_id: str,
        agent_name: str,
        latency_ms: float,
        tokens: int
    ):
        """Track individual agent performance"""
        if request_id in self.active_requests:
            self.active_requests[request_id]["agent_times"][agent_name] = latency_ms
            self.active_requests[request_id]["token_counts"][agent_name] = tokens
    
    def end_request(
        self,
        request_id: str,
        success: bool,
        retry_count: int = 0,
        error: Optional[str] = None
    ) -> PerformanceMetrics:
        """Complete request tracking"""
        if request_id not in self.active_requests:
            raise ValueError(f"Request {request_id} not started")
        
        req = self.active_requests[request_id]
        end_time = datetime.now()
        total_latency = (end_time - req["start_time"]).total_seconds() * 1000
        
        total_tokens = sum(req["token_counts"].values())
        estimated_cost = total_tokens * 0.000001  # $1 per 1M tokens (adjust per model)
        
        metrics = PerformanceMetrics(
            request_id=request_id,
            total_latency_ms=total_latency,
            agent_latencies=req["agent_times"],
            total_tokens=total_tokens,
            token_breakdown=req["token_counts"],
            estimated_cost=estimated_cost,
            completed=success,
            retry_count=retry_count,
            error=error
        )
        
        self.completed_metrics.append(metrics)
        del self.active_requests[request_id]
        
        return metrics
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregate statistics"""
        if not self.completed_metrics:
            return {}
        
        total = len(self.completed_metrics)
        successful = sum(1 for m in self.completed_metrics if m.completed)
        
        avg_latency = sum(m.total_latency_ms for m in self.completed_metrics) / total
        avg_cost = sum(m.estimated_cost for m in self.completed_metrics) / total
        total_cost = sum(m.estimated_cost for m in self.completed_metrics)
        
        return {
            "total_requests": total,
            "success_rate": successful / total * 100,
            "avg_latency_ms": avg_latency,
            "avg_cost": avg_cost,
            "total_cost": total_cost,
            "total_tokens": sum(m.total_tokens for m in self.completed_metrics)
        }


class EvaluationPipeline:
    """
    Complete evaluation pipeline combining all methods
    
    Usage:
        pipeline = EvaluationPipeline()
        result = pipeline.evaluate_request(
            request_id="req_123",
            agent_outputs={"research": "...", "synthesis": "..."},
            original_query="What is Tesla?"
        )
    """
    
    def __init__(self):
        self.llm_judge = LLMJudge()
        self.self_assessor = SelfAssessment()
        self.metrics_tracker = MetricsTracker()
    
    def evaluate_request(
        self,
        request_id: str,
        agent_outputs: Dict[str, str],
        original_query: str,
        ground_truth: Optional[str] = None
    ) -> Dict[str, EvaluationResult]:
        """Evaluate all agent outputs for a request"""
        results = {}
        
        for agent_name, output in agent_outputs.items():
            # LLM judge evaluation
            judge_result = self.llm_judge.evaluate(
                agent_name=agent_name,
                agent_output=output,
                original_query=original_query,
                ground_truth=ground_truth,
                request_id=request_id
            )
            
            results[f"{agent_name}_judge"] = judge_result
            
            # Self-assessment
            self_result = self.self_assessor.assess(
                agent_name=agent_name,
                agent_output=output,
                sources=[],  # Would come from agent
                request_id=request_id
            )
            
            results[f"{agent_name}_self"] = self_result
        
        return results