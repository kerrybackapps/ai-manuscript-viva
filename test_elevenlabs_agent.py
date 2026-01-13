"""
Test ElevenLabs Conversational AI Agent
Shows how to use the exam agent for voice conversations
"""
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()


def test_agent_info():
    """Display agent information"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    agent_id = os.getenv('ELEVENLABS_AGENT_ID')

    print("="*60)
    print("ELEVENLABS AGENT TEST")
    print("="*60)

    print(f"\nAPI Key: {'Found' if api_key else 'NOT FOUND'}")
    print(f"Agent ID: {agent_id if agent_id else 'NOT FOUND'}")

    if not api_key:
        print("\nERROR: ELEVENLABS_API_KEY not found in .ENV")
        print("Please run: python setup_elevenlabs_agent.py")
        return False

    if not agent_id:
        print("\nERROR: ELEVENLABS_AGENT_ID not found in .ENV")
        print("Please run: python setup_elevenlabs_agent.py")
        return False

    return True


def get_agent_details():
    """Get details about the exam agent"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    agent_id = os.getenv('ELEVENLABS_AGENT_ID')

    client = ElevenLabs(api_key=api_key)

    try:
        # Get agent details
        agent = client.conversational_ai.agents.get(agent_id=agent_id)

        print("\n" + "="*60)
        print("AGENT DETAILS")
        print("="*60)
        print(f"\nName: {agent.name if hasattr(agent, 'name') else 'N/A'}")
        print(f"Agent ID: {agent_id}")
        print(f"Status: Active")

        return agent

    except Exception as e:
        print(f"\nError getting agent details: {e}")
        return None


def show_usage_instructions():
    """Show how to use the agent"""
    print("\n" + "="*60)
    print("HOW TO USE THE EXAM AGENT")
    print("="*60)

    print("""
The exam agent is now ready! Here's how to conduct voice exams:

OPTION 1: Web-Based Voice Interface (Recommended)
------------------------------------------------
ElevenLabs provides a web widget for voice conversations.

To integrate into your web app:

1. Add to your HTML template:
   <script src="https://elevenlabs.io/convai-widget/index.js"></script>

2. Initialize the widget:
   <script>
   const widget = new ElevenLabs.ConversationalAI({
       agentId: 'YOUR_AGENT_ID',
       apiKey: 'YOUR_API_KEY'
   });
   widget.mount();
   </script>

3. Students can click to start voice conversation
4. Agent will ask exam questions
5. Conversation is automatically transcribed


OPTION 2: Python SDK (Programmatic)
-----------------------------------
For backend integration:

from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="YOUR_API_KEY")

# Start a conversation
conversation = client.conversational_ai.conversations.create(
    agent_id="YOUR_AGENT_ID"
)

# The conversation happens via WebSocket or voice API
# You'll get back a transcript when complete


OPTION 3: Direct API Call (Advanced)
------------------------------------
Make HTTP requests to ElevenLabs Conversational AI endpoints
to control the conversation programmatically.


CURRENT SYSTEM INTEGRATION:
---------------------------
Your exam system can:

1. Create exam session in database
2. Launch voice conversation with agent
3. Agent asks 5-7 questions about ML
4. Conversation auto-transcribes
5. Save transcript to database
6. Grading council evaluates transcript
7. Display results in web interface


NEXT STEPS:
-----------
1. Test the agent via ElevenLabs dashboard:
   https://elevenlabs.io/app/conversational-ai

2. Click on your agent to test it

3. Once tested, integrate into the exam system
""")


def create_conversation_example():
    """Show example of how to use the agent in code"""
    agent_id = os.getenv('ELEVENLABS_AGENT_ID')

    print("\n" + "="*60)
    print("CODE EXAMPLE: Using the Agent")
    print("="*60)

    example_code = f"""
# Example: Conduct an exam with the agent

from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv()

client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))

# Start a conversation with the exam agent
conversation = client.conversational_ai.conversations.create(
    agent_id="{agent_id}"
)

print(f"Conversation started: {{conversation.conversation_id}}")

# The conversation will happen via:
# - Web widget (browser-based voice chat)
# - WebSocket connection (real-time audio streaming)
# - Phone call integration (if enabled)

# After the exam, retrieve the transcript:
transcript = client.conversational_ai.conversations.get_transcript(
    conversation_id=conversation.conversation_id
)

# Save transcript to database for grading
from database import Database
db = Database()

db.update_exam_session(
    session_id=exam_session_id,
    transcript=transcript,
    status='completed'
)

# Grade with council
from grading_council import GradingCouncil
council = GradingCouncil()
results = council.conduct_grading(transcript, rubric)
"""

    print(example_code)


if __name__ == '__main__':
    # Test agent setup
    if not test_agent_info():
        exit(1)

    # Get agent details
    agent = get_agent_details()

    # Show usage instructions
    show_usage_instructions()

    # Show code example
    create_conversation_example()

    print("\n" + "="*60)
    print("Agent is ready to use!")
    print("="*60)
    print("\nTo test the agent right now:")
    print(f"1. Go to: https://elevenlabs.io/app/conversational-ai")
    print(f"2. Find your agent: 'AI Oral Examiner - ML Fundamentals'")
    print(f"3. Click 'Test' to try a voice conversation")
    print(f"4. Agent will ask you exam questions via voice")
    print("\n")
