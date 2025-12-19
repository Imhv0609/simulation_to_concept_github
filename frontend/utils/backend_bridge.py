"""
Backend Bridge - Step 22
========================
This module acts as a clean interface between the Streamlit frontend
and the LangGraph backend. It handles all backend communication,
state management, and data transformation.

Think of this as a "translator" between frontend and backend.

CHECKPOINTING:
This module uses LangGraph's checkpointing to persist state across invocations.
Each session gets a unique thread_id that allows the graph to resume from
where it paused (e.g., after teaching node, waiting for user input).
"""

import sys
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Add backend to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

# Import backend modules
from backend.graph import compile_graph
from backend.state import TeachingState
import backend.config as backend_config

# Import frontend config (must use absolute import to avoid conflicts)
frontend_path = str(PROJECT_ROOT / "frontend")
if frontend_path not in sys.path:
    sys.path.insert(0, frontend_path)

# Import frontend config module explicitly
import importlib.util
spec = importlib.util.spec_from_file_location(
    "frontend_config", 
    PROJECT_ROOT / "frontend" / "config.py"
)
frontend_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frontend_config)


# ═══════════════════════════════════════════════════════════════════════════
# THREAD ID MANAGEMENT - For checkpointing
# ═══════════════════════════════════════════════════════════════════════════

def generate_thread_id() -> str:
    """
    Generate a unique thread_id for a new learning session.
    This ID is used by the checkpointer to save and restore graph state.
    """
    return f"session_{uuid.uuid4().hex[:12]}"


# ═══════════════════════════════════════════════════════════════════════════
# MAIN FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def initialize_session(
    simulation_name: str, 
    level: str, 
    calibre: str,
    control_mode: str
) -> Dict[str, Any]:
    """
    Initialize a new learning session with the backend.
    
    This function:
    1. Generates a unique thread_id for checkpointing
    2. Converts frontend inputs to backend format
    3. Creates initial state
    4. Invokes the backend graph (runs through ingestion → concepts → planner → teaching)
    5. Graph pauses after teaching node (waiting for user input)
    6. Extracts the first teaching message
    7. Prepares simulation URL
    
    CHECKPOINTING: The graph state is automatically saved at each step.
    When the user responds, we resume from where we paused using the same thread_id.
    
    Args:
        simulation_name: Display name like "Acids and Bases"
        level: "Beginner", "Intermediate", or "Advanced"
        calibre: "Dull", "Medium", or "High IQ"
        control_mode: "AUTO" or "MANUAL"
        
    Returns:
        dict: {
            "backend_state": {...},           # Full backend state
            "thread_id": "session_abc123",    # Unique ID for checkpointing
            "first_message": "Welcome...",    # AI's first message
            "simulation_url": "http://...",   # Initial simulation URL
            "concepts": [...],                # List of concepts
            "total_concepts": 3,              # Number of concepts
            "current_concept_index": 0,       # Starting at concept 0
            "mode": "AUTO"                    # Control mode
        }
        
    Raises:
        Exception: If backend initialization fails
    """
    
    try:
        # Step 1: Generate unique thread_id for this session
        thread_id = generate_thread_id()
        print(f"🆔 Generated thread_id: {thread_id}")
        
        # Step 2: Convert display name to backend key
        backend_key = frontend_config.get_backend_key(simulation_name)
        
        # Step 3: Create initial state for backend
        initial_state: TeachingState = {
            "simulation_name": backend_key,  # e.g., "acids_bases"
            "learner_profile": {
                "level": level,
                "calibre": calibre
            }
        }
        
        # Step 4: Compile and invoke the backend graph WITH checkpointing
        # The config includes thread_id for state persistence
        # Graph will run: ingest → parse → extract → router → planner → teaching
        # Then pause at teaching node (wait_for_start) and save state
        compiled_graph = compile_graph()
        config = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": 25  # Allow enough steps for initialization
        }
        result_state = compiled_graph.invoke(initial_state, config)
        
        print(f"✅ Graph paused at: next_action = {result_state.get('next_action')}")
        
        # Step 5: Extract first teaching message
        first_message = _extract_first_message(result_state)
        
        # Step 6: Generate initial simulation URL
        simulation_url = _generate_simulation_url(
            simulation_name,
            result_state,
            control_mode
        )
        
        # Step 7: Return everything frontend needs (including thread_id!)
        return {
            "backend_state": result_state,
            "thread_id": thread_id,  # IMPORTANT: Frontend must store this for future calls
            "first_message": first_message,
            "simulation_url": simulation_url,
            "concepts": result_state.get("concepts", []),
            "total_concepts": len(result_state.get("concepts", [])),
            "current_concept_index": result_state.get("current_concept_index", 0),
            "mode": control_mode
        }
        
    except Exception as e:
        raise Exception(f"Failed to initialize session: {str(e)}")


def send_message(
    user_input: str,
    current_backend_state: Dict[str, Any],
    simulation_name: str,
    control_mode: str,
    thread_id: str  # REQUIRED: Thread ID for checkpointing
) -> Dict[str, Any]:
    """
    Send user message to backend and get AI response.
    
    CHECKPOINTING: Uses thread_id to resume graph from where it paused.
    The graph will continue from the last checkpoint (e.g., after teaching node)
    and process the user's response through the teaching loop.
    
    This function:
    1. Updates state with user input
    2. Invokes backend graph with same thread_id (resumes from checkpoint!)
    3. Graph continues: probing → understanding_checker → feedback → teaching...
    4. Extracts AI's response message
    5. Updates simulation URL if needed (AUTO mode)
    6. Checks if session is complete
    
    Args:
        user_input: What the user typed
        current_backend_state: Current backend state from session_state
        simulation_name: Display name of simulation
        control_mode: "AUTO" or "MANUAL"
        thread_id: Unique session ID for checkpointing (from initialize_session)
        
    Returns:
        dict: {
            "ai_response": "Great observation!...",  # AI's message
            "updated_state": {...},                  # New backend state
            "simulation_url": "http://...",          # Updated URL (may change in AUTO)
            "next_action": "teach",                  # What backend did
            "ready_for_quiz": False,                 # True if all concepts done
            "current_concept_index": 1,              # Progress info
            "current_takeaway_index": 0,             # Progress info
        }
        
    Raises:
        Exception: If backend communication fails
    """
    
    try:
        print(f"\n📤 send_message called with thread_id: {thread_id}")
        print(f"   User input: {user_input[:50]}...")
        
        # Step 1: Get the compiled graph (singleton)
        compiled_graph = compile_graph()
        config = {"configurable": {"thread_id": thread_id}}
        
        # Step 2: Get current checkpoint state to understand where we are
        current_state = compiled_graph.get_state(config)
        current_values = current_state.values
        print(f"📍 Current checkpoint state:")
        print(f"   next_action: {current_values.get('next_action')}")
        print(f"   current_takeaway_index: {current_values.get('current_takeaway_index')}")
        print(f"   interactions count: {len(current_values.get('interactions', []))}")
        print(f"   messages count: {len(current_values.get('messages', []))}")
        
        # Step 3: Create the interaction record for this Q&A pair
        # The probing node added the question to messages but didn't create an interaction
        # (because it was waiting for student response)
        # Now we create the complete interaction
        import datetime
        messages = current_values.get("messages", [])
        agent_message = messages[-1] if messages else "Question asked"
        
        new_interaction = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agent_message": agent_message,
            "student_response": user_input,
            "understanding_status": None  # Will be filled by understanding_checker
        }
        
        interactions = list(current_values.get("interactions", []))
        interactions.append(new_interaction)
        print(f"✅ Created interaction record (total: {len(interactions)})")
        
        # Step 4: Update the state with student's response AND change next_action
        # The key insight: probing node ended with next_action="wait_for_response"
        # We need to change it to "check_understanding" so conditional edge routes correctly
        print(f"🔄 Updating state with student_response, interactions, and next_action...")
        compiled_graph.update_state(
            config,
            {
                "student_response": user_input,
                "interactions": interactions,  # With new interaction record
                "next_action": "check_understanding"  # This routes to understanding_checker
            },
            as_node="probing"  # Update as if coming from probing node
        )
        
        # Step 5: Resume the graph from the checkpoint
        # With next_action="check_understanding", the conditional edge after probing
        # will route to understanding_checker node
        print(f"▶️  Resuming graph execution...")
        result_state = compiled_graph.invoke(None, {**config, "recursion_limit": 25})
        
        print(f"✅ Graph completed. next_action = {result_state.get('next_action')}")
        
        # Step 3: Determine what happened and extract AI response
        next_action = result_state.get("next_action", "teach")
        ai_response = _extract_ai_response(result_state, next_action)
        
        # Step 4: Generate updated simulation URL
        simulation_url = _generate_simulation_url(
            simulation_name,
            result_state,
            control_mode
        )
        
        # Step 5: Check if session is complete
        ready_for_quiz = next_action == "assess" or _is_session_complete(result_state)
        
        # Step 6: Return everything frontend needs
        return {
            "ai_response": ai_response,
            "updated_state": result_state,
            "simulation_url": simulation_url,
            "next_action": next_action,
            "ready_for_quiz": ready_for_quiz,
            "current_concept_index": result_state.get("current_concept_index", 0),
            "current_takeaway_index": result_state.get("current_takeaway_index", 0),
        }
        
    except Exception as e:
        raise Exception(f"Failed to send message: {str(e)}")


def get_progress_info(backend_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get current learning progress from backend state.
    
    Args:
        backend_state: Current backend state
        
    Returns:
        dict: {
            "current_concept": 2,        # 1-based for display
            "total_concepts": 3,
            "current_takeaway": 1,       # 1-based for display
            "total_takeaways": 2,
            "concept_name": "pH Scale",
            "completion_percentage": 66.7
        }
    """
    
    concepts = backend_state.get("concepts", [])
    current_concept_idx = backend_state.get("current_concept_index", 0)
    takeaways = backend_state.get("takeaways", [])
    current_takeaway_idx = backend_state.get("current_takeaway_index", 0)
    
    total_concepts = len(concepts)
    total_takeaways = len(takeaways)
    
    # Calculate completion percentage
    if total_concepts > 0:
        completion = (current_concept_idx / total_concepts) * 100
    else:
        completion = 0
    
    # Get current concept name
    concept_name = ""
    if 0 <= current_concept_idx < len(concepts):
        concept_name = concepts[current_concept_idx].get("name", "")
    
    return {
        "current_concept": current_concept_idx + 1,  # 1-based for display
        "total_concepts": total_concepts,
        "current_takeaway": current_takeaway_idx + 1,  # 1-based for display
        "total_takeaways": total_takeaways,
        "concept_name": concept_name,
        "completion_percentage": round(completion, 1)
    }


def get_current_concept_info(backend_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get information about the current concept being taught.
    
    Args:
        backend_state: Current backend state
        
    Returns:
        dict or None: {
            "name": "pH Scale",
            "description": "...",
            "importance": "high"
        }
    """
    
    concepts = backend_state.get("concepts", [])
    current_idx = backend_state.get("current_concept_index", 0)
    
    if 0 <= current_idx < len(concepts):
        return concepts[current_idx]
    
    return None


def is_session_complete(backend_state: Dict[str, Any]) -> bool:
    """
    Check if all concepts have been taught.
    
    Args:
        backend_state: Current backend state
        
    Returns:
        bool: True if all concepts completed, False otherwise
    """
    return _is_session_complete(backend_state)


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (Internal Use Only)
# ═══════════════════════════════════════════════════════════════════════════

def _extract_first_message(backend_state: Dict[str, Any]) -> str:
    """
    Extract the first teaching message from backend state.
    
    After initialization, the backend will have:
    - Generated concepts
    - Generated takeaways for first concept
    - Created first teaching explanation
    - Created first probing question
    
    Args:
        backend_state: State returned from initial graph invocation
        
    Returns:
        str: First message to show to user (explanation + question)
    """
    
    # Check if we have messages in state (teaching node adds them)
    messages = backend_state.get("messages", [])
    if messages:
        # Return the last 2 messages (teaching explanation + probing question)
        recent_messages = messages[-2:] if len(messages) >= 2 else messages
        formatted_parts = [msg for msg in recent_messages if msg.strip()]
        if formatted_parts:
            return "\n\n---\n\n".join(formatted_parts)
    
    # Fallback: Try to get from takeaways
    takeaways = backend_state.get("takeaways", [])
    concepts = backend_state.get("concepts", [])
    
    if takeaways and len(takeaways) > 0:
        first_takeaway = takeaways[0]
        explanation = first_takeaway.get("explanation", "")
        probing_question = first_takeaway.get("probing_question", "")
        
        # Build combined message
        msg_parts = []
        
        # Add concept header
        if concepts:
            concept_name = concepts[0].get("name", "")
            if concept_name:
                msg_parts.append(f"**📚 Concept: {concept_name}**")
        
        msg_parts.append("**📖 Takeaway 1 of " + str(len(takeaways)) + "**")
        
        if explanation:
            msg_parts.append(explanation)
        
        if probing_question:
            msg_parts.append(f"\n**❓ Question:** {probing_question}")
        
        if msg_parts:
            return "\n\n".join(msg_parts)
    
    # Fallback: Generic welcome message
    if concepts:
        concept_names = [c.get("name", "") for c in concepts]
        return (
            f"Welcome! Today we'll explore {len(concepts)} key concepts: "
            f"{', '.join(concept_names)}. Let's begin!"
        )
    
    return "Welcome! Let's start exploring this simulation together."


def _extract_ai_response(backend_state: Dict[str, Any], next_action: str) -> str:
    """
    Extract AI's response based on what action the backend took.
    
    The backend stores messages in a list. Each teaching cycle adds:
    1. Teaching message (explanation + instructions)
    2. Probing question
    
    We need to return the NEW messages that were added in this cycle.
    
    Args:
        backend_state: Current backend state
        next_action: "teach", "probe", "assess", "re-explain", "wait_for_start", or "wait_for_response"
        
    Returns:
        str: AI's message to display
    """
    
    messages = backend_state.get("messages", [])
    takeaways = backend_state.get("takeaways", [])
    current_takeaway_idx = backend_state.get("current_takeaway_index", 0)
    concepts = backend_state.get("concepts", [])
    current_concept_idx = backend_state.get("current_concept_index", 0)
    
    # Get current concept name for context
    concept_name = ""
    if 0 <= current_concept_idx < len(concepts):
        concept_name = concepts[current_concept_idx].get("name", "")
    
    # Get current takeaway if available
    current_takeaway = None
    if 0 <= current_takeaway_idx < len(takeaways):
        current_takeaway = takeaways[current_takeaway_idx]
    
    # If we have messages, return the most recent ones
    # After a teaching cycle, the last 2 messages are: [teaching explanation, probing question]
    if messages:
        # Get the last 2 messages (teaching + probing)
        recent_messages = messages[-2:] if len(messages) >= 2 else messages
        
        # Format them nicely
        formatted_parts = []
        for msg in recent_messages:
            if msg.strip():
                formatted_parts.append(msg)
        
        if formatted_parts:
            return "\n\n---\n\n".join(formatted_parts)
    
    # Fallback based on next_action
    if next_action in ["wait_for_start", "wait_for_response"]:
        if current_takeaway:
            explanation = current_takeaway.get("explanation", "")
            question = current_takeaway.get("probing_question", "What do you observe?")
            
            # Build a combined message with takeaway info
            msg_parts = []
            
            # Add takeaway header
            if concept_name:
                msg_parts.append(f"**📚 Concept: {concept_name}**")
            msg_parts.append(f"**📖 Takeaway {current_takeaway_idx + 1} of {len(takeaways)}**")
            
            # Add explanation
            if explanation:
                msg_parts.append(explanation)
            
            # Add question
            msg_parts.append(f"\n**❓ Question:** {question}")
            
            return "\n\n".join(msg_parts)
        else:
            return "What do you observe in the simulation?"
    
    elif next_action == "teach":
        if current_takeaway:
            return current_takeaway.get("explanation", "Let's continue learning.")
        else:
            return "Let's continue with the next concept."
    
    elif next_action == "probe":
        # Backend wants to ask probing question
        if current_takeaway:
            return current_takeaway.get("probing_question", "What do you observe?")
        else:
            return "What do you observe in the simulation?"
    
    elif next_action == "assess":
        # All concepts done, time for quiz
        return (
            "🎉 Excellent work! You've completed all the concepts. "
            "You're now ready for the assessment quiz. Click 'Ready for Quiz' when you're prepared!"
        )
    
    elif next_action == "re-explain":
        # Backend detected confusion, providing feedback
        feedback = backend_state.get("feedback", "")
        if feedback:
            return feedback
        else:
            return "Let me explain that differently..."
    
    # Fallback
    return "Let's continue exploring!"


def _generate_simulation_url(
    simulation_name: str,
    backend_state: Dict[str, Any],
    control_mode: str
) -> str:
    """
    Generate simulation URL based on current state and mode.
    
    Args:
        simulation_name: Display name of simulation
        backend_state: Current backend state
        control_mode: "AUTO" or "MANUAL"
        
    Returns:
        str: Full simulation URL
    """
    
    if control_mode == "AUTO":
        # In AUTO mode, extract parameter values from current takeaway
        takeaways = backend_state.get("takeaways", [])
        current_takeaway_idx = backend_state.get("current_takeaway_index", 0)
        
        # Get parameter values if available
        params = {}
        if 0 <= current_takeaway_idx < len(takeaways):
            current_takeaway = takeaways[current_takeaway_idx]
            params = current_takeaway.get("parameter_values", {})
            
            # Debug: Log what parameters we're using
            print(f"🔧 AUTO Mode URL Generation:")
            print(f"   Takeaway {current_takeaway_idx + 1}: {current_takeaway.get('explanation', '')[:50]}...")
            print(f"   Parameters: {params}")
        
        # Generate URL with parameters
        url = frontend_config.get_simulation_url(simulation_name, params)
        print(f"   Generated URL: {url}")
        return url
    
    else:
        # In MANUAL mode, just show base simulation URL
        return frontend_config.get_simulation_url(simulation_name)


def _is_session_complete(backend_state: Dict[str, Any]) -> bool:
    """
    Check if all concepts have been taught.
    
    Args:
        backend_state: Current backend state
        
    Returns:
        bool: True if session complete
    """
    
    concepts = backend_state.get("concepts", [])
    current_concept_idx = backend_state.get("current_concept_index", 0)
    total_concepts = len(concepts)
    
    # Session complete if we've gone through all concepts
    return current_concept_idx >= total_concepts


# ═══════════════════════════════════════════════════════════════════════════
# DEBUGGING HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def get_state_summary(backend_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a human-readable summary of backend state (for debugging).
    
    Args:
        backend_state: Current backend state
        
    Returns:
        dict: Summary of important state fields
    """
    
    return {
        "simulation": backend_state.get("simulation_name", "Unknown"),
        "concepts_count": len(backend_state.get("concepts", [])),
        "current_concept": backend_state.get("current_concept_index", 0),
        "takeaways_count": len(backend_state.get("takeaways", [])),
        "current_takeaway": backend_state.get("current_takeaway_index", 0),
        "next_action": backend_state.get("next_action", "Unknown"),
        "is_confused": backend_state.get("understanding_status", {}).get("is_confused", False),
        "confidence": backend_state.get("understanding_status", {}).get("confidence_level", 0.0),
    }


def validate_backend_state(backend_state: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that backend state has all required fields.
    
    Args:
        backend_state: Backend state to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    
    required_fields = [
        "simulation_name",
        "concepts",
        "current_concept_index",
        "takeaways",
        "next_action"
    ]
    
    for field in required_fields:
        if field not in backend_state:
            return False, f"Missing required field: {field}"
    
    # Check that concepts is a list
    if not isinstance(backend_state.get("concepts"), list):
        return False, "Field 'concepts' must be a list"
    
    # Check that takeaways is a list
    if not isinstance(backend_state.get("takeaways"), list):
        return False, "Field 'takeaways' must be a list"
    
    return True, "Valid"


# ═══════════════════════════════════════════════════════════════════════════
# MODULE TEST (for development)
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Test the bridge functions"""
    
    print("=" * 70)
    print("BACKEND BRIDGE TEST")
    print("=" * 70)
    
    # Test initialization
    print("\n1. Testing initialize_session()...")
    try:
        result = initialize_session(
            simulation_name="Acids and Bases",
            level="Beginner",
            calibre="Medium",
            control_mode="AUTO"
        )
        
        print("✅ Initialization successful!")
        print(f"   - First message: {result['first_message'][:50]}...")
        print(f"   - Total concepts: {result['total_concepts']}")
        print(f"   - Simulation URL: {result['simulation_url'][:60]}...")
        
        # Test progress info
        print("\n2. Testing get_progress_info()...")
        progress = get_progress_info(result["backend_state"])
        print(f"✅ Progress: Concept {progress['current_concept']}/{progress['total_concepts']}")
        print(f"   - Current concept: {progress['concept_name']}")
        
        # Test state validation
        print("\n3. Testing validate_backend_state()...")
        is_valid, msg = validate_backend_state(result["backend_state"])
        print(f"✅ State validation: {msg}")
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED! ✅")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
