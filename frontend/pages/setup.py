"""
🎓 Setup Page - Step 17
========================
This page collects user inputs to initialize a learning session:
- Simulation selection
- Student profile (Level, Calibre)
- Control mode (AUTO/MANUAL)

Then initializes the backend and navigates to the learning page.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT / "frontend"))

import config


def render_setup_page():
    """Render the setup page where users configure their learning session."""
    
    # ═══════════════════════════════════════════════════════════════════════
    # PAGE HEADER
    # ═══════════════════════════════════════════════════════════════════════
    
    st.title("🎓 AI Teaching Agent")
    st.subheader("Setup Your Learning Session")
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════════════════
    # INTRODUCTION
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown("""
    Welcome! This AI teaching agent will help you learn through **interactive simulations**.
    
    **How it works:**
    1. 🎯 Select a simulation you want to explore
    2. 👤 Tell us about your learning style
    3. 🎮 Choose how you want to interact with the simulation
    4. 🚀 Start learning with personalized AI guidance!
    """)
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 1: SIMULATION SELECTION
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown("### 📚 Step 1: Choose Your Simulation")
    
    st.markdown("Select an interactive simulation to explore:")
    
    selected_simulation = st.selectbox(
        "Available Simulations:",
        options=config.SIMULATION_NAMES,
        index=config.SIMULATION_NAMES.index(st.session_state.selected_simulation) 
              if st.session_state.selected_simulation in config.SIMULATION_NAMES 
              else 0,
        help="Choose a simulation that interests you. The AI will extract key concepts and teach them interactively."
    )
    
    # Show preview/description for selected simulation
    simulation_descriptions = {
        "Acids and Bases": "🧪 Learn about pH, acids, bases, and chemical indicators through interactive experiments.",
        "Fractions": "🔢 Understand fractions, numerators, denominators, and fraction visualization.",
        "STD Simulation": "📊 Explore standard deviation and statistical concepts.",
        "STD Simulation 1": "📊 Statistical learning simulation (variant 1).",
        "STD Simulation 2": "📊 Statistical learning simulation (variant 2).",
        "STD Simulation 3": "📊 Statistical learning simulation (variant 3).",
        "STD Simulation 4": "📊 Statistical learning simulation (variant 4).",
    }
    
    if selected_simulation in simulation_descriptions:
        st.info(f"**Preview:** {simulation_descriptions[selected_simulation]}")
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 2: STUDENT PROFILE
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown("### 👤 Step 2: Tell Us About Yourself")
    
    st.markdown("""
    This helps the AI adapt its teaching to your needs:
    - **Level** determines the depth and complexity of explanations
    - **Calibre** affects the pace and style of teaching
    """)
    
    # Create two columns for profile settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Your Experience Level:**")
        selected_level = st.radio(
            "Select your level:",
            options=config.LEVELS,
            index=config.LEVELS.index(st.session_state.selected_level),
            help="Beginner: New to this topic\nIntermediate: Some understanding\nAdvanced: Strong background",
            label_visibility="collapsed"
        )
        
        # Show what each level means
        level_descriptions = {
            "Beginner": "📗 Simple explanations, basic concepts, step-by-step guidance",
            "Intermediate": "📘 Moderate depth, some technical terms, balanced pace",
            "Advanced": "📕 Complex explanations, advanced concepts, faster pace"
        }
        st.caption(level_descriptions[selected_level])
    
    with col2:
        st.markdown("**Your Learning Pace:**")
        selected_calibre = st.radio(
            "Select your learning style:",
            options=config.CALIBRES,
            index=config.CALIBRES.index(st.session_state.selected_calibre),
            help="Dull: Need more time and repetition\nMedium: Average pace\nHigh IQ: Quick learner",
            label_visibility="collapsed"
        )
        
        # Show what each calibre means
        calibre_descriptions = {
            "Dull": "🐢 Slower pace, more repetition, concrete examples",
            "Medium": "🚶 Balanced speed, standard teaching approach",
            "High IQ": "🚀 Fast pace, abstract concepts, minimal repetition"
        }
        st.caption(calibre_descriptions[selected_calibre])
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 3: CONTROL MODE SELECTION
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown("### 🎮 Step 3: Choose Control Mode")
    
    st.markdown("""
    How do you want to interact with the simulation?
    """)
    
    selected_mode = st.radio(
        "Control Mode:",
        options=config.CONTROL_MODES,
        index=config.CONTROL_MODES.index(st.session_state.selected_mode),
        help="AUTO: AI controls the simulation automatically\nMANUAL: You control the simulation yourself",
        horizontal=True
    )
    
    # Explain the selected mode
    if selected_mode == "AUTO":
        st.info("""
        **🤖 AUTO Mode (Recommended)**
        - The AI will automatically control the simulation parameters
        - You focus on learning and observing
        - The simulation updates automatically to demonstrate concepts
        - Best for guided learning experience
        """)
    else:
        st.info("""
        **👐 MANUAL Mode**
        - The AI will instruct you to change parameters
        - You manually interact with the simulation
        - More hands-on exploration
        - Best if you want direct control
        """)
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════════════════
    # CONFIGURATION SUMMARY
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown("### ✅ Your Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📚 Simulation", selected_simulation)
    with col2:
        st.metric("👤 Profile", f"{selected_level} • {selected_calibre}")
    with col3:
        st.metric("🎮 Mode", selected_mode)
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════════════════
    # START LEARNING BUTTON
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown("### 🚀 Ready to Start?")
    
    # Center the button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        start_button = st.button(
            "🚀 Start Learning Session",
            type="primary",
            use_container_width=True,
            help="Initialize the backend and begin your personalized learning experience"
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # HANDLE START BUTTON CLICK
    # ═══════════════════════════════════════════════════════════════════════
    
    if start_button:
        # Validate selections
        if not selected_simulation:
            st.error("⚠️ Please select a simulation.")
            return
        
        # Show loading state
        with st.spinner("🔧 Initializing your learning session..."):
            # Store selections in session state
            st.session_state.selected_simulation = selected_simulation
            st.session_state.selected_level = selected_level
            st.session_state.selected_calibre = selected_calibre
            st.session_state.selected_mode = selected_mode
            
            # Mark session as started (backend initialization will happen in learning page)
            st.session_state.session_started = True
            
            # Reset any previous session data
            st.session_state.chat_history = []
            st.session_state.waiting_for_response = False
            st.session_state.ready_for_quiz = False
            st.session_state.quiz_started = False
            st.session_state.current_mcq_index = 0
            st.session_state.user_answers = []
            st.session_state.session_complete = False
            st.session_state.backend_state = None
            st.session_state.thread_id = None  # Will be set by initialize_session
            
            # Generate initial simulation URL
            st.session_state.current_simulation_url = config.get_simulation_url(selected_simulation)
            
            st.success("✅ Session initialized successfully!")
        
        # Navigate to learning page
        st.session_state.current_page = "learning"
        st.rerun()
    
    # ═══════════════════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.9em;'>
    💡 <b>Tip:</b> You can change your configuration at any time by clicking "🔄 New Session" in the sidebar.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # This allows the page to be run standalone for testing
    render_setup_page()
