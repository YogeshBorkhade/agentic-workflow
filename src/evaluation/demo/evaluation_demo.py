"""
Evaluation & Metrics Demo
Shows how to measure agent quality and track performance
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.evaluation import (
    LLMJudge,
    SelfAssessment,
    MetricsTracker,
    EvaluationPipeline
)


def demo_1_llm_judge():
    """Demo 1: LLM as Judge - Evaluate agent output quality"""
    print("=" * 70)
    print("Demo 1: LLM as Judge")
    print("=" * 70)
    
    judge = LLMJudge()
    
    # Simulate agent output
    agent_output = "Tesla is an American electric vehicle company founded in 2003. The current CEO is Elon Musk."
    
    # Evaluate
    result = judge.evaluate(
        agent_name="ResearchAgent",
        agent_output=agent_output,
        original_query="Tell me about Tesla",
        ground_truth="Tesla is an EV company founded by Elon Musk",
        criteria=["accuracy", "completeness", "relevance"]
    )
    
    print(f"\n📊 Evaluation Result:")
    print(f"   Overall Score: {result.overall_score:.1f}/10")
    print(f"   Criteria Scores:")
    for criterion, score in result.criteria_scores.items():
        print(f"     • {criterion}: {score:.1f}/10")
    
    print(f"\n✅ Strengths:")
    for strength in result.strengths:
        print(f"     • {strength}")
    
    print(f"\n⚠️ Weaknesses:")
    for weakness in result.weaknesses:
        print(f"     • {weakness}")
    
    print(f"\n💭 Reasoning: {result.reasoning}")
    print(f"\n   Passes Threshold: {'✅ Yes' if result.passes_threshold else '❌ No'}")
    print()


def demo_2_self_assessment():
    """Demo 2: Self-Assessment - Agent evaluates own confidence"""
    print("=" * 70)
    print("Demo 2: Self-Assessment")
    print("=" * 70)
    
    assessor = SelfAssessment()
    
    # Case 1: High confidence output
    print("\n📝 Case 1: Detailed output with sources")
    output1 = """Tesla reported revenue of $96.8 billion in 2023, up 19% from 2022. 
    The company delivered 1.8 million vehicles. Main competitors include BYD, Ford, and GM."""
    
    result1 = assessor.assess(
        agent_name="ResearchAgent",
        agent_output=output1,
        sources=["tesla.com", "sec.gov", "reuters.com"]
    )
    
    print(f"   Confidence Score: {result1.overall_score:.1f}/10")
    print(f"   Assessment: {result1.reasoning}")
    print(f"   Needs Review: {'⚠️ Yes' if result1.needs_review else '✅ No'}")
    
    # Case 2: Low confidence output
    print("\n📝 Case 2: Brief, uncertain output")
    output2 = "Tesla makes electric cars. I'm not sure about exact numbers."
    
    result2 = assessor.assess(
        agent_name="ResearchAgent",
        agent_output=output2,
        sources=[]
    )
    
    print(f"   Confidence Score: {result2.overall_score:.1f}/10")
    print(f"   Assessment: {result2.reasoning}")
    print(f"   Gaps Identified:")
    for gap in result2.weaknesses:
        print(f"     • {gap}")
    print(f"   Needs Review: {'⚠️ Yes' if result2.needs_review else '✅ No'}")
    print()


def demo_3_metrics_tracking():
    """Demo 3: Performance Metrics - Track latency and cost"""
    print("=" * 70)
    print("Demo 3: Performance Metrics")
    print("=" * 70)
    
    tracker = MetricsTracker()
    
    # Simulate request flow
    print("\n🚀 Simulating request flow...\n")
    
    request_id = "req_001"
    tracker.start_request(request_id)
    
    # Track each agent
    tracker.track_agent(request_id, "ClarityAgent", latency_ms=120, tokens=50)
    print("   ✅ ClarityAgent: 120ms, 50 tokens")
    
    tracker.track_agent(request_id, "ResearchAgent", latency_ms=850, tokens=500)
    print("   ✅ ResearchAgent: 850ms, 500 tokens")
    
    tracker.track_agent(request_id, "ValidatorAgent", latency_ms=200, tokens=100)
    print("   ✅ ValidatorAgent: 200ms, 100 tokens")
    
    tracker.track_agent(request_id, "SynthesisAgent", latency_ms=300, tokens=200)
    print("   ✅ SynthesisAgent: 300ms, 200 tokens")
    
    # Complete request
    metrics = tracker.end_request(request_id, success=True, retry_count=0)
    
    print(f"\n📊 Request Metrics:")
    print(f"   Total Latency: {metrics.total_latency_ms:.0f}ms")
    print(f"   Total Tokens: {metrics.total_tokens}")
    print(f"   Estimated Cost: ${metrics.estimated_cost:.4f}")
    print(f"   Success: {'✅ Yes' if metrics.completed else '❌ No'}")
    print(f"   Retries: {metrics.retry_count}")
    
    print(f"\n⚡ Agent Breakdown:")
    for agent, latency in metrics.agent_latencies.items():
        tokens = metrics.token_breakdown[agent]
        print(f"     • {agent}: {latency:.0f}ms, {tokens} tokens")
    print()


def demo_4_aggregate_stats():
    """Demo 4: Aggregate Statistics - Track over time"""
    print("=" * 70)
    print("Demo 4: Aggregate Statistics")
    print("=" * 70)
    
    tracker = MetricsTracker()
    
    # Simulate multiple requests
    print("\n📊 Processing 5 requests...\n")
    
    for i in range(5):
        request_id = f"req_{i:03d}"
        tracker.start_request(request_id)
        
        # Random agent performance
        import random
        tracker.track_agent(request_id, "ResearchAgent", random.randint(500, 1000), random.randint(300, 600))
        tracker.track_agent(request_id, "SynthesisAgent", random.randint(200, 400), random.randint(100, 300))
        
        success = random.random() > 0.1  # 90% success rate
        tracker.end_request(request_id, success=success)
    
    # Get stats
    stats = tracker.get_stats()
    
    print("📈 Aggregate Statistics:")
    print(f"   Total Requests: {stats['total_requests']}")
    print(f"   Success Rate: {stats['success_rate']:.1f}%")
    print(f"   Avg Latency: {stats['avg_latency_ms']:.0f}ms")
    print(f"   Avg Cost per Request: ${stats['avg_cost']:.4f}")
    print(f"   Total Cost: ${stats['total_cost']:.4f}")
    print(f"   Total Tokens: {stats['total_tokens']:,}")
    print()


def demo_5_evaluation_pipeline():
    """Demo 5: Complete Pipeline - All evaluation methods"""
    print("=" * 70)
    print("Demo 5: Complete Evaluation Pipeline")
    print("=" * 70)
    
    pipeline = EvaluationPipeline()
    
    # Simulate multi-agent workflow
    agent_outputs = {
        "research": "Tesla is an American EV company founded in 2003...",
        "synthesis": "Based on research, Tesla leads the EV market..."
    }
    
    print("\n🔍 Evaluating multi-agent workflow...\n")
    
    results = pipeline.evaluate_request(
        request_id="req_123",
        agent_outputs=agent_outputs,
        original_query="Tell me about Tesla"
    )
    
    # Show all evaluation results
    for eval_name, result in results.items():
        print(f"📊 {eval_name}:")
        print(f"   Score: {result.overall_score:.1f}/10")
        print(f"   Method: {result.method.value}")
        print(f"   Passes: {'✅' if result.passes_threshold else '❌'}")
        print()


def demo_6_comparison():
    """Demo 6: Compare LLM Judge vs Self-Assessment"""
    print("=" * 70)
    print("Demo 6: LLM Judge vs Self-Assessment Comparison")
    print("=" * 70)
    
    judge = LLMJudge()
    assessor = SelfAssessment()
    
    output = "Tesla manufactures electric vehicles and energy products."
    
    # LLM Judge
    judge_result = judge.evaluate(
        agent_name="TestAgent",
        agent_output=output,
        original_query="What does Tesla make?"
    )
    
    # Self-Assessment
    self_result = assessor.assess(
        agent_name="TestAgent",
        agent_output=output,
        sources=["tesla.com"]
    )
    
    print(f"\n📊 Same Output, Two Methods:\n")
    print(f"   Output: '{output}'")
    print(f"\n   LLM Judge Score: {judge_result.overall_score:.1f}/10")
    print(f"     - Method: External evaluation")
    print(f"     - Reasoning: {judge_result.reasoning}")
    
    print(f"\n   Self-Assessment Score: {self_result.overall_score:.1f}/10")
    print(f"     - Method: Internal confidence")
    print(f"     - Reasoning: {self_result.reasoning}")
    
    print(f"\n💡 Insight: Use both for comprehensive quality assessment!")
    print()


if __name__ == "__main__":
    demo_1_llm_judge()
    demo_2_self_assessment()
    demo_3_metrics_tracking()
    demo_4_aggregate_stats()
    demo_5_evaluation_pipeline()
    demo_6_comparison()
    
    print("=" * 70)
    print("✅ All Evaluation demos complete!")
    print("=" * 70)