# Input Flow: Test vs Real Application

## 🧪 Current Flow (Testing Phase)

```
┌─────────────────────────────────────┐
│   test_ingestion.py                 │
│   (You manually write the inputs)   │
│                                     │
│   state = {                         │
│     "simulation_name": "fractions", │ ← Hardcoded
│     "learner_profile": {            │
│       "level": "Beginner",          │ ← Hardcoded
│       "calibre": "Medium"           │ ← Hardcoded
│     }                               │
│   }                                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   simulation_ingest_node()          │
│   - Receives the hardcoded state    │
│   - Validates inputs                │
│   - Fetches URL from config         │
│   - Determines control mode         │
└─────────────────────────────────────┘
```

**Purpose**: Testing individual nodes in isolation

---

## 🚀 Real Application Flow (Phase 5 - Streamlit Frontend)

```
┌─────────────────────────────────────┐
│         STREAMLIT UI                │
│  (frontend/app.py - Phase 5)        │
│                                     │
│  1️⃣  Select Simulation:             │
│     [Dropdown] ▼                    │ ← User selects
│     • Fractions                     │
│     • Acids & Bases                 │
│     • Projectile Motion             │
│                                     │
│  2️⃣  Your Level:                    │
│     ( ) Beginner                    │ ← User clicks
│     (•) Intermediate                │
│     ( ) Advanced                    │
│                                     │
│  3️⃣  Your Learning Style:           │
│     ( ) Needs more time (Dull)      │ ← User clicks
│     (•) Average pace (Medium)       │
│     ( ) Quick learner (High IQ)     │
│                                     │
│     [Start Learning] 🚀 Button      │
└─────────────────────────────────────┘
              ↓
      User clicks "Start Learning"
              ↓
┌─────────────────────────────────────┐
│   Streamlit collects inputs:        │
│                                     │
│   simulation_name = "fractions"     │ ← From dropdown
│   level = "Intermediate"            │ ← From radio button
│   calibre = "Medium"                │ ← From radio button
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Create initial state:             │
│                                     │
│   state = {                         │
│     "simulation_name": simulation_name,  ← User input
│     "learner_profile": {            │
│       "level": level,               │     ← User input
│       "calibre": calibre            │     ← User input
│     },                              │
│     # ... other fields              │
│   }                                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   compiled_graph.invoke(state)      │
│   - Runs the workflow               │
│   - Starts with ingestion node      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   simulation_ingest_node()          │
│   - Receives user-provided state    │
│   - Validates inputs                │
│   - Fetches URL from config         │
│   - Determines control mode         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   ... rest of workflow ...          │
│   - Extract concepts                │
│   - Teach each concept              │
│   - Assess understanding            │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Display results in Streamlit UI   │
│   - Show simulation                 │
│   - Display teaching content        │
│   - Show MCQ questions              │
└─────────────────────────────────────┘
```

---

## 📝 Code Examples

### Current (Testing)

```python
# In test_ingestion.py - HARDCODED for testing
state: TeachingState = {
    "simulation_name": "fractions",  # ← You type this
    "learner_profile": {
        "level": "Beginner",         # ← You type this
        "calibre": "Medium",         # ← You type this
    },
    # ... rest
}

result = simulation_ingest_node(state)
```

### Future (Real App - Streamlit)

```python
# In frontend/app.py (Phase 5)
import streamlit as st
from backend.graph import compile_graph

st.title("🎓 Interactive Simulation Teacher")

# 1. User selects simulation
simulation_name = st.selectbox(
    "Choose a simulation:",
    ["fractions", "acids_bases_solutions", "projectile_motion"]
)

# 2. User selects their level
level = st.radio(
    "What's your current level?",
    ["Beginner", "Intermediate", "Advanced"]
)

# 3. User selects their learning style
calibre = st.radio(
    "Your learning pace:",
    ["Dull", "Medium", "High IQ"]
)

# 4. Start button
if st.button("Start Learning"):
    # Create initial state from user inputs
    initial_state = {
        "simulation_name": simulation_name,    # ← From user
        "simulation_url": "",
        "simulation_description": "",
        "learner_profile": {
            "level": level,                    # ← From user
            "calibre": calibre,                # ← From user
        },
        "control_mode": "MANUAL",
        "concepts": [],
        "current_concept_index": 0,
        "current_takeaway_index": 0,
        "view_config": {},
        "interactions": [],
        "understanding_status": "clear",
        "assessment": None,
        "messages": [],
        "next_action": "start",
        "error": None,
    }
    
    # Run the workflow
    graph = compile_graph()
    final_state = graph.invoke(initial_state)
    
    # Display results
    st.success("Teaching session complete!")
    st.write(final_state)
```

---

## 🔄 Where Does ingestion_node Fit?

The `simulation_ingest_node()` **does NOT collect inputs** from users.

### What it DOES:
✅ Receives inputs that were already collected (from test or frontend)  
✅ Validates those inputs (ensures they're not empty/missing)  
✅ Enriches the state with additional data (URL from config, control mode)  
✅ Prepares state for next nodes  

### What it DOES NOT do:
❌ Does NOT ask user for inputs  
❌ Does NOT have any UI/prompts  
❌ Does NOT interact with user directly  

---

## 🎯 Separation of Concerns

```
┌────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                          │
│              (Streamlit - Phase 5)                         │
│                                                            │
│  Responsibilities:                                         │
│  • Show UI to user                                        │
│  • Collect inputs (simulation, level, calibre)           │
│  • Display simulation iframe                             │
│  • Show teaching content                                 │
│  • Handle user interactions                              │
└────────────────────────────────────────────────────────────┘
                           ↓
                  passes initial_state
                           ↓
┌────────────────────────────────────────────────────────────┐
│                    BACKEND LAYER                           │
│              (LangGraph Workflow)                          │
│                                                            │
│  Responsibilities:                                         │
│  • Validate inputs                                        │
│  • Fetch simulation metadata                             │
│  • Extract concepts with LLM                             │
│  • Generate teaching plan                                │
│  • Create MCQ questions                                  │
│  • Grade assessments                                     │
│  • No UI, no user interaction                            │
└────────────────────────────────────────────────────────────┘
```

**Backend nodes are "pure logic"** - they receive data, process it, return results. They don't interact with users.

---

## 💡 Why This Design?

### 1. **Testability**
- Can test backend nodes independently without UI
- Can mock inputs easily
- Faster development cycle

### 2. **Modularity**
- Backend doesn't care WHERE inputs come from (test, Streamlit, API, etc.)
- Can replace frontend without changing backend
- Can add multiple frontends (Streamlit, web app, mobile app)

### 3. **Clear Responsibilities**
- Frontend: User interaction
- Backend: Business logic
- No mixing of concerns

---

## 🚧 Current Development Phase

```
Phase 1-4 (NOW):
    ✅ Build backend nodes
    ✅ Test with hardcoded inputs
    ✅ Validate each node works correctly
    
Phase 5 (FUTURE):
    ⏳ Build Streamlit frontend
    ⏳ Connect frontend to backend
    ⏳ Let real users provide inputs
```

---

## 🎓 Summary

**Current (Testing)**:
- Inputs are **hardcoded** in `test_ingestion.py`
- You manually type: `simulation_name`, `level`, `calibre`
- Purpose: Test backend logic in isolation

**Future (Real App)**:
- Inputs come from **Streamlit UI** (dropdowns, radio buttons)
- User selects: simulation, level, calibre through interface
- Streamlit passes inputs to backend workflow
- Backend processes and returns results
- Streamlit displays results to user

**ingestion_node's Role**:
- Does NOT collect inputs
- DOES validate and enrich inputs that were already provided
- Pure backend logic, no UI
