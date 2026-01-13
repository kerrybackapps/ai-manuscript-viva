"""
Initialize prompts in database from text files (one-time setup)
"""
import os
from database import Database, Prompt
from sqlalchemy import select

def initialize_prompts():
    """Load prompts from text files into database"""

    db = Database()

    prompts_to_initialize = [
        {
            'name': 'manuscript_analysis',
            'display_name': 'Manuscript Analysis',
            'description': 'Claude prompt for analyzing manuscripts before oral exam',
            'category': 'prompt',
            'file': 'rubric_manuscript.txt'  # Temporary - will create proper prompt file
        },
        {
            'name': 'examiner_agent',
            'display_name': 'Examiner Agent',
            'description': 'ElevenLabs agent prompt for conducting oral exams',
            'category': 'prompt',
            'file': None  # Will create default
        },
        {
            'name': 'rubric_manuscript',
            'display_name': 'Manuscript Grading Rubric',
            'description': 'Rubric for grading manuscript quality',
            'category': 'rubric',
            'file': 'rubric_manuscript.txt'
        },
        {
            'name': 'rubric_oral_exam',
            'display_name': 'Oral Exam Grading Rubric',
            'description': 'Rubric for grading oral examination performance',
            'category': 'rubric',
            'file': 'rubric_oral_exam.txt'
        }
    ]

    with db.Session() as session:
        for prompt_info in prompts_to_initialize:
            # Check if already exists
            existing = session.execute(
                select(Prompt).where(Prompt.name == prompt_info['name'])
            ).scalar_one_or_none()

            if existing:
                print(f"[SKIP] {prompt_info['display_name']} already exists")
                continue

            # Read content from file if it exists
            content = ""
            if prompt_info['file'] and os.path.exists(prompt_info['file']):
                with open(prompt_info['file'], 'r', encoding='utf-8') as f:
                    content = f.read()
            elif prompt_info['name'] == 'examiner_agent':
                # Default examiner agent prompt
                content = """You are an oral examiner conducting a viva voce examination based on a student's submitted manuscript.

EXAMINATION GUIDELINES:
- Ask ONE question at a time
- Reference specific parts of their manuscript
- Ask follow-up questions based on their answers
- If they ask you to repeat, repeat the question verbatim
- Allow adequate think time
- Conduct 10-12 questions total across 4 categories:

  1. CONTENT UNDERSTANDING (3-4 questions)
     - Test comprehension of what they wrote
     - Ask about specific claims or arguments
     - Probe deeper into key concepts

  2. REASONING & CHOICES (3-4 questions)
     - Why did you take this approach?
     - How did you arrive at this conclusion?
     - What evidence supports your position?

  3. ALTERNATIVES CONSIDERED (2-3 questions)
     - What other approaches did you consider?
     - What are the trade-offs?
     - How does this compare to alternative methods?

  4. DEPTH & LIMITATIONS (2-3 questions)
     - What are the limitations of your work?
     - What assumptions did you make?
     - What would you do differently?

- End with "EXAMINATION_COMPLETE" when done

Be professional, probing, and fair. Your goal is to assess genuine understanding of their own work."""

            # Create new prompt
            new_prompt = Prompt(
                name=prompt_info['name'],
                display_name=prompt_info['display_name'],
                description=prompt_info['description'],
                content=content,
                category=prompt_info['category'],
                version=1
            )

            session.add(new_prompt)
            print(f"[OK] Initialized {prompt_info['display_name']}")

        session.commit()

    print("\n[COMPLETE] Prompts initialized in database")


if __name__ == '__main__':
    print("="*60)
    print(" INITIALIZING PROMPTS IN DATABASE")
    print("="*60)
    print()
    initialize_prompts()
