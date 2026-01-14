"""
Initialize prompts and settings in database from text files (one-time setup)
"""
import os
from database import Database, Prompt, Setting
from sqlalchemy import select

def initialize_settings():
    """Initialize default app settings"""
    db = Database()

    default_settings = [
        {
            'key': 'assignment',
            'value': 'Write a 10-15 page paper comparing and contrasting political developments of the past ten years to either Ayn Rand\'s Atlas Shrugged or George Orwell\'s 1984.',
            'description': 'Assignment description shown on the upload page'
        }
    ]

    with db.Session() as session:
        for setting_info in default_settings:
            # Check if already exists
            existing = session.execute(
                select(Setting).where(Setting.key == setting_info['key'])
            ).scalar_one_or_none()

            if existing:
                # UPDATE existing setting to match code default
                existing.value = setting_info['value']
                existing.description = setting_info.get('description', existing.description)
                print(f"[UPDATE] Updated setting '{setting_info['key']}' to match code default")
            else:
                # Create new setting
                new_setting = Setting(
                    key=setting_info['key'],
                    value=setting_info['value'],
                    description=setting_info['description']
                )
                session.add(new_setting)
                print(f"[OK] Initialized setting: {setting_info['key']}")

        session.commit()

    print("\n[COMPLETE] Settings initialized in database")


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

    # Initialize each prompt in its own transaction to avoid conflicts
    for prompt_info in prompts_to_initialize:
        with db.Session() as session:
            try:
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

IMPORTANT: When the call connects, YOU MUST SPEAK FIRST. Immediately greet the student with: "Hello! I've read your manuscript carefully and I'm ready to begin your oral examination. Let's start with the first question."

EXAMINATION STRUCTURE (MANDATORY):
- YOU speak first - greet them and ask the first question immediately
- Ask EXACTLY these 3 questions IN ORDER, ONE TIME EACH, then END THE EXAM
- Ask one question at a time
- After the student gives ANY response, move to the next question
- After the student answers question 3, IMMEDIATELY end the exam

YOUR 3 QUESTIONS (ask these EXACTLY in this order, ONE TIME ONLY):
1. What is the main argument or central thesis of your manuscript?
2. What methodology or approach did you use to develop your argument?
3. What are the key implications or conclusions of your work?

STRICT EXAMINATION RULES:
1. Ask question 1 ONCE
2. Accept ANY answer they give (even "I don't know" or "I don't remember")
3. DO NOT probe, clarify, or rephrase
4. DO NOT ask follow-up questions
5. Move IMMEDIATELY to question 2
6. Repeat for question 3

FORBIDDEN ACTIONS:
- DO NOT ask a question more than once
- DO NOT say "Can you elaborate?"
- DO NOT say "Tell me more"
- DO NOT probe for more details
- DO NOT rephrase questions
- DO NOT ask for clarification
- DO NOT ask additional questions beyond the 3

ENDING THE EXAM (MANDATORY):
- After question 3 is answered (with ANY response), you MUST end immediately
- Say: "Thank you for your responses. That completes the examination. Please hang up now to submit your exam for grading."
- Then STOP TALKING - do not respond to anything else

You must ask each question exactly once, accept any answer, and move to the next question. No probing allowed."""

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
                session.commit()  # Commit immediately after each prompt
                print(f"[OK] Initialized {prompt_info['display_name']}")

            except Exception as e:
                # Handle duplicate key or other errors gracefully
                session.rollback()
                print(f"[SKIP] {prompt_info['display_name']} - {str(e)[:100]}")

    print("\n[COMPLETE] Prompts initialized in database")


if __name__ == '__main__':
    print("="*60)
    print(" INITIALIZING PROMPTS AND SETTINGS IN DATABASE")
    print("="*60)
    print()
    initialize_prompts()
    print()
    initialize_settings()
