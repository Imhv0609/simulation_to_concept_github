"""
LangGraph workflow definition.

This file contains the main StateGraph that orchestrates
all the teaching nodes.
"""

from langgraph.graph import StateGraph, END
from state import TeachingState
from nodes.ingestion import simulation_ingest_node, simulation_parser_node, concept_extractor_node
from nodes.router import router_node
from nodes.planner import planner_node


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
    
    # TODO: Steps 9-15 - Remaining nodes will be added here
    
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
    workflow.add_conditional_edges(
        "router",
        lambda state: state.get("next_action", "plan"),
        {
            "plan": "planner",  # Generate lesson plan
            "assess": END,      # TODO: Will connect to MCQ generator (Step 13)
            "re-explain": END   # TODO: Will connect to feedback node (Step 12)
        }
    )
    
    # After planner, end for now (will connect to teaching node in Step 9)
    workflow.add_edge("planner", END)
    
    # TODO: Connect planner → teaching_node → probing_node → understanding_checker → router (loop)
    # etc...
    
    return workflow


def compile_graph() -> StateGraph:
    """
    Compiles the graph for execution.
    
    Returns:
        Compiled graph ready to invoke
    """
    workflow = create_teaching_graph()
    compiled = workflow.compile()
    return compiled


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
