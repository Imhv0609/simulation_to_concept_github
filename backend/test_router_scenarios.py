"""
Test file to demonstrate all 3 routing scenarios:
1. "plan" - Normal flow (concepts remaining, student not confused)
2. "assess" - All concepts taught
3. "re-explain" - Student is confused
"""

from state import TeachingState
from nodes.router import router_node


def test_scenario_1_plan():
    """Test normal flow - should return 'plan'"""
    print("\n" + "="*70)
    print("SCENARIO 1: NORMAL FLOW (Student Progressing Well)")
    print("="*70)
    
    state: TeachingState = {
        "simulation_name": "acids_bases",
        "learner_profile": {"level": "Beginner", "calibre": "Medium"},
        "simulation_url": "",
        "simulation_params": {},
        "control_mode": "MANUAL",
        "concepts": [
            {"name": "pH Scale", "description": "...", "importance": "high"},
            {"name": "Acid Properties", "description": "...", "importance": "high"},
            {"name": "Base Properties", "description": "...", "importance": "medium"},
        ],
        "current_concept_index": 0,  # Still on first concept
        "current_takeaway_index": 0,
        "view_config": {},
        "interactions": [],
        "understanding_status": {
            "is_confused": False,  # Student is doing well
            "confidence_level": 0.8,
            "last_interaction_quality": "good"
        },
        "assessment": None,
        "messages": [],
        "next_action": "",
        "error": None,
    }
    
    result = router_node(state)
    assert result["next_action"] == "plan", "Should route to 'plan'"
    print(f"\n✅ Test Passed: Returned '{result['next_action']}'")


def test_scenario_2_assess():
    """Test all concepts taught - should return 'assess'"""
    print("\n" + "="*70)
    print("SCENARIO 2: ALL CONCEPTS TAUGHT (Ready for Assessment)")
    print("="*70)
    
    state: TeachingState = {
        "simulation_name": "acids_bases",
        "learner_profile": {"level": "Beginner", "calibre": "Medium"},
        "simulation_url": "",
        "simulation_params": {},
        "control_mode": "MANUAL",
        "concepts": [
            {"name": "pH Scale", "description": "...", "importance": "high"},
            {"name": "Acid Properties", "description": "...", "importance": "high"},
            {"name": "Base Properties", "description": "...", "importance": "medium"},
        ],
        "current_concept_index": 3,  # Index = 3, but only 3 concepts (0,1,2)
        "current_takeaway_index": 0,
        "view_config": {},
        "interactions": [],
        "understanding_status": {
            "is_confused": False,
            "confidence_level": 0.9,
            "last_interaction_quality": "good"
        },
        "assessment": None,
        "messages": [],
        "next_action": "",
        "error": None,
    }
    
    result = router_node(state)
    assert result["next_action"] == "assess", "Should route to 'assess'"
    print(f"\n✅ Test Passed: Returned '{result['next_action']}'")


def test_scenario_3_reexplain():
    """Test student confused - should return 're-explain'"""
    print("\n" + "="*70)
    print("SCENARIO 3: STUDENT CONFUSED (Needs Re-explanation)")
    print("="*70)
    
    state: TeachingState = {
        "simulation_name": "acids_bases",
        "learner_profile": {"level": "Beginner", "calibre": "Dull"},
        "simulation_url": "",
        "simulation_params": {},
        "control_mode": "MANUAL",
        "concepts": [
            {"name": "pH Scale", "description": "...", "importance": "high"},
            {"name": "Acid Properties", "description": "...", "importance": "high"},
            {"name": "Base Properties", "description": "...", "importance": "medium"},
        ],
        "current_concept_index": 1,  # On second concept
        "current_takeaway_index": 0,
        "view_config": {},
        "interactions": [],
        "understanding_status": {
            "is_confused": True,  # Student is confused!
            "confidence_level": 0.3,
            "last_interaction_quality": "poor"
        },
        "assessment": None,
        "messages": [],
        "next_action": "",
        "error": None,
    }
    
    result = router_node(state)
    assert result["next_action"] == "re-explain", "Should route to 're-explain'"
    print(f"\n✅ Test Passed: Returned '{result['next_action']}'")


if __name__ == "__main__":
    print("\n" + "🧪" * 35)
    print("TESTING ALL ROUTER SCENARIOS")
    print("🧪" * 35)
    
    test_scenario_1_plan()
    test_scenario_2_assess()
    test_scenario_3_reexplain()
    
    print("\n" + "="*70)
    print("🎉 ALL TESTS PASSED! Router correctly handles all 3 scenarios.")
    print("="*70)
    print("\nRouter Logic Summary:")
    print("  1. 'plan' → Continue teaching (concepts left, student OK)")
    print("  2. 'assess' → Test student (all concepts taught)")
    print("  3. 're-explain' → Give feedback (student confused)")
    print()
