"""
Main entry point for testing the teaching workflow.

This script tests individual nodes and the complete workflow.
"""

from state import TeachingState, LearnerProfile, SimulationParameter
from graph import create_teaching_graph, compile_graph


def test_state_structure():
    """Test that state structure is properly defined"""
    
    print("=" * 50)
    print("Testing State Definition")
    print("=" * 50)
    
    # Create a sample state
    sample_state: TeachingState = {
        # Input data
        "sim_link": "file:///path/to/fractions.html",
        "sim_description": "Pizza fraction simulator",
        "sim_parameters": [
            {
                "name": "denominator",
                "description": "Number of slices",
                "type": "number",
                "min": 1.0,
                "max": 12.0,
                "default": 8,
                "html_id": "denom"
            }
        ],
        "ncert_context": "Class 6 Fractions",
        "learner_profile": {
            "level": "Beginner",
            "calibre": "Medium"
        },
        
        # Metadata (will be filled by nodes)
        "sim_metadata": {
            "name": "",
            "link": "",
            "description": "",
            "control_mode": "MANUAL",
            "topic": None,
            "chapter": None
        },
        
        # Extracted data (will be filled by nodes)
        "concepts": [],
        "level_plan": [],
        "current_takeaway_idx": 0,
        "interaction_history": [],
        "view_config": {
            "mode": "single",
            "instructions": None,
            "left_instructions": None,
            "right_instructions": None,
            "observation_prompt": None
        },
        "mcqs": [],
        "student_answers": None,
        "assessment": None,
        "retry_count": 0,
        "session_id": None
    }
    
    print("\n✅ State structure created successfully!")
    print(f"\n📋 Sample State Keys: {list(sample_state.keys())}")
    print(f"\n👤 Learner Profile: {sample_state['learner_profile']}")
    
    return sample_state


def test_graph():
    """Test that graph can be created"""
    
    print("\n" + "=" * 50)
    print("Testing Graph Creation")
    print("=" * 50)
    
    workflow = create_teaching_graph()
    print("\n✅ Graph created successfully!")
    print(f"Graph nodes: {workflow.nodes}")
    
    return workflow


if __name__ == "__main__":
    # Test state definition
    test_state = test_state_structure()
    
    # Test graph creation
    test_graph()
    
    print("\n" + "=" * 50)
    print("✅ Steps 2 & 3 Complete!")
    print("=" * 50)
    print("\n🎯 Ready for Step 4: SimulationIngestNode")
