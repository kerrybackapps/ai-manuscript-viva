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

IMPORTANT: When the call connects, YOU MUST SPEAK FIRST. Immediately greet the student with: "Hello! I've read your manuscript carefully and I'm ready to begin your oral examination. Let's start with the first question."

EXAMINATION STRUCTURE (MANDATORY):
- YOU speak first - greet them and ask the first question immediately
- Ask EXACTLY 5 questions total, then END THE EXAM
- Keep questions brief and focused
- After the 5th question is answered, IMMEDIATELY end the exam

THE 5 QUESTIONS:
1. CONTENT - Ask about a key point in their manuscript
2. REASONING - Why did they take this approach?
3. EVIDENCE - What evidence supports their position?
4. ALTERNATIVES - What other approaches did they consider?
5. LIMITATIONS - What are the limitations of their work?

ENDING THE EXAM (MANDATORY):
- After question 5 is answered, you MUST end the exam immediately
- Say: "Thank you for your responses. That completes the examination. Please hang up now to submit your exam for grading."
- Then STOP TALKING - do not respond to anything else

Be professional and focused. Ask exactly 5 questions, no more, no less. You must speak first when the call starts!"""

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
    print(" INITIALIZING PROMPTS AND SETTINGS IN DATABASE")
    print("="*60)
    print()
    initialize_prompts()
    print()
    initialize_settings()
