# Mode Switching Guide 🎛️

## Overview

The teaching agent has a **modular control mode system** that acts like a "clipper" - you can switch between AUTO and MANUAL modes with a single parameter change in `config.py`.

## The Clipper Concept

```python
# In backend/config.py - THIS IS THE CLIPPER!
SIMULATION_CONTROL_MODE: Literal["MANUAL", "AUTO"] = "MANUAL"
```

Change this **one parameter**, and the **entire system adapts**:
- ✅ Ingestion nodes check this config
- ✅ Teaching nodes check this config  
- ✅ Router node checks this config
- ✅ All behavior changes automatically

---

## Two Modes Explained

### 1️⃣ MANUAL Mode (Current - Default)

**Use Case:** Works with existing HTML simulation files

**Behavior:**
- ❌ Agent **cannot** programmatically control simulation
- ✅ Agent **provides instructions** to student
- ✅ Student **manually changes** parameters in the simulation
- ✅ Agent **guides** the learning process

**Configuration:**
```python
MANUAL_MODE_CONFIG = {
    "requires_instructions": True,   # Agent tells student what to do
    "can_modify_params": False,      # Agent can't change simulation directly
    "interaction_type": "guided",    # Agent guides student
    "view_mode": "full",            # Student sees full simulation
}
```

**Example Teaching Flow:**
1. Agent: "Please set the denominator to 8 using the slider"
2. Student manually moves slider in simulation
3. Agent: "Great! Now observe what happens when you change numerator to 3"
4. Student manually makes the change
5. Agent asks comprehension questions

---

### 2️⃣ AUTO Mode (Future - When You Host Simulations)

**Use Case:** When simulations are hosted and accept URL parameters

**Behavior:**
- ✅ Agent **can** programmatically control simulation
- ✅ Agent **directly modifies** parameters via URL
- ✅ Agent **shows** specific parameter combinations
- ✅ More direct, automated teaching

**Configuration:**
```python
AUTO_MODE_CONFIG = {
    "requires_instructions": False,  # No need for manual instructions
    "can_modify_params": True,       # Agent controls simulation directly
    "interaction_type": "direct",    # Direct manipulation
    "view_mode": "controlled",       # Agent controls what student sees
}
```

**Example Teaching Flow:**
1. Agent automatically loads: `simulation.html?denominator=8&numerator=1`
2. Student observes the pre-configured view
3. Agent automatically changes to: `simulation.html?denominator=8&numerator=3`
4. Student sees the change happen automatically
5. Agent asks comprehension questions

---

## How to Switch Modes

### Option 1: Edit Config File (Recommended)

1. Open `backend/config.py`
2. Find line 11:
   ```python
   SIMULATION_CONTROL_MODE: Literal["MANUAL", "AUTO"] = "MANUAL"
   ```
3. Change to:
   ```python
   SIMULATION_CONTROL_MODE: Literal["MANUAL", "AUTO"] = "AUTO"
   ```
4. Save file
5. **Done!** All nodes will now use AUTO mode

### Option 2: Programmatic Switching (Advanced)

```python
import config

# Check current mode
if config.is_manual_mode():
    print("Currently in MANUAL mode")

# Get mode-specific configuration
mode_config = config.get_current_mode_config()
print(f"Can modify params: {mode_config['can_modify_params']}")

# Get simulation URL
url = config.get_simulation_url("fractions")
```

---

## Testing Mode Switching

### Quick Test
```bash
cd backend
python demo_mode_switch.py
```

This shows how the same code behaves differently based on the mode.

### Full Test
```bash
cd backend
python test_ingestion.py
```

This tests the complete ingestion node with current mode settings.

---

## When to Use Each Mode

### Use MANUAL Mode When:
- ✅ Using existing HTML simulations (like NCERT files)
- ✅ Simulations don't support URL parameters
- ✅ You want students to physically interact with controls
- ✅ Testing/development phase
- ✅ **Now** - current implementation

### Use AUTO Mode When:
- ✅ You host simulations with URL parameter support
- ✅ You want programmatic control
- ✅ You want to show specific parameter combinations
- ✅ You want faster, more automated teaching
- ✅ **Future** - when you deploy hosted simulations

---

## Implementation Details

### How Nodes Check Mode

All nodes import and check the config:

```python
import config

def my_node(state: TeachingState):
    # Check mode at runtime
    if config.is_manual_mode():
        # Provide instructions to student
        return {
            "instructions": "Please move the slider to value 5"
        }
    else:  # AUTO mode
        # Modify simulation directly
        return {
            "view_config": {
                "url": "simulation.html?value=5"
            }
        }
```

### Adding Simulations

Edit `SIMULATION_URLS` in `config.py`:

```python
SIMULATION_URLS: Dict[str, str] = {
    # For MANUAL mode (local files)
    "my_sim": "../path/to/my_sim.html",
    
    # For AUTO mode (hosted URLs with params)
    "my_sim_hosted": "https://example.com/sim?param={value}",
}
```

---

## Future Roadmap

### Phase 1: MANUAL Mode (Current)
- ✅ Single config parameter
- ✅ Mode-aware ingestion node
- ✅ Instruction-based teaching
- ⏳ Complete all teaching nodes
- ⏳ Streamlit frontend

### Phase 2: AUTO Mode (Future)
- ⏳ Host simulations with URL param support
- ⏳ Add hosted URLs to config
- ⏳ Switch config to AUTO
- ⏳ Test with programmatic control

---

## Benefits of This Approach

### 1. **Single Source of Truth**
- One parameter controls everything
- No scattered configuration
- Easy to understand and maintain

### 2. **Future-Proof**
- Works with existing simulations NOW
- Easy upgrade path when you host simulations
- No code rewrite needed - just change config

### 3. **Modular & Clean**
- Config separated from logic
- Nodes check config at runtime
- Easy to test both modes

### 4. **Type-Safe**
- `Literal["MANUAL", "AUTO"]` prevents typos
- IDE autocomplete support
- Compile-time error checking

---

## Quick Reference

```python
# Current mode
config.SIMULATION_CONTROL_MODE  # "MANUAL" or "AUTO"

# Mode checking
config.is_manual_mode()  # Returns True if MANUAL
config.is_auto_mode()    # Returns True if AUTO

# Get configuration
config.get_current_mode_config()  # Returns dict with mode settings

# Get simulation URL
config.get_simulation_url("fractions")  # Returns URL for simulation
```

---

## Questions?

**Q: Can I switch modes at runtime?**  
A: No, mode is set at import time. Restart the application after changing config.

**Q: Can I have different modes for different simulations?**  
A: Currently no - it's a global setting. But you could extend the system to support per-simulation modes.

**Q: Do I need to change any other code when switching modes?**  
A: No! That's the beauty of the clipper approach. Change one parameter, everything adapts.

**Q: What if I forget to update simulation URLs for AUTO mode?**  
A: AUTO mode will try to use the URLs in config. Make sure to add hosted URLs before switching to AUTO.

---

## Example: Full Workflow

### MANUAL Mode Workflow
1. Student opens simulation in browser
2. Agent: "Set denominator to 8"
3. Student moves slider
4. Agent: "What do you observe?"
5. Student responds
6. Agent provides feedback
7. Repeat for next concept

### AUTO Mode Workflow
1. Agent loads: `sim.html?denom=8`
2. Agent: "What do you observe?"
3. Student responds
4. Agent loads: `sim.html?denom=4`
5. Agent: "How did it change?"
6. Student responds
7. Agent provides feedback
8. Repeat for next concept

**Both use the SAME code - just different mode in config!** 🎉
