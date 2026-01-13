# AI Manuscript Viva Oral Exam System

AI-powered oral examination system where students submit manuscripts and undergo personalized voice-based oral exams conducted by AI.

Inspired by: ["Fighting Fire with Fire: Scalable Oral Exams Using AI"](https://www.behind-the-enemy-lines.com/2025/12/fighting-fire-with-fire-scalable-oral.html)

## Features

- **📄 Manuscript Upload**: Students submit papers (PDF, DOCX, or TXT)
- **🤖 AI Analysis**: Claude analyzes manuscripts and identifies key areas to probe
- **🎤 Voice Exam**: ElevenLabs AI conducts 10-12 question oral examination
- **📊 Dual Grading**: Separate evaluation of manuscript quality and oral defense
- **🏛️ Grading Council**: 3-model consensus (Claude Sonnet 4.5, OpenAI o1, Gemini 2.0)

## Grading System

### Part A: Manuscript Quality (4-point scale)
- **Clarity**: Precision of language and explanations
- **Coherence**: Logical structure and flow
- **Comprehensiveness**: Depth of coverage and evidence

### Part B: Oral Examination (4-point scale)
- **Understanding**: Can explain and defend own work
- **Reasoning**: Clear justification for choices
- **Alternatives**: Awareness of other approaches and trade-offs

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file with:

```
ANTHROPIC_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
GEMINI_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

Get API keys from:
- **Anthropic (Claude)**: https://console.anthropic.com/
- **OpenAI**: https://platform.openai.com/api-keys
- **Google (Gemini)**: https://aistudio.google.com/app/apikey
- **ElevenLabs**: https://elevenlabs.io/

### 3. Run the Demo

```bash
python demo_app.py
```

Open browser to: `http://localhost:5001`

## Usage

1. **Upload manuscript**: Submit your paper or use a sample
2. **AI analyzes**: Claude reads and analyzes your work
3. **Take oral exam**: Click microphone and answer 10-12 questions
4. **View results**: See dual grading from 3-model council

## Project Structure

```
AI Exams/
├── demo.py                      # Main demo script
├── exam_conversation.py         # Exam conversation logic
├── grading_council.py          # Multi-model grading system
├── sample_rubric.txt           # Grading rubric
├── sample_exam_context.txt     # Exam topic and context
├── requirements.txt            # Python dependencies
├── .env.example               # API key template
└── results/                   # Saved exam results (auto-created)
```

## How It Works

### Exam Flow

1. **Authentication**: Student identifies themselves
2. **Context Loading**: System loads exam topic and rubric
3. **Conversation**: AI examiner asks 5-7 questions
4. **Transcript Generation**: Complete conversation is recorded

### Grading Flow

1. **Round 1 - Independent Grading**:
   - Claude, GPT, and Gemini each grade the transcript independently
   - No communication between models
   - Each provides scores and justifications

2. **Round 2+ - Deliberation**:
   - Each model reviews the others' assessments
   - Models can adjust their scores based on peer feedback
   - Justifications updated with deliberation notes

3. **Convergence Analysis**:
   - Calculate average score
   - Check within-1-point agreement
   - Measure standard deviation
   - Report score range

## Sample Output

```
GRADING COUNCIL SESSION
============================================================

Round 1: Independent Grading...
  - Claude grading...
  - GPT grading...
  - Gemini grading...

Round 2: Deliberation...
  - Claude deliberating...
  - GPT deliberating...
  - Gemini deliberating...

============================================================
GRADING RESULTS
============================================================

FINAL SCORES:
----------------------------------------

CLAUDE: 3.4
Assessment: The student demonstrates solid understanding of ML concepts...

GPT: 3.5
Assessment: Strong grasp of practical applications and trade-offs...

GEMINI: 3.3
Assessment: Good conceptual knowledge with some areas for improvement...

----------------------------------------
CONVERGENCE METRICS:
----------------------------------------
Average Score: 3.4
Within-1-Point Agreement: True
Standard Deviation: 0.082
Score Range: 3.3 - 3.5
```

## Key Lessons from the Original Research

- **One question at a time**: Prevents cognitive overload
- **Verbatim repetition**: When students ask, repeat exactly
- **Think time**: Allow adequate pause before answering
- **Deterministic randomization**: Code-based scenario selection
- **Cost efficiency**: ~$0.42 per student exam
- **Convergence**: 62% within-1-point agreement after deliberation

## Customization

### Modify the Rubric

Edit [sample_rubric.txt](sample_rubric.txt) to change:
- Grading categories
- Score scales
- Category weights
- Evaluation criteria

### Modify Exam Context

Edit [sample_exam_context.txt](sample_exam_context.txt) to change:
- Subject matter
- Topics to cover
- Project background
- Focus areas

### Adjust Deliberation Rounds

In [demo.py](demo.py), change the `deliberation_rounds` parameter:

```python
grading_results = council.conduct_grading(
    transcript=transcript,
    rubric=rubric,
    deliberation_rounds=2  # Increase for more convergence
)
```

## Cost Estimation

Based on average usage:
- **Exam conversation**: ~2,000 tokens (~$0.01)
- **Initial grading (3 models)**: ~6,000 tokens (~$0.15)
- **Deliberation round**: ~6,000 tokens (~$0.15)

**Total per student**: ~$0.30-0.50 depending on conversation length

## Future Enhancements (Not in POC)

- Voice interface using ElevenLabs Conversational AI
- Web-based dashboard for exam administration
- Student authentication system
- Batch exam processing
- Analytics and reporting
- Video recording for anti-cheating
- Custom scenario randomization
- Multi-language support

## License

This is a proof-of-concept demonstration for educational purposes.

## References

- Original article: [Fighting Fire with Fire: Scalable Oral Exams Using AI](https://www.behind-the-enemy-lines.com/2025/12/fighting-fire-with-fire-scalable-oral.html)
- ElevenLabs Conversational AI: https://elevenlabs.io/conversational-ai
