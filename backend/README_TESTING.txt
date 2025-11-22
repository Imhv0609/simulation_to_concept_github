╔═══════════════════════════════════════════════════════════════════╗
║                    SIMPLE TESTING GUIDE                           ║
╚═══════════════════════════════════════════════════════════════════╝

📁 SIMPLIFIED FILE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

backend/
├── 🧪 easy_test.py       ← THE ONLY TEST FILE - Edit this to test!
├── ⚙️  config.py           ← Configuration (control mode, URLs)
├── 📋 state.py            ← State structure definition
├── 🔄 graph.py            ← Workflow setup (not used yet)
├── 📖 DATA_FLOW.txt       ← Detailed explanation (read if confused)
└── 📂 nodes/
    └── ingestion.py       ← Backend logic (Step 4 complete)


🎯 HOW TO TEST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Open easy_test.py
2. Edit 3 lines (18, 19, 20):
   
   TEST_SIMULATION = "fractions"    ← Change this
   TEST_LEVEL = "Beginner"          ← Change this
   TEST_CALIBRE = "Medium"          ← Change this

3. Save and run:
   
   $ cd backend
   $ python easy_test.py

4. See results!


📚 AVAILABLE OPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Simulations (7):
  fractions, acids_bases_solutions, concentration, masses_springs,
  molecule_shapes, ph_scale, projectile_motion

Levels (3):
  Beginner, Intermediate, Advanced

Calibre (3):
  Dull, Medium, High IQ


🔄 DATA FLOW (Simplified)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOU edit easy_test.py
      ↓
Test file creates state with your values
      ↓
Calls simulation_ingest_node(state)
      ↓
Node validates & enriches state
      ↓
Returns updated state
      ↓
Test file prints results


📖 NEED MORE DETAILS?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Read: DATA_FLOW.txt for complete explanation


🎓 WHAT EACH FILE DOES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

easy_test.py:     You edit this, simulates user input
config.py:        Settings (mode, URLs), you can change mode here
state.py:         Defines data structure, you DON'T edit this
nodes/ingestion.py: Backend logic, you DON'T edit this
DATA_FLOW.txt:    Detailed explanation, read when confused


💡 REMEMBER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Only ONE test file: easy_test.py
✓ Edit 3 values to test different scenarios
✓ Backend validates, not collects inputs
✓ In Phase 5, Streamlit will collect inputs instead of you
✓ Keep it simple!
