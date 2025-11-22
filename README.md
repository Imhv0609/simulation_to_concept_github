# 🎓 Simulation Teaching Agent

An adaptive AI agent that teaches students through interactive HTML simulations using LangGraph and Google Gemini.

## 📋 Project Overview

This system:
- Ingests any HTML-based science simulation
- Extracts key concepts and learning goals
- Adapts teaching based on student level (Beginner/Intermediate/Advanced)
- Guides students through interactive exploration
- Tests understanding via MCQs
- **🎛️ Supports MANUAL and AUTO control modes** (see [MODE_SWITCHING.md](MODE_SWITCHING.md))

## 🚀 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Create a `.env` file and add your Google Gemini API key:
```
GOOGLE_API_KEY=your_api_key_here
```

### 3. Configure Control Mode (Optional)
Edit `backend/config.py` to choose between MANUAL or AUTO mode:
```python
SIMULATION_CONTROL_MODE = "MANUAL"  # or "AUTO"
```
See [MODE_SWITCHING.md](MODE_SWITCHING.md) for details.

### 4. Run Tests
```bash
cd backend
python test_ingestion.py    # Test ingestion with mode switching
python demo_mode_switch.py  # See mode switching demo
```

### 5. Run the Backend
```bash
cd backend
python main.py
```

### 6. Run the Frontend (Phase 5)
```bash
streamlit run frontend/app.py
```

## 📁 Project Structure

```
simulation_to_concept/
├── backend/              # LangGraph workflow
│   ├── nodes/           # Node implementations
│   │   ├── ingestion.py       # ✅ Ingest, parse, extract concepts
│   │   ├── router.py          # ⏳ Route workflow decisions
│   │   ├── planner.py         # ⏳ Plan teaching strategy
│   │   ├── teaching_loop.py   # ⏳ Main teaching nodes
│   │   └── assessment.py      # ⏳ MCQ generation & grading
│   ├── utils/           # Helper functions
│   ├── config.py        # 🎛️ Control mode configuration
│   ├── state.py         # ✅ State definition
│   ├── graph.py         # ✅ Workflow graph
│   ├── main.py          # Entry point
│   ├── test_ingestion.py     # ✅ Test ingestion nodes
│   └── demo_mode_switch.py   # ✅ Demo mode switching
├── frontend/            # Streamlit UI (Phase 5)
├── SimulationsNCERT-main/    # HTML simulations
├── index.html           # Simulation dashboard
├── MODE_SWITCHING.md    # 📖 Mode switching guide
└── README.md            # This file
```

## 🎛️ Control Modes

The system supports two control modes that can be switched with a **single parameter**:

### MANUAL Mode (Current - Default)
- ✅ Works with existing HTML simulations
- ✅ Agent provides **instructions** to student
- ✅ Student **manually changes** parameters
- ✅ Best for interactive learning

### AUTO Mode (Future)
- 🔄 Requires hosted simulations with URL parameter support
- 🔄 Agent **programmatically controls** simulation
- 🔄 Agent directly modifies parameters
- 🔄 Best for automated demos

**Switch modes:** Edit `backend/config.py` → `SIMULATION_CONTROL_MODE = "MANUAL"` or `"AUTO"`

📖 **Full documentation:** [MODE_SWITCHING.md](MODE_SWITCHING.md)

## 🔄 Development Status

- [x] Phase 1: Foundation Setup
- [ ] Phase 2: Node Implementation
- [ ] Phase 3: Teaching Loop
- [ ] Phase 4: Assessment
- [ ] Phase 5: Frontend

## 📝 License

Educational project for NCERT simulation teaching.
