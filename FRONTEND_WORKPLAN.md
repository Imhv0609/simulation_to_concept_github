# 🎨 PHASE 5: FRONTEND DEVELOPMENT WORKPLAN

## Overview

This document outlines the complete step-by-step plan for building the Streamlit frontend that integrates with our existing backend.

**Backend Status:** ✅ Complete (Steps 1-15)
**Frontend Status:** 🚧 Starting

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STREAMLIT FRONTEND                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │   PAGE 1    │   │   PAGE 2    │   │   PAGE 3    │   │   PAGE 4    │     │
│  │   Setup     │──▶│  Learning   │──▶│ Assessment  │──▶│  Results    │     │
│  │             │   │   Session   │   │    Quiz     │   │  Summary    │     │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘     │
│         │                │                  │                │              │
│         └────────────────┴──────────────────┴────────────────┘              │
│                                    │                                        │
│                          ┌─────────▼─────────┐                              │
│                          │  SESSION STATE    │                              │
│                          │  (Shared Data)    │                              │
│                          └─────────┬─────────┘                              │
│                                    │                                        │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LANGGRAPH BACKEND                                 │
│                                                                             │
│  ingestion → parser → concepts → router → planner → teaching → assessment  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HTML SIMULATION SERVER                               │
│                                                                             │
│  http://localhost:8000/simulation.html?pH=2&volume=100&type=acid           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Step-by-Step Implementation Plan

---

### **STEP 16: Project Setup & Basic Structure**
**Estimated Time:** 1 hour

#### What We'll Build:
- Streamlit app entry point
- Folder structure
- Session state initialization
- HTTP server for simulations

#### Files to Create:
```
frontend/
├── app.py              # Main Streamlit entry point
├── config.py           # Frontend configuration
├── server.py           # HTTP server for simulations
└── utils/
    └── __init__.py
```

#### Tasks:
1. Create `frontend/app.py` - main entry with page navigation
2. Create `frontend/config.py` - ports, paths, settings
3. Create `frontend/server.py` - HTTP server to serve HTML simulations
4. Initialize session state with default values
5. Add basic navigation sidebar

#### Success Criteria:
- [ ] `streamlit run frontend/app.py` starts without errors
- [ ] Sidebar navigation shows all 4 pages
- [ ] Session state persists between page switches

---

### **STEP 17: Setup Page (Simulation Selection)**
**Estimated Time:** 1.5 hours

#### What We'll Build:
- Simulation selection dropdown
- Student profile configuration (Level, Calibre)
- Control mode selection (AUTO/MANUAL) - **AUTO is default**
- Start session button

#### UI Layout:
```
┌─────────────────────────────────────────────────────────────────┐
│  🎓 AI Teaching Agent - Setup                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📚 Select Simulation:                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ▼ Acids and Bases                                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  👤 Student Profile:                                            │
│  ┌─────────────────────┐  ┌─────────────────────┐               │
│  │ Level: Beginner ▼   │  │ Calibre: Medium ▼   │               │
│  └─────────────────────┘  └─────────────────────┘               │
│                                                                 │
│  🎮 Control Mode:                                               │
│  ● AUTO (AI controls simulation) ← DEFAULT                      │
│  ○ MANUAL (You control simulation)                              │
│                                                                 │
│              ┌────────────────────────┐                         │
│              │   🚀 Start Learning    │                         │
│              └────────────────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Tasks:
1. Create `frontend/pages/setup.py`
2. Scan `SimulationsNCERT-main/` folder for available simulations
3. Add Level dropdown (Beginner, Intermediate, Advanced)
4. Add Calibre dropdown (Dull, Medium, High IQ)
5. Add Control Mode radio buttons
6. "Start Learning" button triggers backend initialization
7. Store selections in session state

#### Success Criteria:
- [ ] Can select any simulation from dropdown
- [ ] Profile settings saved to session state
- [ ] Clicking "Start Learning" initializes backend and navigates to Learning page

---

### **STEP 18: Learning Session Page (Core Teaching)**
**Estimated Time:** 3 hours

#### What We'll Build:
- Split screen: Simulation (left) + Chat (right)
- Simulation displayed in iframe with URL parameters
- Chat interface connected to teaching loop
- Real-time simulation updates in AUTO mode
- **Modify HTML simulation files to read URL parameters**

#### HTML Modification (for AUTO mode):
Add this JavaScript to `acids bases.html` and other simulations:
```javascript
// Read URL parameters and auto-configure simulation
(function() {
    const params = new URLSearchParams(window.location.search);
    
    if (params.has('pH')) {
        document.getElementById('phSlider').value = params.get('pH');
        document.getElementById('phSlider').dispatchEvent(new Event('input'));
    }
    if (params.has('volume')) {
        document.getElementById('beakerVolume').value = params.get('volume');
        document.getElementById('beakerVolume').dispatchEvent(new Event('change'));
    }
    // ... other parameters
})();
```

#### UI Layout:
```
┌─────────────────────────────────────────────────────────────────────────┐
│  🎓 Learning: Acids and Bases                    [Concept 1/3] [EXIT]   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────┐  ┌──────────────────────────────────┐  │
│  │                             │  │  💬 AI Tutor                     │  │
│  │     📺 SIMULATION           │  │                                  │  │
│  │                             │  │  AI: "Look at the beaker. When   │  │
│  │   ┌─────────────────────┐   │  │       pH is 2, what color do    │  │
│  │   │                     │   │  │       you see?"                  │  │
│  │   │    🧪 Beaker        │   │  │                                  │  │
│  │   │    pH: 2.0          │   │  │  You: "It's red!"               │  │
│  │   │    ACIDIC (RED)     │   │  │                                  │  │
│  │   │                     │   │  │  AI: "Correct! Red indicates    │  │
│  │   └─────────────────────┘   │  │       an acidic solution..."    │  │
│  │                             │  │                                  │  │
│  │   [Slider controls if       │  │  ┌──────────────────────────┐   │  │
│  │    MANUAL mode]             │  │  │  Type your response...   │   │  │
│  │                             │  │  └──────────────────────────┘   │  │
│  └─────────────────────────────┘  └──────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Tasks:
1. Create `frontend/pages/learning.py`
2. Create two-column layout (60% simulation, 40% chat)
3. **Modify HTML simulations to read URL parameters (AUTO mode support)**
4. Embed simulation via `st.components.iframe()`
5. Build chat interface with message history
6. Connect chat to backend teaching loop
7. Implement AUTO mode: backend sends URL params → iframe updates
8. Implement MANUAL mode: user interacts directly with simulation
9. Add concept progress indicator
10. Add "Move to Assessment" button when teaching complete

#### Backend Integration Points:
- Call `teaching_node()` for explanations
- Call `probing_node()` for questions
- Call `understanding_checker_node()` to analyze responses
- Call `feedback_node()` for adaptive responses
- Update `simulation_params` in state for AUTO mode

#### Success Criteria:
- [ ] Simulation loads in iframe
- [ ] Chat messages display correctly
- [ ] User can type and receive AI responses
- [ ] AUTO mode: simulation changes automatically
- [ ] MANUAL mode: user can control simulation
- [ ] Progress through concepts works

---

### **STEP 19: Assessment Quiz Page**
**Estimated Time:** 2 hours

#### What We'll Build:
- MCQ quiz interface
- One question at a time
- Visual feedback on answers
- Score tracking

#### UI Layout:
```
┌─────────────────────────────────────────────────────────────────┐
│  📝 Assessment Quiz                          Question 2/3       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                                                           │  │
│  │  Q2: What happens to pH when you add a strong acid        │  │
│  │      to a neutral solution?                               │  │
│  │                                                           │  │
│  │  ○ A) pH increases above 7                                │  │
│  │  ● B) pH decreases below 7                                │  │
│  │  ○ C) pH stays at 7                                       │  │
│  │  ○ D) pH becomes exactly 14                               │  │
│  │                                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  ✅ Correct! Acids lower pH below 7.                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│                    ┌─────────────────────┐                      │
│                    │   Next Question →   │                      │
│                    └─────────────────────┘                      │
│                                                                 │
│  Progress: ████████░░░░░░░░ 2/3                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Tasks:
1. Create `frontend/pages/assessment.py`
2. Display current MCQ question
3. Radio buttons for answer selection
4. Submit button to check answer
5. Show feedback (correct/incorrect with explanation)
6. Track score in session state
7. Navigate to next question or results page
8. Connect to backend `assessment_node()` and `mcq_generator_node()`

#### Success Criteria:
- [ ] Questions display one at a time
- [ ] Can select and submit answers
- [ ] Feedback shown after each answer
- [ ] Score tracked correctly
- [ ] Navigates to Results after last question

---

### **STEP 20: Results & Summary Page**
**Estimated Time:** 1.5 hours

#### What We'll Build:
- Final score display
- Performance breakdown
- Teaching metrics
- Level recommendation
- Restart option

#### UI Layout:
```
┌─────────────────────────────────────────────────────────────────┐
│  🎉 Session Complete!                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                                                           │  │
│  │           📊 YOUR RESULTS                                 │  │
│  │                                                           │  │
│  │           Score: 2/3 (67%)                                │  │
│  │                                                           │  │
│  │           ████████████░░░░░░                              │  │
│  │                                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  📈 Performance Breakdown:                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • Concepts Learned: 3                                    │  │
│  │  • Total Interactions: 22                                 │  │
│  │  • Understanding Rate: 35%                                │  │
│  │  • Re-explanation Rate: 65%                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  💡 Recommendation:                                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Stay at BEGINNER level. Focus on strengthening           │  │
│  │  foundational concepts before advancing.                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│       ┌──────────────────┐    ┌──────────────────┐              │
│       │  🔄 Try Again    │    │  🏠 New Session  │              │
│       └──────────────────┘    └──────────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Tasks:
1. Create `frontend/pages/results.py`
2. Display final score with visual progress bar
3. Show teaching metrics from backend
4. Display level recommendation from `summary_node()`
5. "Try Again" button - restart same simulation
6. "New Session" button - go back to setup

#### Success Criteria:
- [ ] Score displayed correctly
- [ ] Teaching metrics shown
- [ ] Level recommendation displayed
- [ ] Both restart options work

---

### **STEP 21: Simulation Server Setup**
**Estimated Time:** 1 hour

#### What We'll Build:
- HTTP server to serve HTML simulations
- Auto-start server with Streamlit app
- Server configuration

#### Tasks:
1. Create `frontend/sim_server.py` - dedicated simulation server
2. Configure server to serve from `SimulationsNCERT-main/` folder
3. Ensure server starts automatically with Streamlit app
4. Test URL parameters work end-to-end

#### Note:
HTML files are already modified in Step 18 to support URL parameters.

#### Success Criteria:
- [ ] Simulation server runs on port 8000
- [ ] Server starts automatically with app
- [ ] AUTO mode works end-to-end with real simulations

---

### **STEP 22: Backend-Frontend Integration**
**Estimated Time:** 2 hours

#### What We'll Build:
- Bridge between Streamlit and LangGraph backend
- State synchronization
- Real-time updates

#### Tasks:
1. Create `frontend/utils/backend_bridge.py`
2. Initialize LangGraph workflow from frontend
3. Call backend nodes and retrieve results
4. Update session state with backend responses
5. Handle async operations

#### Key Functions:
```python
def initialize_session(simulation, profile, mode):
    """Start new learning session"""
    
def send_message(user_input):
    """Send user message to teaching loop"""
    
def get_simulation_params():
    """Get current simulation parameters for AUTO mode"""
    
def submit_mcq_answer(answer):
    """Submit MCQ answer to assessment"""
```

#### Success Criteria:
- [ ] Backend initializes correctly from frontend
- [ ] Messages flow between frontend and backend
- [ ] Simulation params update in AUTO mode
- [ ] Assessment results return correctly

---

### **STEP 23: Polish & Error Handling**
**Estimated Time:** 1.5 hours

#### What We'll Build:
- Loading states
- Error messages
- Edge case handling
- UI polish

#### Tasks:
1. Add loading spinners during backend calls
2. Add error messages for failures
3. Handle edge cases (empty responses, timeouts)
4. Add CSS styling for better UI
5. Test all user flows

#### Success Criteria:
- [ ] No crashes on edge cases
- [ ] Loading states shown during waits
- [ ] Errors displayed gracefully
- [ ] UI looks polished

---

### **STEP 24: End-to-End Testing**
**Estimated Time:** 1 hour

#### What We'll Build:
- Complete flow testing
- Bug fixes
- Documentation

#### Tasks:
1. Test complete flow: Setup → Learning → Assessment → Results
2. Test AUTO mode end-to-end
3. Test MANUAL mode end-to-end
4. Fix any bugs found
5. Update README with usage instructions

#### Success Criteria:
- [ ] Complete flow works without errors
- [ ] Both AUTO and MANUAL modes work
- [ ] README has clear usage instructions

---

## 📅 Summary Timeline

| Step | Description | Est. Time |
|------|-------------|-----------|
| 16 | Project Setup & Basic Structure | 1 hr |
| 17 | Setup Page (Simulation Selection) | 1.5 hr |
| 18 | Learning Session Page (Core) | 3 hr |
| 19 | Assessment Quiz Page | 2 hr |
| 20 | Results & Summary Page | 1.5 hr |
| 21 | Simulation Server Integration | 1.5 hr |
| 22 | Backend-Frontend Integration | 2 hr |
| 23 | Polish & Error Handling | 1.5 hr |
| 24 | End-to-End Testing | 1 hr |
| **TOTAL** | | **15 hours** |

---

## 🗂️ Final Folder Structure

```
frontend/
├── app.py                      # Main entry point
├── config.py                   # Configuration
├── sim_server.py               # HTTP server for simulations
├── pages/
│   ├── __init__.py
│   ├── setup.py                # Step 17
│   ├── learning.py             # Step 18
│   ├── assessment.py           # Step 19
│   └── results.py              # Step 20
└── utils/
    ├── __init__.py
    ├── backend_bridge.py       # Step 22
    └── helpers.py              # UI helpers
```

---

## 🎯 Dependencies to Add

```txt
# Add to requirements.txt
streamlit>=1.28.0
```

---

## ✅ Ready to Start?

Begin with **Step 16: Project Setup & Basic Structure**

This creates the foundation for all subsequent steps.
