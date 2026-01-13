# Model Architecture & Usage

## Overview

This system uses **4 different AI models** for different purposes:

1. **Claude Sonnet 4.5** - Manuscript analysis
2. **ElevenLabs' Model** - Voice exam conductor
3. **Claude Sonnet 4.5, OpenAI o1, Gemini 2.0 Flash** - Grading council

---

## (i) Running the Exam - 2 Models

### 1. Pre-Exam Analysis: **Claude Sonnet 4.5**

**Purpose**: Analyze the student's manuscript before the oral exam

**What it does**:
- Reads the entire manuscript
- Identifies key claims and arguments
- Spots methodology gaps
- Recognizes potential weak points
- Generates 7-10 targeted question areas

**Input**:
- Student's manuscript text
- Assignment prompt

**Output**:
```json
{
  "key_claims": ["claim 1", "claim 2", ...],
  "methodology": "description of approach",
  "gaps": ["gap 1", "gap 2", ...],
  "question_areas": ["area 1", "area 2", ...]
}
```

**Code location**: `manuscript_viva_system.py` - `ManuscriptAnalyzer` class

**Model**: `claude-sonnet-4-5-20250929` via Anthropic API

---

### 2. Conducting the Oral Exam: **ElevenLabs' Model**

**Purpose**: Conduct the live voice-based oral examination

**What it does**:
- Asks 10-12 questions during voice conversation
- Generates follow-up questions based on student responses
- Maintains natural conversation flow
- Adapts questioning strategy in real-time

**Important**: ElevenLabs uses **their own language model**, NOT Claude/GPT/Gemini. We configure it by providing a detailed prompt, but ElevenLabs' model generates the actual questions during the conversation.

**How we configure it**:
```python
agent_config = {
    "agent": {
        "prompt": {
            "prompt": detailed_examiner_prompt  # We write this
        }
    }
}
```

The prompt includes:
- Instructions on questioning strategy
- Manuscript context and Claude's pre-analysis
- Types of questions to ask (4 categories):
  1. Content Understanding (3-4 questions)
  2. Reasoning & Choices (3-4 questions)
  3. Alternatives Considered (2-3 questions)
  4. Depth & Limitations (2-3 questions)

**Code location**: `manuscript_viva_system.py` - `create_examiner_agent()` method

**Model**: ElevenLabs' proprietary conversational AI model via ElevenLabs API

---

## (ii) Grading - 3 Models (All Required)

All three models grade **both** parts:
- Part A: Manuscript Quality
- Part B: Oral Examination

### 1. **Claude Sonnet 4.5**

**Model ID**: `claude-sonnet-4-5-20250929`
**API**: Anthropic
**Cost**: ~$3 per million input tokens, ~$15 per million output tokens

**Grading approach**:
- Very analytical
- Focuses on logical structure
- Detailed justifications
- Conservative with high scores

---

### 2. **OpenAI o1**

**Model ID**: `o1`
**API**: OpenAI
**Cost**: ~$15 per million input tokens, ~$60 per million output tokens

**Grading approach**:
- Deep reasoning
- Considers multiple perspectives
- Balanced assessments
- Moderate scoring

---

### 3. **Gemini 2.0 Flash**

**Model ID**: `gemini-2.0-flash-exp`
**API**: Google AI
**Cost**: Free (experimental, rate limited)

**Grading approach**:
- Fast and efficient
- Practical focus
- Clear feedback
- Slightly more lenient

---

## Grading Process

### Round 1: Independent Grading
Each model grades independently **without seeing** other models' grades:

**Part A - Manuscript** (4-point scale):
- Clarity: Precision of language
- Coherence: Logical flow
- Comprehensiveness: Depth of coverage

**Part B - Oral Exam** (4-point scale):
- Understanding: Can explain own work
- Reasoning: Justifies choices
- Alternatives: Considers trade-offs

### Round 2: Deliberation
Each model:
- Sees the other models' grades and justifications
- Can adjust their scores based on peer feedback
- Provides deliberation notes explaining any changes

### Final Output
For each student, you get **6 grading results**:
1. Claude - Manuscript (score + detailed assessment)
2. Claude - Oral (score + detailed assessment)
3. o1 - Manuscript (score + detailed assessment)
4. o1 - Oral (score + detailed assessment)
5. Gemini - Manuscript (score + detailed assessment)
6. Gemini - Oral (score + detailed assessment)

**Average scores** are calculated for:
- Manuscript: avg of 3 model scores
- Oral: avg of 3 model scores

---

## Complete Workflow

```
1. Student uploads manuscript (PDF/DOCX/TXT)
   ↓
2. Claude Sonnet 4.5 analyzes manuscript
   ↓
3. Custom ElevenLabs agent created with:
   - Manuscript text
   - Claude's analysis
   - Examiner prompt
   ↓
4. Student takes voice exam with ElevenLabs
   ↓
5. Transcript saved to database
   ↓
6. Grading Council evaluates (2 rounds):
   - Round 1: Claude, o1, Gemini grade independently
   - Round 2: Models deliberate and adjust
   ↓
7. Results saved to database with 6 separate grades
   ↓
8. Admin reviews in control panel
```

---

## API Keys Required

```bash
# .env file
ANTHROPIC_KEY=sk-ant-...           # For Claude Sonnet 4.5
OPENAI_API_KEY=sk-proj-...         # For OpenAI o1
GEMINI_KEY=AIzaSy...               # For Gemini 2.0 Flash
ELEVENLABS_API_KEY=sk_...          # For voice exams
```

All four keys are **required** for the system to work.

---

## Cost Per Exam (Approximate)

| Component | Model | Cost |
|-----------|-------|------|
| Pre-analysis | Claude Sonnet 4.5 | ~$0.05 |
| Voice exam | ElevenLabs | ~$0.30 |
| Manuscript grading (3 models × 2 rounds) | Claude, o1, Gemini | ~$0.40 |
| Oral grading (3 models × 2 rounds) | Claude, o1, Gemini | ~$0.40 |
| **Total per student** | | **~$1.15** |

---

## Question: Who Generates the Exam Questions?

**Short answer**: ElevenLabs' model generates the questions, but we heavily guide it.

**Longer explanation**:
- We write a detailed prompt that tells ElevenLabs:
  - What the manuscript is about (Claude analyzed it)
  - What topics to probe (from Claude's analysis)
  - What question types to use
  - How to structure the exam
- ElevenLabs' model reads this prompt and generates actual questions during the live conversation
- The questions are adaptive - they change based on student responses
- Think of it like: **Claude provides the exam outline, ElevenLabs conducts the actual interview**

---

## Model Selection Rationale

**Why these models?**

1. **Claude Sonnet 4.5**: Best for manuscript analysis - strong reading comprehension and structured output
2. **ElevenLabs**: Only option for natural voice conversations with real-time interaction
3. **o1**: Excellent reasoning for grading - deeper analysis than GPT-4
4. **Gemini 2.0 Flash**: Fast, efficient, provides alternative perspective, free

**Why not use Claude for the voice exam?**
- Claude doesn't have voice conversation capabilities
- ElevenLabs is specialized for natural voice interactions
- We leverage Claude's strengths (analysis/grading) and ElevenLabs' strengths (conversation)

---

## Configuration

Edit these files to customize behavior:

**Prompts** (via Admin Panel at `/admin/prompts`):
- `prompt_manuscript_analysis.txt` - How Claude analyzes manuscripts
- `prompt_examiner_agent.txt` - How ElevenLabs conducts exams
- `rubric_manuscript.txt` - How to grade manuscripts
- `rubric_oral_exam.txt` - How to grade oral performance

Changes take effect immediately for new exams.
