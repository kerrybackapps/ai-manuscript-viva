"""
AI-Powered Oral Exam System - Proof of Concept Demo

This demo demonstrates:
1. Conducting a text-based oral exam conversation
2. Using a 3-model grading council (Claude, GPT, Gemini)
3. Deliberation rounds for grade convergence
"""
import os
import json
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv
from exam_conversation import ExamConversation
from grading_council import GradingCouncil


def load_file_content(filepath: str) -> str:
    """Load content from a text file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")
        return ""


def save_results(transcript: str, grading_results: Dict, student_name: str):
    """Save exam transcript and grading results"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exam_results_{student_name.replace(' ', '_')}_{timestamp}.json"

    results = {
        "student": student_name,
        "timestamp": timestamp,
        "transcript": transcript,
        "grading_results": grading_results
    }

    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)

    filepath = os.path.join("results", filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {filepath}")
    return filepath


def run_demo_mode():
    """Run with pre-recorded student responses for testing grading council"""
    print("\n" + "="*60)
    print("DEMO MODE - Using Pre-recorded Exam Transcript")
    print("="*60 + "\n")

    # Sample transcript for demonstration
    sample_transcript = """EXAM TRANSCRIPT
Student: Alex Johnson
============================================================

EXAMINER: Let's begin with your project. You built a customer churn prediction model. Can you explain why you chose to use a random forest classifier for this problem?

ALEX JOHNSON: I chose random forest because it handles both numerical and categorical features well, and it's less prone to overfitting compared to a single decision tree. It also gives feature importance scores which helped me understand which factors most influenced churn.

EXAMINER: Good. Now, you mentioned overfitting. How did you actually verify that your model wasn't overfitting to the training data?

ALEX JOHNSON: I used cross-validation with 5 folds and compared the training accuracy to validation accuracy. The training accuracy was about 87% and validation was 82%, so there was some overfitting but not too severe. I also used a holdout test set that I didn't touch during development.

EXAMINER: What evaluation metrics did you use beyond accuracy, and why did you choose those specific metrics?

ALEX JOHNSON: I focused on recall and precision because in customer churn, false negatives are costly - missing a customer who will churn means we lose them. I used F1 score to balance precision and recall, and also looked at the AUC-ROC curve to evaluate performance across different thresholds.

EXAMINER: Interesting. Can you explain a scenario where your model might fail or produce misleading predictions?

ALEX JOHNSON: Umm, if the patterns in customer behavior change suddenly, like during a pandemic or major company policy change, the model would still be predicting based on historical patterns. Also, if there's class imbalance and we have very few examples of churned customers, the model might just predict everyone stays.

EXAMINER: How would you explain your model's predictions to a non-technical business stakeholder who wants to know why a specific customer is predicted to churn?

ALEX JOHNSON: I would use the feature importance from the random forest to show which factors contributed most. For example, I might say "This customer is predicted to churn because they haven't used our service in 30 days, they had 3 support tickets in the last month, and their usage is declining compared to similar customers." I'd avoid technical jargon and focus on actionable insights.

EXAMINER: Thank you. The exam is now complete.
"""

    # Load rubric
    rubric = load_file_content("sample_rubric.txt")

    # Grade with the council
    council = GradingCouncil()
    grading_results = council.conduct_grading(
        transcript=sample_transcript,
        rubric=rubric,
        deliberation_rounds=1
    )

    # Print results
    council.print_results(grading_results)

    # Save results
    save_results(sample_transcript, grading_results, "Alex_Johnson_Demo")


def run_interactive_mode():
    """Run interactive exam with live student"""
    print("\n" + "="*60)
    print("INTERACTIVE MODE - Live Oral Exam")
    print("="*60 + "\n")

    # Get student info
    student_name = input("Enter student name: ").strip()
    if not student_name:
        student_name = "Test Student"

    # Load exam context
    exam_context = load_file_content("sample_exam_context.txt")

    # Conduct exam
    exam = ExamConversation(student_name=student_name, exam_context=exam_context)
    transcript = exam.conduct_exam()

    print("\n" + "="*60)
    print("EXAM COMPLETE - Proceeding to Grading")
    print("="*60)

    # Load rubric
    rubric = load_file_content("sample_rubric.txt")

    # Grade with the council
    council = GradingCouncil()
    grading_results = council.conduct_grading(
        transcript=transcript,
        rubric=rubric,
        deliberation_rounds=1
    )

    # Print results
    council.print_results(grading_results)

    # Save results
    save_results(transcript, grading_results, student_name)


def main():
    """Main entry point for the demo"""
    # Load environment variables
    load_dotenv()

    # Check for API keys (support multiple key name variations)
    anthropic_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_KEY') or os.getenv('CLAUDE')
    openai_key = os.getenv('OPENAI_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_KEY')

    # Need at least 2 models for grading council
    available_count = sum([bool(anthropic_key), bool(openai_key), bool(google_key)])

    if available_count < 2:
        print("ERROR: Need at least 2 API keys for the grading council.")
        print("\nAvailable keys:")
        print(f"  - Anthropic/Claude: {'✓' if anthropic_key else '✗'}")
        print(f"  - OpenAI: {'✓' if openai_key else '✗'}")
        print(f"  - Google Gemini: {'✓' if google_key else '✗ (optional)'}")
        print("\nPlease add API keys to your .env file.")
        print("See .env.example for the required format.")
        return

    if not google_key:
        print("\nNote: Google Gemini key not found. Running with 2-model grading council.")
        print("Available models: Claude Sonnet 4.5, OpenAI o1\n")
    else:
        print(f"\nRunning with 3-model grading council.")
        print("Available models: Claude Sonnet 4.5, OpenAI o1, Gemini 2.0\n")

    print("\n" + "="*60)
    print("AI-POWERED ORAL EXAM SYSTEM - PROOF OF CONCEPT")
    print("="*60)
    print("\nThis demo showcases:")
    print("  1. Structured oral exam conversations")
    print("  2. Multi-model grading council (Claude + GPT + Gemini)")
    print("  3. Deliberation-based grade convergence")
    print("\nBased on: 'Fighting Fire with Fire: Scalable Oral Exams Using AI'")
    print("="*60 + "\n")

    # Choose mode
    print("Select mode:")
    print("  1. Demo Mode (use pre-recorded transcript)")
    print("  2. Interactive Mode (conduct live exam)")
    print()

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        run_demo_mode()
    elif choice == "2":
        run_interactive_mode()
    else:
        print("Invalid choice. Running demo mode...")
        run_demo_mode()


if __name__ == "__main__":
    main()
