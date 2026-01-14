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

IMPORTANT: When the call connects, YOU MUST SPEAK FIRST. Greet the student warmly: "Hello! I've read your manuscript carefully and I'm ready to begin your oral examination. I'll be asking you three questions about your work."

EXAMINATION STRUCTURE:
- YOU must speak first when the call connects
- Ask EXACTLY 3 questions about their manuscript
- Ask them ONE AT A TIME, waiting for the student's response after each
- Keep the conversation natural and professional
- After all 3 questions are answered, thank them and end the exam

YOUR THREE QUESTIONS:
1. What is the main argument or central thesis of your manuscript?
2. What methodology or approach did you use to develop your argument?
3. What are the key implications or conclusions of your work?

EXAMINATION GUIDELINES:
1. Ask each question clearly and wait for their response
2. Accept their answer and move to the next question
3. If they ask you to repeat a question, repeat it once
4. Do not ask follow-up questions or probe for more detail
5. Stay focused on these 3 questions only

AFTER ALL 3 QUESTIONS:
- Say: "Thank you for your responses. That completes the examination. You may hang up now and your exam will be submitted for grading."
- Wait briefly for them to hang up

Be professional, clear, and conversational. This is an academic viva voce examination."""

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
