"""
Multi-Model Grading Council
Uses Claude, GPT, and Gemini to grade exam transcripts with deliberation
"""
import os
import json
from typing import Dict, List, Tuple
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class GradingCouncil:
    """Manages the three-model grading council with deliberation rounds"""

    def __init__(self):
        # Support multiple Anthropic key name variations
        anthropic_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_KEY') or os.getenv('CLAUDE')
        if not anthropic_key:
            raise ValueError("ANTHROPIC_KEY is required. Add to .env file.")
        self.claude_client = Anthropic(api_key=anthropic_key)

        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("OPENAI_API_KEY is required. Add to .env file.")
        self.openai_client = OpenAI(api_key=openai_key)

        # Gemini - support multiple key names
        google_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_KEY')
        if not google_key:
            raise ValueError("GEMINI_KEY is required. Add to .env file.")
        if not genai:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")

        genai.configure(api_key=google_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # All three models are required
        self.available_models = ['claude', 'gpt', 'gemini']

    def get_grading_prompt(self, transcript: str, rubric: str) -> str:
        """Generate the grading prompt"""
        return f"""You are an expert grader evaluating an oral exam transcript.

GRADING RUBRIC:
{rubric}

EXAM TRANSCRIPT:
{transcript}

INSTRUCTIONS:
Evaluate the student's performance based on the rubric. Provide:
1. A score for each rubric category (scale provided in rubric)
2. Brief justification for each score (2-3 sentences)
3. Overall assessment of understanding

Format your response as JSON:
{{
    "scores": {{
        "category_name": {{
            "score": X,
            "justification": "..."
        }}
    }},
    "overall_score": X.X,
    "overall_assessment": "Brief summary of student's performance"
}}

Be fair but rigorous. Focus on demonstrated understanding, not presentation style.
"""

    def get_deliberation_prompt(self, transcript: str, rubric: str, all_grades: Dict) -> str:
        """Generate prompt for deliberation round"""
        return f"""You are participating in a grading council deliberation.

EXAM TRANSCRIPT:
{transcript}

GRADING RUBRIC:
{rubric}

OTHER GRADERS' ASSESSMENTS:
{json.dumps(all_grades, indent=2)}

INSTRUCTIONS:
Review the other graders' scores and justifications. Consider their perspectives and:
1. Identify where you agree or disagree
2. Adjust your scores if you find their reasoning compelling
3. Provide your final grades using the same JSON format

Your goal is consensus while maintaining rigorous standards.

Format your response as JSON:
{{
    "scores": {{
        "category_name": {{
            "score": X,
            "justification": "...",
            "deliberation_notes": "How other graders influenced this score"
        }}
    }},
    "overall_score": X.X,
    "overall_assessment": "Final summary"
}}
"""

    def grade_with_claude(self, prompt: str) -> Dict:
        """Get grade from Claude"""
        try:
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.content[0].text
            # Extract JSON from markdown code blocks if present
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            return json.loads(result)
        except Exception as e:
            print(f"Claude grading error: {e}")
            return {"error": str(e), "model": "Claude"}

    def grade_with_gpt(self, prompt: str) -> Dict:
        """Get grade from GPT"""
        try:
            response = self.openai_client.chat.completions.create(
                model="o1",
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content
            # Extract JSON from markdown code blocks if present
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            return json.loads(result)
        except Exception as e:
            print(f"GPT grading error: {e}")
            return {"error": str(e), "model": "GPT"}

    def grade_with_gemini(self, prompt: str) -> Dict:
        """Get grade from Gemini"""
        try:
            response = self.gemini_model.generate_content(prompt)
            result = response.text
            # Extract JSON from markdown code blocks if present
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            return json.loads(result)
        except Exception as e:
            print(f"Gemini grading error: {e}")
            return {"error": str(e), "model": "Gemini"}

    def conduct_grading(self, transcript: str, rubric: str, deliberation_rounds: int = 1) -> Dict:
        """
        Conduct multi-model grading with deliberation

        Args:
            transcript: The exam transcript to grade
            rubric: The grading rubric
            deliberation_rounds: Number of deliberation rounds (default 1)

        Returns:
            Dictionary containing all grades and convergence metrics
        """
        print("\n" + "="*60)
        print("GRADING COUNCIL SESSION")
        print(f"Available models: {', '.join(self.available_models)}")
        print("="*60 + "\n")

        if len(self.available_models) < 2:
            print("ERROR: Need at least 2 models for grading council")
            return {"error": "Insufficient models available"}

        # Round 1: Initial independent grading
        print("Round 1: Independent Grading...")
        initial_prompt = self.get_grading_prompt(transcript, rubric)

        round_1_grades = {}

        if 'claude' in self.available_models:
            print("  - Claude grading...")
            round_1_grades['claude'] = self.grade_with_claude(initial_prompt)

        if 'gpt' in self.available_models:
            print("  - GPT grading...")
            round_1_grades['gpt'] = self.grade_with_gpt(initial_prompt)

        if 'gemini' in self.available_models:
            print("  - Gemini grading...")
            round_1_grades['gemini'] = self.grade_with_gemini(initial_prompt)

        results = {
            "round_1": round_1_grades
        }

        # Deliberation rounds
        for round_num in range(2, deliberation_rounds + 2):
            print(f"\nRound {round_num}: Deliberation...")

            # Get previous round results
            prev_round = results[f"round_{round_num - 1}"]
            current_round_grades = {}

            # Each model reviews others' grades
            for model in self.available_models:
                # Get other models' grades for this model to review
                other_grades = {k: v for k, v in prev_round.items() if k != model}

                deliberation_prompt = self.get_deliberation_prompt(
                    transcript, rubric, other_grades
                )

                print(f"  - {model.upper()} deliberating...")

                if model == 'claude':
                    current_round_grades['claude'] = self.grade_with_claude(deliberation_prompt)
                elif model == 'gpt':
                    current_round_grades['gpt'] = self.grade_with_gpt(deliberation_prompt)
                elif model == 'gemini':
                    current_round_grades['gemini'] = self.grade_with_gemini(deliberation_prompt)

            results[f"round_{round_num}"] = current_round_grades

        # Calculate convergence metrics
        final_round = results[f"round_{deliberation_rounds + 1}"]
        convergence = self.calculate_convergence(final_round)

        results["convergence_metrics"] = convergence
        results["final_grades"] = final_round

        return results

    def calculate_convergence(self, grades: Dict) -> Dict:
        """Calculate agreement metrics between the available models"""
        try:
            # Extract scores from all available models
            scores = []
            for model, grade_data in grades.items():
                if isinstance(grade_data, dict) and "overall_score" in grade_data:
                    scores.append(grade_data["overall_score"])

            if len(scores) < 2:
                return {"error": "Need at least 2 scores for convergence"}

            avg_score = sum(scores) / len(scores)

            # Check within-1-point agreement (all pairs must agree)
            within_1_point = True
            for i in range(len(scores)):
                for j in range(i + 1, len(scores)):
                    if abs(scores[i] - scores[j]) > 1.0:
                        within_1_point = False
                        break
                if not within_1_point:
                    break

            # Standard deviation
            variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
            std_dev = variance ** 0.5

            return {
                "average_score": round(avg_score, 2),
                "within_1_point_agreement": within_1_point,
                "standard_deviation": round(std_dev, 3),
                "score_range": {
                    "min": min(scores),
                    "max": max(scores)
                },
                "num_models": len(scores)
            }
        except Exception as e:
            return {"error": str(e)}

    def print_results(self, results: Dict):
        """Pretty print the grading results"""
        print("\n" + "="*60)
        print("GRADING RESULTS")
        print("="*60 + "\n")

        # Show final grades
        final = results["final_grades"]

        print("FINAL SCORES:")
        print("-" * 40)
        for model, grade in final.items():
            if "error" not in grade:
                print(f"\n{model.upper()}: {grade.get('overall_score', 'N/A')}")
                print(f"Assessment: {grade.get('overall_assessment', 'N/A')[:100]}...")

        # Show convergence
        print("\n" + "-" * 40)
        print("CONVERGENCE METRICS:")
        print("-" * 40)
        conv = results["convergence_metrics"]
        print(f"Average Score: {conv.get('average_score', 'N/A')}")
        print(f"Within-1-Point Agreement: {conv.get('within_1_point_agreement', 'N/A')}")
        print(f"Standard Deviation: {conv.get('standard_deviation', 'N/A')}")
        print(f"Score Range: {conv.get('score_range', {}).get('min', 'N/A')} - {conv.get('score_range', {}).get('max', 'N/A')}")
        print()
