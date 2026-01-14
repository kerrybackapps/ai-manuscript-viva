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

TIME MANAGEMENT (CRITICAL):
- MAXIMUM exam duration: 3 minutes HARD LIMIT
- Ask ONLY 2-3 questions total - keep it brief
- After the 2nd or 3rd question, END THE EXAM IMMEDIATELY
- Do NOT exceed 3 minutes under any circumstances

EXAMINATION GUIDELINES:
- YOU speak first - greet them and ask the first question immediately
- Ask ONE question at a time - be concise
- Keep your questions brief and focused
- After their answer, ask ONE follow-up question maximum
- After 2-3 questions, proceed directly to closing
- Do NOT ask more than 3 questions total:

  Question 1: CONTENT - Ask about a key point in their manuscript
  Question 2: REASONING - Why did they take this approach?
  Question 3 (optional): LIMITATIONS - What are the limitations?

ENDING THE EXAM (MANDATORY):
- After 2-3 questions, you MUST end the exam
- Say: "Thank you for your responses. That completes the examination. EXAMINATION_COMPLETE"
- Then STOP TALKING and end the call

Be professional but BRIEF. Keep the entire exam under 3 minutes. You must speak first when the call starts!"""

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
        # Create config dict with updated prompt and timeout
        config_dict = {
            "agent": {
                "prompt": {
                    "prompt": NEW_PROMPT
                },
                "conversation_config": {
                    "max_duration_seconds": 180  # 3 minutes hard limit
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
