"""
Frontend Configuration
======================
All configuration values for the Streamlit frontend.
"""

import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════════════════

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Backend directory
BACKEND_DIR = PROJECT_ROOT / "backend"

# Simulations directory
SIMULATIONS_DIR = PROJECT_ROOT / "SimulationsNCERT-main"

# ═══════════════════════════════════════════════════════════════════════════
# SERVER SETTINGS
# ═══════════════════════════════════════════════════════════════════════════

# Port for simulation HTTP server (local only)
SIMULATION_SERVER_PORT = 8000

# Detect if running on Streamlit Cloud
IS_CLOUD = os.environ.get("STREAMLIT_SHARING_MODE") or os.environ.get("STREAMLIT_SERVER_HEADLESS")

# GitHub Pages URL for cloud deployment
GITHUB_PAGES_URL = "https://imhv0609.github.io/simulation_to_concept_github/SimulationsNCERT-main"

# Base URL for simulations - use GitHub Pages in cloud, localhost locally
if IS_CLOUD:
    SIMULATION_BASE_URL = GITHUB_PAGES_URL
else:
    SIMULATION_BASE_URL = f"http://localhost:{SIMULATION_SERVER_PORT}"

# ═══════════════════════════════════════════════════════════════════════════
# DEFAULT VALUES
# ═══════════════════════════════════════════════════════════════════════════

# Default control mode (AUTO = AI controls simulation via URL params)
DEFAULT_CONTROL_MODE = "AUTO"

# Default student profile
DEFAULT_LEVEL = "Beginner"
DEFAULT_CALIBRE = "Medium"

# ═══════════════════════════════════════════════════════════════════════════
# AVAILABLE OPTIONS
# ═══════════════════════════════════════════════════════════════════════════

# Student levels
LEVELS = ["Beginner", "Intermediate", "Advanced"]

# Student calibre options
CALIBRES = ["Dull", "Medium", "High IQ"]

# Control modes
CONTROL_MODES = ["AUTO", "MANUAL"]

# ═══════════════════════════════════════════════════════════════════════════
# SIMULATION MAPPINGS
# ═══════════════════════════════════════════════════════════════════════════

# Complete simulation mapping: Display Name → Backend Key → HTML Filename
# This allows the frontend to use friendly names while backend uses snake_case
SIMULATION_MAPPING = {
    # Display Name (for UI): (backend_key, html_filename)
    "Acids and Bases": ("acids_bases", "acids bases.html"),
    "Fractions": ("fractions", "fractions.html"),
    "Final Output": ("final_output", "4_final_output.html"),
    "Simple Pendulum": ("simple_pendulum", "simple_pendulum.html"),
    "STD Simulation": ("std", "std.html"),
    "STD Simulation 1": ("std1", "std1.html"),
    "STD Simulation 2": ("std2", "std2.html"),
    "STD Simulation 3": ("std3", "std3.html"),
    "STD Simulation 4": ("std4", "std4.html"),
}

# Reverse mapping: Backend Key → Display Name (for looking up display names)
BACKEND_TO_DISPLAY = {
    backend_key: display_name 
    for display_name, (backend_key, _) in SIMULATION_MAPPING.items()
}

# Simple list of display names for dropdown (alphabetically sorted)
SIMULATION_NAMES = sorted(SIMULATION_MAPPING.keys())


def get_backend_key(display_name: str) -> str:
    """
    Convert display name to backend key.
    
    Args:
        display_name: Frontend display name (e.g., "Acids and Bases")
        
    Returns:
        Backend key (e.g., "acids_bases")
        
    Example:
        >>> get_backend_key("Acids and Bases")
        'acids_bases'
    """
    if display_name not in SIMULATION_MAPPING:
        raise ValueError(f"Unknown simulation: {display_name}")
    return SIMULATION_MAPPING[display_name][0]


def get_display_name(backend_key: str) -> str:
    """
    Convert backend key to display name.
    
    Args:
        backend_key: Backend key (e.g., "acids_bases")
        
    Returns:
        Display name (e.g., "Acids and Bases")
        
    Example:
        >>> get_display_name("acids_bases")
        'Acids and Bases'
    """
    if backend_key not in BACKEND_TO_DISPLAY:
        raise ValueError(f"Unknown backend key: {backend_key}")
    return BACKEND_TO_DISPLAY[backend_key]


def get_simulation_url(display_name: str, params: dict = None) -> str:
    """
    Build the full URL for a simulation with optional parameters.
    
    Args:
        display_name: Display name of the simulation (e.g., "Acids and Bases")
        params: Optional dict of URL parameters (for AUTO mode)
        
    Returns:
        Full URL like http://localhost:8000/acids%20bases.html?pH=2
        
    Example:
        >>> get_simulation_url("Acids and Bases", {"pH": 2})
        'http://localhost:8000/acids%20bases.html?pH=2'
    """
    from urllib.parse import urlencode, quote
    
    if display_name not in SIMULATION_MAPPING:
        raise ValueError(f"Unknown simulation: {display_name}")
    
    # Get the HTML filename
    _, filename = SIMULATION_MAPPING[display_name]
    
    # URL encode the filename (spaces become %20)
    encoded_filename = quote(filename)
    url = f"{SIMULATION_BASE_URL}/{encoded_filename}"
    
    if params:
        # Convert Python booleans to lowercase strings for JavaScript compatibility
        # Python's True becomes "True" but JavaScript expects "true"
        converted_params = {}
        for key, value in params.items():
            if isinstance(value, bool):
                converted_params[key] = "true" if value else "false"
            else:
                converted_params[key] = value
        url = f"{url}?{urlencode(converted_params)}"
    
    return url
