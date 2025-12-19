"""
🎓 AI Teaching Agent - Main Application
========================================
This is the main entry point for the Streamlit frontend.

Run with: streamlit run frontend/app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT / "frontend"))

from sim_server import start_simulation_server
import config


# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="AI Teaching Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ═══════════════════════════════════════════════════════════════════════════
# START SIMULATION SERVER
# ═══════════════════════════════════════════════════════════════════════════

# Start HTTP server for simulations (runs once)
start_simulation_server()


# ═══════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

def init_session_state():
    """Initialize session state with default values"""
    
    # ─────────────────────────────────────────────────────────────────────
    # Page navigation
    # ─────────────────────────────────────────────────────────────────────
    if "current_page" not in st.session_state:
        st.session_state.current_page = "setup"
    
    # ─────────────────────────────────────────────────────────────────────
    # Setup page selections
    # ─────────────────────────────────────────────────────────────────────
    if "selected_simulation" not in st.session_state:
        st.session_state.selected_simulation = config.SIMULATION_NAMES[0]  # First simulation alphabetically
    
    if "selected_level" not in st.session_state:
        st.session_state.selected_level = config.DEFAULT_LEVEL
    
    if "selected_calibre" not in st.session_state:
        st.session_state.selected_calibre = config.DEFAULT_CALIBRE
    
    if "selected_mode" not in st.session_state:
        st.session_state.selected_mode = config.DEFAULT_CONTROL_MODE
    
    # ─────────────────────────────────────────────────────────────────────
    # Backend state (populated after session starts)
    # ─────────────────────────────────────────────────────────────────────
    if "backend_state" not in st.session_state:
        st.session_state.backend_state = None
    
    # Thread ID for checkpointing (allows graph to resume from where it paused)
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    
    # ─────────────────────────────────────────────────────────────────────
    # Learning session state
    # ─────────────────────────────────────────────────────────────────────
    if "session_started" not in st.session_state:
        st.session_state.session_started = False
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "current_simulation_url" not in st.session_state:
        st.session_state.current_simulation_url = None
    
    if "waiting_for_response" not in st.session_state:
        st.session_state.waiting_for_response = False
    
    if "ready_for_quiz" not in st.session_state:
        st.session_state.ready_for_quiz = False
    
    # ─────────────────────────────────────────────────────────────────────
    # Assessment state
    # ─────────────────────────────────────────────────────────────────────
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    
    if "current_mcq_index" not in st.session_state:
        st.session_state.current_mcq_index = 0
    
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = []
    
    # ─────────────────────────────────────────────────────────────────────
    # Results state
    # ─────────────────────────────────────────────────────────────────────
    if "session_complete" not in st.session_state:
        st.session_state.session_complete = False


def reset_session():
    """Reset all session state for a new session"""
    st.session_state.current_page = "setup"
    st.session_state.backend_state = None
    st.session_state.session_started = False
    st.session_state.chat_history = []
    st.session_state.current_simulation_url = None
    st.session_state.waiting_for_response = False
    st.session_state.ready_for_quiz = False
    st.session_state.quiz_started = False
    st.session_state.current_mcq_index = 0
    st.session_state.user_answers = []
    st.session_state.session_complete = False


# Initialize session state
init_session_state()


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("🎓 AI Teaching Agent")
    st.markdown("---")
    
    # Show current session info if started
    if st.session_state.session_started:
        st.markdown("**📚 Current Session:**")
        st.markdown(f"- Simulation: {st.session_state.selected_simulation}")
        st.markdown(f"- Level: {st.session_state.selected_level}")
        st.markdown(f"- Mode: {st.session_state.selected_mode}")
        st.markdown("---")
    
    # Navigation
    st.markdown("**📍 Navigation:**")
    
    # Setup page - always accessible
    if st.button("1️⃣ Setup", use_container_width=True, 
                 disabled=st.session_state.session_started):
        st.session_state.current_page = "setup"
        st.rerun()
    
    # Learning page - only after session started
    if st.button("2️⃣ Learning", use_container_width=True,
                 disabled=not st.session_state.session_started):
        st.session_state.current_page = "learning"
        st.rerun()
    
    # Assessment page - only when ready for quiz
    if st.button("3️⃣ Assessment", use_container_width=True,
                 disabled=not st.session_state.ready_for_quiz):
        st.session_state.current_page = "assessment"
        st.rerun()
    
    # Results page - only after session complete
    if st.button("4️⃣ Results", use_container_width=True,
                 disabled=not st.session_state.session_complete):
        st.session_state.current_page = "results"
        st.rerun()
    
    st.markdown("---")
    
    # Reset button
    if st.session_state.session_started:
        if st.button("🔄 New Session", use_container_width=True):
            reset_session()
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# MAIN CONTENT AREA
# ═══════════════════════════════════════════════════════════════════════════

# Import page modules
from pages.setup import render_setup_page
from pages.learning import render_learning_page

# Route to the correct page based on current_page
current_page = st.session_state.current_page

if current_page == "setup":
    # Step 17: Setup page implementation ✅
    render_setup_page()

elif current_page == "learning":
    # Step 18: Learning page implementation ✅
    render_learning_page()

elif current_page == "assessment":
    st.title("📝 Assessment Quiz")
    
    st.markdown("---")
    
    # Placeholder for assessment content (will be implemented in Step 19)
    st.info("📝 **Step 19:** Assessment page will be implemented here.")
    st.markdown("""
    This page will include:
    - MCQ questions one at a time
    - Answer selection
    - Progress indicator
    """)

elif current_page == "results":
    st.title("🎉 Session Complete!")
    
    st.markdown("---")
    
    # Placeholder for results content (will be implemented in Step 20)
    st.info("📝 **Step 20:** Results page will be implemented here.")
    st.markdown("""
    This page will include:
    - Final score
    - Performance breakdown
    - Level recommendation
    - Restart options
    """)


# ═══════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Built with Streamlit + LangGraph | Phase 5: Frontend Development"
    "</div>",
    unsafe_allow_html=True
)
