"""
Planner Node - Step 8

This node generates a structured lesson plan for teaching a single concept.
It uses Gemini LLM to create 2-3 "takeaways" - each takeaway is a mini-lesson
that explains one aspect of the concept with specific simulation parameters
to vary and probing questions to check understanding.

The lesson plan adapts to:
- Student level (Beginner/Intermediate/Advanced)
- Student calibre (Dull/Medium/High IQ)
- Control mode (MANUAL/AUTO)
"""

from typing import Dict, Any, List
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from state import TeachingState
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def planner_node(state: TeachingState) -> Dict[str, Any]:
    """
    Generates a lesson plan for the current concept.
    
    Creates 2-3 takeaways that:
    1. Explain different aspects of the concept
    2. Specify which simulation parameters to vary
    3. Define display mode (single or before_after)
    4. Include probing questions for understanding checks
    
    Args:
        state: Current teaching state
        
    Returns:
        Dict with lesson plan (takeaways) and next action
        
    State Fields Used:
        - concepts: List of concepts to teach
        - current_concept_index: Which concept to plan for
        - learner_profile: Student's level and calibre
        - simulation_params: Available parameters from simulation
        - control_mode: MANUAL or AUTO mode
    """
    
    print("\n" + "="*60)
    print("PLANNER NODE - Generating Lesson Plan")
    print("="*60)
    
    # Extract current concept
    current_index = state.get("current_concept_index", 0)
    concepts = state.get("concepts", [])
    
    if current_index >= len(concepts):
        print("\n❌ Error: No concept to plan for")
        return {
            "error": "No concept available at current index",
            "next_action": "assess"
        }
    
    current_concept = concepts[current_index]
    learner_profile = state.get("learner_profile", {})
    simulation_params = state.get("simulation_params", {})
    simulation_buttons = state.get("simulation_buttons", [])
    control_mode = state.get("control_mode", "MANUAL")
    
    # Display planning context
    print(f"\n📚 Planning for Concept #{current_index + 1}")
    print(f"   Concept: '{current_concept.get('name', 'Unknown')}'")
    print(f"   Importance: {current_concept.get('importance', 'N/A')}")
    print(f"\n👤 Student Profile:")
    print(f"   Level: {learner_profile.get('level', 'Unknown')}")
    print(f"   Calibre: {learner_profile.get('calibre', 'Unknown')}")
    print(f"\n🎛️  Control Mode: {control_mode}")
    print(f"   Available Parameters: {len(simulation_params)}")
    print(f"   Available Buttons: {len(simulation_buttons)}")
    
    # Initialize LLM
    print(f"\n🤖 Initializing LLM...")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    temperature = float(os.getenv("TEMPERATURE", "0.7"))
    # max_tokens = int(os.getenv("MAX_TOKENS", "2048"))
    # max_tokens = 4096  # Increased token limit
    
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        # max_tokens=max_tokens
    )
    print(f"✅ LLM initialized: {model_name}")
    
    # Build prompt for lesson plan generation
    prompt = build_planner_prompt(
        concept=current_concept,
        learner_profile=learner_profile,
        simulation_params=simulation_params,
        simulation_buttons=simulation_buttons,
        control_mode=control_mode
    )
    
    print(f"\n🔄 Calling LLM to generate lesson plan...")
    
    try:
        # Call 
        # print(f"See here 123 prompt = {prompt}")
        response = llm.invoke(prompt)
        # print(f"See here 123 response = {response}")
        response_text = response.content
        
        print(f"📄 LLM Response length: {len(response_text)} characters")
        
        # Parse JSON response
        print("REACHED HERE")
        takeaways = parse_takeaways(response_text)
        print("PARSED NOW SO SHOULD WORK")
        
        if not takeaways:
            print("\n⚠️  No takeaways generated, using fallback")
            takeaways = create_fallback_takeaways(current_concept, simulation_params)
        
        print(f"\n✅ Generated {len(takeaways)} takeaways:")
        for i, takeaway in enumerate(takeaways, 1):
            print(f"   {i}. {takeaway.get('explanation', 'N/A')[:80]}...")
            print(f"      Parameters: {takeaway.get('parameters_to_vary', [])}")
            print(f"      Param Values: {takeaway.get('parameter_values', {})}")  # Debug: Show actual values
            print(f"      Display: {takeaway.get('display_mode', 'single')}")
        
        print("\n" + "="*60)
        print("🎯 LESSON PLAN COMPLETE")
        print("="*60 + "\n")
        
        # Return updated state
        return {
            "takeaways": takeaways,
            "current_takeaway_index": 0,
            "next_action": "teach",
            "messages": state.get("messages", []) + [
                f"Planner: Generated {len(takeaways)} takeaways for '{current_concept.get('name')}'"
            ]
        }
        
    except Exception as e:
        print(f"\n❌ Error generating lesson plan: {str(e)}")
        # Use fallback
        takeaways = create_fallback_takeaways(current_concept, simulation_params)
        raise e
        return {
            "takeaways": takeaways,
            "current_takeaway_index": 0,
            "next_action": "teach",
            "error": f"Planner error (using fallback): {str(e)}"
        }


def build_planner_prompt(
    concept: Dict[str, Any],
    learner_profile: Dict[str, str],
    simulation_params: Dict[str, Any],
    simulation_buttons: List[Dict[str, str]],
    control_mode: str
) -> str:
    """
    Builds the LLM prompt for lesson plan generation.
    
    Args:
        concept: The concept to teach
        learner_profile: Student's level and calibre
        simulation_params: Available simulation parameters
        simulation_buttons: Available buttons in the simulation
        control_mode: MANUAL or AUTO
        
    Returns:
        Formatted prompt string
    """
    
    # Format parameters for prompt
    param_list = []
    for param_name, param_info in simulation_params.items():
        param_type = param_info.get('type', 'unknown')
        if param_type == 'range':
            param_list.append(f"- {param_name} (slider: {param_info.get('min')} to {param_info.get('max')})")
        elif param_type == 'select':
            options = param_info.get('options', [])
            param_list.append(f"- {param_name} (dropdown: {', '.join(options)})")
        else:
            param_list.append(f"- {param_name} ({param_type})")
    
    params_text = "\n".join(param_list) if param_list else "No parameters available"
    
    # Format buttons for prompt
    button_list = []
    for btn in simulation_buttons:
        btn_id = btn.get('id', '')
        btn_label = btn.get('label', '')
        if btn_label:
            button_list.append(f"- \"{btn_label}\" button" + (f" (id: {btn_id})" if btn_id else ""))
    
    buttons_text = "\n".join(button_list) if button_list else "No action buttons"
    
    # Adapt complexity based on student level
    level = learner_profile.get('level', 'Beginner')
    calibre = learner_profile.get('calibre', 'Medium')
    
    if level == "Beginner":
        complexity_instruction = "Use simple language, focus on basic understanding. Create 2 takeaways."
    elif level == "Intermediate":
        complexity_instruction = "Use moderate complexity, include some technical terms. Create 2-3 takeaways."
    else:  # Advanced
        complexity_instruction = "Use advanced terminology, focus on deeper concepts. Create 3 takeaways."
    
    if calibre == "Dull":
        pace_instruction = "Keep explanations very simple with concrete examples. One parameter per takeaway."
    elif calibre == "Medium":
        pace_instruction = "Balance simplicity and depth. 1-2 parameters per takeaway."
    else:  # High IQ
        pace_instruction = "Can use complex explanations and multiple parameters. 2-3 parameters per takeaway."
    
    # Display mode instruction (same for all levels)
    display_instruction = """
DISPLAY MODE SELECTION:
- Use "before_after" when the takeaway demonstrates a CHANGE or COMPARISON
  Examples: "Adding acid lowers pH", "Increasing speed reduces time", "Comparing two substances"
  This shows cause-and-effect clearly with side-by-side comparison
  
- Use "single" only when showing a STATIC STATE or DEFINITION
  Examples: "This is what neutral pH looks like", "The pH scale ranges from 0-14"
  This introduces the simulation without demonstrating changes

IMPORTANT: Prefer "before_after" for most teaching scenarios as it makes learning more concrete.
"""
    
    # Mode-specific instructions
    if control_mode == "MANUAL":
        mode_instruction = """
The system is in MANUAL mode - the student will change parameters themselves.
Do NOT include specific parameter values in your takeaways.
Instead, provide clear instructions like "Increase the concentration slider" or "Change the substance type to base".
"""
    else:  # AUTO
        mode_instruction = """
The system is in AUTO mode - parameters will be set automatically via URL.
YOU MUST INCLUDE "parameter_values" FOR EVERY TAKEAWAY!

CRITICAL RULE - Parameter values REQUIRED for ALL display modes:

For "single" display mode:
  "parameter_values": {"lengthSlider": 5.0, "autoStart": true}

For "before_after" display mode - YOU MUST PROVIDE ALL THREE:
  "parameter_values": {"lengthSlider": 8.0, "autoStart": true},  // The 'after' value
  "before_state": {"lengthSlider": 3.0, "autoStart": true},      // State before the change
  "after_state": {"lengthSlider": 8.0, "autoStart": true}        // State after the change

🚀 AUTO-START REQUIREMENT:
ALWAYS include "autoStart": true in parameter_values, before_state, and after_state!
This makes the simulation automatically start/run after setting parameters.
Without autoStart, the student would need to manually click the Start button.

EXAMPLE VALUES for phSlider (acids/bases):
- Acidic:  phSlider = 1.0 to 6.0
- Neutral: phSlider = 7.0
- Basic:   phSlider = 8.0 to 14.0

If the simulation won't change, "parameter_values" is EMPTY - that's a BUG!
Always provide specific numeric values for the parameters.
"""
    
    prompt = f"""You are an expert teacher creating a lesson plan to teach a scientific concept using an interactive simulation.

CONCEPT TO TEACH:
Name: {concept.get('name', 'Unknown')}
Description: {concept.get('description', 'No description')}
Importance: {concept.get('importance', 'medium')}

⚠️ CRITICAL: Your takeaways MUST focus specifically on "{concept.get('name', 'Unknown')}"!
- Do NOT repeat basic concepts like "pH 7 is neutral" or "acids lower pH" unless this IS the concept being taught
- Each takeaway must directly relate to the concept name above
- If the concept is about "Volume's Impact" - focus on VOLUME
- If the concept is about "Concentration" - focus on CONCENTRATION
- Generate UNIQUE content for THIS specific concept

🎯 PARAMETER SELECTION - VERY IMPORTANT:
Use the RELEVANT parameter for each concept, not just phSlider!
- For "Concentration" concepts → VARY addConc (e.g., show addConc=0.5 vs addConc=2.0)
- For "Volume" concepts → VARY beakerVolume (e.g., show beakerVolume=100 vs beakerVolume=500)
- For "Acid vs Base" concepts → VARY addType (acid vs base)
- For "Drop size" concepts → VARY dropVol
- For "Pendulum length" concepts → VARY lengthSlider
- For "Speed/Time" concepts → VARY rotationSpeed, revolutionSpeed, etc.

The student learns better by ADJUSTING the relevant parameter and SEEING its effect!
Example: To teach concentration, don't just show pH=2 vs pH=5.
Instead, show: "With addConc=0.5, pH drops slowly" vs "With addConc=2.0, pH drops quickly"

STUDENT PROFILE:
- Level: {level}
- Learning Pace: {calibre}

ADAPTATION GUIDELINES:
{complexity_instruction}
{pace_instruction}

{display_instruction}

AVAILABLE SIMULATION PARAMETERS:
{params_text}

AVAILABLE BUTTONS/ACTIONS:
{buttons_text}

🔘 IMPORTANT - SIMULATION WORKFLOW:
Some simulations require clicking buttons AFTER setting parameters to see the effect.
- If there's a "Start" button → Student must click it to run the simulation
- If there's an "Add Drop" button → Student must click it to add substances
- If there's a "Reset" button → Student can use it to restart

In your takeaway explanation, INCLUDE instructions about which buttons to click!
Example: "Set the pendulum length to 8, then click 'Start' to observe the longer swing period."
Example: "After setting the concentration, click 'Add Drop' to see the pH change."

CONTROL MODE:
{mode_instruction}

YOUR TASK:
Create a structured lesson plan with 2-3 "takeaways" that are SPECIFIC to "{concept.get('name', 'Unknown')}".
Each takeaway is a mini-lesson that:
1. Explains ONE specific aspect of THIS concept (not generic basics)
2. Specifies which simulation parameters to vary - USE THE RELEVANT PARAMETER for this concept!
3. Defines display mode based on the type of demonstration:
   - "before_after": When showing parameter changes, comparisons, or cause-effect relationships
   - "single": Only when showing static states or introducing the simulation
4. Includes a probing question about THIS specific concept

RETURN FORMAT (JSON array):
[
  {{
    "id": 1,
    "explanation": "Clear explanation (2-3 sentences, keep concise)",
    "parameters_to_vary": ["addConc"],
    "parameter_values": {{"addConc": 0.5, "autoStart": true}},  // Use the RELEVANT parameter + autoStart!
    "display_mode": "single",
    "probing_question": "Question about THIS concept"
  }},
  {{
    "id": 2,
    "explanation": "Show the effect of changing the relevant parameter",
    "parameters_to_vary": ["addConc"],
    "parameter_values": {{"addConc": 2.0, "autoStart": true}},  // Higher concentration
    "display_mode": "before_after",
    "before_state": {{"addConc": 0.5, "autoStart": true}},  // Low concentration
    "after_state": {{"addConc": 2.0, "autoStart": true}},   // High concentration - see the difference!
    "probing_question": "What happens when concentration increases"
  }}
]

EXAMPLE FOR DIFFERENT CONCEPTS:
- For "Volume" concept: Use beakerVolume (100 vs 500) + autoStart: true
- For "Concentration" concept: Use addConc (0.5 vs 2.0) + autoStart: true
- For "Acid/Base" concept: Use addType (acid vs base) + autoStart: true
- For basic pH concept: Use phSlider (7 vs 2 vs 12) + autoStart: true
- For "Pendulum Length" concept: Use lengthSlider (3 vs 8) + autoStart: true

🚀 REMEMBER: Always include "autoStart": true in parameter_values, before_state, and after_state!

CRITICAL JSON FORMATTING RULES:
- Keep all text in explanations and questions SHORT and SIMPLE
- Avoid complex punctuation like dashes, parentheses, or apostrophes in JSON strings
- Use simple sentences
- If you need special characters, use simple alternatives
- Close all strings properly with double quotes

IMPORTANT:
- Return ONLY valid JSON array, no markdown formatting, no code blocks, no extra text
- Start with [ and end with ]
- Use double quotes for all strings
- Escape any quotes inside strings
- Choose parameters from the available list above
- Adapt complexity to student level (language/terminology), NOT display mode
- Use "before_after" display whenever demonstrating parameter changes or comparisons
- Use "single" display only for static introductions or definitions
- Probing questions should match the student's level
- Keep explanations concise (2-3 sentences max)

⚠️ FINAL CHECK: Before generating, ask yourself:
- Am I varying the RELEVANT parameter for "{concept.get('name', 'Unknown')}"?
- For concentration → addConc, for volume → beakerVolume, for acid/base → addType
- Are my probing questions about THIS concept, not generic pH questions?
- Did I include "autoStart": true in ALL parameter objects?

Generate the lesson plan now as valid JSON:"""
    
    return prompt


def parse_takeaways(response_text: str) -> List[Dict[str, Any]]:
    """
    Parses LLM response into takeaway objects.
    
    Args:
        response_text: Raw LLM response
        
    Returns:
        List of takeaway dictionaries
    """
    try:
        # Remove markdown code blocks if present
        text = response_text.strip()
        if text.startswith("```"):
            # Find the JSON content between code blocks
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
        takeaways = json.loads(text)
        
        # Validate structure
        if not isinstance(takeaways, list):
            print("⚠️  Response is not a list")
            return []
        
        # Ensure each takeaway has required fields
        validated_takeaways = []
        for i, takeaway in enumerate(takeaways, 1):
            if not isinstance(takeaway, dict):
                continue
            
            # Set defaults for missing fields
            validated_takeaway = {
                "id": takeaway.get("id", i),
                "explanation": takeaway.get("explanation", ""),
                "parameters_to_vary": takeaway.get("parameters_to_vary", []),
                "parameter_values": takeaway.get("parameter_values", {}),
                "display_mode": takeaway.get("display_mode", "single"),
                "before_state": takeaway.get("before_state"),
                "after_state": takeaway.get("after_state"),
                "probing_question": takeaway.get("probing_question", "Do you understand this concept?")
            }
            
            # FIX: If parameter_values is empty but we have after_state, use after_state
            # This handles the case where LLM forgets to include parameter_values for before_after mode
            if not validated_takeaway["parameter_values"] and validated_takeaway["after_state"]:
                validated_takeaway["parameter_values"] = validated_takeaway["after_state"].copy()
                print(f"   ⚡ Auto-filled parameter_values from after_state: {validated_takeaway['parameter_values']}")
            
            validated_takeaways.append(validated_takeaway)
        
        return validated_takeaways
        
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parsing error: {str(e)}")
        print(f"Response text: {response_text[:200]}...")
        raise e
        return []
    except Exception as e:
        print(f"⚠️  Error parsing takeaways: {str(e)}")
        raise e
        return []


def create_fallback_takeaways(
    concept: Dict[str, Any],
    simulation_params: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Creates fallback takeaways when LLM fails.
    
    Args:
        concept: The concept to teach
        simulation_params: Available parameters
        
    Returns:
        List of basic takeaway dictionaries
    """
    # Get first few parameters
    param_names = list(simulation_params.keys())[:3]
    
    return [
        {
            "id": 1,
            "explanation": f"Understanding {concept.get('name', 'this concept')}: {concept.get('description', 'Explore the simulation to learn more.')}",
            "parameters_to_vary": param_names[:1] if param_names else [],
            "parameter_values": {},
            "display_mode": "single",
            "before_state": None,
            "after_state": None,
            "probing_question": f"What do you observe about {concept.get('name', 'this concept')}?"
        },
        {
            "id": 2,
            "explanation": f"Let's explore how different parameters affect {concept.get('name', 'this concept')}.",
            "parameters_to_vary": param_names[1:2] if len(param_names) > 1 else param_names,
            "parameter_values": {},
            "display_mode": "single",
            "before_state": None,
            "after_state": None,
            "probing_question": "How does changing this parameter affect the outcome?"
        }
    ]
