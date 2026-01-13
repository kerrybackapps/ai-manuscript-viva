"""
ElevenLabs Conversational AI Agent Setup
Creates an exam agent for conducting oral exams with voice
"""
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv()

def create_exam_agent():
    """Create a conversational AI agent for oral exams"""

    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY not found in .ENV file")
        return None

    print("="*60)
    print("ELEVENLABS EXAM AGENT SETUP")
    print("="*60)
    print(f"\nAPI Key found: {api_key[:20]}...")

    # Initialize ElevenLabs client
    client = ElevenLabs(api_key=api_key)

    print("\nCreating conversational AI agent...")

    # Create the exam agent
    try:
        response = client.conversational_ai.agents.create(
            name="AI Oral Examiner - ML Fundamentals",
            conversation_config={
                "agent": {
                    "prompt": {
                        "prompt": """You are an AI examiner conducting an oral exam on machine learning fundamentals.

EXAM GUIDELINES:
- Ask ONE question at a time (never stack multiple questions)
- Wait for the student's complete answer before asking the next question
- If the student asks you to repeat, repeat the question verbatim
- Allow adequate think time - don't rush the student
- Ask 5-7 questions total to assess understanding

QUESTION FOCUS AREAS:
1. Understanding of core ML concepts (supervised learning, overfitting, evaluation metrics)
2. Ability to explain their project decisions and rationale
3. Recognition of limitations and failure modes
4. Application of knowledge to practical scenarios
5. Communication of technical concepts clearly

CONVERSATION FLOW:
- Start by asking about their project
- Follow up with probing questions about their choices
- Ask scenario-based questions to test understanding
- End with "EXAM_COMPLETE" when you have sufficient information

Be patient, encouraging, and professional. Your goal is to assess genuine understanding, not to trick the student."""
                    },
                    "first_message": "Hello! I'm ready to conduct your oral exam on machine learning. Let's begin by discussing your project. Can you tell me about the machine learning project you worked on and what problem you were trying to solve?"
                }
            }
        )

        agent_id = response.agent_id

        print("\n" + "="*60)
        print("SUCCESS! Exam Agent Created")
        print("="*60)
        print(f"\nAgent Name: AI Oral Examiner - ML Fundamentals")
        print(f"Agent ID: {agent_id}")

        # Save agent ID to file
        with open('elevenlabs_agent_id.txt', 'w') as f:
            f.write(agent_id)

        print(f"\nAgent ID saved to: elevenlabs_agent_id.txt")

        # Update .ENV file with agent ID
        print("\nUpdating .ENV file with agent ID...")
        update_env_file(agent_id)

        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\n1. Your exam agent is now created and ready to use")
        print("2. The agent ID has been saved to your .ENV file")
        print("3. You can now conduct voice exams using this agent")
        print("\nTo test the agent, run:")
        print("  python test_elevenlabs_agent.py")
        print("\nTo conduct a full exam, the agent will:")
        print("  - Have voice conversations with students")
        print("  - Ask 5-7 questions about ML concepts")
        print("  - Generate a transcript automatically")
        print("  - End when assessment is complete")

        return agent_id

    except Exception as e:
        print(f"\nERROR creating agent: {e}")
        print("\nTroubleshooting:")
        print("1. Check that your API key has 'Conversational AI' permissions enabled")
        print("2. Verify you have credits available in your ElevenLabs account")
        print("3. Make sure your API key is correct in .ENV file")
        return None


def update_env_file(agent_id):
    """Add agent ID to .ENV file"""
    try:
        # Read existing .ENV file
        env_path = '.ENV'
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
        else:
            lines = []

        # Check if ELEVENLABS_AGENT_ID already exists
        agent_id_exists = False
        for i, line in enumerate(lines):
            if line.startswith('ELEVENLABS_AGENT_ID='):
                lines[i] = f'ELEVENLABS_AGENT_ID={agent_id}\n'
                agent_id_exists = True
                break

        # Add if it doesn't exist
        if not agent_id_exists:
            lines.append(f'ELEVENLABS_AGENT_ID={agent_id}\n')

        # Write back to file
        with open(env_path, 'w') as f:
            f.writelines(lines)

        print(f"Agent ID added to .ENV file: ELEVENLABS_AGENT_ID={agent_id}")

    except Exception as e:
        print(f"Warning: Could not update .ENV file: {e}")
        print(f"Please manually add: ELEVENLABS_AGENT_ID={agent_id}")


def list_existing_agents():
    """List all existing conversational AI agents"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY not found")
        return

    try:
        client = ElevenLabs(api_key=api_key)

        print("\n" + "="*60)
        print("EXISTING CONVERSATIONAL AI AGENTS")
        print("="*60)

        # Note: This endpoint might vary based on ElevenLabs API version
        # You may need to adjust based on actual API
        agents = client.conversational_ai.agents.list()

        if agents:
            for agent in agents:
                print(f"\nAgent: {agent.name}")
                print(f"ID: {agent.agent_id}")
        else:
            print("\nNo agents found.")

    except Exception as e:
        print(f"\nNote: Could not list agents: {e}")
        print("This feature may not be available in your API version.")


if __name__ == '__main__':
    print("\n")

    # Option to list existing agents
    print("Would you like to:")
    print("1. Create a new exam agent")
    print("2. List existing agents")
    print()

    choice = input("Enter choice (1 or 2, or just press Enter for option 1): ").strip()

    if choice == '2':
        list_existing_agents()
    else:
        agent_id = create_exam_agent()

        if agent_id:
            print("\n" + "="*60)
            print("Setup complete! Agent is ready to use.")
            print("="*60 + "\n")
