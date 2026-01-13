# Prompts & Rubrics System

## Overview

All prompts and rubrics are stored in the **database**, not in text files. This means:

✅ **Changes persist** across deployments and container restarts
✅ **No rebuild needed** - edits take effect immediately for new exams
✅ **Version tracking** - see what version you're on, track changes
✅ **Cloud-friendly** - works on Koyeb, Heroku, AWS, etc.

---

## How It Works

### Storage
- Prompts are stored in the `prompts` database table
- Each prompt has: name, display name, description, content, category, version
- Edited via admin panel at `/admin/prompts`

### Usage
- When creating an exam, the system reads the **current prompt from database**
- Each exam session stores which version it used
- Changes affect **new exams only** - existing exams keep their original prompts

### No Rebuild Required
- Edit prompts in admin panel → Save → Done!
- New exams immediately use updated prompts
- No code changes, no deployment, no restart needed

---

## Available Prompts

### 1. Manuscript Analysis (`manuscript_analysis`)
**Category**: prompt
**Used by**: Claude Sonnet 4.5
**When**: Before oral exam - analyzes student's manuscript

**Purpose**: Tells Claude how to analyze the manuscript and what to look for

**Output**: JSON with:
- Key claims
- Methodology
- Gaps
- Question areas for oral exam

---

### 2. Examiner Agent (`examiner_agent`)
**Category**: prompt
**Used by**: ElevenLabs
**When**: During oral exam - conducting voice conversation

**Purpose**: Configures how ElevenLabs conducts the oral examination

**Instructions include**:
- Ask 10-12 questions across 4 categories
- Reference specific parts of manuscript
- Ask follow-up questions
- Allow think time
- End with "EXAMINATION_COMPLETE"

---

### 3. Manuscript Grading Rubric (`rubric_manuscript`)
**Category**: rubric
**Used by**: Claude, o1, Gemini
**When**: Grading manuscript quality

**Evaluates**:
1. **Clarity** (4-point scale)
   - Precision of language
   - Proper terminology
   - Clear explanations

2. **Coherence** (4-point scale)
   - Logical structure
   - Smooth transitions
   - Unified argument

3. **Comprehensiveness** (4-point scale)
   - Depth of coverage
   - Supporting evidence
   - Thorough treatment

---

### 4. Oral Exam Grading Rubric (`rubric_oral_exam`)
**Category**: rubric
**Used by**: Claude, o1, Gemini
**When**: Grading oral examination performance

**Evaluates**:
1. **Understanding of Own Work** (4-point scale)
   - Can explain content
   - Defend claims
   - Answer probing questions

2. **Reasoning & Justification** (4-point scale)
   - Clear rationale for choices
   - Evidence-based reasoning
   - Logical arguments

3. **Consideration of Alternatives** (4-point scale)
   - Awareness of other approaches
   - Understands trade-offs
   - Acknowledges limitations

---

## Editing Prompts

### Via Admin Panel

1. Login at `/admin/login` (password: see .ENV file)
2. Navigate to **Edit Prompts**
3. Select prompt to edit
4. Make changes in the editor
5. Click **Save Changes**
6. Done! Next exam will use new version

### Version Tracking

Each save increments the version number:
- v1 → Initial version
- v2 → First edit
- v3 → Second edit
- etc.

Future enhancement: Could add version history and rollback.

---

## Database Schema

```sql
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    category VARCHAR(50),
    version INTEGER DEFAULT 1,
    updated_at DATETIME,
    updated_by VARCHAR(100)
);
```

---

## Initialization

Prompts are initialized automatically when:
1. Running `initialize_prompts.py` manually
2. First time database is created
3. Adding new prompts to the system

**Re-running is safe** - existing prompts are not overwritten.

---

## Cloud Deployment Benefits

### Problem with File-Based Storage:
```
User edits prompt → Saves to file → Container restarts → File is gone 😞
```

### Solution with Database Storage:
```
User edits prompt → Saves to database → Container restarts → Prompt still there! ✅
```

Works on:
- ✅ Koyeb
- ✅ Heroku
- ✅ AWS (ECS, Lambda, etc.)
- ✅ Google Cloud Run
- ✅ Azure Container Apps
- ✅ Any platform with ephemeral file systems

---

## Code Usage

### Reading a Prompt from Database

```python
from database import Database, Prompt
from sqlalchemy import select

db = Database()

with db.Session() as session:
    prompt = session.execute(
        select(Prompt).where(Prompt.name == 'rubric_manuscript')
    ).scalar_one()

    rubric_content = prompt.content
```

### Helper Function (Coming Soon)

```python
def get_prompt(prompt_name):
    """Convenience function to get prompt content"""
    # Will be added to database.py or utils.py
    pass
```

---

## API Endpoints

### Get Prompt
```
GET /admin/api/prompts/<prompt_name>
```

Response:
```json
{
  "id": 1,
  "name": "manuscript_analysis",
  "display_name": "Manuscript Analysis",
  "content": "You are...",
  "category": "prompt",
  "version": 3,
  "updated_at": "2026-01-13T14:30:00"
}
```

### Update Prompt
```
POST /admin/api/prompts/<prompt_name>
Content-Type: application/json

{
  "content": "New prompt text..."
}
```

Response:
```json
{
  "success": true,
  "message": "Prompt updated successfully",
  "version": 4
}
```

---

## Best Practices

1. **Test changes** with a sample exam before production use
2. **Document significant changes** (future: add change notes to db)
3. **Keep backups** of working prompts (future: version history)
4. **Gradual rollout** - test with one student first
5. **Monitor results** - check if grading quality changes

---

## Future Enhancements

- [ ] Version history table (track all changes)
- [ ] Rollback to previous version
- [ ] Change notes/comments for each edit
- [ ] Compare versions side-by-side
- [ ] Prompt templates library
- [ ] Import/export prompts
- [ ] A/B testing different prompts

---

## Summary

**Key Point**: Prompts are in the database, not files. This means you can edit them via the admin panel and changes persist across deployments without rebuilding the app.

**To Edit**: `/admin/login` → Edit Prompts → Select prompt → Edit → Save

**Effect**: Immediate for new exams, existing exams keep original prompts

**Works on**: Any cloud platform (Koyeb, Heroku, AWS, etc.)
