"""
Teaching Loop Nodes - Steps 9-12

This file contains the nodes that handle the interactive teaching loop:
- teaching_node (Step 9): Presents takeaways to the student
- probing_node (Step 10): Asks probing questions and records responses
- understanding_checker_node (Step 11): Analyzes student comprehension
- feedback_node (Step 12): Provides adaptive feedback

These nodes work together to create an interactive learning experience.
"""

from typing import Dict, Any, List
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from state import TeachingState


def teaching_node(state: TeachingState) -> Dict[str, Any]:
    """
    Step 9: Teaching Node
    
    Presents the current takeaway to the student. This node:
    1. Gets the current takeaway from the lesson plan
    2. Displays the explanation
    3. Prepares mode-aware instructions (MANUAL vs AUTO)
    4. Configures the simulation view (single or before_after)
    5. Sets next_action to "probe" for question asking
    
    NO LLM REQUIRED - This is a display/presentation node.
    
    Args:
        state: Current teaching state with takeaways from Planner Node
        
    Returns:
        Dict with:
        - view_config: How to display the simulation
        - messages: Agent message to show student
        - next_action: "probe" (to ask probing question)
        
    State Fields Used:
        - takeaways: List of takeaways from Planner Node
        - current_takeaway_index: Which takeaway we're presenting
        - control_mode: MANUAL or AUTO
        - simulation_params: Available parameters for instructions
        - simulation_url: URL of the simulation
    """
    
    print("\n" + "="*60)
    print("TEACHING NODE - Presenting Takeaway")
    print("="*60)
    
    # Extract relevant state
    takeaways = state.get("takeaways", [])
    current_takeaway_idx = state.get("current_takeaway_index", 0)
    control_mode = state.get("control_mode", "MANUAL")
    simulation_params = state.get("simulation_params", {})
    simulation_url = state.get("simulation_url", "")
    concepts = state.get("concepts", [])
    current_concept_idx = state.get("current_concept_index", 0)
    
    # Get current concept name for context
    current_concept_name = "Unknown Concept"
    if current_concept_idx < len(concepts):
        current_concept_name = concepts[current_concept_idx].get("name", "Unknown Concept")
    
    # Validate takeaways exist
    if not takeaways:
        print("\n❌ Error: No takeaways available to teach")
        return {
            "error": "No takeaways available. Planner node may have failed.",
            "next_action": "router",  # Go back to router to decide what to do
            "messages": state.get("messages", []) + [
                "Teaching: Error - No lesson plan available"
            ]
        }
    
    # Check if we've completed all takeaways for this concept
    if current_takeaway_idx >= len(takeaways):
        print(f"\n✅ All {len(takeaways)} takeaways for this concept have been taught!")
        print("   Moving to next concept...")
        
        # Increment concept index and reset takeaway index
        return {
            "current_concept_index": current_concept_idx + 1,
            "current_takeaway_index": 0,
            "takeaways": [],  # Clear takeaways for next concept
            "next_action": "router",  # Router will decide: plan next concept or assess
            "messages": state.get("messages", []) + [
                f"Teaching: Completed all takeaways for '{current_concept_name}'. Moving to next concept."
            ]
        }
    
    # Get current takeaway
    current_takeaway = takeaways[current_takeaway_idx]
    
    print(f"\n📚 Current Concept: '{current_concept_name}'")
    print(f"📖 Takeaway {current_takeaway_idx + 1} of {len(takeaways)}")
    print(f"🎛️  Control Mode: {control_mode}")
    
    # Extract takeaway details
    explanation = current_takeaway.get("explanation", "Explore the simulation.")
    parameters_to_vary = current_takeaway.get("parameters_to_vary", [])
    display_mode = current_takeaway.get("display_mode", "single")
    parameter_values = current_takeaway.get("parameter_values", {})
    before_state = current_takeaway.get("before_state", {})
    after_state = current_takeaway.get("after_state", {})
    probing_question = current_takeaway.get("probing_question", "What do you observe?")
    
    print(f"\n📝 Explanation: {explanation[:100]}...")
    print(f"🔧 Parameters to vary: {parameters_to_vary}")
    print(f"👁️  Display mode: {display_mode}")
    
    # Build view configuration based on display mode and control mode
    view_config = build_view_config(
        display_mode=display_mode,
        control_mode=control_mode,
        parameters_to_vary=parameters_to_vary,
        parameter_values=parameter_values,
        before_state=before_state,
        after_state=after_state,
        simulation_params=simulation_params,
        simulation_url=simulation_url
    )
    
    # Build agent message to student
    agent_message = build_agent_message(
        explanation=explanation,
        control_mode=control_mode,
        display_mode=display_mode,
        parameters_to_vary=parameters_to_vary,
        parameter_values=parameter_values,
        before_state=before_state,
        after_state=after_state,
        simulation_params=simulation_params,
        takeaway_num=current_takeaway_idx + 1,
        total_takeaways=len(takeaways)
    )
    
    print(f"\n💬 Agent Message Preview:")
    print(f"   {agent_message[:150]}...")
    
    print("\n" + "="*60)
    print(f"🎯 TEACHING COMPLETE: Ready to probe understanding")
    print(f"   Next: Ask probing question")
    print("="*60 + "\n")
    
    # Return updated state - always go to probe
    # With checkpointing, the graph will pause at probing node if no student_response
    return {
        "view_config": view_config,
        "next_action": "probe",
        "messages": state.get("messages", []) + [agent_message]
    }


def build_view_config(
    display_mode: str,
    control_mode: str,
    parameters_to_vary: List[str],
    parameter_values: Dict[str, Any],
    before_state: Dict[str, Any],
    after_state: Dict[str, Any],
    simulation_params: Dict[str, Any],
    simulation_url: str
) -> Dict[str, Any]:
    """
    Builds the view configuration for displaying the simulation.
    
    Args:
        display_mode: "single" or "before_after"
        control_mode: "MANUAL" or "AUTO"
        parameters_to_vary: List of parameter names to change
        parameter_values: Specific values for AUTO mode
        before_state: Parameter values for "before" view
        after_state: Parameter values for "after" view
        simulation_params: All available simulation parameters
        simulation_url: URL of the simulation
        
    Returns:
        ViewConfig dictionary for the frontend
    """
    
    view_config = {
        "mode": display_mode,
        "simulation_url": simulation_url,
        "control_mode": control_mode,
        "parameters_to_vary": parameters_to_vary,
    }
    
    if display_mode == "single":
        # Single view mode
        if control_mode == "AUTO":
            # AUTO: Include parameter values to set
            view_config["current_params"] = parameter_values
            view_config["instructions"] = None  # No manual instructions needed
        else:
            # MANUAL: Provide instructions for student
            instructions = generate_manual_instructions(
                parameters_to_vary, 
                simulation_params,
                parameter_values
            )
            view_config["instructions"] = instructions
            view_config["current_params"] = {}
            
    else:  # before_after mode
        # Before/After comparison view
        if control_mode == "AUTO":
            # AUTO: Set both states programmatically
            view_config["before_params"] = before_state or {}
            view_config["after_params"] = after_state or {}
            view_config["left_instructions"] = None
            view_config["right_instructions"] = None
        else:
            # MANUAL: Provide instructions for both states
            view_config["left_instructions"] = generate_before_instructions(
                parameters_to_vary,
                simulation_params,
                before_state
            )
            view_config["right_instructions"] = generate_after_instructions(
                parameters_to_vary,
                simulation_params,
                after_state
            )
            view_config["before_params"] = {}
            view_config["after_params"] = {}
    
    # Add observation prompt
    view_config["observation_prompt"] = "Observe the simulation carefully. What do you notice?"
    
    return view_config


def generate_manual_instructions(
    parameters_to_vary: List[str],
    simulation_params: Dict[str, Any],
    target_values: Dict[str, Any] = None
) -> str:
    """
    Generates manual instructions for the student in MANUAL mode.
    
    Args:
        parameters_to_vary: Parameters the student should change
        simulation_params: Available parameter details (for descriptions)
        target_values: Optional specific values to set
        
    Returns:
        Instruction string for the student
    """
    if not parameters_to_vary:
        return "Explore the simulation and observe the current state."
    
    instructions = []
    
    for param_name in parameters_to_vary:
        param_info = simulation_params.get(param_name, {})
        param_type = param_info.get("type", "unknown")
        
        if target_values and param_name in target_values:
            # We have a specific value to set
            target_val = target_values[param_name]
            instructions.append(f"Set '{param_name}' to {target_val}")
        elif param_type == "range":
            min_val = param_info.get("min", 0)
            max_val = param_info.get("max", 100)
            instructions.append(f"Adjust the '{param_name}' slider (range: {min_val} to {max_val})")
        elif param_type == "select":
            options = param_info.get("options", [])
            if options:
                instructions.append(f"Try different options in '{param_name}': {', '.join(str(o) for o in options[:3])}")
            else:
                instructions.append(f"Change the '{param_name}' dropdown")
        elif param_type == "number":
            instructions.append(f"Enter a value for '{param_name}'")
        elif param_type == "checkbox":
            instructions.append(f"Toggle the '{param_name}' checkbox")
        else:
            instructions.append(f"Adjust '{param_name}'")
    
    return "👉 " + "\n👉 ".join(instructions)


def generate_before_instructions(
    parameters_to_vary: List[str],
    simulation_params: Dict[str, Any],
    before_state: Dict[str, Any]
) -> str:
    """
    Generates instructions for the "BEFORE" state in before_after mode.
    """
    if before_state:
        parts = [f"Set '{k}' to {v}" for k, v in before_state.items()]
        return "BEFORE State:\n👉 " + "\n👉 ".join(parts)
    else:
        return "BEFORE State:\n👉 Start with the default values"


def generate_after_instructions(
    parameters_to_vary: List[str],
    simulation_params: Dict[str, Any],
    after_state: Dict[str, Any]
) -> str:
    """
    Generates instructions for the "AFTER" state in before_after mode.
    """
    if after_state:
        parts = [f"Set '{k}' to {v}" for k, v in after_state.items()]
        return "AFTER State:\n👉 " + "\n👉 ".join(parts)
    else:
        # Generate general instructions
        instructions = generate_manual_instructions(
            parameters_to_vary, 
            simulation_params,
            {}
        )
        return f"AFTER State:\n{instructions}"


def build_agent_message(
    explanation: str,
    control_mode: str,
    display_mode: str,
    parameters_to_vary: List[str],
    parameter_values: Dict[str, Any],
    before_state: Dict[str, Any],
    after_state: Dict[str, Any],
    simulation_params: Dict[str, Any],
    takeaway_num: int,
    total_takeaways: int
) -> str:
    """
    Builds the complete agent message to display to the student.
    
    This message includes:
    - Progress indicator (Takeaway X of Y)
    - The explanation from the lesson plan
    - Mode-specific instructions
    """
    
    # Header with progress
    message_parts = [
        f"📖 **Takeaway {takeaway_num} of {total_takeaways}**",
        "",
        explanation,
        ""
    ]
    
    # Add mode-specific instructions
    if control_mode == "MANUAL":
        if display_mode == "single":
            instructions = generate_manual_instructions(
                parameters_to_vary,
                simulation_params,
                parameter_values
            )
            message_parts.append("**Try this in the simulation:**")
            message_parts.append(instructions)
        else:  # before_after
            message_parts.append("**Compare these two states:**")
            message_parts.append("")
            message_parts.append(generate_before_instructions(
                parameters_to_vary, simulation_params, before_state
            ))
            message_parts.append("")
            message_parts.append(generate_after_instructions(
                parameters_to_vary, simulation_params, after_state
            ))
    else:  # AUTO mode
        if display_mode == "single":
            message_parts.append("**Watch the simulation** - I've set the parameters for you.")
            if parameter_values:
                message_parts.append(f"   Parameters set: {parameter_values}")
        else:  # before_after
            message_parts.append("**Compare these two states** - I've set both views for you.")
            if before_state:
                message_parts.append(f"   Before: {before_state}")
            if after_state:
                message_parts.append(f"   After: {after_state}")
    
    message_parts.append("")
    message_parts.append("👁️ Take a moment to observe, then I'll ask you a question.")
    
    return "\n".join(message_parts)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 10: Probing Node
# ═══════════════════════════════════════════════════════════════════════════════

def probing_node(state: TeachingState) -> Dict[str, Any]:
    """
    Step 10: Probing Node
    
    Asks the probing question from the current takeaway and records the
    student's response. This node:
    1. Gets the probing question from the current takeaway
    2. Presents the question to the student
    3. Records the student response (simulated in testing, real in frontend)
    4. Stores the interaction in the interactions list
    5. Sets next_action to "check_understanding"
    
    NO LLM REQUIRED - This is a question presentation and recording node.
    
    Args:
        state: Current teaching state with takeaways and current index
        
    Returns:
        Dict with:
        - interactions: Updated list with new interaction
        - messages: Agent's probing question
        - next_action: "check_understanding"
        
    State Fields Used:
        - takeaways: List of takeaways from Planner Node
        - current_takeaway_index: Which takeaway we're on
        - interactions: Existing interaction history
        - student_response: Optional - if provided by frontend
    """
    
    print("\n" + "="*60)
    print("PROBING NODE - Asking Understanding Question")
    print("="*60)
    
    # Extract relevant state
    takeaways = state.get("takeaways", [])
    current_takeaway_idx = state.get("current_takeaway_index", 0)
    interactions = state.get("interactions", [])
    concepts = state.get("concepts", [])
    current_concept_idx = state.get("current_concept_index", 0)
    
    # Get current concept name for context
    current_concept_name = "Unknown Concept"
    if current_concept_idx < len(concepts):
        current_concept_name = concepts[current_concept_idx].get("name", "Unknown Concept")
    
    # Validate takeaways exist
    if not takeaways or current_takeaway_idx >= len(takeaways):
        print("\n❌ Error: No takeaway available for probing")
        return {
            "error": "No takeaway available for probing question",
            "next_action": "router",
            "messages": state.get("messages", []) + [
                "Probing: Error - No takeaway available"
            ]
        }
    
    # Get current takeaway
    current_takeaway = takeaways[current_takeaway_idx]
    probing_question = current_takeaway.get("probing_question", "What did you observe?")
    
    print(f"\n📚 Concept: '{current_concept_name}'")
    print(f"📖 Takeaway: {current_takeaway_idx + 1} of {len(takeaways)}")
    print(f"\n❓ Probing Question:")
    print(f"   {probing_question}")
    
    # Build the agent message with the probing question
    agent_message = build_probing_message(
        probing_question=probing_question,
        takeaway_num=current_takeaway_idx + 1,
        total_takeaways=len(takeaways),
        concept_name=current_concept_name
    )
    
    # Get student response
    # In real app: This comes from the frontend (Streamlit input)
    # In testing: We simulate a response
    student_response = state.get("student_response", None)
    
    if student_response is None:
        # REAL-TIME MODE: No simulation, wait for actual user input
        # The graph will pause here until frontend provides a response
        print(f"\n⏸️  [WAITING] No student response yet - graph will pause here")
        print(f"   Frontend must call send_message() with student's answer")
        
        # Return current state without advancing
        # This allows the graph to pause and wait for user input
        return {
            "messages": state.get("messages", []) + [agent_message],
            "next_action": "wait_for_response"
        }
    else:
        print(f"\n👤 Student Response:")
        print(f"   \"{student_response}\"")
    
    # Create interaction record
    new_interaction = create_interaction_record(
        agent_message=agent_message,
        student_response=student_response
    )
    
    # Add to interactions list
    updated_interactions = interactions + [new_interaction]
    
    print(f"\n📝 Interaction recorded:")
    print(f"   Timestamp: {new_interaction['timestamp']}")
    print(f"   Total interactions: {len(updated_interactions)}")
    
    print("\n" + "="*60)
    print("🎯 PROBING COMPLETE: Ready to check understanding")
    print("   Next: Analyze student response with LLM")
    print("="*60 + "\n")
    
    # Return updated state
    return {
        "interactions": updated_interactions,
        "next_action": "check_understanding",
        "messages": state.get("messages", []) + [agent_message],
        "student_response": None  # Clear for next interaction
    }


def build_probing_message(
    probing_question: str,
    takeaway_num: int,
    total_takeaways: int,
    concept_name: str
) -> str:
    """
    Builds the agent message containing the probing question.
    
    Args:
        probing_question: The question to ask
        takeaway_num: Current takeaway number (1-indexed)
        total_takeaways: Total number of takeaways
        concept_name: Name of the current concept
        
    Returns:
        Formatted question message
    """
    message_parts = [
        f"❓ **Question** (Takeaway {takeaway_num}/{total_takeaways})",
        "",
        f"Based on what you observed about *{concept_name}*:",
        "",
        f"**{probing_question}**",
        "",
        "💭 Take your time to think, then share your answer."
    ]
    
    return "\n".join(message_parts)


def simulate_student_response(
    probing_question: str,
    concept_name: str,
    learner_profile: Dict[str, Any]
) -> str:
    """
    Simulates a student response for testing purposes.
    
    The simulated response varies based on the learner's calibre:
    - High IQ: Detailed, correct response
    - Medium: Partially correct response
    - Dull: Simple or confused response
    
    Args:
        probing_question: The question asked
        concept_name: The concept being taught
        learner_profile: Student's level and calibre
        
    Returns:
        Simulated student response string
    """
    calibre = learner_profile.get("calibre", "Medium")
    
    # Generate different quality responses based on calibre
    # These are generic responses that work for any concept
    
    if calibre == "High IQ":
        responses = [
            f"I observed that when I changed the parameter, the {concept_name.lower()} responded as expected. The relationship seems to be direct.",
            f"Yes, I noticed the change clearly. The effect on the simulation matches what you explained about {concept_name.lower()}.",
            f"The simulation shows exactly what the lesson described. I can see how the parameters affect the outcome."
        ]
    elif calibre == "Dull":
        responses = [
            "I'm not sure what I saw. Can you explain again?",
            "Something changed but I don't understand why.",
            "I saw the colors change but I'm confused about what it means.",
            "The numbers went up... or was it down?"
        ]
    else:  # Medium
        responses = [
            f"I think I saw the {concept_name.lower()} change when I adjusted the slider.",
            "The simulation showed some change, I believe it increased.",
            f"I noticed something different happening with the {concept_name.lower()}.",
            "I saw the effect, but I'm not 100% sure I understood everything."
        ]
    
    # Randomly pick one response for variety in testing
    import random
    return random.choice(responses)


def create_interaction_record(
    agent_message: str,
    student_response: str
) -> Dict[str, Any]:
    """
    Creates an interaction record for the interactions history.
    
    Args:
        agent_message: What the agent asked
        student_response: What the student answered
        
    Returns:
        Interaction dictionary matching the Interaction TypedDict
    """
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "agent_message": agent_message,
        "student_response": student_response,
        "understanding_status": None  # Will be filled by Understanding Checker Node
    }


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 11: Understanding Checker Node
# ═══════════════════════════════════════════════════════════════════════════════

def understanding_checker_node(state: TeachingState) -> Dict[str, Any]:
    """
    Step 11: Understanding Checker Node
    
    Analyzes the student's response using LLM to determine their level
    of understanding. This node:
    1. Gets the latest interaction (question + student response)
    2. Gets the concept and takeaway context
    3. Uses LLM to analyze if the student understood
    4. Classifies understanding as: "understood", "partial", or "confused"
    5. Updates understanding_status in state
    6. Sets next_action to "feedback"
    
    REQUIRES LLM - Semantic analysis of student response.
    
    Args:
        state: Current teaching state with interactions
        
    Returns:
        Dict with:
        - understanding_status: Updated understanding classification
        - interactions: Updated with understanding_status filled in
        - next_action: "feedback"
        
    State Fields Used:
        - interactions: List with latest interaction to analyze
        - concepts: Current concept being taught
        - current_concept_index: Which concept we're on
        - takeaways: Current lesson plan
        - current_takeaway_index: Which takeaway was just taught
        - learner_profile: For context about expected response level
    """
    
    print("\n" + "="*60)
    print("UNDERSTANDING CHECKER NODE - Analyzing Student Response")
    print("="*60)
    
    # Extract relevant state
    interactions = state.get("interactions", [])
    concepts = state.get("concepts", [])
    current_concept_idx = state.get("current_concept_index", 0)
    takeaways = state.get("takeaways", [])
    current_takeaway_idx = state.get("current_takeaway_index", 0)
    learner_profile = state.get("learner_profile", {})
    
    # Validate we have an interaction to analyze
    if not interactions:
        print("\n❌ Error: No interactions to analyze")
        return {
            "error": "No interactions available for analysis",
            "next_action": "feedback",
            "understanding_status": {
                "is_confused": False,
                "confidence_level": 0.5,
                "last_interaction_quality": "neutral"
            }
        }
    
    # Get the latest interaction
    latest_interaction = interactions[-1]
    student_response = latest_interaction.get("student_response", "")
    
    # Get current concept and takeaway for context
    current_concept = {}
    if current_concept_idx < len(concepts):
        current_concept = concepts[current_concept_idx]
    
    current_takeaway = {}
    if current_takeaway_idx < len(takeaways):
        current_takeaway = takeaways[current_takeaway_idx]
    
    concept_name = current_concept.get("name", "Unknown Concept")
    concept_description = current_concept.get("description", "")
    takeaway_explanation = current_takeaway.get("explanation", "")
    probing_question = current_takeaway.get("probing_question", "")
    
    print(f"\n📚 Concept: '{concept_name}'")
    print(f"❓ Question: {probing_question[:60]}...")
    print(f"💬 Student Response: \"{student_response[:80]}...\"" if len(student_response) > 80 else f"💬 Student Response: \"{student_response}\"")
    
    # Initialize LLM
    print(f"\n🤖 Initializing LLM for response analysis...")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from dotenv import load_dotenv
        import os
        import json
        
        load_dotenv()
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.3  # Lower temperature for more consistent analysis
        )
        print(f"✅ LLM initialized: {model_name}")
        
        # Build the analysis prompt
        prompt = build_understanding_prompt(
            concept_name=concept_name,
            concept_description=concept_description,
            takeaway_explanation=takeaway_explanation,
            probing_question=probing_question,
            student_response=student_response,
            learner_level=learner_profile.get("level", "Beginner")
        )
        
        print(f"\n🔄 Analyzing student response...")
        
        # Call LLM
        response = llm.invoke(prompt)
        response_text = response.content
        
        print(f"📄 LLM Response: {response_text[:100]}...")
        
        # Parse the response
        understanding_result = parse_understanding_response(response_text)
        
    except Exception as e:
        print(f"\n⚠️ LLM Error: {str(e)}")
        print("   Using fallback analysis...")
        # Fallback: simple keyword-based analysis
        understanding_result = fallback_understanding_analysis(
            student_response=student_response,
            probing_question=probing_question
        )
    
    # Extract classification
    classification = understanding_result.get("classification", "partial")
    confidence = understanding_result.get("confidence", 0.5)
    reasoning = understanding_result.get("reasoning", "Analysis completed.")
    
    # Map classification to understanding_status
    is_confused = classification == "confused"
    
    if classification == "understood":
        interaction_quality = "good"
    elif classification == "confused":
        interaction_quality = "poor"
    else:  # partial
        interaction_quality = "neutral"
    
    understanding_status = {
        "is_confused": is_confused,
        "confidence_level": confidence,
        "last_interaction_quality": interaction_quality
    }
    
    # Update the latest interaction with understanding status
    updated_interactions = interactions.copy()
    updated_interactions[-1] = {
        **latest_interaction,
        "understanding_status": understanding_status
    }
    
    # Display results
    print(f"\n📊 Understanding Analysis Results:")
    print(f"   Classification: {classification.upper()}")
    print(f"   Confidence: {confidence:.0%}")
    print(f"   Is Confused: {is_confused}")
    print(f"   Reasoning: {reasoning[:100]}...")
    
    print("\n" + "="*60)
    print("🎯 UNDERSTANDING CHECK COMPLETE: Ready for feedback")
    print(f"   Next: Generate {'encouragement' if classification == 'understood' else 'helpful feedback'}")
    print("="*60 + "\n")
    
    # Return updated state
    return {
        "understanding_status": understanding_status,
        "interactions": updated_interactions,
        "next_action": "feedback",
        "messages": state.get("messages", []) + [
            f"Understanding Checker: Student shows '{classification}' understanding (confidence: {confidence:.0%})"
        ]
    }


def build_understanding_prompt(
    concept_name: str,
    concept_description: str,
    takeaway_explanation: str,
    probing_question: str,
    student_response: str,
    learner_level: str
) -> str:
    """
    Builds the LLM prompt for analyzing student understanding.
    
    The prompt is designed to:
    - Accept short, informal answers
    - Focus on semantic meaning, not exact wording
    - Be tolerant of typos and casual language
    - Adapt expectations based on learner level
    
    Args:
        concept_name: Name of the concept being taught
        concept_description: Description of the concept
        takeaway_explanation: What was explained to the student
        probing_question: The question that was asked
        student_response: The student's answer
        learner_level: Beginner/Intermediate/Advanced
        
    Returns:
        Formatted prompt string
    """
    
    # Adjust expectations based on level
    if learner_level == "Beginner":
        level_guidance = "For a beginner, accept simple and basic correct answers. Don't expect technical terminology."
    elif learner_level == "Advanced":
        level_guidance = "For an advanced student, expect more precise and detailed understanding."
    else:
        level_guidance = "For an intermediate student, expect reasonable understanding with some detail."
    
    prompt = f"""You are an expert teacher analyzing a student's response to check their understanding.

CONTEXT:
- Concept being taught: {concept_name}
- Concept description: {concept_description}
- What was explained: {takeaway_explanation}
- Question asked: {probing_question}

STUDENT'S RESPONSE:
"{student_response}"

STUDENT LEVEL: {learner_level}
{level_guidance}

ANALYSIS GUIDELINES:
1. Focus on whether the student grasped the CORE IDEA, not exact wording
2. Accept short answers like "7", "neutral", "yes" if they're correct
3. Accept informal language, abbreviations (idk, etc.), and minor typos
4. Look for understanding of the concept, not memorized definitions
5. Consider if the answer addresses what was asked

CLASSIFY THE RESPONSE AS:
- "understood": Student clearly grasped the concept (even if answer is brief)
- "partial": Student has some understanding but is incomplete or slightly off
- "confused": Student's answer is wrong, irrelevant, or shows misunderstanding

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "classification": "understood" or "partial" or "confused",
    "confidence": 0.0 to 1.0,
    "reasoning": "Brief explanation of why you classified it this way"
}}

Analyze the response now:"""
    
    return prompt


def parse_understanding_response(response_text: str) -> Dict[str, Any]:
    """
    Parses the LLM response into understanding classification.
    
    Args:
        response_text: Raw LLM response
        
    Returns:
        Dict with classification, confidence, and reasoning
    """
    import json
    
    try:
        # Try to extract JSON from response
        text = response_text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith("```"):
                    in_json = not in_json
                elif in_json:
                    json_lines.append(line)
            text = "\n".join(json_lines)
        
        # Parse JSON
        result = json.loads(text)
        
        # Validate and normalize
        classification = result.get("classification", "partial").lower()
        if classification not in ["understood", "partial", "confused"]:
            classification = "partial"
        
        confidence = float(result.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
        
        reasoning = result.get("reasoning", "Analysis completed.")
        
        return {
            "classification": classification,
            "confidence": confidence,
            "reasoning": reasoning
        }
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"⚠️ Error parsing LLM response: {e}")
        # Try to extract classification from text
        text_lower = response_text.lower()
        if "understood" in text_lower:
            return {"classification": "understood", "confidence": 0.7, "reasoning": "Extracted from text response"}
        elif "confused" in text_lower:
            return {"classification": "confused", "confidence": 0.7, "reasoning": "Extracted from text response"}
        else:
            return {"classification": "partial", "confidence": 0.5, "reasoning": "Could not parse response, defaulting to partial"}


def fallback_understanding_analysis(
    student_response: str,
    probing_question: str
) -> Dict[str, Any]:
    """
    Fallback analysis when LLM is unavailable.
    Uses simple heuristics to estimate understanding.
    
    Args:
        student_response: The student's answer
        probing_question: The question that was asked
        
    Returns:
        Dict with classification, confidence, and reasoning
    """
    response_lower = student_response.lower().strip()
    
    # Check for confusion indicators
    confusion_phrases = [
        "i don't know", "idk", "not sure", "confused", "don't understand",
        "can you explain", "what do you mean", "huh", "?", "i'm lost"
    ]
    
    for phrase in confusion_phrases:
        if phrase in response_lower:
            return {
                "classification": "confused",
                "confidence": 0.6,
                "reasoning": f"Response contains confusion indicator: '{phrase}'"
            }
    
    # Check for very short responses (might be correct but brief)
    if len(response_lower) < 5:
        return {
            "classification": "partial",
            "confidence": 0.4,
            "reasoning": "Response is very short, unclear if understood"
        }
    
    # Check for positive engagement indicators
    positive_phrases = [
        "i see", "i understand", "makes sense", "got it", "yes",
        "the", "when", "because", "so", "it"
    ]
    
    positive_count = sum(1 for phrase in positive_phrases if phrase in response_lower)
    
    if positive_count >= 2 and len(response_lower) > 20:
        return {
            "classification": "understood",
            "confidence": 0.6,
            "reasoning": "Response shows engagement and reasonable length"
        }
    
    # Default to partial
    return {
        "classification": "partial",
        "confidence": 0.5,
        "reasoning": "Fallback analysis - unable to determine with confidence"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 12: Feedback Node
# ═══════════════════════════════════════════════════════════════════════════════

# Maximum re-explanation attempts before moving on
MAX_RE_EXPLAIN_ATTEMPTS = 3


def feedback_node(state: TeachingState) -> Dict[str, Any]:
    """
    Step 12: Feedback Node
    
    Generates adaptive feedback based on the student's understanding level.
    This is the CRITICAL node that closes the teaching loop by deciding
    whether to:
    - Move forward (understood)
    - Give a hint and re-probe (partial)
    - Re-explain the same takeaway (confused)
    
    The node uses understanding_status from the Understanding Checker Node
    to make its decision.
    
    NO LLM REQUIRED - Uses rule-based logic for routing decisions.
    (Could be enhanced with LLM for personalized feedback messages)
    
    Args:
        state: Current teaching state with understanding_status
        
    Returns:
        Dict with:
        - feedback_message: Message to show student
        - next_action: "next_takeaway", "re_probe", or "re_explain"
        - current_takeaway_index: Possibly incremented
        - re_explain_count: Tracked to prevent infinite loops
        
    State Fields Used:
        - understanding_status: From Understanding Checker Node
        - current_takeaway_index: Which takeaway we're on
        - takeaways: List of all takeaways
        - current_concept_index: Which concept we're teaching
        - concepts: List of all concepts
        - re_explain_count: How many times we've re-explained
        - interactions: For context in feedback
    """
    
    print("\n" + "="*60)
    print("FEEDBACK NODE - Generating Adaptive Feedback")
    print("="*60)
    
    # Extract relevant state
    understanding_status = state.get("understanding_status", {})
    current_takeaway_idx = state.get("current_takeaway_index", 0)
    takeaways = state.get("takeaways", [])
    current_concept_idx = state.get("current_concept_index", 0)
    concepts = state.get("concepts", [])
    re_explain_count = state.get("re_explain_count", 0)
    interactions = state.get("interactions", [])
    learner_profile = state.get("learner_profile", {})
    
    # Get understanding classification
    is_confused = understanding_status.get("is_confused", False)
    confidence_level = understanding_status.get("confidence_level", 0.5)
    interaction_quality = understanding_status.get("last_interaction_quality", "neutral")
    
    # Get current concept name for context
    current_concept_name = "the concept"
    if current_concept_idx < len(concepts):
        current_concept_name = concepts[current_concept_idx].get("name", "the concept")
    
    # Get current takeaway for context
    current_takeaway = {}
    if current_takeaway_idx < len(takeaways):
        current_takeaway = takeaways[current_takeaway_idx]
    
    takeaway_concept = current_takeaway.get("concept", current_concept_name)
    
    print(f"\n📚 Concept: '{current_concept_name}'")
    print(f"📖 Takeaway: {current_takeaway_idx + 1} of {len(takeaways)}")
    print(f"\n📊 Understanding Status:")
    print(f"   Is Confused: {is_confused}")
    print(f"   Confidence: {confidence_level:.0%}")
    print(f"   Quality: {interaction_quality}")
    print(f"   Re-explain Count: {re_explain_count}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DECISION LOGIC: Determine feedback path
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Path 1: UNDERSTOOD - Move to next takeaway
    if not is_confused and confidence_level >= 0.7:
        feedback_message, next_action, new_takeaway_idx, new_re_explain_count = handle_understood(
            current_takeaway_idx=current_takeaway_idx,
            total_takeaways=len(takeaways),
            takeaway_concept=takeaway_concept,
            learner_calibre=learner_profile.get("calibre", "Medium")
        )
    
    # Path 2: PARTIAL - Give hint and re-probe
    elif not is_confused and confidence_level >= 0.4:
        feedback_message, next_action, new_takeaway_idx, new_re_explain_count = handle_partial(
            current_takeaway=current_takeaway,
            current_takeaway_idx=current_takeaway_idx,
            takeaway_concept=takeaway_concept,
            re_explain_count=re_explain_count,
            total_takeaways=len(takeaways)
        )
    
    # Path 3: CONFUSED - Re-explain or move on
    else:
        feedback_message, next_action, new_takeaway_idx, new_re_explain_count = handle_confused(
            current_takeaway=current_takeaway,
            current_takeaway_idx=current_takeaway_idx,
            total_takeaways=len(takeaways),
            takeaway_concept=takeaway_concept,
            re_explain_count=re_explain_count
        )
    
    # Log decision
    print(f"\n🎯 Feedback Decision:")
    print(f"   Path: {'UNDERSTOOD' if not is_confused and confidence_level >= 0.7 else 'PARTIAL' if not is_confused else 'CONFUSED'}")
    print(f"   Next Action: {next_action}")
    print(f"   New Takeaway Index: {new_takeaway_idx}")
    print(f"   New Re-explain Count: {new_re_explain_count}")
    print(f"   (Max attempts: {MAX_RE_EXPLAIN_ATTEMPTS})")
    
    print("\n" + "="*60)
    print(f"🎯 FEEDBACK COMPLETE: Next action = '{next_action}'")
    print("="*60 + "\n")
    
    # Build return dict
    result = {
        "feedback_message": feedback_message,
        "next_action": next_action,
        "current_takeaway_index": new_takeaway_idx,
        "re_explain_count": new_re_explain_count,
        "messages": state.get("messages", []) + [
            f"Feedback: {feedback_message[:100]}..."
        ]
    }
    
    # If concept is complete, increment concept index and reset everything
    if next_action == "concept_complete":
        result["current_concept_index"] = current_concept_idx + 1
        result["current_takeaway_index"] = 0
        result["takeaways"] = []  # Clear takeaways for next concept
        result["re_explain_count"] = 0
        # IMPORTANT: Reset understanding_status so router doesn't think we're still confused
        result["understanding_status"] = {
            "is_confused": False,
            "confidence_level": 0.5,
            "last_interaction_quality": "neutral"
        }
        print(f"   📚 Incrementing concept index: {current_concept_idx} → {current_concept_idx + 1}")
        print(f"   🔄 Reset understanding_status for new concept")
    
    return result


def handle_understood(
    current_takeaway_idx: int,
    total_takeaways: int,
    takeaway_concept: str,
    learner_calibre: str
) -> tuple:
    """
    Handles the case when student UNDERSTOOD the takeaway.
    
    Actions:
    - Generate praise message (calibrated to learner)
    - Increment takeaway index
    - Reset re_explain_count
    - Set next_action to continue teaching or go to router
    
    Args:
        current_takeaway_idx: Current takeaway index
        total_takeaways: Total number of takeaways
        takeaway_concept: Name of the concept in this takeaway
        learner_calibre: Student's calibre (High IQ/Medium/Dull)
        
    Returns:
        Tuple of (feedback_message, next_action, new_takeaway_idx, re_explain_count)
    """
    
    # Generate praise message based on calibre
    praise_messages = generate_praise_message(takeaway_concept, learner_calibre)
    
    # Increment takeaway index
    new_takeaway_idx = current_takeaway_idx + 1
    
    # Check if we've completed all takeaways
    if new_takeaway_idx >= total_takeaways:
        feedback_message = f"{praise_messages}\n\n🎉 You've completed all the takeaways for this concept! Let's move on."
        next_action = "concept_complete"  # Signal to router that concept is done
    else:
        feedback_message = f"{praise_messages}\n\n➡️ Let's move to the next takeaway!"
        next_action = "next_takeaway"  # Continue with next takeaway
    
    return feedback_message, next_action, new_takeaway_idx, 0  # Reset re_explain_count


def handle_partial(
    current_takeaway: Dict[str, Any],
    current_takeaway_idx: int,
    takeaway_concept: str,
    re_explain_count: int,
    total_takeaways: int = 0
) -> tuple:
    """
    Handles the case when student has PARTIAL understanding.
    
    Actions:
    - If under max attempts: Generate a hint and re-probe
    - If at/over max attempts: Move on with encouragement (avoid infinite loop)
    - Stay on same takeaway (no index increment) unless max reached
    - Set next_action to re-probe (ask again)
    
    Args:
        current_takeaway: The current takeaway dictionary
        current_takeaway_idx: Current takeaway index
        takeaway_concept: Name of the concept in this takeaway
        re_explain_count: How many times we've already tried
        total_takeaways: Total number of takeaways (for completion check)
        
    Returns:
        Tuple of (feedback_message, next_action, new_takeaway_idx, re_explain_count)
    """
    
    # Check if we've exceeded max attempts (prevent infinite loop)
    if re_explain_count >= MAX_RE_EXPLAIN_ATTEMPTS:
        # Student is making progress but struggling - move on with encouragement
        feedback_message = (
            f"👍 You're getting there with {takeaway_concept}!\n\n"
            f"Let's move forward - sometimes the next concept helps clarify things."
        )
        
        new_takeaway_idx = current_takeaway_idx + 1
        
        # Check if we've completed all takeaways
        if new_takeaway_idx >= total_takeaways:
            next_action = "concept_complete"
        else:
            next_action = "next_takeaway"
        
        return feedback_message, next_action, new_takeaway_idx, 0  # Reset count
    
    # Generate hint based on takeaway
    hint = generate_hint(current_takeaway, takeaway_concept)
    
    feedback_message = f"🤔 You're on the right track!\n\n💡 **Hint:** {hint}\n\nLet me ask you again..."
    
    # Stay on same takeaway, ask again
    next_action = "re_probe"
    
    # Increment re_explain_count (partial attempts count too)
    return feedback_message, next_action, current_takeaway_idx, re_explain_count + 1


def handle_confused(
    current_takeaway: Dict[str, Any],
    current_takeaway_idx: int,
    total_takeaways: int,
    takeaway_concept: str,
    re_explain_count: int
) -> tuple:
    """
    Handles the case when student is CONFUSED.
    
    Actions:
    - If under MAX_RE_EXPLAIN_ATTEMPTS: Re-explain the takeaway
    - If at/over MAX: Move on with encouragement (avoid infinite loop)
    
    Args:
        current_takeaway: The current takeaway dictionary
        current_takeaway_idx: Current takeaway index
        total_takeaways: Total number of takeaways
        takeaway_concept: Name of the concept in this takeaway
        re_explain_count: How many times we've already re-explained
        
    Returns:
        Tuple of (feedback_message, next_action, new_takeaway_idx, re_explain_count)
    """
    
    # Check if we've exceeded max re-explanation attempts
    if re_explain_count >= MAX_RE_EXPLAIN_ATTEMPTS:
        # Give up on this takeaway, move forward with encouragement
        feedback_message = (
            f"😊 That's okay! {takeaway_concept} can be tricky.\n\n"
            f"Let's come back to this later. For now, let's continue and things might become clearer."
        )
        
        new_takeaway_idx = current_takeaway_idx + 1
        
        # Check if we've completed all takeaways
        if new_takeaway_idx >= total_takeaways:
            next_action = "concept_complete"
        else:
            next_action = "next_takeaway"
        
        return feedback_message, next_action, new_takeaway_idx, 0  # Reset count
    
    else:
        # Re-explain the takeaway in a different way
        simpler_explanation = generate_simpler_explanation(current_takeaway, re_explain_count)
        
        feedback_message = (
            f"🔄 No worries! Let me explain this differently...\n\n"
            f"💡 {simpler_explanation}\n\n"
            f"Take a moment to observe the simulation again."
        )
        
        next_action = "re_explain"
        
        # Increment re_explain_count
        return feedback_message, next_action, current_takeaway_idx, re_explain_count + 1


def generate_praise_message(takeaway_concept: str, learner_calibre: str) -> str:
    """
    Generates a praise message tailored to the learner's calibre.
    
    - High IQ: More substantive acknowledgment
    - Medium: Balanced encouragement
    - Dull: Extra enthusiastic support
    
    Args:
        takeaway_concept: The concept that was understood
        learner_calibre: Student's calibre
        
    Returns:
        Praise message string
    """
    import random
    
    if learner_calibre == "High IQ":
        praises = [
            f"✅ Excellent! You've got a solid grasp of {takeaway_concept}.",
            f"✅ Perfect! Your understanding of {takeaway_concept} is clear.",
            f"✅ Well done! You've captured the essence of {takeaway_concept}."
        ]
    elif learner_calibre == "Dull":
        praises = [
            f"🌟 Fantastic job! You really understood {takeaway_concept}! Keep it up!",
            f"🌟 Amazing work! You're doing great with {takeaway_concept}!",
            f"🌟 Wonderful! You're making excellent progress on {takeaway_concept}!"
        ]
    else:  # Medium
        praises = [
            f"✅ Great job! You understood {takeaway_concept} well.",
            f"✅ Nice work! You've got {takeaway_concept} figured out.",
            f"✅ Good! You clearly understand {takeaway_concept}."
        ]
    
    return random.choice(praises)


def generate_hint(current_takeaway: Dict[str, Any], takeaway_concept: str) -> str:
    """
    Generates a hint based on the current takeaway content.
    
    Uses the explanation and parameters to create a helpful nudge
    without giving away the answer completely.
    
    Args:
        current_takeaway: The takeaway dictionary
        takeaway_concept: The concept name
        
    Returns:
        Hint string
    """
    explanation = current_takeaway.get("explanation", "")
    parameters = current_takeaway.get("parameters_to_vary", [])
    
    # Extract key terms from explanation
    if parameters:
        params_str = ", ".join(parameters[:2])  # First 2 parameters
        hint = f"Focus on what happens when you change {params_str}. What relationship do you see?"
    elif explanation:
        # Extract first sentence or key phrase
        first_sentence = explanation.split(".")[0]
        if len(first_sentence) > 100:
            first_sentence = first_sentence[:100] + "..."
        hint = f"Think about this: {first_sentence}"
    else:
        hint = f"Think about how {takeaway_concept} changes when you adjust the controls."
    
    return hint


def generate_simpler_explanation(current_takeaway: Dict[str, Any], attempt_number: int) -> str:
    """
    Generates a progressively simpler explanation for re-teaching.
    
    Each attempt uses a simpler approach:
    - Attempt 1: Focus on one key aspect
    - Attempt 2: Use an analogy
    - Attempt 3+: Break down to basics
    
    Args:
        current_takeaway: The takeaway dictionary
        attempt_number: Which re-explanation attempt this is (0-indexed)
        
    Returns:
        Simpler explanation string
    """
    original_explanation = current_takeaway.get("explanation", "Let's try again.")
    concept = current_takeaway.get("concept", "this concept")
    parameters = current_takeaway.get("parameters_to_vary", [])
    
    if attempt_number == 0:
        # First re-explain: Focus on one thing
        if parameters:
            return f"Let's focus on just one thing: When you change '{parameters[0]}', what happens? Watch carefully!"
        else:
            return f"Let's simplify: {original_explanation.split('.')[0]}. Just observe this one thing."
    
    elif attempt_number == 1:
        # Second re-explain: Use an analogy
        return f"Think of {concept} like a cause-and-effect relationship. When you change something on the left side, what changes on the right? It's like turning up the heat - the temperature rises!"
    
    else:
        # Third+ re-explain: Ultra simple
        return f"Let's make it super simple: Just watch what moves or changes when you interact with the simulation. Don't worry about 'why' yet - just observe 'what' happens!"


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTING HELPER (for graph.py)
# ═══════════════════════════════════════════════════════════════════════════════

def route_after_feedback(state: TeachingState) -> str:
    """
    Routing function for conditional edges after feedback node.
    
    This function is used by graph.py to determine where to go after feedback.
    
    Possible routes:
    - "teaching": Go back to teaching node (next takeaway or re-explain)
    - "probing": Go directly to probing (for re-probe)
    - "router": Go to router (concept complete or error)
    
    Args:
        state: Current teaching state
        
    Returns:
        String name of the next node
    """
    next_action = state.get("next_action", "teaching")
    
    if next_action == "next_takeaway":
        # Move to next takeaway, teaching node will present it
        return "teaching"
    
    elif next_action == "re_explain":
        # Re-explain same takeaway, teaching node will re-present
        return "teaching"
    
    elif next_action == "re_probe":
        # Ask the same question again with a hint
        return "probing"
    
    elif next_action == "concept_complete":
        # All takeaways done, go back to router to decide next step
        return "router"
    
    else:
        # Default: go to teaching
        return "teaching"
