"""
Router Node - Step 7

This node acts as a traffic controller for the teaching workflow.
It decides the next action based on current teaching state:
- "plan": Continue with next concept (normal flow)
- "assess": All concepts taught, move to assessment
- "re-explain": Student is confused, needs feedback/re-explanation

No LLM required - pure conditional logic based on state tracking.
"""

from typing import Dict, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from state import TeachingState


def router_node(state: TeachingState) -> Dict[str, Any]:
    """
    Routes the teaching workflow based on current state.
    
    Decision Logic:
    1. Check if all concepts are taught -> "assess"
    2. Check if student is confused -> "re-explain"
    3. Otherwise -> "plan" (continue normal teaching)
    
    Args:
        state: Current teaching state with concepts and progress tracking
        
    Returns:
        Dict with updated next_action field
        
    State Fields Used:
        - concepts: List of concepts to teach
        - current_concept_index: Which concept we're on (0-based)
        - understanding_status: Student's comprehension status
            - is_confused: Boolean flag set by Understanding Checker Node
    """
    
    print("\n" + "="*60)
    print("ROUTER NODE - Deciding Next Action")
    print("="*60)
    
    # Extract relevant state
    concepts = state.get("concepts", [])
    current_index = state.get("current_concept_index", 0)
    understanding_status = state.get("understanding_status", {})
    
    # Display current state
    print(f"\n📊 Current State:")
    print(f"   Total Concepts: {len(concepts)}")
    print(f"   Current Index: {current_index}")
    print(f"   Concepts Remaining: {len(concepts) - current_index}")
    
    if understanding_status:
        print(f"\n🧠 Understanding Status:")
        print(f"   Is Confused: {understanding_status.get('is_confused', False)}")
        print(f"   Confidence Level: {understanding_status.get('confidence_level', 'N/A')}")
        print(f"   Last Interaction: {understanding_status.get('last_interaction_quality', 'N/A')}")
    
    # DECISION LOGIC
    
    # Decision 1: All concepts taught?
    if current_index >= len(concepts):
        next_action = "assess"
        reason = "All concepts have been taught. Moving to assessment phase."
        print(f"\n✅ Decision: ASSESS")
        print(f"   Reason: {reason}")
        print(f"   Next: Generate MCQ questions and test student understanding")
    
    # Decision 2: Student confused?
    elif understanding_status.get("is_confused", False):
        next_action = "re-explain"
        reason = "Student is showing signs of confusion. Need to provide feedback and re-explanation."
        print(f"\n🔄 Decision: RE-EXPLAIN")
        print(f"   Reason: {reason}")
        print(f"   Next: Provide feedback and simplify explanation")
    
    # Decision 3: Normal flow
    else:
        next_action = "plan"
        reason = "Student is progressing well. Continue with normal teaching flow."
        print(f"\n➡️  Decision: PLAN")
        print(f"   Reason: {reason}")
        
        # Show which concept we're about to plan for
        if current_index < len(concepts):
            current_concept = concepts[current_index]
            print(f"   Next Concept: '{current_concept.get('name', 'Unknown')}'")
            print(f"   Next: Generate lesson plan with takeaways and probing questions")
        else:
            print(f"   Next: Plan next teaching iteration")
    
    print("\n" + "="*60)
    print(f"🎯 ROUTING COMPLETE: next_action = '{next_action}'")
    print("="*60 + "\n")
    
    # Return updated state
    return {
        "next_action": next_action,
        "messages": state.get("messages", []) + [
            f"Router: Decided to '{next_action}' - {reason}"
        ]
    }
