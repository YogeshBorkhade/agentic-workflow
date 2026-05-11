"""
Interactive HITL Demo - Real Human Approval Required!
You'll actually review and approve/reject agent outputs
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.hitl import HITLSystem, HITLConfig, TaskPriority, ApprovalStatus
import time


def print_separator():
    print("\n" + "=" * 70 + "\n")


def print_request_details(request):
    """Display approval request in a nice format"""
    print("┌" + "─" * 68 + "┐")
    print(f"│ {'APPROVAL REQUEST'.center(66)} │")
    print("├" + "─" * 68 + "┤")
    print(f"│ Request ID: {request.id[:30]}... │")
    print(f"│ Agent: {request.agent_name.ljust(54)} │")
    print(f"│ Task Type: {request.task_type.ljust(52)} │")
    print(f"│ Confidence: {request.confidence_score:.1%}".ljust(68) + " │")
    print(f"│ Priority: {request.priority.value.upper().ljust(56)} │")
    print("├" + "─" * 68 + "┤")
    print("│ CONTENT:".ljust(68) + " │")
    
    # Show content
    for key, value in request.content.items():
        line = f"│   {key}: {str(value)[:50]}"
        print(line.ljust(68) + " │")
    
    print("└" + "─" * 68 + "┘")


def get_user_decision():
    """Get human decision with validation"""
    print("\n🤔 What do you want to do?")
    print("  [a] Approve")
    print("  [r] Reject")
    print("  [e] Edit and approve")
    print("  [s] Skip (leave pending)")
    print("  [q] Quit demo")
    
    while True:
        choice = input("\nYour choice: ").lower().strip()
        if choice in ['a', 'r', 'e', 's', 'q']:
            return choice
        print("❌ Invalid choice. Please enter a, r, e, s, or q")


def interactive_demo_1():
    """Demo 1: Simple approval workflow"""
    print_separator()
    print("🎯 DEMO 1: Basic Approval Workflow")
    print_separator()
    
    hitl = HITLSystem()
    
    # Simulate agent output
    print("📊 ResearchAgent completed a query...")
    time.sleep(1)
    
    research_result = {
        "query": "What is the capital of France?",
        "answer": "The capital of France is Paris",
        "sources": ["wikipedia.org", "britannica.com"],
        "confidence": 0.85
    }
    
    print("✅ Agent produced this output:")
    print(f"   Answer: {research_result['answer']}")
    print(f"   Confidence: {research_result['confidence']:.0%}")
    
    # Submit for approval
    request_id = hitl.submit_for_approval(
        task_type="research_output",
        content=research_result,
        confidence=0.85,
        agent_name="ResearchAgent",
        original_query="What is the capital of France?"
    )
    
    # Show pending request
    print("\n⏳ Waiting for YOUR approval...")
    time.sleep(1)
    
    request = hitl.approval_queue[request_id]
    print_request_details(request)
    
    # Get human decision
    decision = get_user_decision()
    
    if decision == 'a':
        hitl.approve(request_id, reviewer_id="you", notes="Looks good!")
        print("\n✅ You APPROVED the request!")
        print("   ➜ Agent output will be sent to user")
        
    elif decision == 'r':
        reason = input("\n💬 Why are you rejecting? ")
        hitl.reject(request_id, reviewer_id="you", notes=reason)
        print("\n❌ You REJECTED the request!")
        print("   ➜ Agent output blocked, error returned to user")
        
    elif decision == 'e':
        print("\n✏️ Enter corrected answer:")
        new_answer = input("   New answer: ")
        edited_content = research_result.copy()
        edited_content['answer'] = new_answer
        edited_content['confidence'] = 1.0
        
        hitl.edit_and_approve(
            request_id,
            edited_content=edited_content,
            reviewer_id="you",
            notes="Fixed the answer"
        )
        print("\n✏️ You EDITED and APPROVED!")
        print(f"   Original: {research_result['answer']}")
        print(f"   Edited: {new_answer}")
        print("   ➜ Your edited version will be sent to user")
        
    elif decision == 's':
        print("\n⏭️ Skipped - request still pending")
        
    elif decision == 'q':
        print("\n👋 Exiting demo...")
        return False
    
    return True


def interactive_demo_2():
    """Demo 2: Multiple requests with priority"""
    print_separator()
    print("🎯 DEMO 2: Priority Queue - Review Multiple Requests")
    print_separator()
    
    config = HITLConfig(
        auto_approve_threshold=0.95,  # Only auto-approve very high confidence
        critical_keywords=["delete", "payment", "cancel"]
    )
    hitl = HITLSystem(config)
    
    # Create multiple agent outputs
    requests = [
        {
            "agent": "DataAgent",
            "task": "data_modification",
            "content": {"action": "delete 100 customer records", "reason": "cleanup"},
            "confidence": 0.88
        },
        {
            "agent": "ResearchAgent", 
            "task": "research_query",
            "content": {"query": "Best practices for ML", "answer": "Use cross-validation..."},
            "confidence": 0.72
        },
        {
            "agent": "AnalyticsAgent",
            "task": "report_generation",
            "content": {"report": "Q4 revenue: $5.2M, growth: 23%"},
            "confidence": 0.65
        }
    ]
    
    print("📊 Three agents have produced outputs...")
    time.sleep(1)
    
    # Submit all for approval
    request_ids = []
    for req_data in requests:
        request_id = hitl.submit_for_approval(
            task_type=req_data["task"],
            content=req_data["content"],
            confidence=req_data["confidence"],
            agent_name=req_data["agent"]
        )
        request_ids.append(request_id)
    
    # Show queue with priority ordering
    pending = hitl.get_pending_requests()
    
    print(f"\n📋 Approval Queue ({len(pending)} pending):")
    print("   Items sorted by priority (CRITICAL → HIGH → MEDIUM → LOW)\n")
    
    for i, req in enumerate(pending, 1):
        priority_emoji = {
            TaskPriority.CRITICAL: "🔴",
            TaskPriority.HIGH: "🟠", 
            TaskPriority.MEDIUM: "🟡",
            TaskPriority.LOW: "🟢"
        }
        emoji = priority_emoji[req.priority]
        print(f"   {i}. {emoji} [{req.priority.value.upper()}] {req.agent_name}")
        print(f"      Task: {req.task_type} | Confidence: {req.confidence_score:.0%}")
    
    print("\n⚠️ Notice: CRITICAL items appear first!")
    print("   (Contains 'delete' keyword → high priority)\n")
    
    # Review each request
    for request in pending:
        print_separator()
        print_request_details(request)
        
        decision = get_user_decision()
        
        if decision == 'a':
            hitl.approve(request.id, reviewer_id="you")
            print("\n✅ APPROVED")
            
        elif decision == 'r':
            reason = input("💬 Rejection reason: ")
            hitl.reject(request.id, reviewer_id="you", notes=reason)
            print("\n❌ REJECTED")
            
        elif decision == 's':
            print("\n⏭️ Skipped")
            continue
            
        elif decision == 'q':
            print("\n👋 Exiting...")
            return False
    
    return True


def interactive_demo_3():
    """Demo 3: Watch confidence-based routing in action"""
    print_separator()
    print("🎯 DEMO 3: Confidence-Based Routing")
    print_separator()
    
    hitl = HITLSystem()
    
    test_cases = [
        ("Very high confidence", 0.97, "should auto-approve"),
        ("High confidence", 0.88, "needs your review"),
        ("Medium confidence", 0.65, "needs your review"),
        ("Low confidence", 0.25, "should auto-reject")
    ]
    
    print("🧪 Testing different confidence levels...\n")
    
    for name, confidence, expected in test_cases:
        print(f"📊 Agent output: {name} ({confidence:.0%})")
        print(f"   Expected: {expected}")
        
        request_id = hitl.submit_for_approval(
            task_type="test",
            content={"test": name},
            confidence=confidence,
            agent_name="TestAgent"
        )
        
        time.sleep(0.5)
        
        # Check if it needed human review
        if request_id in hitl.approval_queue:
            print("   ✋ PAUSED - Waiting for YOUR approval")
            
            request = hitl.approval_queue[request_id]
            print_request_details(request)
            
            decision = get_user_decision()
            
            if decision == 'a':
                hitl.approve(request_id, reviewer_id="you")
                print("\n✅ You approved it!")
            elif decision == 'r':
                hitl.reject(request_id, reviewer_id="you")
                print("\n❌ You rejected it!")
            elif decision == 'q':
                return False
        else:
            # Auto-processed
            for req in hitl.history:
                if req.id == request_id:
                    if req.status == ApprovalStatus.AUTO_APPROVED:
                        print("   ✅ AUTO-APPROVED (confidence > 95%)")
                    elif req.status == ApprovalStatus.REJECTED:
                        print("   ❌ AUTO-REJECTED (confidence < 30%)")
        
        print()
    
    return True


def show_final_stats(hitl):
    """Show approval statistics at the end"""
    print_separator()
    print("📈 YOUR REVIEW SESSION STATS")
    print_separator()
    
    stats = hitl.get_stats()
    
    print(f"Total requests: {stats['total_requests']}")
    print(f"You approved: {stats['approved']}")
    print(f"You rejected: {stats['rejected']}")
    print(f"Auto-approved: {stats['auto_approved']}")
    print(f"Edited: {stats['edited']}")
    print(f"Still pending: {stats['pending']}")
    print(f"\nApproval rate: {stats['approval_rate']:.1f}%")
    
    if stats['approval_rate'] > 90:
        print("✅ Great! High-quality agent outputs")
    elif stats['approval_rate'] > 70:
        print("⚠️ Moderate quality - agents need improvement")
    else:
        print("❌ Low approval rate - agents need retraining")


def main():
    print("\n" + "=" * 70)
    print("🎮 INTERACTIVE HITL DEMO - You Are The Human!".center(70))
    print("=" * 70)
    
    print("\nIn this demo, YOU will:")
    print("  ✅ Review agent outputs")
    print("  ✅ Approve or reject them")
    print("  ✅ Edit incorrect results")
    print("  ✅ See how HITL protects users")
    
    input("\nPress ENTER to start...")
    
    hitl = HITLSystem()
    
    # Run demos
    demos = [
        ("Demo 1: Basic Approval", interactive_demo_1),
        ("Demo 2: Priority Queue", interactive_demo_2),
        ("Demo 3: Confidence Routing", interactive_demo_3)
    ]
    
    for demo_name, demo_func in demos:
        print(f"\n🎯 Starting {demo_name}...")
        time.sleep(1)
        
        if not demo_func():
            print("\n👋 Demo interrupted by user")
            break
        
        print(f"\n✅ {demo_name} complete!")
        
        continue_choice = input("\nContinue to next demo? (y/n): ").lower()
        if continue_choice != 'y':
            break
    
    print_separator()
    print("🎉 INTERACTIVE DEMO COMPLETE!")
    print_separator()
    print("\nNow you understand Human-in-the-Loop!")
    print("YOU were the human making the approval decisions 🤝")
    print("\nIn production:")
    print("  • This would be a web dashboard")
    print("  • Multiple reviewers can approve")
    print("  • Real-time notifications")
    print("  • Mobile app for on-the-go reviews")


if __name__ == "__main__":
    main()