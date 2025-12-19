"""
🎓 Learning Session Page - Step 18
===================================
This is the main teaching interface where students interact with simulations
and learn through AI-guided conversations.

FEATURES:
- Split-screen layout: Simulation (60%) + Chat (40%)
- Real-time backend communication via bridge
- AUTO mode: AI controls simulation parameters
- MANUAL mode: AI provides instructions, student controls
- Progress tracking through concepts and takeaways
- Automatic session completion detection

ARCHITECTURE:
frontend/pages/learning.py (this file)
    ↓ uses
frontend/utils/backend_bridge.py
    ↓ calls
backend/graph.py → All teaching nodes
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT / "frontend"))

# Import bridge and helpers
from utils.backend_bridge import (
    initialize_session,
    send_message,
    get_progress_info,
    get_current_concept_info,
    is_session_complete
)
from utils.helpers import (
    display_chat_message,
    show_loading_message,
    show_error_message,
    get_timestamp
)
import config


# ═══════════════════════════════════════════════════════════════════════════
# MAIN RENDER FUNCTION
# ═══════════════════════════════════════════════════════════════════════════

def render_learning_page():
    """
    Main function to render the learning session page.
    
    This handles:
    1. Backend initialization (first load)
    2. Simulation display
    3. Chat interface
    4. Message handling
    5. Progress tracking
    6. Session completion
    """
    
    # ───────────────────────────────────────────────────────────────────────
    # STEP 1: Backend Initialization (First Time Only)
    # ───────────────────────────────────────────────────────────────────────
    
    if st.session_state.backend_state is None:
        _initialize_backend()
        if st.session_state.backend_state is None:
            # Initialization failed, error already shown
            return
    
    # ───────────────────────────────────────────────────────────────────────
    # STEP 2: Page Header & Navigation
    # ───────────────────────────────────────────────────────────────────────
    
    _render_header()
    
    # ───────────────────────────────────────────────────────────────────────
    # STEP 3: Main Content Area (Split Screen)
    # ───────────────────────────────────────────────────────────────────────
    
    # Create two columns: 60% simulation, 40% chat
    col_sim, col_chat = st.columns([6, 4])
    
    # LEFT SIDE: Simulation Display
    with col_sim:
        _render_simulation_panel()
    
    # RIGHT SIDE: Chat Interface
    with col_chat:
        _render_chat_panel()
    
    # ───────────────────────────────────────────────────────────────────────
    # STEP 4: Check for Session Completion
    # ───────────────────────────────────────────────────────────────────────
    
    if st.session_state.ready_for_quiz:
        st.markdown("---")
        _render_completion_section()


# ═══════════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

def _initialize_backend():
    """
    Initialize the backend on first page load.
    
    This function:
    1. Calls the backend bridge to initialize session
    2. Runs backend graph: ingest → parse → extract → router → planner → teaching
    3. Stores backend state in session
    4. Adds first AI message to chat
    5. Sets initial simulation URL
    """
    
    st.markdown("### 🔧 Initializing Your Learning Session")
    
    with st.spinner("Analyzing simulation and generating personalized lesson plan..."):
        try:
            # Call backend bridge
            result = initialize_session(
                simulation_name=st.session_state.selected_simulation,
                level=st.session_state.selected_level,
                calibre=st.session_state.selected_calibre,
                control_mode=st.session_state.selected_mode
            )
            
            # Store everything in session state (including thread_id for checkpointing!)
            st.session_state.backend_state = result["backend_state"]
            st.session_state.thread_id = result["thread_id"]  # CRITICAL: Store for future calls
            st.session_state.current_simulation_url = result["simulation_url"]
            
            # Add first AI message to chat
            st.session_state.chat_history.append({
                "role": "ai",
                "content": result["first_message"],
                "timestamp": get_timestamp()
            })
            
            # Show success and info
            st.success("✅ Session initialized successfully!")
            
            # Show what concepts will be covered
            concepts = result["concepts"]
            if concepts:
                concept_names = [c.get("name", "") for c in concepts]
                st.info(
                    f"📚 **Today's Learning Plan:**\n\n"
                    f"We'll explore {len(concepts)} key concepts:\n" +
                    "\n".join([f"  {i+1}. {name}" for i, name in enumerate(concept_names)])
                )
            
            st.markdown("---")
            st.markdown("**Scroll down to start learning! 👇**")
            
        except Exception as e:
            show_error_message(f"Failed to initialize learning session: {str(e)}")
            st.markdown("**Please try:**")
            st.markdown("1. Check your internet connection")
            st.markdown("2. Verify backend is running")
            st.markdown("3. Click '🔄 New Session' in sidebar to restart")
            
            # Leave backend_state as None so initialization can be retried
            st.session_state.backend_state = None


# ═══════════════════════════════════════════════════════════════════════════
# HEADER SECTION
# ═══════════════════════════════════════════════════════════════════════════

def _render_header():
    """Render page header with title and progress."""
    
    # Title row
    col1, col2, col3 = st.columns([4, 3, 1])
    
    with col1:
        st.title(f"📚 Learning: {st.session_state.selected_simulation}")
    
    with col2:
        # Show progress if backend initialized
        if st.session_state.backend_state:
            progress = get_progress_info(st.session_state.backend_state)
            
            # Progress indicator
            st.markdown(
                f"<div style='text-align: center; padding: 10px;'>"
                f"<h3 style='margin: 0;'>Concept {progress['current_concept']}/{progress['total_concepts']}</h3>"
                f"<p style='margin: 0; color: gray;'>{progress['concept_name']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )
    
    with col3:
        # Exit button
        if st.button("❌ Exit", help="Return to setup page"):
            if st.session_state.backend_state:
                st.warning("⚠️ Progress will be lost. Are you sure?")
                if st.button("✅ Yes, Exit"):
                    st.session_state.current_page = "setup"
                    st.session_state.backend_state = None
                    st.rerun()
            else:
                st.session_state.current_page = "setup"
                st.rerun()
    
    st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════════
# SIMULATION PANEL (LEFT SIDE - 60%)
# ═══════════════════════════════════════════════════════════════════════════

def _render_simulation_panel():
    """
    Render the simulation display panel.
    
    Shows the HTML simulation in an iframe.
    - AUTO mode: URL includes parameters that update automatically
    - MANUAL mode: Base URL, student controls manually
    """
    
    st.markdown("### 📺 Interactive Simulation")
    
    # Get current simulation URL
    simulation_url = st.session_state.current_simulation_url
    
    if simulation_url:
        # Display mode indicator
        mode = st.session_state.selected_mode
        if mode == "AUTO":
            st.caption("🤖 **AUTO Mode:** AI is controlling the simulation parameters")
        else:
            st.caption("👐 **MANUAL Mode:** You control the simulation yourself")
        
        # Display simulation in iframe
        # Height: 700px gives good visibility
        st.components.v1.iframe(
            simulation_url,
            height=700,
            scrolling=True
        )
        
        # Show current parameters in AUTO mode (for debugging/transparency)
        if mode == "AUTO" and st.session_state.backend_state:
            with st.expander("🔍 Current Parameters (AUTO mode)"):
                takeaways = st.session_state.backend_state.get("takeaways", [])
                current_idx = st.session_state.backend_state.get("current_takeaway_index", 0)
                
                if 0 <= current_idx < len(takeaways):
                    params = takeaways[current_idx].get("parameter_values", {})
                    if params:
                        for key, value in params.items():
                            st.text(f"• {key}: {value}")
                    else:
                        st.text("No specific parameters set")
    else:
        st.warning("⚠️ Simulation not loaded. Please go back to setup.")


# ═══════════════════════════════════════════════════════════════════════════
# CHAT PANEL (RIGHT SIDE - 40%)
# ═══════════════════════════════════════════════════════════════════════════

def _render_chat_panel():
    """
    Render the chat interface panel.
    
    Features:
    - Scrollable chat history
    - Different styling for AI vs User messages
    - Timestamps
    - Input field
    - Send button
    """
    
    st.markdown("### 💬 AI Tutor Chat")
    
    # ───────────────────────────────────────────────────────────────────────
    # Current Concept Display (Always visible at top)
    # ───────────────────────────────────────────────────────────────────────
    
    if st.session_state.backend_state:
        current_concept = get_current_concept_info(st.session_state.backend_state)
        progress = get_progress_info(st.session_state.backend_state)
        
        if current_concept:
            concept_name = current_concept.get('name', 'Unknown')
            concept_desc = current_concept.get('description', '')
            importance = current_concept.get('importance', 'medium')
            
            # Importance badge color
            importance_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(importance, "⚪")
            
            # Display concept card
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 15px; border-radius: 10px; margin-bottom: 15px; color: white;">
                    <div style="font-size: 12px; opacity: 0.9;">
                        📚 Concept {progress['current_concept']} of {progress['total_concepts']} | 
                        📖 Takeaway {progress['current_takeaway']} of {progress['total_takeaways']}
                    </div>
                    <div style="font-size: 18px; font-weight: bold; margin-top: 5px;">
                        {concept_name} {importance_color}
                    </div>
                    <div style="font-size: 13px; opacity: 0.85; margin-top: 5px;">
                        {concept_desc[:100]}{'...' if len(concept_desc) > 100 else ''}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # ───────────────────────────────────────────────────────────────────────
    # Chat History Display
    # ───────────────────────────────────────────────────────────────────────
    
    # Create a container for chat messages (scrollable)
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history:
                display_chat_message(
                    role=msg.get("role", "user"),
                    content=msg.get("content", ""),
                    timestamp=msg.get("timestamp")
                )
        else:
            st.info("👋 Welcome! The AI tutor will start the conversation once initialized.")
    
    # ───────────────────────────────────────────────────────────────────────
    # User Input Area
    # ───────────────────────────────────────────────────────────────────────
    
    st.markdown("---")
    
    # Input field using chat_input (Streamlit's built-in chat input)
    user_input = st.chat_input(
        "Type your response here...",
        key="user_message_input",
        disabled=st.session_state.waiting_for_response or not st.session_state.backend_state
    )
    
    # ───────────────────────────────────────────────────────────────────────
    # Handle User Message
    # ───────────────────────────────────────────────────────────────────────
    
    if user_input:
        _handle_user_message(user_input)


# ═══════════════════════════════════════════════════════════════════════════
# MESSAGE HANDLING
# ═══════════════════════════════════════════════════════════════════════════

def _handle_user_message(user_input: str):
    """
    Handle user message submission.
    
    This function:
    1. Adds user message to chat
    2. Calls backend via bridge
    3. Backend runs: understanding_checker → feedback → (teaching/probing/router)
    4. Extracts AI response
    5. Updates simulation URL (AUTO mode)
    6. Checks if session complete
    7. Updates chat with AI response
    
    Args:
        user_input: The message user typed
    """
    
    # Set waiting state
    st.session_state.waiting_for_response = True
    
    # Add user message to chat immediately
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": get_timestamp()
    })
    
    # Show loading indicator
    with st.spinner("🤔 AI is thinking..."):
        try:
            # Call backend bridge with thread_id for checkpointing
            result = send_message(
                user_input=user_input,
                current_backend_state=st.session_state.backend_state,
                simulation_name=st.session_state.selected_simulation,
                control_mode=st.session_state.selected_mode,
                thread_id=st.session_state.thread_id  # Pass thread_id for checkpointing!
            )
            
            # Update session state with results
            st.session_state.backend_state = result["updated_state"]
            st.session_state.current_simulation_url = result["simulation_url"]
            st.session_state.ready_for_quiz = result["ready_for_quiz"]
            
            # Add AI response to chat
            st.session_state.chat_history.append({
                "role": "ai",
                "content": result["ai_response"],
                "timestamp": get_timestamp()
            })
            
            # Reset waiting state
            st.session_state.waiting_for_response = False
            
            # Rerun to update UI
            st.rerun()
            
        except Exception as e:
            # Handle errors gracefully
            st.session_state.waiting_for_response = False
            
            error_message = f"❌ **Error:** {str(e)}\n\nPlease try again or restart the session."
            st.session_state.chat_history.append({
                "role": "ai",
                "content": error_message,
                "timestamp": get_timestamp()
            })
            
            show_error_message("Failed to process your message. Please try again.")
            
            # Allow user to retry
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# COMPLETION SECTION
# ═══════════════════════════════════════════════════════════════════════════

def _render_completion_section():
    """
    Render the completion section when all concepts are taught.
    
    Shows:
    - Congratulations message
    - Summary of what was learned
    - "Ready for Quiz" button
    """
    
    st.success("🎉 **Congratulations!** You've completed all concepts!")
    
    # Show summary
    if st.session_state.backend_state:
        concepts = st.session_state.backend_state.get("concepts", [])
        
        st.markdown("### 📚 What You Learned:")
        for i, concept in enumerate(concepts, 1):
            st.markdown(f"**{i}. {concept.get('name', 'Unknown')}**")
            st.markdown(f"   _{concept.get('description', 'No description')}_")
    
    st.markdown("---")
    
    # Big button to proceed to assessment
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button(
            "📝 Ready for Assessment Quiz",
            type="primary",
            use_container_width=True,
            help="Test your understanding with multiple choice questions"
        ):
            st.session_state.current_page = "assessment"
            st.session_state.quiz_started = True
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def _get_session_stats() -> Dict[str, Any]:
    """
    Get current session statistics.
    
    Returns:
        dict: Session stats including message count, concepts, etc.
    """
    
    return {
        "total_messages": len(st.session_state.chat_history),
        "user_messages": len([m for m in st.session_state.chat_history if m["role"] == "user"]),
        "ai_messages": len([m for m in st.session_state.chat_history if m["role"] == "ai"]),
        "simulation": st.session_state.selected_simulation,
        "level": st.session_state.selected_level,
        "calibre": st.session_state.selected_calibre,
        "mode": st.session_state.selected_mode,
    }


# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # This allows the page to be run standalone for testing
    # In production, this is called from app.py
    render_learning_page()
