# 🎓 Learning Session Page - Complete Documentation

## 📋 Overview

The **Learning Session Page** is the core teaching interface where students interact with simulations and learn through AI-guided conversations. This is the most complex and important component of the frontend.

**Location:** `frontend/pages/learning.py`

---

## 🎯 What This Page Does

### Primary Functions:
1. **Initialize Backend** - Connects to LangGraph backend on first load
2. **Display Simulation** - Shows HTML simulation in iframe (60% of screen)
3. **Chat Interface** - Interactive conversation with AI tutor (40% of screen)
4. **Handle Messages** - Processes user responses and gets AI replies
5. **Track Progress** - Shows current concept and completion percentage
6. **Manage Teaching Loop** - Backend handles re-teaching, hints, progression
7. **Detect Completion** - Automatically shows "Ready for Quiz" when done

---

## 🖼️ UI Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  📚 Learning: Acids and Bases         [Concept 2/3]           [❌ Exit]  │
├────────────────────────────┬─────────────────────────────────────────────┤
│                            │                                             │
│  📺 SIMULATION (60%)       │  💬 AI TUTOR CHAT (40%)                    │
│                            │                                             │
│  ┌──────────────────────┐  │  ┌────────────────────────────────────┐    │
│  │                      │  │  │  Chat History (scrollable):        │    │
│  │  <iframe>            │  │  │                                    │    │
│  │  Simulation with     │  │  │  🤖 AI: "Let's explore pH..."      │    │
│  │  URL parameters      │  │  │  👤 You: "What is pH?"            │    │
│  │                      │  │  │  🤖 AI: "pH measures acidity..."  │    │
│  │  AUTO mode:          │  │  │  👤 You: "Got it!"                │    │
│  │  http://localhost    │  │  │  🤖 AI: "Great! Now let's..."     │    │
│  │  :8000/acids.html    │  │  │                                    │    │
│  │  ?pH=2               │  │  │  (auto-scrolls to bottom)          │    │
│  │                      │  │  └────────────────────────────────────┘    │
│  │  MANUAL mode:        │  │                                             │
│  │  Base URL only       │  │  📖 Current: pH Scale                      │
│  │                      │  │                                             │
│  └──────────────────────┘  │  ┌────────────────────────────────────┐    │
│                            │  │  Type your response here...        │    │
│  🤖 AUTO Mode              │  └────────────────────────────────────┘    │
│  AI controls parameters    │                                             │
│                            │                                             │
└────────────────────────────┴─────────────────────────────────────────────┘
│                                                                          │
│  🎉 Congratulations! You've completed all concepts!                     │
│                                                                          │
│  📚 What You Learned: [concept list]                                    │
│                                                                          │
│             [📝 Ready for Assessment Quiz] (big button)                 │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete User Flow

### Step 1: Page Loads (First Time)
```
1. Check if backend initialized
   └─ No → Run initialization
       ├─ Show loading spinner "Analyzing simulation..."
       ├─ Call initialize_session() from bridge
       ├─ Backend runs: ingest → parse → extract → router → planner → teaching
       ├─ Store backend_state in session
       ├─ Get first AI message
       ├─ Generate simulation URL
       └─ Display success + learning plan
```

### Step 2: Display Interface
```
Split screen renders:
├─ LEFT (60%): Simulation iframe
│   ├─ Mode indicator (AUTO/MANUAL)
│   ├─ Simulation loads with URL
│   └─ Optional: Parameter display (debugging)
│
└─ RIGHT (40%): Chat interface
    ├─ Chat history (all messages)
    ├─ Current concept name
    └─ Input field for user responses
```

### Step 3: User Types Response
```
User types: "The solution is red"
   ↓
Click Send (or press Enter)
   ↓
Frontend:
1. Add user message to chat history
2. Show loading spinner "AI is thinking..."
3. Call send_message() from bridge
   ↓
Bridge:
4. Update backend state with user input
5. Invoke backend graph
   ↓
Backend (Teaching Loop):
6. understanding_checker_node analyzes response
   ├─ Student confused? → Route to feedback → re-teach/re-probe
   ├─ Student understood? → Route to next takeaway/concept
   └─ All concepts done? → Route to assessment
7. Generate appropriate AI response
8. Update simulation parameters (if AUTO mode)
9. Return everything to bridge
   ↓
Bridge:
10. Extract AI response based on next_action
11. Generate new simulation URL (if AUTO)
12. Check if session complete
13. Return to frontend
   ↓
Frontend:
14. Update backend_state
15. Update simulation_url
16. Add AI response to chat
17. Set ready_for_quiz if needed
18. Rerun page to show updates
```

### Step 4: Teaching Loop Continues
```
Backend handles ALL intelligence:
├─ Student confused?
│   └─ feedback_node routes back to teaching/probing
│       └─ AI re-explains or gives hint
│
├─ Student understood current takeaway?
│   └─ Move to next takeaway
│       └─ teaching_node loads next explanation
│
├─ All takeaways in concept done?
│   └─ router_node moves to next concept
│       └─ planner_node generates new takeaways
│
└─ All concepts done?
    └─ router_node sets next_action = "assess"
        └─ Frontend shows "Ready for Quiz" button
```

### Step 5: Session Complete
```
When all concepts taught:
1. Backend returns next_action = "assess"
2. Bridge sets ready_for_quiz = True
3. Frontend shows completion section:
   ├─ Congratulations message
   ├─ Summary of concepts learned
   └─ Big "Ready for Quiz" button
4. User clicks button
5. Navigate to assessment page
```

---

## 🧩 Component Breakdown

### Main Function: `render_learning_page()`
**Purpose:** Entry point that orchestrates the entire page.

**Flow:**
1. Check if backend initialized → call `_initialize_backend()` if needed
2. Render header with progress
3. Create split layout (60/40 columns)
4. Render simulation panel (left)
5. Render chat panel (right)
6. Check for completion → show quiz button if ready

---

### Initialization: `_initialize_backend()`
**Purpose:** Connect to backend and start teaching session.

**What it does:**
```python
def _initialize_backend():
    # 1. Show loading spinner
    # 2. Call bridge.initialize_session()
    #    - Backend runs full ingestion pipeline
    #    - Extracts concepts
    #    - Generates first lesson plan
    #    - Prepares first teaching message
    # 3. Store backend_state
    # 4. Store simulation_url
    # 5. Add first AI message to chat
    # 6. Show success + learning plan
    # 7. Handle errors gracefully
```

**Error Handling:**
- Shows clear error message if initialization fails
- Provides troubleshooting steps
- Allows retry by keeping backend_state = None

---

### Header: `_render_header()`
**Purpose:** Display title, progress, and exit button.

**Components:**
- **Title:** Shows simulation name
- **Progress Indicator:** 
  - Concept X/Y
  - Current concept name
  - Calculated from backend state
- **Exit Button:**
  - Confirms before exiting
  - Clears session data
  - Returns to setup page

---

### Simulation Panel: `_render_simulation_panel()`
**Purpose:** Display the HTML simulation in an iframe.

**Features:**
- **Mode Indicator:** Shows if AUTO or MANUAL
- **Iframe Display:** 700px height for good visibility
- **URL Management:**
  - AUTO mode: URL includes parameters (e.g., `?pH=2&volume=100`)
  - MANUAL mode: Base URL only
- **Parameter Display:** (Optional expander)
  - Shows current parameters in AUTO mode
  - Useful for debugging and transparency

**Technical Details:**
```python
st.components.v1.iframe(
    url=st.session_state.current_simulation_url,
    height=700,
    scrolling=True
)
```

---

### Chat Panel: `_render_chat_panel()`
**Purpose:** Interactive conversation interface with AI tutor.

**Components:**

1. **Chat History Display:**
   - Container with all messages
   - Different styling for AI vs User
   - Timestamps on each message
   - Auto-scrolls to bottom on new messages
   - Uses `display_chat_message()` helper

2. **Current Concept Indicator:**
   - Shows what topic is being taught
   - Updated from backend state

3. **Input Field:**
   - Streamlit's `chat_input()` widget
   - Disabled during processing (waiting_for_response)
   - Disabled if backend not initialized
   - Placeholder: "Type your response here..."

**Message Flow:**
```
User types → chat_input captures → _handle_user_message() called
```

---

### Message Handler: `_handle_user_message(user_input)`
**Purpose:** Process user messages and get AI responses.

**Flow:**
```python
1. Set waiting_for_response = True (disables input)
2. Add user message to chat_history immediately
3. Show loading spinner "🤔 AI is thinking..."
4. Call bridge.send_message()
   ├─ Backend processes input (teaching loop)
   ├─ Returns AI response + updated state
   └─ May update simulation URL (AUTO mode)
5. Update session_state with results:
   ├─ backend_state = result["updated_state"]
   ├─ current_simulation_url = result["simulation_url"]
   └─ ready_for_quiz = result["ready_for_quiz"]
6. Add AI response to chat_history
7. Set waiting_for_response = False
8. Rerun page to display updates
```

**Error Handling:**
- Try-catch around bridge call
- Shows error message in chat
- Allows user to retry
- Doesn't crash the session

---

### Completion Section: `_render_completion_section()`
**Purpose:** Show when all concepts are taught.

**Displays:**
1. **Success message:** "🎉 Congratulations!"
2. **Concept summary:** List of what was learned
3. **Big button:** "📝 Ready for Assessment Quiz"
4. **Click handler:** Navigates to assessment page

**Trigger:** `st.session_state.ready_for_quiz = True`

---

## 🔗 Integration with Backend Bridge

### Function Calls:

#### 1. `initialize_session()`
**Called:** Once on first page load

**Parameters:**
- simulation_name (display name)
- level ("Beginner"/"Intermediate"/"Advanced")
- calibre ("Dull"/"Medium"/"High IQ")
- control_mode ("AUTO"/"MANUAL")

**Returns:**
```python
{
    "backend_state": {...},              # Store in session_state
    "first_message": "Welcome...",       # Add to chat
    "simulation_url": "http://...",      # Display in iframe
    "concepts": [...],                   # For display
    "total_concepts": 3,
    "current_concept_index": 0,
    "mode": "AUTO"
}
```

---

#### 2. `send_message()`
**Called:** Every time user sends a message

**Parameters:**
- user_input (what user typed)
- current_backend_state (from session_state)
- simulation_name (display name)
- control_mode ("AUTO"/"MANUAL")

**Returns:**
```python
{
    "ai_response": "Great observation!...",  # Add to chat
    "updated_state": {...},                  # Update session_state
    "simulation_url": "http://...",          # Update iframe
    "next_action": "teach",                  # For debugging
    "ready_for_quiz": False,                 # Check completion
    "current_concept_index": 1,
    "current_takeaway_index": 0,
}
```

---

#### 3. `get_progress_info()`
**Called:** Every render to show progress

**Parameters:**
- backend_state (from session_state)

**Returns:**
```python
{
    "current_concept": 2,          # 1-based for display
    "total_concepts": 3,
    "current_takeaway": 1,
    "total_takeaways": 2,
    "concept_name": "Neutralization",
    "completion_percentage": 66.7
}
```

---

## 🎮 AUTO vs MANUAL Mode Handling

### AUTO Mode:
**Backend provides:** `parameter_values` in each takeaway

**Frontend does:**
1. Bridge extracts parameters: `{"pH": 2, "volume": 100}`
2. Builds URL: `http://localhost:8000/acids.html?pH=2&volume=100`
3. Iframe reloads with new parameters
4. Simulation automatically shows correct state

**AI says:** "Observe the solution at pH 2"

**User sees:** Simulation already set to pH 2

---

### MANUAL Mode:
**Backend provides:** Instructions in explanation text

**Frontend does:**
1. Shows base URL: `http://localhost:8000/acids.html`
2. User controls simulation manually
3. AI provides text instructions

**AI says:** "Please move the pH slider to 2 and observe the color change"

**User does:** Manually drags slider in simulation

---

## ⚠️ Error Handling

### Initialization Errors:
```python
try:
    result = initialize_session(...)
except Exception as e:
    # Show error message
    # Provide troubleshooting steps
    # Keep backend_state = None to allow retry
```

### Message Processing Errors:
```python
try:
    result = send_message(...)
except Exception as e:
    # Add error message to chat
    # Show user-friendly error
    # Allow retry without crashing
```

### Common Errors:
1. **Backend not running:** Show message to start backend
2. **Network error:** Check internet connection
3. **LLM API error:** May need to retry
4. **State corruption:** Offer session restart

---

## 🎨 UI/UX Features

### Loading States:
- ✅ Spinner during backend initialization
- ✅ Spinner while AI processes response
- ✅ Input disabled during processing
- ✅ Clear progress indicators

### Message Display:
- ✅ Different colors for AI vs User
- ✅ Timestamps on all messages
- ✅ Auto-scroll to latest message
- ✅ Readable formatting

### Progress Tracking:
- ✅ Concept X/Y display
- ✅ Current concept name
- ✅ Percentage completion (optional)
- ✅ Visual progress bar (optional)

### Responsive Design:
- ✅ 60/40 split for simulation/chat
- ✅ Scrollable chat history
- ✅ Resizable iframe
- ✅ Mobile-friendly (Streamlit handles this)

---

## 🐛 Debugging Features

### Parameter Display:
- Expander showing current parameters (AUTO mode)
- Helps verify simulation state

### State Inspection:
```python
# Add to page for debugging:
with st.expander("🔍 Debug: Backend State"):
    st.json(st.session_state.backend_state)
```

### Message Timestamps:
- All messages have timestamps
- Helps track conversation flow

---

## 📊 Session State Variables

The page uses these session_state variables:

```python
# Backend
st.session_state.backend_state           # Full backend state dict
st.session_state.current_simulation_url  # Current iframe URL

# Chat
st.session_state.chat_history            # List of messages
st.session_state.waiting_for_response    # Bool: processing?

# Progress
st.session_state.ready_for_quiz          # Bool: all concepts done?

# Configuration (from setup page)
st.session_state.selected_simulation     # Display name
st.session_state.selected_level          # Level
st.session_state.selected_calibre        # Calibre
st.session_state.selected_mode           # AUTO/MANUAL
```

---

## 🧪 Testing Checklist

### Basic Functionality:
- [ ] Page loads without errors
- [ ] Backend initializes successfully
- [ ] First AI message appears
- [ ] Simulation displays in iframe
- [ ] Can type in chat input
- [ ] Sending message works
- [ ] AI response appears
- [ ] Chat history persists

### Teaching Loop:
- [ ] Student confused → AI re-teaches
- [ ] Student understood → moves to next takeaway
- [ ] All takeaways done → moves to next concept
- [ ] All concepts done → shows quiz button

### AUTO Mode:
- [ ] Simulation URL includes parameters
- [ ] URL updates when teaching progresses
- [ ] Iframe reloads with new parameters
- [ ] Simulation shows correct state

### MANUAL Mode:
- [ ] Shows base URL only
- [ ] AI provides text instructions
- [ ] Student can control simulation manually

### Error Handling:
- [ ] Handles initialization errors gracefully
- [ ] Handles message errors without crashing
- [ ] Shows helpful error messages
- [ ] Allows retry after errors

### UI/UX:
- [ ] Progress indicator updates correctly
- [ ] Exit button works
- [ ] Chat scrolls properly
- [ ] Messages display correctly
- [ ] Loading spinners show
- [ ] Quiz button appears when done

---

## 🚀 Future Enhancements

### Potential Improvements:
1. **Voice Input:** Allow speaking responses
2. **Hints Button:** "Give me a hint" feature
3. **Review Mode:** Replay previous concepts
4. **Bookmark:** Save current position
5. **Export Chat:** Download conversation history
6. **Visual Progress:** Animated progress bar
7. **Concept Navigation:** Jump to specific concepts
8. **Side-by-side Comparison:** Show before/after states simultaneously

---

## 📝 Usage Example

```python
# In app.py:
from pages.learning import render_learning_page

if st.session_state.current_page == "learning":
    render_learning_page()
```

That's it! The page handles everything internally.

---

## 🔧 Troubleshooting

### Problem: Backend not initializing
**Solution:** 
- Check backend is running
- Verify API keys in .env
- Check network connection

### Problem: Simulation not loading
**Solution:**
- Verify simulation server is running (port 8000)
- Check simulation file exists
- Verify URL is correct

### Problem: Chat not responding
**Solution:**
- Check browser console for errors
- Verify backend_state is not None
- Try restarting session

### Problem: Parameters not updating (AUTO mode)
**Solution:**
- Check takeaway has parameter_values
- Verify URL is being updated
- Check iframe is reloading

---

## 📚 Related Files

- **Backend Bridge:** `frontend/utils/backend_bridge.py`
- **UI Helpers:** `frontend/utils/helpers.py`
- **Frontend Config:** `frontend/config.py`
- **Backend Graph:** `backend/graph.py`
- **Teaching Nodes:** `backend/nodes/teaching_loop.py`

---

**Last Updated:** December 12, 2025  
**Status:** ✅ Complete and Ready for Use
