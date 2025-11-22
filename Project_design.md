#️⃣ 1. Introduction

This project aims to build a complete adaptive simulation teaching system using:

LangGraph (agent & workflow)

Streamlit (frontend UI)

HTML/JS simulations (NCERT / other)

AI-driven pedagogy (adaptive teaching loop)

The goal is to allow any interactive simulation to be taught by an intelligent tutoring agent who:

Explains concepts

Tailors depth/difficulty

Guides the student step-by-step

Shows before/after comparisons

Evaluates via MCQs

Adapts based on Level and Calibre

This document gives the entire end-to-end architecture & reasoning required to build the system.

#️⃣ 2. Core Problem & Key Requirements

We want the system to accomplish:

✅ 1. Load ANY HTML simulation

Simulation types:

Physics (pendulum, waves, motion)

Chemistry (acids/bases, indicators)

Biology (ecosystems, cells)

Maths (geometry, transformations)

✅ 2. Extract key domain concepts

We want 3–4 “core intuitions” from the simulation.

✅ 3. Adapt based on student profile

Two dimensions:

Attribute	Values
Level	Beginner, Intermediate, Advanced
Calibre	Dull, Medium, High IQ

This determines:

Depth of explanation

Speed of progression

Hint complexity

Style of language

✅ 4. Teach takeaways through an interactive loop

Includes:

Asking the student to change parameters

Observing outcomes

Answering reflective questions

Going deeper/simpler

✅ 5. Display simulation with dynamic (or manual) parameter changes

Two display modes:

Single View

Before/After View

✅ 6. End with MCQ-based evaluation
#️⃣ 3. System Inputs

The user supplies:

Simulation HTML link

e.g., https://…/Pendulum/index.html

Simulation description

NCERT chapter breakdown

Parameter list
(statically prepared by you)

Learner Level

Learner Calibre

#️⃣ 4. Simulation Metadata (VERY IMPORTANT)

We define a simulation.json for each simulation.

Example Metadata for Pendulum:
{
  "name": "Simple Pendulum",
  "topic": "Oscillations",
  "chapter": "NCERT Class 9 - Motion",
  "control_mode": "manual",
  "parameters": [
    {
      "name": "length",
      "type": "number",
      "unit": "m",
      "min": 1,
      "max": 20,
      "default": 2
    },
    {
      "name": "mass",
      "type": "number",
      "unit": "kg",
      "min": 0.1,
      "max": 5,
      "default": 1
    },
    {
      "name": "gravity",
      "type": "number",
      "unit": "m/s^2",
      "min": 1,
      "max": 20,
      "default": 9.8
    }
  ]
}

Parameter Types:

number

category

boolean

#️⃣ 5. Two Approaches for Parameter Control

This section is core — everything depends on this.

🅰️ Approach A — AUTO MODE (Ideal)

(You control / host the simulation HTML)

Precondition:

You download the HTML & JS files → add a small script to read URL params.

You add:
window.onload = function () {
  const params = new URLSearchParams(window.location.search);

  const length = parseFloat(params.get("length")) || 2;
  document.getElementById("lengthSlider").value = length;

  setPendulumLength(length);
  updateSimulation();
};

Now you can control simulation using:
sim.html?length=2
sim.html?length=10
sim.html?mass=3

Result:

Fully automated

You can generate side-by-side before/after without user interaction

🅱️ Approach B — MANUAL MODE (Your Actual Case)

(You cannot modify the original HTML — only link available)

Implications:

NO automatic parameter setting

Student must change parameters manually

Agent gives explicit instructions

But:

You can still embed the simulation in two iframes, allowing manual before/after:

Left iframe = original link
Right iframe = same link

Agent says:

"In the LEFT simulation, set length to 2 m.
In the RIGHT simulation, set length to 10 m.
Observe and describe the difference."

This keeps 80% of system functionality intact.
#️⃣ 6. Frontend Responsibilities (Streamlit)

Streamlit does:

✔ Display simulation in iframe
components.iframe(sim_url, height=500)

✔ Display before/after view

Two iframes side-by-side:

col1, col2 = st.columns(2)
col1.iframe(sim_url)
col2.iframe(sim_url)

✔ Show agent messages
✔ Take student input
✔ Send to LangGraph
✔ Render view_config (instructions)
❌ Streamlit does NOT

Control the simulation

Update sliders

Modify HTML

Inject JS

The simulation runs inside the browser, not inside Python.

#️⃣ 7. LangGraph Architecture (Approach 1)

This is the main backbone of the project.

🧩 Pipeline Nodes
Node 1 — SimulationIngestNode

Loads metadata

Reads parameter types

Stores sim_metadata, sim_params

Node 2 — ConceptExtractorNode

Extracts:

Core scientific concepts

Learning goals

Relationships between parameters

Based on simulation description + NCERT content

Node 3 — ProfileRouterNode

Based on:

Level (B/I/A)

Calibre (D/M/H)

It decides:

Explanation difficulty

Complexity of takeaways

Number of steps

Node 4 — LessonPlannerNode

For each takeaway:

Which parameter to vary

Whether before/after is useful

Which probing questions to ask

How many steps for that takeaway

How to tailor steps per profile

🧩 Teaching Loop Subgraph (Core Interactive Engine)

This loop repeats for each takeaway.

Nodes inside:
1. PromptStudentNode

Generates message:

what to do

why

how to observe

Updates view_config

2. RecordStudentResponseNode

Logs reply in interaction_history

3. InterpretResponseNode

Outputs:

local_status: understood / partial / confused
suggestion: repeat_simpler / go_deeper / proceed

4. TeachOrClarifyNode

Tailors explanation based on:

level

calibre

response difficulty

5. TakeawayProgressNode

If:

Not done → repeat

Done → move to next takeaway

No more → go to MCQs

#️⃣ 8. View Configuration (Critical for Simulation UI)

View config determines display.

In AUTO MODE:
{
  "mode": "before_after",
  "left_params": {"length": 2},
  "right_params": {"length": 10}
}

In MANUAL MODE:
{
  "mode": "before_after",
  "left_instructions": "Set length to 2 m",
  "right_instructions": "Set length to 10 m"
}


Streamlit reads view_config and displays UI accordingly.

#️⃣ 9. MCQ System

After teaching:

Node — MCQGeneratorNode

Creates 3–5 MCQs

Based on takeaways

Node — MCQEvaluatorNode

Evaluates response

Gives feedback

Suggests next level/study

#️⃣ 10. Overall State Structure
{
  "sim_link": "",
  "sim_metadata": {},
  "sim_params": {},
  "concepts": [],
  "level_plan": [],
  "current_takeaway_idx": 0,
  "interaction_history": [],
  "learner_profile": {
      "level": "",
      "calibre": ""
  },
  "view_config": {},
  "mcqs": [],
  "assessment": {}
}

#️⃣ 11. Repository Structure (Recommended)
simulation-teaching-agent/
│
├── simulations/          # your hosted or manual reference simulations
├── metadata/             # JSON files
│   ├── pendulum.json
│   ├── acids.json
│   └── etc…
│
├── backend/              # LangGraph
│   ├── nodes/
│   ├── teaching_loop/
│   └── workflow.py
│
├── frontend/             # Streamlit
│   ├── app.py
│   └── components/
│
└── docs/
    └── project_design.md

#️⃣ 12. Implementation Roadmap (Clear Step-by-Step)
Phase 1 — Foundation

Create metadata JSON for one simulation

Build SimulationIngestNode

Build ConceptExtractorNode

Implement ProfileRouter

Phase 2 — Teaching Logic

Build LessonPlanner

Build Teaching Loop subgraph

View config logic

Interpretation logic

Phase 3 — Frontend

Streamlit UI

Chat interface

Simulation iframe embedding

Manual before/after integration

Phase 4 — MCQs

MCQ generator

MCQ evaluator

Phase 5 — End-to-end integration

Connect LangGraph ↔ Streamlit

Test interactions manually

Add more simulations

#️⃣ 13. Example End-to-End Flow
User selects:

Simulation: Pendulum

Level: Beginner

Calibre: Medium

Agent:

Extracts concepts

Selects 3 takeaways

Creates steps

Frontend:

Shows before/after (manual or auto)

Student interacts

Agent probes understanding

End:

MCQs

Score + feedback

#️⃣ 14. Conclusion

This document includes EVERYTHING needed to begin implementing the project:

✔ Both AUTO & MANUAL parameter control approaches
✔ Complete LangGraph design
✔ Simulation metadata strategy
✔ Teaching loop logic
✔ Frontend architecture
✔ Full workflow overview
✔ Example views
✔ Implementation plan