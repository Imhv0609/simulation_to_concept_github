"""
State definition for the teaching workflow.

This defines the complete state structure that flows between nodes
in the LangGraph workflow.
"""

from typing import TypedDict, List, Dict, Optional, Literal


# Type aliases for better readability
Level = Literal["Beginner", "Intermediate", "Advanced"]
Calibre = Literal["Dull", "Medium", "High IQ"]
ControlMode = Literal["AUTO", "MANUAL"]
ViewMode = Literal["single", "before_after"]


class LearnerProfile(TypedDict):
    """Student's learning profile"""
    level: Level
    calibre: Calibre


class UnderstandingStatus(TypedDict):
    """Tracks student's understanding of current concept"""
    is_confused: bool  # Set by Understanding Checker Node
    confidence_level: float  # 0.0 to 1.0
    last_interaction_quality: str  # "good", "poor", "neutral"


class SimulationParameter(TypedDict):
    """Definition of a simulation parameter"""
    name: str
    description: Optional[str]
    type: str  # "number", "category", "boolean"
    min: Optional[float]  # For number type
    max: Optional[float]  # For number type
    default: Optional[any]
    html_id: Optional[str]  # HTML element ID for reference


class SimulationMetadata(TypedDict):
    """Metadata about the simulation"""
    name: str
    link: str
    description: str
    control_mode: ControlMode
    topic: Optional[str]
    chapter: Optional[str]


class Concept(TypedDict):
    """A key concept to be taught"""
    name: str
    description: str
    importance: str  # "high", "medium", "low"


class Takeaway(TypedDict):
    """A single learning takeaway"""
    id: int
    concept: str
    explanation: str
    parameters_to_vary: List[str]  # Parameter names
    parameter_values: Dict[str, any]  # Specific values to set
    display_mode: ViewMode  # "single" or "before_after"
    before_state: Optional[Dict[str, any]]  # For before_after mode
    after_state: Optional[Dict[str, any]]  # For before_after mode
    probing_question: str


class ViewConfig(TypedDict):
    """Configuration for displaying the simulation"""
    mode: ViewMode
    instructions: Optional[str]
    left_instructions: Optional[str]  # For before_after mode
    right_instructions: Optional[str]  # For before_after mode
    observation_prompt: Optional[str]


class Interaction(TypedDict):
    """Record of a student-agent interaction"""
    timestamp: str
    agent_message: str
    student_response: Optional[str]
    understanding_status: Optional[UnderstandingStatus]


class MCQ(TypedDict):
    """A multiple choice question"""
    id: int
    question: str
    options: List[str]  # List of option texts
    correct_answer: int  # Index of correct option (0-based)
    explanation: str


class Assessment(TypedDict):
    """Assessment results"""
    total_questions: int
    correct_answers: int
    score_percentage: float
    feedback: str
    recommended_next_level: Optional[Level]


class TeachingState(TypedDict):
    """
    Complete state for the teaching workflow.
    This is passed between all nodes in the LangGraph.
    """
    
    # ===== INPUT DATA (from frontend) =====
    simulation_name: str  # Name of the simulation (key for config lookup)
    learner_profile: LearnerProfile
    
    # ===== SIMULATION DETAILS (populated by ingestion node) =====
    simulation_url: str  # Full URL/path to simulation HTML
    simulation_params: Dict[str, SimulationParameter]  # Parsed parameters
    simulation_buttons: List[Dict[str, str]]  # Extracted buttons [{id, label, type}]
    control_mode: ControlMode  # AUTO or MANUAL
    
    # ===== EXTRACTED CONCEPTS (populated by concept extractor) =====
    concepts: List[Concept]
    current_concept_index: int
    
    # ===== LESSON PLAN (populated by planner) =====
    takeaways: List[Takeaway]  # Lesson plan for current concept
    current_takeaway_index: int
    re_explain_count: int  # Track re-explanation attempts (for loop safety)
    
    # ===== DISPLAY CONTROL =====
    view_config: ViewConfig
    
    # ===== INTERACTION TRACKING =====
    interactions: List[Interaction]
    understanding_status: UnderstandingStatus
    
    # ===== ASSESSMENT =====
    mcqs: List[MCQ]  # Generated MCQ questions
    current_mcq_index: int  # Which MCQ we're on
    student_answers: List[int]  # Student's answers (indices)
    assessment: Optional[Assessment]  # Final assessment results
    
    # ===== CONTROL/MESSAGING =====
    messages: List[str]  # Agent messages to display
    feedback_message: Optional[str]  # Feedback from feedback node
    next_action: str  # What to do next
    error: Optional[str]  # Error message if any
