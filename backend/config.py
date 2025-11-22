"""
Configuration file for the teaching agent.
This is the central place to control simulation behavior.
"""

from typing import Dict, Literal

# ============================================
# SIMULATION CONTROL MODE CONFIGURATION
# ============================================
# Change this single parameter to switch between AUTO and MANUAL modes globally
# - "MANUAL": Student manually changes parameters (works with existing HTML files)
# - "AUTO": Agent programmatically controls parameters (requires hosted simulations with URL params)
SIMULATION_CONTROL_MODE: Literal["MANUAL", "AUTO"] = "MANUAL"


# ============================================
# SIMULATION URL MAPPINGS
# ============================================
# Map simulation names to their URLs
# For MANUAL mode: These can be local file paths or existing URLs
# For AUTO mode: These should be hosted URLs that accept URL parameters

SIMULATION_URLS: Dict[str, str] = {
    # NCERT Simulations (Local - for MANUAL mode)
    "fractions": "../SimulationsNCERT-main/fractions.html",
    "acids_bases": "../SimulationsNCERT-main/acids bases.html",
    "std": "../SimulationsNCERT-main/std.html",
    "std1": "../SimulationsNCERT-main/std1.html",
    "std2": "../SimulationsNCERT-main/std2.html",
    "std3": "../SimulationsNCERT-main/std3.html",
    "std4": "../SimulationsNCERT-main/std4.html",
    
    # Future: Add hosted URLs here for AUTO mode
    # "fractions_hosted": "https://your-domain.com/simulations/fractions?param1={value1}&param2={value2}",
    # "acids_bases_hosted": "https://your-domain.com/simulations/acids_bases?param1={value1}",
}


# ============================================
# MODE-SPECIFIC CONFIGURATIONS
# ============================================

# Configuration for MANUAL mode
MANUAL_MODE_CONFIG = {
    "requires_instructions": True,  # Agent provides instructions to student
    "can_modify_params": False,     # Agent cannot directly change simulation
    "interaction_type": "guided",    # Agent guides student through changes
    "view_mode": "full",            # Student sees full simulation
}

# Configuration for AUTO mode
AUTO_MODE_CONFIG = {
    "requires_instructions": False,  # Agent directly controls simulation
    "can_modify_params": True,      # Agent can programmatically change parameters
    "interaction_type": "direct",    # Agent directly manipulates simulation
    "view_mode": "controlled",      # Agent can control what student sees
}


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_current_mode_config() -> Dict:
    """
    Returns the configuration dictionary for the current control mode.
    
    Returns:
        Dict: Configuration settings based on SIMULATION_CONTROL_MODE
    """
    if SIMULATION_CONTROL_MODE == "AUTO":
        return AUTO_MODE_CONFIG
    else:
        return MANUAL_MODE_CONFIG


def get_simulation_url(simulation_name: str) -> str:
    """
    Get the URL for a simulation based on its name.
    
    Args:
        simulation_name: Name of the simulation
        
    Returns:
        str: URL or file path to the simulation
        
    Raises:
        ValueError: If simulation name not found
    """
    url = SIMULATION_URLS.get(simulation_name)
    if url is None:
        raise ValueError(f"Simulation '{simulation_name}' not found in SIMULATION_URLS")
    return url


def is_auto_mode() -> bool:
    """Check if current mode is AUTO."""
    return SIMULATION_CONTROL_MODE == "AUTO"


def is_manual_mode() -> bool:
    """Check if current mode is MANUAL."""
    return SIMULATION_CONTROL_MODE == "MANUAL"


# ============================================
# LLM CONFIGURATION
# ============================================

LLM_MODEL = "gemini-2.0-flash-exp"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2000

# ============================================
# TEACHING PARAMETERS
# ============================================

# Number of concepts to extract from simulation
NUM_CONCEPTS = 3

# Number of takeaways per concept
NUM_TAKEAWAYS_PER_CONCEPT = 2

# Number of MCQs in assessment
NUM_ASSESSMENT_QUESTIONS = 3

# Interaction limits
MAX_INTERACTIONS_PER_CONCEPT = 5
MAX_CLARIFICATION_ATTEMPTS = 3
