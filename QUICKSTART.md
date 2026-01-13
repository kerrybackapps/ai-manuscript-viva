# Quick Start Guide

## 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 2. Set Up API Keys

### Option A: Use .env file (Recommended)

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your keys
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
# GOOGLE_API_KEY=...
```

### Option B: Set environment variables

**Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=your_key_here
set OPENAI_API_KEY=your_key_here
set GOOGLE_API_KEY=your_key_here
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="your_key_here"
$env:OPENAI_API_KEY="your_key_here"
$env:GOOGLE_API_KEY="your_key_here"
```

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here
export GOOGLE_API_KEY=your_key_here
```

## 3. Get API Keys

- **Anthropic Claude**: https://console.anthropic.com/
- **OpenAI GPT**: https://platform.openai.com/api-keys
- **Google Gemini**: https://makersuite.google.com/app/apikey

## 4. Run the Demo

```bash
python demo.py
```

## 5. Choose Your Mode

### Demo Mode (Recommended First)
- Uses a pre-recorded transcript
- See the grading council in action immediately
- No interaction required

### Interactive Mode
- Conduct a live oral exam
- Answer questions as a student
- Test the full exam flow

## Example Session

```
AI-POWERED ORAL EXAM SYSTEM - PROOF OF CONCEPT
============================================================

Select mode:
  1. Demo Mode (use pre-recorded transcript)
  2. Interactive Mode (conduct live exam)

Enter choice (1 or 2): 1

DEMO MODE - Using Pre-recorded Exam Transcript
============================================================

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

[Results displayed...]
```

## Troubleshooting

### "Missing required API keys"
- Make sure you've created a `.env` file OR set environment variables
- Check that your keys are valid and have credits

### "Module not found"
- Run `pip install -r requirements.txt`
- Make sure you're using Python 3.8+

### "API Error"
- Check your API key is correct
- Verify you have credits/quota available
- Check your internet connection

## Next Steps

- Customize [sample_rubric.txt](sample_rubric.txt) for your grading criteria
- Modify [sample_exam_context.txt](sample_exam_context.txt) for your subject
- Try interactive mode and answer exam questions
- Review saved results in the `results/` folder

## Cost Tracking

Each exam costs approximately $0.30-0.50 depending on:
- Length of conversation
- Number of deliberation rounds
- Complexity of grading rubric

The demo mode transcript costs about $0.30 to grade.
