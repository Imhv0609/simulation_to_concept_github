"""
Assessment Nodes - Steps 13-15

This file contains the nodes that handle the assessment phase:
- mcq_generator_node (Step 13): Generates MCQ questions based on taught concepts
- assessment_node (Step 14): Presents MCQs and evaluates answers
- summary_node (Step 15): Generates final summary and recommendations

These nodes complete the teaching workflow with assessment.
"""

from typing import Dict, Any, List
import sys
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from state import TeachingState


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 13: MCQ Generator Node
# ═══════════════════════════════════════════════════════════════════════════════

# Number of MCQs to generate based on concepts taught
MIN_MCQS = 3
MAX_MCQS = 5


def mcq_generator_node(state: TeachingState) -> Dict[str, Any]:
    """
    Step 13: MCQ Generator Node
    
    Generates multiple choice questions based on all the concepts that were
    taught during the teaching phase. This node:
    1. Collects all concepts that were taught
    2. Gathers interaction history for context
    3. Uses LLM to generate appropriate MCQs
    4. Stores MCQs in state for assessment
    
    REQUIRES LLM - Semantic generation of quiz questions.
    
    Args:
        state: Current teaching state with concepts and interactions
        
    Returns:
        Dict with:
        - mcqs: List of generated MCQ questions
        - current_mcq_index: Set to 0 (start of quiz)
        - student_answers: Empty list (no answers yet)
        - next_action: "assess" (to start assessment)
        
    State Fields Used:
        - concepts: All concepts that were taught
        - interactions: History of teaching interactions
        - learner_profile: Student's level and calibre
        - simulation_name: For context in questions
    """
    
    print("\n" + "="*60)
    print("MCQ GENERATOR NODE - Creating Assessment Questions")
    print("="*60)
    
    # Extract relevant state
    concepts = state.get("concepts", [])
    interactions = state.get("interactions", [])
    learner_profile = state.get("learner_profile", {})
    simulation_name = state.get("simulation_name", "the simulation")
    
    # Validate we have concepts to assess
    if not concepts:
        print("\n❌ Error: No concepts available for assessment")
        return {
            "error": "No concepts available to generate MCQs",
            "mcqs": [],
            "next_action": "end",
            "messages": state.get("messages", []) + [
                "MCQ Generator: Error - No concepts to assess"
            ]
        }
    
    # Determine number of MCQs based on concepts
    num_concepts = len(concepts)
    num_mcqs = min(max(num_concepts, MIN_MCQS), MAX_MCQS)
    
    print(f"\n📚 Concepts to assess: {num_concepts}")
    for i, concept in enumerate(concepts, 1):
        print(f"   {i}. {concept.get('name', 'Unknown')}")
    
    print(f"\n📊 Student Profile:")
    print(f"   Level: {learner_profile.get('level', 'Beginner')}")
    print(f"   Calibre: {learner_profile.get('calibre', 'Medium')}")
    
    print(f"\n🎯 Generating {num_mcqs} MCQ questions...")
    
    # Initialize LLM and generate MCQs
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.7  # Slightly higher for variety in questions
        )
        print(f"✅ LLM initialized: {model_name}")
        
        # Build the MCQ generation prompt
        prompt = build_mcq_prompt(
            concepts=concepts,
            interactions=interactions,
            learner_level=learner_profile.get("level", "Beginner"),
            simulation_name=simulation_name,
            num_mcqs=num_mcqs
        )
        
        print(f"\n🔄 Calling LLM to generate MCQs...")
        
        # Call LLM
        response = llm.invoke(prompt)
        response_text = response.content
        
        print(f"📄 LLM Response received: {len(response_text)} characters")
        
        # Parse the MCQs from response
        mcqs = parse_mcq_response(response_text, num_mcqs)
        
    except Exception as e:
        print(f"\n⚠️ LLM Error: {str(e)}")
        print("   Using fallback MCQ generation...")
        # Fallback: Generate simple MCQs without LLM
        mcqs = generate_fallback_mcqs(concepts, learner_profile)
    
    # Validate MCQs
    if not mcqs:
        print("\n⚠️ No valid MCQs generated, using fallback...")
        mcqs = generate_fallback_mcqs(concepts, learner_profile)
    
    # Display generated MCQs
    print(f"\n✅ Generated {len(mcqs)} MCQs:")
    for i, mcq in enumerate(mcqs, 1):
        print(f"\n   Q{i}: {mcq['question'][:60]}...")
        print(f"       Options: {len(mcq['options'])} choices")
        print(f"       Correct: Option {mcq['correct_answer'] + 1}")
    
    print("\n" + "="*60)
    print("🎯 MCQ GENERATION COMPLETE: Ready for assessment")
    print(f"   Total questions: {len(mcqs)}")
    print("="*60 + "\n")
    
    # Return updated state
    return {
        "mcqs": mcqs,
        "current_mcq_index": 0,
        "student_answers": [],
        "next_action": "present_mcq",
        "messages": state.get("messages", []) + [
            f"MCQ Generator: Created {len(mcqs)} assessment questions"
        ]
    }


def build_mcq_prompt(
    concepts: List[Dict[str, Any]],
    interactions: List[Dict[str, Any]],
    learner_level: str,
    simulation_name: str,
    num_mcqs: int
) -> str:
    """
    Builds the LLM prompt for generating MCQ questions.
    
    The prompt is designed to:
    - Create questions at the appropriate difficulty level
    - Cover all taught concepts
    - Include plausible distractors
    - Provide explanations for correct answers
    
    Args:
        concepts: List of concepts that were taught
        interactions: Teaching interaction history
        learner_level: Beginner/Intermediate/Advanced
        simulation_name: Name of the simulation
        num_mcqs: Number of MCQs to generate
        
    Returns:
        Formatted prompt string
    """
    
    # Build concepts summary
    concepts_text = "\n".join([
        f"- {c.get('name', 'Unknown')}: {c.get('description', 'No description')}"
        for c in concepts
    ])
    
    # Adjust difficulty based on level
    if learner_level == "Beginner":
        difficulty_guidance = """
- Use simple, clear language
- Focus on basic understanding and recognition
- Avoid complex calculations
- Make correct answers clearly distinguishable
- Distractors should be obviously wrong for someone who understood"""
    elif learner_level == "Advanced":
        difficulty_guidance = """
- Use technical terminology appropriately
- Include application and analysis questions
- Distractors should be plausible misconceptions
- Some questions can involve reasoning across concepts
- Include subtle distinctions"""
    else:  # Intermediate
        difficulty_guidance = """
- Use clear language with some technical terms
- Mix recall and application questions
- Distractors should be reasonable alternatives
- Test understanding, not just memorization"""
    
    prompt = f"""You are an expert educator creating assessment questions for a student who just learned about a simulation.

SIMULATION: {simulation_name}

CONCEPTS TAUGHT:
{concepts_text}

STUDENT LEVEL: {learner_level}
{difficulty_guidance}

TASK: Generate exactly {num_mcqs} multiple choice questions to assess understanding.

REQUIREMENTS:
1. Each question should test ONE concept
2. Provide exactly 4 options (A, B, C, D)
3. Only ONE option should be correct
4. Include a brief explanation for why the correct answer is right
5. Questions should relate to the simulation context
6. Distribute questions across all concepts if possible

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "mcqs": [
        {{
            "id": 1,
            "question": "Your question text here?",
            "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
            "correct_answer": 0,
            "explanation": "Brief explanation of why this is correct"
        }},
        {{
            "id": 2,
            "question": "Second question?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": 2,
            "explanation": "Explanation"
        }}
    ]
}}

Note: correct_answer is 0-indexed (0=A, 1=B, 2=C, 3=D)

Generate the {num_mcqs} MCQ questions now:"""
    
    return prompt


def parse_mcq_response(response_text: str, expected_count: int) -> List[Dict[str, Any]]:
    """
    Parses the LLM response into a list of MCQ dictionaries.
    
    Args:
        response_text: Raw LLM response
        expected_count: Expected number of MCQs
        
    Returns:
        List of MCQ dictionaries
    """
    
    try:
        # Try to extract JSON from response
        text = response_text.strip()
        
        # Remove markdown code blocks if present
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()
        
        # Parse JSON
        data = json.loads(text)
        
        # Extract MCQs
        mcqs = data.get("mcqs", [])
        
        # Validate and normalize each MCQ
        validated_mcqs = []
        for i, mcq in enumerate(mcqs):
            validated = validate_mcq(mcq, i + 1)
            if validated:
                validated_mcqs.append(validated)
        
        print(f"   Parsed {len(validated_mcqs)} valid MCQs from response")
        return validated_mcqs
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"⚠️ Error parsing MCQ response: {e}")
        return []


def validate_mcq(mcq: Dict[str, Any], default_id: int) -> Dict[str, Any]:
    """
    Validates and normalizes an MCQ dictionary.
    
    Args:
        mcq: Raw MCQ dictionary
        default_id: Default ID if not provided
        
    Returns:
        Validated MCQ dictionary or None if invalid
    """
    
    try:
        # Required fields
        question = mcq.get("question", "").strip()
        options = mcq.get("options", [])
        correct_answer = mcq.get("correct_answer", 0)
        
        # Validate
        if not question:
            return None
        if len(options) < 2:
            return None
        if not isinstance(correct_answer, int) or correct_answer < 0 or correct_answer >= len(options):
            correct_answer = 0
        
        # Normalize
        return {
            "id": mcq.get("id", default_id),
            "question": question,
            "options": [str(opt) for opt in options],
            "correct_answer": correct_answer,
            "explanation": mcq.get("explanation", "See the lesson for more details.")
        }
        
    except Exception:
        return None


def generate_fallback_mcqs(
    concepts: List[Dict[str, Any]],
    learner_profile: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generates simple fallback MCQs when LLM is unavailable.
    
    Creates basic questions based on concept names and descriptions.
    
    Args:
        concepts: List of concepts
        learner_profile: Student's profile
        
    Returns:
        List of fallback MCQ dictionaries
    """
    
    fallback_mcqs = []
    
    for i, concept in enumerate(concepts[:MAX_MCQS]):
        concept_name = concept.get("name", f"Concept {i+1}")
        description = concept.get("description", "this concept")
        
        # Generate a simple question about the concept
        mcq = {
            "id": i + 1,
            "question": f"Which of the following best describes {concept_name}?",
            "options": [
                f"{description[:100]}..." if len(description) > 100 else description,
                "This concept is not related to the simulation",
                "This is an incorrect understanding",
                "None of the above applies"
            ],
            "correct_answer": 0,
            "explanation": f"The correct answer describes {concept_name} as taught in the lesson."
        }
        fallback_mcqs.append(mcq)
    
    # Add a general understanding question if we have room
    if len(fallback_mcqs) < MIN_MCQS:
        fallback_mcqs.append({
            "id": len(fallback_mcqs) + 1,
            "question": "What is the main purpose of using simulations in learning?",
            "options": [
                "To visualize and interact with concepts",
                "To replace textbooks completely",
                "To make learning more difficult",
                "To test computer skills only"
            ],
            "correct_answer": 0,
            "explanation": "Simulations help students visualize and interact with concepts in an engaging way."
        })
    
    return fallback_mcqs


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 14: Assessment Node
# ═══════════════════════════════════════════════════════════════════════════════

def assessment_node(state: TeachingState) -> Dict[str, Any]:
    """
    Step 14: Assessment Node
    
    Presents MCQ questions to the student and collects their answers.
    This node handles the quiz-taking process:
    
    1. Presents current MCQ with options
    2. Collects student answer (simulated in test mode)
    3. Records answer and moves to next question
    4. When all questions answered, moves to summary
    
    NO LLM REQUIRED - Just presentation and answer collection.
    
    Args:
        state: Current teaching state with MCQs
        
    Returns:
        Dict with:
        - student_answers: Updated list of answers
        - current_mcq_index: Incremented or same
        - assessment: Partial results during quiz
        - next_action: "next_mcq" or "summarize"
        
    State Fields Used:
        - mcqs: List of MCQ questions
        - current_mcq_index: Which question we're on
        - student_answers: Answers collected so far
        - learner_profile: For simulating responses
    """
    
    print("\n" + "="*60)
    print("ASSESSMENT NODE - Quiz in Progress")
    print("="*60)
    
    # Extract relevant state
    mcqs = state.get("mcqs", [])
    current_index = state.get("current_mcq_index", 0)
    student_answers = state.get("student_answers", [])
    learner_profile = state.get("learner_profile", {})
    
    # Validate we have MCQs
    if not mcqs:
        print("\n❌ Error: No MCQs available for assessment")
        return {
            "error": "No MCQs available",
            "next_action": "end",
            "messages": state.get("messages", []) + [
                "Assessment: Error - No questions to present"
            ]
        }
    
    # Check if we've finished all questions
    if current_index >= len(mcqs):
        print("\n✅ All questions answered! Moving to summary...")
        
        # Calculate results
        correct_count = 0
        for i, answer in enumerate(student_answers):
            if i < len(mcqs) and answer == mcqs[i].get("correct_answer", -1):
                correct_count += 1
        
        score_pct = (correct_count / len(mcqs)) * 100 if mcqs else 0
        
        print(f"\n📊 Quiz Results:")
        print(f"   Correct: {correct_count}/{len(mcqs)}")
        print(f"   Score: {score_pct:.0f}%")
        
        # Create partial assessment (summary node will finalize)
        partial_assessment = {
            "total_questions": len(mcqs),
            "correct_answers": correct_count,
            "score_percentage": score_pct,
            "feedback": "",  # Summary node will generate
            "recommended_next_level": None  # Summary node will decide
        }
        
        print("\n" + "="*60)
        print("🎯 ASSESSMENT COMPLETE: Ready for summary")
        print("="*60 + "\n")
        
        return {
            "assessment": partial_assessment,
            "next_action": "summarize",
            "messages": state.get("messages", []) + [
                f"Assessment: Completed quiz with score {score_pct:.0f}%"
            ]
        }
    
    # Present current MCQ
    current_mcq = mcqs[current_index]
    question_num = current_index + 1
    total_questions = len(mcqs)
    
    print(f"\n📝 Question {question_num} of {total_questions}")
    print(f"\n❓ {current_mcq.get('question', 'No question text')}")
    
    options = current_mcq.get("options", [])
    print("\n   Options:")
    for i, option in enumerate(options):
        print(f"      {chr(65+i)}. {option}")
    
    # In test mode, simulate student answer
    # In production (Streamlit), this would wait for real input
    simulated_answer = simulate_student_answer(
        mcq=current_mcq,
        learner_profile=learner_profile,
        question_num=question_num
    )
    
    print(f"\n🧪 [TEST MODE] Student selected: {chr(65 + simulated_answer)}")
    
    # Check if correct
    correct_answer = current_mcq.get("correct_answer", 0)
    is_correct = simulated_answer == correct_answer
    
    if is_correct:
        print(f"   ✅ Correct!")
    else:
        print(f"   ❌ Incorrect. Correct answer was: {chr(65 + correct_answer)}")
    
    # Update answers list
    new_answers = student_answers + [simulated_answer]
    
    # Move to next question
    new_index = current_index + 1
    
    # Check if this was the last question
    if new_index >= len(mcqs):
        # Calculate final results now
        correct_count = 0
        for i, answer in enumerate(new_answers):
            if i < len(mcqs) and answer == mcqs[i].get("correct_answer", -1):
                correct_count += 1
        
        score_pct = (correct_count / len(mcqs)) * 100 if mcqs else 0
        
        print(f"\n📊 Final Quiz Results:")
        print(f"   Correct: {correct_count}/{len(mcqs)}")
        print(f"   Score: {score_pct:.0f}%")
        
        # Create assessment results
        final_assessment = {
            "total_questions": len(mcqs),
            "correct_answers": correct_count,
            "score_percentage": score_pct,
            "feedback": "",  # Summary node will generate
            "recommended_next_level": None  # Summary node will decide
        }
        
        print(f"\n   Progress: {new_index}/{len(mcqs)} questions answered")
        
        print("\n" + "="*60)
        print("🎯 ASSESSMENT COMPLETE: Ready for summary")
        print("="*60 + "\n")
        
        return {
            "student_answers": new_answers,
            "current_mcq_index": new_index,
            "assessment": final_assessment,
            "next_action": "summarize",
            "messages": state.get("messages", []) + [
                f"Assessment: Answered Q{question_num} - {'Correct' if is_correct else 'Incorrect'}",
                f"Assessment: Quiz complete! Score: {correct_count}/{len(mcqs)} ({score_pct:.0f}%)"
            ]
        }
    
    # More questions remaining
    print(f"\n   Progress: {new_index}/{len(mcqs)} questions answered")
    
    print("\n" + "="*60)
    print(f"🎯 QUESTION {question_num} COMPLETE: Next = 'next_mcq'")
    print("="*60 + "\n")
    
    return {
        "student_answers": new_answers,
        "current_mcq_index": new_index,
        "next_action": "next_mcq",
        "messages": state.get("messages", []) + [
            f"Assessment: Answered Q{question_num} - {'Correct' if is_correct else 'Incorrect'}"
        ]
    }


def simulate_student_answer(
    mcq: Dict[str, Any],
    learner_profile: Dict[str, Any],
    question_num: int
) -> int:
    """
    Simulates a student's answer for testing purposes.
    
    The simulation considers:
    - Student's calibre (High IQ students more likely correct)
    - Some randomness for realistic testing
    - Ensures valid option index
    
    Args:
        mcq: The MCQ question
        learner_profile: Student's profile
        question_num: Question number (for variety)
        
    Returns:
        Index of selected option (0-based)
    """
    import random
    
    calibre = learner_profile.get("calibre", "Medium")
    correct_answer = mcq.get("correct_answer", 0)
    num_options = len(mcq.get("options", []))
    
    if num_options == 0:
        return 0
    
    # Probability of correct answer based on calibre
    if calibre == "High IQ":
        correct_prob = 0.85  # 85% chance of correct
    elif calibre == "Medium":
        correct_prob = 0.65  # 65% chance of correct
    else:  # Dull
        correct_prob = 0.45  # 45% chance of correct
    
    # Add some variation per question
    # (so not every test run is identical)
    random.seed(question_num * 42 + hash(mcq.get("question", "")[:20]) % 100)
    
    if random.random() < correct_prob:
        return correct_answer
    else:
        # Pick a wrong answer
        wrong_options = [i for i in range(num_options) if i != correct_answer]
        if wrong_options:
            return random.choice(wrong_options)
        return 0


def route_after_assessment(state: TeachingState) -> str:
    """
    Routing function for after assessment node.
    
    Determines whether to:
    - Continue to next MCQ question
    - Move to summary (all questions answered)
    
    Args:
        state: Current teaching state
        
    Returns:
        "assessment" to continue quiz, or "summary" to finish
    """
    next_action = state.get("next_action", "")
    current_index = state.get("current_mcq_index", 0)
    mcqs = state.get("mcqs", [])
    
    if next_action == "summarize" or current_index >= len(mcqs):
        return "summary"
    else:
        return "assessment"  # Loop back for next question


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 15: Summary Node
# ═══════════════════════════════════════════════════════════════════════════════

def summary_node(state: TeachingState) -> Dict[str, Any]:
    """
    Step 15: Summary Node
    
    Generates a comprehensive summary of the teaching session including:
    1. Final assessment score and feedback
    2. Personalized performance analysis
    3. Recommendation for next level
    4. Session statistics
    
    This is the FINAL node in the teaching workflow.
    
    NO LLM REQUIRED - Uses rule-based logic for recommendations.
    (Could optionally use LLM for personalized feedback messages)
    
    Args:
        state: Current teaching state with assessment results
        
    Returns:
        Dict with:
        - assessment: Updated with feedback and recommendations
        - next_action: "complete" (session finished)
        - messages: Final summary message
        
    State Fields Used:
        - assessment: Score and correct answers
        - learner_profile: Current level and calibre
        - concepts: What was taught
        - interactions: Teaching history
        - mcqs: Quiz questions
        - student_answers: Quiz responses
    """
    
    print("\n" + "="*60)
    print("SUMMARY NODE - Generating Session Summary")
    print("="*60)
    
    # Extract relevant state
    assessment = state.get("assessment", {})
    learner_profile = state.get("learner_profile", {})
    concepts = state.get("concepts", [])
    interactions = state.get("interactions", [])
    mcqs = state.get("mcqs", [])
    student_answers = state.get("student_answers", [])
    simulation_name = state.get("simulation_name", "the simulation")
    
    # Get current level and score
    current_level = learner_profile.get("level", "Beginner")
    current_calibre = learner_profile.get("calibre", "Medium")
    score_pct = assessment.get("score_percentage", 0)
    correct_count = assessment.get("correct_answers", 0)
    total_questions = assessment.get("total_questions", 0)
    
    print(f"\n📊 Session Statistics:")
    print(f"   Simulation: {simulation_name}")
    print(f"   Student Level: {current_level}")
    print(f"   Student Calibre: {current_calibre}")
    print(f"   Concepts Taught: {len(concepts)}")
    print(f"   Total Interactions: {len(interactions)}")
    print(f"   Quiz Score: {correct_count}/{total_questions} ({score_pct:.0f}%)")
    
    # Generate personalized feedback based on score
    feedback = generate_feedback_message(
        score_pct=score_pct,
        current_level=current_level,
        concepts=concepts,
        mcqs=mcqs,
        student_answers=student_answers
    )
    
    print(f"\n💬 Feedback:")
    print(f"   {feedback[:100]}..." if len(feedback) > 100 else f"   {feedback}")
    
    # Determine recommended next level
    recommended_level = determine_next_level(
        score_pct=score_pct,
        current_level=current_level,
        current_calibre=current_calibre
    )
    
    print(f"\n🎯 Level Recommendation:")
    print(f"   Current: {current_level}")
    print(f"   Recommended: {recommended_level}")
    
    # Calculate teaching efficiency metrics
    teaching_stats = calculate_teaching_stats(interactions, concepts)
    
    print(f"\n📈 Teaching Metrics:")
    print(f"   Avg interactions per concept: {teaching_stats['avg_interactions_per_concept']:.1f}")
    print(f"   Re-explanation rate: {teaching_stats['re_explain_rate']:.0%}")
    print(f"   Understanding rate: {teaching_stats['understanding_rate']:.0%}")
    
    # Build final assessment with all details
    final_assessment = {
        "total_questions": total_questions,
        "correct_answers": correct_count,
        "score_percentage": score_pct,
        "feedback": feedback,
        "recommended_next_level": recommended_level,
        "teaching_stats": teaching_stats
    }
    
    # Generate summary message
    summary_message = build_summary_message(
        simulation_name=simulation_name,
        concepts=concepts,
        score_pct=score_pct,
        recommended_level=recommended_level,
        current_level=current_level
    )
    
    print("\n" + "="*60)
    print("🎉 SESSION COMPLETE!")
    print("="*60)
    print(f"\n{summary_message}")
    print("\n" + "="*60 + "\n")
    
    return {
        "assessment": final_assessment,
        "next_action": "complete",
        "messages": state.get("messages", []) + [
            f"Summary: Session complete! Score: {score_pct:.0f}%, Recommended: {recommended_level}"
        ]
    }


def generate_feedback_message(
    score_pct: float,
    current_level: str,
    concepts: List[Dict[str, Any]],
    mcqs: List[Dict[str, Any]],
    student_answers: List[int]
) -> str:
    """
    Generates personalized feedback based on quiz performance.
    
    Args:
        score_pct: Score percentage
        current_level: Student's current level
        concepts: Concepts that were taught
        mcqs: Quiz questions
        student_answers: Student's answers
        
    Returns:
        Personalized feedback string
    """
    
    # Identify which questions were wrong
    wrong_questions = []
    for i, (answer, mcq) in enumerate(zip(student_answers, mcqs)):
        if answer != mcq.get("correct_answer", -1):
            wrong_questions.append(mcq.get("question", f"Question {i+1}")[:50])
    
    # Generate feedback based on score ranges
    if score_pct >= 90:
        base_feedback = "🌟 Excellent work! You've demonstrated a strong understanding of all the concepts."
        if current_level == "Beginner":
            base_feedback += " You're ready to advance to more challenging material!"
        elif current_level == "Intermediate":
            base_feedback += " You're well prepared for advanced topics!"
        else:
            base_feedback += " You've mastered this material at the highest level!"
            
    elif score_pct >= 70:
        base_feedback = "👍 Good job! You understand most of the concepts well."
        if wrong_questions:
            base_feedback += f" You might want to review: {wrong_questions[0]}..."
            
    elif score_pct >= 50:
        base_feedback = "📚 You're making progress, but some concepts need more practice."
        if wrong_questions:
            base_feedback += f" Focus on reviewing these areas for improvement."
            
    else:
        base_feedback = "💪 Keep practicing! The concepts take time to master."
        base_feedback += " Consider revisiting the simulation and paying close attention to how parameters affect the results."
    
    return base_feedback


def determine_next_level(
    score_pct: float,
    current_level: str,
    current_calibre: str
) -> str:
    """
    Determines the recommended next level based on performance.
    
    Uses a combination of score and current level to make recommendations.
    
    Args:
        score_pct: Quiz score percentage
        current_level: Current student level
        current_calibre: Student's learning calibre
        
    Returns:
        Recommended next level
    """
    
    # Level progression thresholds
    # Higher calibre students need higher scores to advance
    if current_calibre == "High IQ":
        advance_threshold = 85
        stay_threshold = 60
    elif current_calibre == "Medium":
        advance_threshold = 75
        stay_threshold = 50
    else:  # Dull
        advance_threshold = 65
        stay_threshold = 40
    
    # Determine recommendation
    if score_pct >= advance_threshold:
        # Ready to advance
        if current_level == "Beginner":
            return "Intermediate"
        elif current_level == "Intermediate":
            return "Advanced"
        else:
            return "Advanced"  # Already at max
            
    elif score_pct >= stay_threshold:
        # Stay at current level
        return current_level
        
    else:
        # Consider going back a level
        if current_level == "Advanced":
            return "Intermediate"
        elif current_level == "Intermediate":
            return "Beginner"
        else:
            return "Beginner"  # Already at min


def calculate_teaching_stats(
    interactions: List[Dict[str, Any]],
    concepts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculates teaching efficiency statistics.
    
    Args:
        interactions: List of teaching interactions
        concepts: List of concepts taught
        
    Returns:
        Dictionary with teaching statistics
    """
    
    num_interactions = len(interactions)
    num_concepts = len(concepts) if concepts else 1
    
    # Count interactions where student was confused
    confused_count = 0
    understood_count = 0
    
    for interaction in interactions:
        understanding = interaction.get("understanding_status", {})
        if isinstance(understanding, dict):
            if understanding.get("is_confused", False):
                confused_count += 1
            else:
                understood_count += 1
    
    total_checked = confused_count + understood_count
    
    return {
        "total_interactions": num_interactions,
        "concepts_taught": num_concepts,
        "avg_interactions_per_concept": num_interactions / num_concepts if num_concepts > 0 else 0,
        "re_explain_rate": confused_count / total_checked if total_checked > 0 else 0,
        "understanding_rate": understood_count / total_checked if total_checked > 0 else 0
    }


def build_summary_message(
    simulation_name: str,
    concepts: List[Dict[str, Any]],
    score_pct: float,
    recommended_level: str,
    current_level: str
) -> str:
    """
    Builds a comprehensive summary message for the session.
    
    Args:
        simulation_name: Name of the simulation
        concepts: Concepts that were taught
        score_pct: Quiz score percentage
        recommended_level: Recommended next level
        current_level: Current student level
        
    Returns:
        Formatted summary message
    """
    
    concept_names = [c.get("name", "Unknown") for c in concepts]
    concepts_str = ", ".join(concept_names) if concept_names else "various concepts"
    
    # Determine level change message
    if recommended_level == current_level:
        level_msg = f"Continue practicing at the {current_level} level."
    elif recommended_level > current_level:  # String comparison works for our levels
        level_msg = f"🎉 Congratulations! You're ready to advance to {recommended_level}!"
    else:
        level_msg = f"Consider reviewing at the {recommended_level} level for stronger foundations."
    
    summary = f"""
╔══════════════════════════════════════════════════════════╗
║                    SESSION SUMMARY                       ║
╠══════════════════════════════════════════════════════════╣
║  Simulation: {simulation_name[:40]:<40}  ║
║  Concepts Learned: {len(concepts):<35}  ║
║  Quiz Score: {score_pct:.0f}%{' ' * 40}║
║  Current Level: {current_level:<38}  ║
║  Recommended: {recommended_level:<41}  ║
╠══════════════════════════════════════════════════════════╣
║  {level_msg[:54]:<54}  ║
╚══════════════════════════════════════════════════════════╝
"""
    
    return summary
