"""
LangGraph workflow definition.

This file contains the main StateGraph that orchestrates
all the teaching nodes.
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from state import TeachingState
from nodes.ingestion import simulation_ingest_node, simulation_parser_node, concept_extractor_node
from nodes.router import router_node
from nodes.planner import planner_node
from nodes.teaching_loop import teaching_node, probing_node, understanding_checker_node, feedback_node, route_after_feedback
from nodes.assessment import mcq_generator_node, assessment_node, route_after_assessment, summary_node


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL CHECKPOINTER - Shared across all sessions for state persistence
# ═══════════════════════════════════════════════════════════════════════════
# MemorySaver stores checkpoints in memory, keyed by thread_id
# This allows the graph to resume from where it paused
_checkpointer = MemorySaver()

# Global compiled graph instance - reuse to maintain checkpoint state
_compiled_graph = None


def create_teaching_graph() -> StateGraph:
    """
    Creates the teaching workflow graph.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    
    # Initialize the graph with our state type
    workflow = StateGraph(TeachingState)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NODES - Added incrementally as we implement each node
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Step 4: Ingestion node ✅
    workflow.add_node("ingest", simulation_ingest_node)
    
    # Step 5: Parser node ✅
    workflow.add_node("parse", simulation_parser_node)
    
    # Step 6: Concept extractor node ✅
    workflow.add_node("extract_concepts", concept_extractor_node)
    
    # Step 7: Router node ✅
    workflow.add_node("router", router_node)
    
    # Step 8: Planner node ✅
    workflow.add_node("planner", planner_node)
    
    # Step 9: Teaching node ✅
    workflow.add_node("teaching", teaching_node)
    
    # Step 10: Probing node ✅
    workflow.add_node("probing", probing_node)
    
    # Step 11: Understanding checker node ✅
    workflow.add_node("understanding_checker", understanding_checker_node)
    
    # Step 12: Feedback node ✅
    workflow.add_node("feedback", feedback_node)
    
    # Step 13: MCQ Generator node ✅
    workflow.add_node("mcq_generator", mcq_generator_node)
    
    # Step 14: Assessment node ✅
    workflow.add_node("assessment", assessment_node)
    
    # Step 15: Summary node ✅
    workflow.add_node("summary", summary_node)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EDGES - Define the flow between nodes
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Set the starting point
    workflow.set_entry_point("ingest")
    
    # Connect nodes in sequence
    workflow.add_edge("ingest", "parse")
    workflow.add_edge("parse", "extract_concepts")
    workflow.add_edge("extract_concepts", "router")
    
    # Router uses conditional edges to decide next step
    # Note: Router only decides "plan" or "assess". Confusion is handled by feedback_node.
    workflow.add_conditional_edges(
        "router",
        lambda state: state.get("next_action", "plan"),
        {
            "plan": "planner",         # Generate lesson plan for current concept
            "assess": "mcq_generator"  # Step 13: Generate MCQs for assessment
        }
    )
    
    # After MCQ generator, go to assessment node
    workflow.add_edge("mcq_generator", "assessment")
    
    # Assessment node loops through MCQs, then goes to summary
    workflow.add_conditional_edges(
        "assessment",
        route_after_assessment,
        {
            "assessment": "assessment",  # Loop for next MCQ question
            "summary": "summary"          # Step 15: Generate final summary
        }
    )
    
    # After summary, end the workflow
    workflow.add_edge("summary", END)
    
    # After planner, go to teaching node
    workflow.add_edge("planner", "teaching")
    
    # Teaching node uses conditional edges based on next_action
    workflow.add_conditional_edges(
        "teaching",
        lambda state: state.get("next_action", "probe"),
        {
            "probe": "probing",           # Ask probing question
            "router": "router"            # When all takeaways done, go back to router
        }
    )
    
    # After probing, use conditional routing to handle wait states
    workflow.add_conditional_edges(
        "probing",
        lambda state: state.get("next_action", "check_understanding"),
        {
            "check_understanding": "understanding_checker",  # Student responded, analyze it
            "wait_for_response": END  # No response yet, pause here
        }
    )
    
    # After understanding checker, go to feedback
    workflow.add_edge("understanding_checker", "feedback")
    
    # After feedback, use conditional edges to route based on next_action
    # This is where the TEACHING LOOP is closed!
    workflow.add_conditional_edges(
        "feedback",
        route_after_feedback,  # Uses the routing function from teaching_loop.py
        {
            "teaching": "teaching",   # Re-explain or next takeaway
            "probing": "probing",     # Re-probe same question with hint
            "router": "router"        # Concept complete, go to router
        }
    )
    
    # The complete teaching loop is now:
    # teaching → probing → understanding_checker → feedback → (back to teaching/probing/router)
    
    return workflow


def compile_graph():
    """
    Compiles the graph for execution WITH checkpointing enabled.
    
    IMPORTANT: Returns a SINGLETON compiled graph to maintain checkpoint state.
    The checkpointer allows the graph to:
    - Save state at each node execution
    - Resume from where it paused using thread_id
    - Support human-in-the-loop interactions
    
    Returns:
        Compiled graph ready to invoke with checkpointing
    """
    global _compiled_graph
    
    # Only compile once - reuse the same instance to maintain checkpoints
    if _compiled_graph is None:
        print("🔧 Compiling graph with checkpointer (first time)")
        workflow = create_teaching_graph()
        _compiled_graph = workflow.compile(checkpointer=_checkpointer)
    
    return _compiled_graph


def get_checkpointer():
    """
    Returns the global checkpointer instance.
    Useful for accessing state history or debugging.
    """
    return _checkpointer


# Test function to verify graph can be created
def test_graph_creation():
    """Test that graph can be created without errors"""
    print("=" * 50)
    print("Testing Graph Creation")
    print("=" * 50)
    
    try:
        workflow = create_teaching_graph()
        print("\n✅ Graph created successfully!")
        print(f"Graph type: {type(workflow)}")
        print(f"Graph nodes: {workflow.nodes}")
        
        return workflow
        
    except Exception as e:
        print(f"\n❌ Error creating graph: {e}")
        raise


if __name__ == "__main__":
    # Test graph creation
    graph = test_graph_creation()
    
    print("\n" + "=" * 50)
    print("✅ Step 3 Complete: Graph Setup Works!")
    print("=" * 50)
