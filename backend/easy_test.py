"""
═══════════════════════════════════════════════════════════════════════════
                        SIMPLE TEST FILE
═══════════════════════════════════════════════════════════════════════════

This is THE ONLY test file you need!

HOW IT WORKS:
1. You edit the 3 values below (simulation, level, calibre)
2. Run: python easy_test.py
3. See how the ingestion node processes your inputs
4. Change values and run again to test different scenarios

═══════════════════════════════════════════════════════════════════════════
"""

from state import TeachingState
from nodes.ingestion import simulation_ingest_node
from graph import create_teaching_graph, compile_graph
import config


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 EDIT THESE 4 VALUES TO TEST DIFFERENT SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════

TEST_SIMULATION = "acids_bases"            # Which simulation to use
TEST_LEVEL = "Beginner"                    # Student's knowledge level
TEST_CALIBRE = "Medium"                    # Student's learning pace
TEST_MODE = "MANUAL"                       # Control mode: MANUAL or AUTO

# ═══════════════════════════════════════════════════════════════════════════
# 📚 AVAILABLE OPTIONS (copy-paste one of these):
#
# SIMULATIONS:  fractions, acids_bases, std, std1, std2, std3, std4
#
# LEVELS:       Beginner, Intermediate, Advanced
#
# CALIBRE:      Dull, Medium, High IQ
#
# MODE:         MANUAL (agent gives instructions, student changes params)
#               AUTO   (agent controls params programmatically)
# ═══════════════════════════════════════════════════════════════════════════


def run_test():
    """
    This function does 3 things:
    1. Creates a state with your test values
    2. Runs the ingestion node
    3. Shows the results
    """
    
    # Override config mode with test mode temporarily
    original_mode = config.SIMULATION_CONTROL_MODE
    config.SIMULATION_CONTROL_MODE = TEST_MODE
    
    print("\n" + "="*70)
    print("🧪 TESTING INGESTION NODE")
    print("="*70)
    
    print(f"\n📝 Your Test Inputs:")
    print(f"   • Simulation: {TEST_SIMULATION}")
    print(f"   • Student Level: {TEST_LEVEL}")
    print(f"   • Learning Pace: {TEST_CALIBRE}")
    print(f"   • Control Mode: {TEST_MODE} (set in test file)")
    
    # STEP 1: Create state with your test values
    # (In real app, Streamlit would create this from user clicks)
    state: TeachingState = {
        "simulation_name": TEST_SIMULATION,
        "simulation_url": "",
        "simulation_description": "",
        "learner_profile": {
            "level": TEST_LEVEL,
            "calibre": TEST_CALIBRE,
        },
        "control_mode": "MANUAL",
        "concepts": [],
        "current_concept_index": 0,
        "takeaways": [],
        "current_takeaway_index": 0,
        "view_config": {},
        "interactions": [],
        "understanding_status": {
            "is_confused": False,
            "confidence_level": 0.0,
            "last_interaction_quality": "neutral"
        },
        "assessment": None,
        "messages": [],
        "next_action": "start",
        "error": None,
    }
    
    # STEP 2: Run the ingestion node
    print("\n" + "-"*70)
    result = simulation_ingest_node(state)
    print("-"*70)
    
    # STEP 3: Show what the node returned
    print(f"\n✅ Ingestion Complete!")
    print(f"   • Loaded simulation: {result['simulation_name']}")
    print(f"   • URL: {result['simulation_url'][:50]}...")
    print(f"   • Control mode: {result['control_mode']}")
    print(f"   • Can agent modify params: {result['view_config']['can_modify_params']}")
    
    mode_config = config.get_current_mode_config()
    print(f"\n🎛️  Mode Behavior:")
    print(f"   • Requires instructions: {mode_config['requires_instructions']}")
    print(f"   • Interaction type: {mode_config['interaction_type']}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BONUS: Test the graph execution (currently just runs ingest node)
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("🔄 TESTING GRAPH EXECUTION")
    print("="*70)
    
    # Create fresh state for graph (graph needs the inputs in the state)
    graph_state = {
        "simulation_name": TEST_SIMULATION,
        "learner_profile": {"level": TEST_LEVEL, "calibre": TEST_CALIBRE},
        "simulation_url": "",
        "simulation_params": {},
        "control_mode": "",
        "concepts": [],
        "current_concept_index": 0,
        "takeaways": [],
        "current_takeaway_index": 0,
        "view_config": {},
        "interactions": [],
        "understanding_status": {
            "is_confused": False,
            "confidence_level": 0.0,
            "last_interaction_quality": "neutral"
        },
        "assessment": None,
        "messages": [],
        "next_action": "start",
        "error": None,
        "re_explain_count": 0,  # Track re-explanation attempts
        "mcqs": [],  # Step 13: Generated MCQs for assessment
        "current_mcq_index": 0,  # Step 14: Which MCQ we're on
        "student_answers": [],  # Step 14: Student's quiz answers
    }
    
    graph = compile_graph()
    # Set recursion limit higher to allow the teaching loop to run
    # In production, real student responses would break the loop naturally
    # For testing with hardcoded responses:
    # - Each takeaway can loop up to 3 times (MAX_RE_EXPLAIN_ATTEMPTS)
    # - Multiple takeaways per concept
    # - Multiple concepts
    # So we need: concepts × takeaways × 3 attempts × ~4 nodes per loop = ~100+ iterations
    graph_result = graph.invoke(graph_state, {"recursion_limit": 150})
    
    print(f"✅ Graph executed successfully!")
    print(f"   • Final simulation: {graph_result['simulation_name']}")
    print(f"   • Parameters extracted: {len(graph_result.get('simulation_params', {}))}")
    print(f"   • Concepts identified: {len(graph_result.get('concepts', []))}")
    print(f"   • Takeaways generated: {len(graph_result.get('takeaways', []))}")
    print(f"   • Interactions recorded: {len(graph_result.get('interactions', []))}")
    print(f"   • Next action: {graph_result.get('next_action', 'N/A')}")
    print(f"   • Nodes executed: 12 (ingest → parse → extract_concepts → router → planner → teaching → probing → understanding_checker → feedback → mcq_generator → assessment → summary)")
    
    # Show feedback message if available
    feedback_msg = graph_result.get('feedback_message', '')
    if feedback_msg:
        print(f"\n💬 Feedback Message:")
        print(f"   {feedback_msg[:200]}..." if len(feedback_msg) > 200 else f"   {feedback_msg}")
    
    # Show re-explain count
    re_explain_count = graph_result.get('re_explain_count', 0)
    print(f"\n🔄 Re-explain Count: {re_explain_count}")
    
    # Show understanding status
    understanding = graph_result.get('understanding_status', {})
    if understanding:
        print(f"\n🧠 Understanding Status:")
        print(f"   • Is Confused: {understanding.get('is_confused', 'N/A')}")
        print(f"   • Confidence: {understanding.get('confidence_level', 0):.0%}")
        print(f"   • Quality: {understanding.get('last_interaction_quality', 'N/A')}")
    
    # Show extracted concepts
    concepts = graph_result.get('concepts', [])
    if concepts:
        print(f"\n📚 Extracted Concepts:")
        for i, concept in enumerate(concepts, 1):
            print(f"   {i}. {concept.get('name', 'Unnamed')}")
            print(f"      - Importance: {concept.get('importance', 'N/A')}")
    
    # Show generated takeaways
    takeaways = graph_result.get('takeaways', [])
    if takeaways:
        print(f"\n📖 Generated Lesson Plan (Takeaways):")
        for i, takeaway in enumerate(takeaways, 1):
            print(f"\n   Takeaway {i}:")
            print(f"   - Explanation: {takeaway.get('explanation', 'N/A')[:100]}...")
            print(f"   - Parameters to vary: {takeaway.get('parameters_to_vary', [])}")
            print(f"   - Display mode: {takeaway.get('display_mode', 'single')}")
            print(f"   - Probing Q: {takeaway.get('probing_question', 'N/A')[:80]}...")
    
    # Show interactions
    interactions = graph_result.get('interactions', [])
    if interactions:
        print(f"\n💬 Recorded Interactions:")
        for i, interaction in enumerate(interactions, 1):
            print(f"\n   Interaction {i}:")
            print(f"   - Timestamp: {interaction.get('timestamp', 'N/A')}")
            print(f"   - Agent asked: {interaction.get('agent_message', 'N/A')[:80]}...")
            print(f"   - Student said: {interaction.get('student_response', 'N/A')[:80]}...")
            print(f"   - Understanding: {interaction.get('understanding_status', 'Pending analysis')}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NEW: Show generated MCQs (Step 13)
    # ═══════════════════════════════════════════════════════════════════════════
    mcqs = graph_result.get('mcqs', [])
    if mcqs:
        print(f"\n" + "="*70)
        print(f"📝 GENERATED MCQs ({len(mcqs)} questions)")
        print("="*70)
        for i, mcq in enumerate(mcqs, 1):
            print(f"\n   Question {i}: {mcq.get('question', 'N/A')}")
            print(f"   Related to concept: {mcq.get('concept_name', 'N/A')}")
            print(f"   Difficulty: {mcq.get('difficulty', 'N/A')}")
            options = mcq.get('options', [])
            if options:
                print(f"   Options:")
                for j, opt in enumerate(options):
                    marker = "✓" if j == mcq.get('correct_answer_index', -1) else " "
                    print(f"      [{marker}] {chr(65+j)}. {opt}")
            print(f"   Explanation: {mcq.get('explanation', 'N/A')[:100]}...")
    else:
        print(f"\n📝 No MCQs generated yet (need to complete all concepts first)")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NEW: Show Assessment Results (Step 14)
    # ═══════════════════════════════════════════════════════════════════════════
    assessment = graph_result.get('assessment')
    student_answers = graph_result.get('student_answers', [])
    
    if assessment:
        print(f"\n" + "="*70)
        print(f"🎓 ASSESSMENT RESULTS")
        print("="*70)
        print(f"\n   📊 Score: {assessment.get('correct_answers', 0)}/{assessment.get('total_questions', 0)}")
        print(f"   📈 Percentage: {assessment.get('score_percentage', 0):.0f}%")
        
        # Show answer breakdown
        if student_answers and mcqs:
            print(f"\n   📋 Answer Breakdown:")
            for i, (answer, mcq) in enumerate(zip(student_answers, mcqs), 1):
                correct = mcq.get('correct_answer', 0)
                is_correct = "✅" if answer == correct else "❌"
                print(f"      Q{i}: Selected {chr(65+answer)}, Correct {chr(65+correct)} {is_correct}")
        
        if assessment.get('feedback'):
            print(f"\n   💬 Feedback: {assessment.get('feedback')}")
        if assessment.get('recommended_next_level'):
            print(f"   🎯 Recommended Level: {assessment.get('recommended_next_level')}")
        
        # Show teaching stats if available (from summary node)
        teaching_stats = assessment.get('teaching_stats')
        if teaching_stats:
            print(f"\n   📈 Teaching Metrics:")
            print(f"      • Avg interactions per concept: {teaching_stats.get('avg_interactions_per_concept', 0):.1f}")
            print(f"      • Re-explanation rate: {teaching_stats.get('re_explain_rate', 0):.0%}")
            print(f"      • Understanding rate: {teaching_stats.get('understanding_rate', 0):.0%}")
    
    # Show router decision
    next_action = graph_result.get('next_action', 'unknown')
    print(f"\n🎯 Final State:")
    print(f"   • Current concept index: {graph_result.get('current_concept_index', 0)}")
    print(f"   • Current takeaway index: {graph_result.get('current_takeaway_index', 0)}")
    print(f"   • Next action: '{next_action}'")
    if next_action == "complete":
        print(f"   ✅ Session fully complete!")
    
    # Show message history
    messages = graph_result.get('messages', [])
    if messages:
        print(f"\n📝 Message History (last 3):")
        for msg in messages[-3:]:  # Show last 3 messages
            print(f"   • {msg[:100]}...")
    
    # Restore original mode
    config.SIMULATION_CONTROL_MODE = original_mode
    
    print("\n💡 To test another scenario:")
    print("   1. Edit lines 18-21 in this file")
    print("   2. Save and run: python easy_test.py")
    print()
    
    return result


if __name__ == "__main__":
    run_test()
