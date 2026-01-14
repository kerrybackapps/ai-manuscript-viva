"""
Update ElevenLabs Agent with new system prompt
"""
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

# Your agent ID from .ENV file
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')
API_KEY = os.getenv('ELEVENLABS_API_KEY')

# New system prompt with "speak first" instruction
NEW_PROMPT = """You are an oral examiner conducting a viva voce examination based on a student's submitted manuscript.

IMPORTANT: When the call connects, YOU MUST SPEAK FIRST. Immediately greet the student with: "Hello! I've read your manuscript carefully and I'm ready to begin your oral examination. Let's start with the first question."

EXAMINATION GUIDELINES:
- YOU speak first - greet them and ask the first question immediately
- Ask ONE question at a time
- Reference specific parts of their manuscript
- Ask follow-up questions based on their answers
- If they ask you to repeat, repeat the question verbatim
- Allow adequate think time (pause after they finish answering before asking the next question)
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

- When finished with all questions, say: "Thank you for your responses. That completes the examination. EXAMINATION_COMPLETE"

Be professional, probing, and fair. Your goal is to assess genuine understanding of their own work. Remember: YOU must speak first when the call starts!"""

def update_agent():
    """Update the ElevenLabs agent with new prompt"""
    client = ElevenLabs(api_key=API_KEY)

    print(f"Updating agent: {AGENT_ID}")
    print(f"API Key: {API_KEY[:10]}...")

    try:
        # Create config dict with updated prompt (SDK will handle conversion)
        config_dict = {
            "agent": {
                "prompt": {
                    "prompt": NEW_PROMPT
                }
            }
        }

        # Update the agent
        response = client.conversational_ai.agents.update(
            agent_id=AGENT_ID,
            conversation_config=config_dict
        )

        print("\nAgent updated successfully!")
        print(f"Agent ID: {AGENT_ID}")
        print("\nNew prompt preview:")
        print(NEW_PROMPT[:200] + "...")

    except Exception as e:
        print(f"\nError updating agent: {e}")
        print("\nIf this doesn't work, you may need to:")
        print("1. Go to https://elevenlabs.io/app/conversational-ai")
        print("2. Find your agent")
        print("3. Update the 'System Prompt' or 'Instructions' field manually")
        print(f"\nAgent ID: {AGENT_ID}")

if __name__ == '__main__':
    if not AGENT_ID or not API_KEY:
        print("Error: ELEVENLABS_AGENT_ID and ELEVENLABS_API_KEY must be set in .env file")
    else:
        update_agent()
