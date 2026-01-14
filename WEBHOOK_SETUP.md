# ElevenLabs Webhook Setup Guide

## Overview

The webhook automatically captures oral exam transcripts and triggers grading when the ElevenLabs conversation ends.

## Setup Steps

### 1. Deploy Your App

Make sure your app is deployed and accessible via HTTPS:
- **Koyeb URL**: `https://your-app.koyeb.app`
- **Webhook endpoint**: `https://your-app.koyeb.app/webhook/elevenlabs`

### 2. Add Webhook URL to .env

Add this line to your `.env` file:
```
WEBHOOK_URL=https://your-app.koyeb.app/webhook/elevenlabs
```

Replace `your-app.koyeb.app` with your actual deployment URL.

### 3. Update ElevenLabs Agent

Run the update script:
```bash
python update_elevenlabs_agent.py
```

This will:
- Update the agent prompt with time management (15-20 minute exams)
- Configure the webhook to trigger on `conversation.ended` event
- Show confirmation of changes

### 4. Manual Configuration (If Script Fails)

If the script doesn't work, configure manually:

1. Go to https://elevenlabs.io/app/conversational-ai
2. Select your agent
3. **Update System Prompt**: Copy prompt from `update_elevenlabs_agent.py` lines 15-59
4. **Configure Webhook**:
   - Settings → Webhooks
   - URL: `https://your-app.koyeb.app/webhook/elevenlabs`
   - Event: `conversation.ended`

## How It Works

### Exam Flow

1. Student uploads manuscript
2. System creates exam session (status: `pending`)
3. Student takes oral exam via ElevenLabs
4. **Examiner agent ends exam after 15-20 minutes** (before timeout)
5. ElevenLabs sends webhook to `/webhook/elevenlabs`
6. Webhook:
   - Fetches transcript from ElevenLabs API
   - Saves to `oral_transcript` field
   - Updates status to `completed`
   - **Automatically triggers grading**
7. Grading council evaluates both manuscript and oral performance
8. Results appear in admin panel

### Time Management

The examiner agent prompt now includes:
- **Target duration**: 15-20 minutes
- **Soft wrap-up**: After 18 minutes, begin concluding
- **Hard cutoff**: At 20 minutes, immediately end exam

This prevents ElevenLabs timeout (typically 30 minutes) and ensures clean exam completion.

### Webhook Payload

Expected webhook data:
```json
{
  "conversation_id": "conv_abc123",
  "agent_id": "agent_xyz789",
  "status": "ended"
}
```

### Debugging

Check server logs for webhook activity:
- `[WEBHOOK] Received:` - Webhook payload received
- `[WEBHOOK] Processing conversation:` - Conversation ID extracted
- `[WEBHOOK] Matched to exam session X` - Exam found
- `[WEBHOOK] Extracted transcript: N chars` - Transcript fetched
- `[WEBHOOK] Updated exam session X` - Database updated
- `[WEBHOOK] Grading completed successfully` - Grading triggered

### Fallback: Manual Grading

If webhook fails, you can manually trigger grading:
```bash
POST /grade/<session_id>
```

Or via admin panel (future feature).

## Testing

1. Upload a test manuscript
2. Take the exam (speak for 2-3 minutes)
3. Wait for examiner to end call
4. Check admin panel - exam should show:
   - Status: `completed`
   - Oral transcript populated
   - Grades from all 3 models

## Troubleshooting

**Problem**: Webhook not receiving calls
- Check ElevenLabs dashboard → Agent → Settings → Webhooks
- Verify URL is correct and HTTPS
- Check server logs for incoming requests

**Problem**: Transcript not captured
- Check ElevenLabs API key in `.env`
- Verify conversation ID in webhook payload
- Check server logs for API errors

**Problem**: Grading not triggered
- Check `oral_transcript` field is populated
- Manually trigger: `POST /grade/<session_id>`
- Check API keys for Claude/OpenAI/Gemini

## Security Note

The webhook endpoint is currently open (no authentication). For production:
1. Add webhook signature verification
2. Use ElevenLabs webhook secret
3. Verify incoming request source
