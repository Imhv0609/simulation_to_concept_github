"""
UI Helper Functions
===================
Common UI components and utilities for the frontend.
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any


def display_chat_message(role: str, content: str, timestamp: str = None):
    """
    Display a chat message with proper styling.
    
    Args:
        role: "ai" or "user"
        content: Message text
        timestamp: Optional timestamp string
    """
    
    if role == "ai":
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(content)
            if timestamp:
                st.caption(f"🕐 {timestamp}")
    else:
        with st.chat_message("user", avatar="👤"):
            st.markdown(content)
            if timestamp:
                st.caption(f"🕐 {timestamp}")


def display_chat_history(chat_history: List[Dict[str, Any]]):
    """
    Display entire chat history.
    
    Args:
        chat_history: List of message dicts with 'role', 'content', 'timestamp'
    """
    
    for msg in chat_history:
        display_chat_message(
            role=msg.get("role", "user"),
            content=msg.get("content", ""),
            timestamp=msg.get("timestamp")
        )


def display_progress_bar(current: int, total: int, label: str = "Progress"):
    """
    Display a progress bar with label.
    
    Args:
        current: Current progress (1-based)
        total: Total items
        label: Label text
    """
    
    if total > 0:
        progress_value = current / total
        st.progress(progress_value, text=f"{label}: {current}/{total}")
    else:
        st.progress(0, text=f"{label}: 0/0")


def get_timestamp() -> str:
    """
    Get current timestamp as formatted string.
    
    Returns:
        str: Timestamp like "10:30 AM"
    """
    return datetime.now().strftime("%I:%M %p")


def show_loading_message(message: str = "Processing..."):
    """
    Show a loading spinner with message.
    
    Args:
        message: Loading message text
        
    Returns:
        Spinner context manager
    """
    return st.spinner(message)


def show_success_message(message: str, duration: int = 3):
    """
    Show a temporary success message.
    
    Args:
        message: Success message
        duration: Duration in seconds (Streamlit default)
    """
    st.success(message, icon="✅")


def show_error_message(message: str):
    """
    Show an error message.
    
    Args:
        message: Error message
    """
    st.error(message, icon="❌")


def show_info_message(message: str):
    """
    Show an info message.
    
    Args:
        message: Info message
    """
    st.info(message, icon="ℹ️")


def show_warning_message(message: str):
    """
    Show a warning message.
    
    Args:
        message: Warning message
    """
    st.warning(message, icon="⚠️")


def create_metric_card(label: str, value: str, delta: str = None):
    """
    Create a metric display card.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta value
    """
    st.metric(label=label, value=value, delta=delta)


def confirm_action(message: str, button_text: str = "Confirm") -> bool:
    """
    Show a confirmation dialog.
    
    Args:
        message: Confirmation message
        button_text: Button text
        
    Returns:
        bool: True if confirmed
    """
    st.warning(message)
    return st.button(button_text, type="primary")
