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

# New system prompt with "speak first" instruction and time management
NEW_PROMPT = """You are an oral examiner conducting a viva voce examination based on a student's submitted manuscript.

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

def update_agent():
    """Update the ElevenLabs agent with new prompt and webhook"""
    client = ElevenLabs(api_key=API_KEY)

    # Get webhook URL from environment or prompt user
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        print("\nNo WEBHOOK_URL found in .env file.")
        print("Example: https://your-app.koyeb.app/webhook/elevenlabs")
        webhook_url = input("Enter your webhook URL (or press Enter to skip): ").strip()

    print(f"\nUpdating agent: {AGENT_ID}")
    print(f"API Key: {API_KEY[:10]}...")
    if webhook_url:
        print(f"Webhook URL: {webhook_url}")

    try:
        # Create config dict with updated prompt
        config_dict = {
            "agent": {
                "prompt": {
                    "prompt": NEW_PROMPT
                }
            }
        }

        # Add webhook URL if provided
        if webhook_url:
            config_dict["webhook"] = {
                "url": webhook_url,
                "events": ["conversation.ended"]  # Trigger on conversation end
            }

        # Update the agent
        response = client.conversational_ai.agents.update(
            agent_id=AGENT_ID,
            conversation_config=config_dict
        )

        print("\n[SUCCESS] Agent updated successfully!")
        print(f"  Agent ID: {AGENT_ID}")
        print("\nNew prompt preview:")
        print(NEW_PROMPT[:200] + "...")
        if webhook_url:
            print(f"\n[SUCCESS] Webhook configured: {webhook_url}")
            print("  Event: conversation.ended")

    except Exception as e:
        print(f"\n[ERROR] Error updating agent: {e}")
        print("\nIf this doesn't work, you may need to:")
        print("1. Go to https://elevenlabs.io/app/conversational-ai")
        print("2. Find your agent")
        print("3. Update the 'System Prompt' or 'Instructions' field manually")
        if webhook_url:
            print("4. Add webhook URL in Settings > Webhooks section")
        print(f"\nAgent ID: {AGENT_ID}")

if __name__ == '__main__':
    if not AGENT_ID or not API_KEY:
        print("Error: ELEVENLABS_AGENT_ID and ELEVENLABS_API_KEY must be set in .env file")
    else:
        update_agent()
