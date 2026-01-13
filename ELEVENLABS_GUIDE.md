# ElevenLabs Voice Exam Setup Guide

## What You Have Now

I've created two scripts for you:

1. **setup_elevenlabs_agent.py** - Creates your exam agent
2. **test_elevenlabs_agent.py** - Tests and shows how to use it

## Step 1: Create Your Exam Agent

Run this command:

```bash
python setup_elevenlabs_agent.py
```

**What this does:**
- Creates a Conversational AI agent on ElevenLabs
- Configures it as an oral exam examiner
- Saves the Agent ID to your .ENV file
- The agent is ready to conduct voice exams!

**The agent will:**
- Ask ONE question at a time (not stack questions)
- Ask 5-7 questions about ML concepts
- Allow think time
- Repeat questions if asked
- End with "EXAM_COMPLETE"

## Step 2: Test Your Agent

After creating the agent, run:

```bash
python test_elevenlabs_agent.py
```

**What this shows:**
- Your agent ID and status
- How to use the agent in code
- Integration options (web widget, Python SDK, API)
- Example code for conducting exams

## Step 3: Try It Out (Manually)

The easiest way to test your agent right now:

1. Go to: https://elevenlabs.io/app/conversational-ai
2. Find your agent: "AI Oral Examiner - ML Fundamentals"
3. Click the "Test" button
4. **Have a voice conversation!**
5. The agent will ask you exam questions via voice
6. Answer by speaking
7. It will automatically transcribe the conversation

## How Voice Exams Work

### Web Interface (Easiest)

The web widget allows students to have voice conversations:

```html
<!-- Add to your exam page -->
<script src="https://elevenlabs.io/convai-widget/index.js"></script>

<script>
const widget = new ElevenLabs.ConversationalAI({
    agentId: 'YOUR_AGENT_ID',  // From .ENV file
    apiKey: 'YOUR_API_KEY'      // From .ENV file
});
widget.mount();
</script>
```

Students click a button → voice conversation starts → agent asks questions → auto-transcribed

### Python Integration

```python
from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv()

client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
agent_id = os.getenv('ELEVENLABS_AGENT_ID')

# Start voice conversation
conversation = client.conversational_ai.conversations.create(
    agent_id=agent_id
)

# After exam, get transcript
transcript = client.conversational_ai.conversations.get_transcript(
    conversation_id=conversation.conversation_id
)

# Save to database and grade
```

## Full Exam Workflow

### Current (Text-Based):
1. Create exam session in web interface
2. Run `python demo.py` for text conversation
3. Copy/paste transcript to web
4. System grades with 3 models
5. View results

### With Voice (ElevenLabs):
1. Create exam session in web interface
2. Student clicks "Start Voice Exam" button
3. Voice conversation with agent (auto-recorded)
4. Transcript automatically saved
5. System grades with 3 models
6. View results + listen to recording

## Cost Comparison

**Text Exams (Current):**
- Grading only: ~$0.09-0.18 per exam

**Voice Exams (With ElevenLabs):**
- Voice conversation: ~$0.05-0.15 per exam
- Grading: ~$0.09-0.18 per exam
- **Total: ~$0.14-0.33 per exam**

Still much cheaper than human graders!

## Troubleshooting

### "No permissions" error
- Go to ElevenLabs → Developers → API Keys
- Edit your key
- Enable "Conversational AI" permission
- Enable "Text to Speech" permission

### "Insufficient credits"
- Check your ElevenLabs account balance
- Add credits if needed
- Free tier includes some credits

### Agent not found
- Run `python setup_elevenlabs_agent.py` first
- Check `.ENV` file has `ELEVENLABS_AGENT_ID`

## Next Steps

**To integrate voice into the exam system:**

1. I can create a voice exam module that:
   - Embeds the ElevenLabs widget in web interface
   - Handles conversation start/stop
   - Auto-saves transcripts to database
   - Triggers grading when complete

2. Or you can test the agent manually first:
   - Visit ElevenLabs dashboard
   - Test your agent
   - See how it works
   - Then decide on integration

**What would you like to do next?**
- Test the agent manually first?
- Integrate voice exams into the web system?
- Just use text exams for now?
