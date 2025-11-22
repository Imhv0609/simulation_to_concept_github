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
    }
    
    graph = compile_graph()
    graph_result = graph.invoke(graph_state)
    
    print(f"✅ Graph executed successfully!")
    print(f"   • Final simulation: {graph_result['simulation_name']}")
    print(f"   • Parameters extracted: {len(graph_result.get('simulation_params', {}))}")
    print(f"   • Concepts identified: {len(graph_result.get('concepts', []))}")
    print(f"   • Takeaways generated: {len(graph_result.get('takeaways', []))}")
    print(f"   • Next action (from router): {graph_result.get('next_action', 'N/A')}")
    print(f"   • Nodes executed: 5 (ingest → parse → extract_concepts → router → planner)")
    
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
    
    # Show router decision
    next_action = graph_result.get('next_action', 'unknown')
    print(f"\n🎯 Final State:")
    print(f"   • Router routed to: planner")
    print(f"   • Planner set next_action: '{next_action}'")
    if next_action == "teach":
        print(f"   → Ready to start teaching Takeaway #1")
    
    # Show message history
    messages = graph_result.get('messages', [])
    if messages:
        print(f"\n📝 Message History:")
        for msg in messages[-3:]:  # Show last 3 messages
            print(f"   • {msg}")
    
    # Restore original mode
    config.SIMULATION_CONTROL_MODE = original_mode
    
    print("\n💡 To test another scenario:")
    print("   1. Edit lines 18-21 in this file")
    print("   2. Save and run: python easy_test.py")
    print()
    
    return result


if __name__ == "__main__":
    run_test()
