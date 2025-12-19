"""
Ingestion nodes:
1. SimulationIngestNode - Validates and structures initial input
2. SimulationParserNode - Extracts parameters from HTML (optional)
3. ConceptExtractorNode - Extracts key concepts using LLM

These nodes handle the complete ingestion pipeline.
"""

from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import json

from state import TeachingState
# Import backend config with absolute path to avoid conflicts
from backend import config as backend_config

# Load environment variables
load_dotenv()


def simulation_ingest_node(state: TeachingState) -> Dict[str, Any]:
    """
    Step 4: Simulation Ingest Node
    
    Responsibilities:
    - Validates that required input data is present
    - Structures simulation metadata (name, URL, description)
    - Initializes empty fields in state
    - Determines and sets control mode based on config.py
    - Returns mode-specific configuration
    
    Args:
        state: Current teaching state
        
    Returns:
        Dict with updated state fields
    """
    print("\n=== Simulation Ingest Node ===")
    
    # Get simulation name from state
    sim_name = state.get("simulation_name")
    if not sim_name:
        raise ValueError("simulation_name is required in state")
    
    print(f"🔍 DEBUG: simulation_name = '{sim_name}' (type: {type(sim_name).__name__})")
    print(f"🔍 DEBUG: simulation_name repr = {repr(sim_name)}")
    print(f"🔍 DEBUG: Available simulations = {list(backend_config.SIMULATION_URLS.keys())}")
    
    # Get simulation URL from config
    try:
        sim_url = backend_config.get_simulation_url(sim_name)
        print(f"✅ Found URL: {sim_url}")
    except ValueError as e:
        print(f"❌ ValueError: {e}")
        print(f"🔍 Checking if '{sim_name}' in SIMULATION_URLS...")
        print(f"🔍 Result: {sim_name in backend_config.SIMULATION_URLS}")
        raise ValueError(f"Error loading simulation: {e}")
    
    # Get learner profile
    learner = state.get("learner_profile")
    if not learner:
        raise ValueError("learner_profile is required in state")
    
    print(f"📚 Simulation: {sim_name}")
    print(f"🔗 URL: {sim_url}")
    print(f"👤 Learner: Level={learner['level']}, Calibre={learner['calibre']}")
    
    # Determine control mode from config (the "clipper" parameter)
    control_mode = backend_config.SIMULATION_CONTROL_MODE
    mode_config = backend_config.get_current_mode_config()
    
    print(f"\n🎛️  Control Mode: {control_mode}")
    print(f"   - Can modify params: {mode_config['can_modify_params']}")
    print(f"   - Requires instructions: {mode_config['requires_instructions']}")
    print(f"   - Interaction type: {mode_config['interaction_type']}")
    
    # Initialize view_config based on mode
    view_config = {
        "mode": control_mode,
        "url": sim_url,
        "can_modify_params": mode_config["can_modify_params"],
        "current_params": {},  # Will be populated by parser node
    }
    
    # Prepare simulation metadata
    simulation_description = state.get("simulation_description", f"Interactive simulation for {sim_name}")
    
    # Return updated state fields
    return {
        "simulation_name": sim_name,
        "simulation_url": sim_url,
        "simulation_description": simulation_description,
        "control_mode": control_mode,
        "view_config": view_config,
        "concepts": [],  # Will be filled by concept extractor
        "current_concept_index": 0,
        "interactions": [],
        "assessment": None,
    }


def simulation_parser_node(state: TeachingState) -> Dict[str, Any]:
    """
    Step 5: Simulation Parser Node (Optional)
    
    Responsibilities:
    - Parses HTML simulation file to extract available parameters
    - Identifies input controls (sliders, dropdowns, checkboxes, etc.)
    - Extracts parameter ranges and default values
    - Updates simulation_params with parameter information
    
    Note: This is optional and mainly useful for AUTO mode or for understanding
    what parameters are available in MANUAL mode.
    
    Args:
        state: Current teaching state
        
    Returns:
        Dict with updated simulation_params containing extracted parameters
    """
    print("\n=== Simulation Parser Node ===")
    
    sim_url = state.get("simulation_url", "")
    sim_name = state.get("simulation_name", "")
    
    if not sim_url:
        print("⚠️  No simulation URL provided - skipping parsing")
        return {"simulation_params": {}}
    
    print(f"📄 Parsing HTML: {sim_url}")
    
    # Read the HTML file
    html_content = None
    try:
        # Check if URL is HTTP/HTTPS
        if sim_url.startswith("http://") or sim_url.startswith("https://"):
            # Fetch from HTTP server
            import urllib.request
            from urllib.parse import unquote
            
            print(f"🌐 Fetching from HTTP: {sim_url}")
            
            try:
                with urllib.request.urlopen(sim_url, timeout=5) as response:
                    html_content = response.read().decode('utf-8')
                print(f"✅ Successfully fetched HTML ({len(html_content)} chars)")
            except urllib.error.URLError as e:
                print(f"⚠️  Could not fetch from HTTP: {e}")
                # Try to read from local file as fallback
                # Extract filename from URL
                from urllib.parse import urlparse
                parsed = urlparse(sim_url)
                filename = unquote(parsed.path.lstrip('/'))
                
                # Try to find file in SimulationsNCERT-main folder
                backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                project_root = os.path.dirname(backend_dir)
                local_path = os.path.join(project_root, "SimulationsNCERT-main", filename)
                
                print(f"🔄 Trying local fallback: {local_path}")
                
                if os.path.exists(local_path):
                    with open(local_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    print(f"✅ Read from local file")
                else:
                    print(f"⚠️  Local file not found either")
                    return {"simulation_params": {}}
        
        # Handle relative paths from project root
        elif sim_url.startswith("../"):
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            project_root = os.path.dirname(backend_dir)
            html_path = os.path.join(project_root, sim_url.replace("../", ""))
            
            print(f"📂 Reading file: {html_path}")
            
            if not os.path.exists(html_path):
                print(f"⚠️  File not found: {html_path}")
                return {"simulation_params": {}}
            
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        
        # Handle absolute paths
        else:
            html_path = sim_url
            print(f"📂 Reading file: {html_path}")
            
            if not os.path.exists(html_path):
                print(f"⚠️  File not found: {html_path}")
                return {"simulation_params": {}}
            
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        
        if not html_content:
            print("⚠️  No HTML content loaded")
            return {"simulation_params": {}}
            
    except Exception as e:
        print(f"❌ Error reading HTML file: {e}")
        return {"simulation_params": {}}
    
    # Parse HTML with BeautifulSoup
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        print(f"✅ HTML parsed successfully")
        
    except Exception as e:
        print(f"❌ Error parsing HTML: {e}")
        return {"simulation_params": {}}
    
    # Extract parameters from HTML
    params = {}
    param_count = 0
    
    # 1. Extract range inputs (sliders)
    for input_elem in soup.find_all('input', {'type': 'range'}):
        param_id = input_elem.get('id') or input_elem.get('name') or f"slider_{param_count}"
        params[param_id] = {
            "type": "range",
            "html_id": param_id,
            "min": float(input_elem.get('min', 0)),
            "max": float(input_elem.get('max', 100)),
            "default": float(input_elem.get('value', 50)),
            "step": float(input_elem.get('step', 1)),
        }
        param_count += 1
    
    # 2. Extract number inputs
    for input_elem in soup.find_all('input', {'type': 'number'}):
        param_id = input_elem.get('id') or input_elem.get('name') or f"number_{param_count}"
        params[param_id] = {
            "type": "number",
            "html_id": param_id,
            "min": float(input_elem.get('min', 0)) if input_elem.get('min') else None,
            "max": float(input_elem.get('max', 100)) if input_elem.get('max') else None,
            "default": float(input_elem.get('value', 0)) if input_elem.get('value') else None,
        }
        param_count += 1
    
    # 3. Extract select dropdowns
    for select_elem in soup.find_all('select'):
        param_id = select_elem.get('id') or select_elem.get('name') or f"select_{param_count}"
        options = [opt.get('value', opt.text.strip()) for opt in select_elem.find_all('option')]
        default_opt = select_elem.find('option', selected=True)
        default_value = default_opt.get('value', default_opt.text.strip()) if default_opt else (options[0] if options else None)
        
        params[param_id] = {
            "type": "select",
            "html_id": param_id,
            "options": options,
            "default": default_value,
        }
        param_count += 1
    
    # 4. Extract checkboxes
    for input_elem in soup.find_all('input', {'type': 'checkbox'}):
        param_id = input_elem.get('id') or input_elem.get('name') or f"checkbox_{param_count}"
        params[param_id] = {
            "type": "checkbox",
            "html_id": param_id,
            "default": input_elem.get('checked') is not None,
        }
        param_count += 1
    
    # 5. Extract text inputs
    for input_elem in soup.find_all('input', {'type': 'text'}):
        param_id = input_elem.get('id') or input_elem.get('name') or f"text_{param_count}"
        params[param_id] = {
            "type": "text",
            "html_id": param_id,
            "default": input_elem.get('value', ''),
        }
        param_count += 1
    
    # 6. Extract buttons (for simulation workflow understanding)
    buttons = []
    for button_elem in soup.find_all('button'):
        button_id = button_elem.get('id', '')
        button_text = button_elem.get_text(strip=True)
        if button_id or button_text:
            buttons.append({
                "id": button_id,
                "label": button_text,
                "type": "button"
            })
    
    # Also check for input type="button" and input type="submit"
    for input_elem in soup.find_all('input', {'type': ['button', 'submit']}):
        button_id = input_elem.get('id') or input_elem.get('name') or ''
        button_text = input_elem.get('value', '')
        if button_id or button_text:
            buttons.append({
                "id": button_id,
                "label": button_text,
                "type": input_elem.get('type')
            })
    
    print(f"\n📊 Extracted Parameters:")
    print(f"   • Total parameters found: {len(params)}")
    
    if params:
        for param_id, param_data in list(params.items())[:3]:  # Show first 3
            print(f"   • {param_id}: {param_data['type']}")
        if len(params) > 3:
            print(f"   • ... and {len(params) - 3} more")
    else:
        print("   • No interactive parameters found in HTML")
    
    if buttons:
        print(f"\n🔘 Extracted Buttons:")
        print(f"   • Total buttons found: {len(buttons)}")
        for btn in buttons[:3]:
            print(f"   • {btn['label']} (id: {btn['id']})")
        if len(buttons) > 3:
            print(f"   • ... and {len(buttons) - 3} more")
    
    return {
        "simulation_params": params,
        "simulation_buttons": buttons,
    }


def concept_extractor_node(state: TeachingState) -> Dict[str, Any]:
    """
    Step 6: Concept Extractor Node
    
    Responsibilities:
    - Uses LLM (Gemini 2.0 Flash) to analyze simulation and extract 3-4 key concepts
    - Each concept includes name, description, and importance
    - Orders concepts from simple to complex
    - Adapts concept difficulty to learner's level and calibre
    
    Args:
        state: Current teaching state
        
    Returns:
        Dict with extracted concepts list
    """
    print("\n=== Concept Extractor Node ===")
    
    sim_name = state.get("simulation_name", "")
    sim_params = state.get("simulation_params", {})
    learner = state.get("learner_profile", {})
    
    print(f"🤖 Analyzing simulation: {sim_name}")
    print(f"👤 Learner: {learner.get('level')} level, {learner.get('calibre')} calibre")
    print(f"📊 Available parameters: {len(sim_params)}")
    
    # Initialize LLM
    try:
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        temperature = float(os.getenv("TEMPERATURE", "0.7"))
        max_tokens = int(os.getenv("MAX_TOKENS", "200000"))
        
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        print(f"✅ LLM initialized: {model_name}")
    except Exception as e:
        print(f"❌ Error initializing LLM: {e}")
        print("   Returning placeholder concepts")
        return {
            "concepts": [
                {"name": f"Concept from {sim_name}", "description": "Placeholder", "importance": "high"}
            ]
        }
    
    # Create parameter summary for LLM
    param_summary = ""
    if sim_params:
        param_summary = "\n".join([
            f"- {param_id}: {param_data.get('type', 'unknown')} "
            f"(range: {param_data.get('min', 'N/A')} to {param_data.get('max', 'N/A')})"
            for param_id, param_data in list(sim_params.items())[:10]  # Limit to first 10
        ])
    else:
        param_summary = "No parameters extracted yet"
    
    # Create prompt for LLM
    prompt = f"""You are an expert science educator analyzing an interactive simulation.

**Simulation Name:** {sim_name}

**Available Parameters:**
{param_summary}

**Student Profile:**
- Level: {learner.get('level', 'Unknown')}
- Learning Pace: {learner.get('calibre', 'Unknown')}

**Task:** Extract 3-4 key concepts that a student should learn from this simulation.

**Requirements:**
1. Each concept should be fundamental to understanding the simulation
2. Order concepts from simple to complex
3. Adapt the depth/complexity to the student's level and calibre
4. Focus on concepts that can be demonstrated by changing the parameters

**Output Format (JSON):**
{{
  "concepts": [
    {{
      "name": "Concept name (short, 3-7 words)",
      "description": "Clear explanation of what the concept means (1-2 sentences, max 50 words)",
      "importance": "high/medium/low"
    }}
  ]
}}

Return ONLY valid JSON, no additional text."""

    # Call LLM
    try:
        print("🔄 Calling LLM to extract concepts...")
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        print(f"📄 LLM Response length: {len(response_text)} characters")
        
        # Try to parse JSON from response
        # Sometimes LLM wraps JSON in ```json blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        concepts = result.get("concepts", [])
        
        print(f"\n✅ Extracted {len(concepts)} concepts:")
        for i, concept in enumerate(concepts, 1):
            print(f"   {i}. {concept.get('name', 'Unnamed')} ({concept.get('importance', 'unknown')} importance)")
        
        return {
            "concepts": concepts,
            "current_concept_index": 0,
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing LLM response as JSON: {e}")
        print(f"📄 Full response:\n{response_text}")
        print("   Returning placeholder concepts")
        return {
            "concepts": [
                {
                    "name": f"Understanding {sim_name}",
                    "description": f"Basic principles of {sim_name} simulation",
                    "importance": "high"
                }
            ],
            "current_concept_index": 0,
        }
    except Exception as e:
        print(f"❌ Error calling LLM: {e}")
        print("   Returning placeholder concepts")
        return {
            "concepts": [
                {
                    "name": f"Understanding {sim_name}",
                    "description": f"Basic principles of {sim_name} simulation",
                    "importance": "high"
                }
            ],
            "current_concept_index": 0,
        }
