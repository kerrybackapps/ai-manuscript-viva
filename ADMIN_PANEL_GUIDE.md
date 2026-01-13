# Admin Control Panel Guide

## Access

Navigate to: `http://your-domain.com/admin/login`

Default password: `changeme123` (change this in your `.env` file)

## Features

### 1. Dashboard (`/admin/dashboard`)

- View all exam sessions
- See manuscript and oral scores for each student
- Quick statistics (total exams, average scores)
- Filter and sort exam sessions
- Direct access to detailed exam views

### 2. Exam Details (`/admin/exam/<id>`)

**Student Information:**
- Name, ID, exam type, date

**Part A - Manuscript Grading:**
- Scores from all 3 models (Claude, o1, Gemini)
- Average manuscript score
- Individual category scores (Clarity, Coherence, Comprehensiveness)
- Full assessments from each grader

**Part B - Oral Examination Grading:**
- Scores from all 3 models
- Average oral score
- Individual category scores (Understanding, Reasoning, Alternatives)
- Full assessments from each grader

**Transcript:**
- Complete manuscript text
- Full oral examination transcript
- Audio playback (if available from ElevenLabs)

### 3. Prompts Editor (`/admin/prompts`)

Edit system prompts and rubrics:

**Manuscript Analysis Prompt** (`prompt_manuscript_analysis.txt`)
- Claude prompt for analyzing manuscripts before oral exams
- Identifies key claims, gaps, and question areas

**Examiner Agent Prompt** (`prompt_examiner_agent.txt`)
- ElevenLabs agent configuration
- Defines questioning strategy and exam conduct

**Manuscript Grading Rubric** (`rubric_manuscript.txt`)
- Criteria for grading clarity, coherence, comprehensiveness
- 4-point scale definitions

**Oral Exam Grading Rubric** (`rubric_oral_exam.txt`)
- Criteria for grading understanding, reasoning, alternatives
- 4-point scale definitions

## Configuration

### Set Admin Password

In your `.env` file:
```
ADMIN_PASSWORD=your_secure_password_here
SECRET_KEY=your_random_secret_key_here
```

Generate a secure secret key:
```python
import secrets
print(secrets.token_hex(32))
```

### Session Security

- Sessions last 7 days
- Logout from `/admin/logout`
- Sessions are encrypted with SECRET_KEY

## Workflow

### For Each Student Exam:

1. **Student submits manuscript** via public interface
2. **System processes:**
   - Extracts text from PDF/DOCX
   - Claude analyzes manuscript
   - Creates custom ElevenLabs examiner agent
   - Generates exam page
3. **Student takes oral exam** (voice-based, 10-12 questions)
4. **After exam completes**, run grading:
   ```python
   from manuscript_viva_system import ManuscriptVivaSystem
   system = ManuscriptVivaSystem()
   system.grade_manuscript_and_oral(session_id)
   ```
5. **Admin reviews results** in control panel:
   - See all grading details
   - Compare scores across models
   - Read full assessments
   - Review transcript

### Viewing Grades:

- **Dashboard**: See all students and average scores at a glance
- **Exam Detail**: Deep dive into individual student performance
- **Compare Models**: See how Claude, o1, and Gemini each graded
- **Identify Patterns**: Find common strengths/weaknesses

### Editing Prompts:

- Changes take effect immediately for **new** exam sessions
- Existing sessions keep their original prompts
- Test changes with a sample exam before production use
- Keep backups of working prompts

## Tips

1. **Regular Review**: Check dashboard daily during exam periods
2. **Prompt Tuning**: Adjust prompts based on grading quality
3. **Model Comparison**: Note which models are more strict/lenient
4. **Student Feedback**: Use transcripts to improve questions
5. **Security**: Change default admin password immediately

## Troubleshooting

**Can't login:**
- Check ADMIN_PASSWORD in `.env`
- Verify SECRET_KEY is set
- Clear browser cookies

**No grades showing:**
- Ensure grading has been run for that session
- Check API keys are valid
- Review logs for errors

**Can't save prompts:**
- Check file permissions on `prompts/` directory
- Verify admin session is valid

## API Endpoints

For custom integrations:

- `GET /admin/api/exam/<id>` - Get exam details JSON
- `GET /admin/api/prompts/<filename>` - Get prompt content
- `POST /admin/api/prompts/<filename>` - Update prompt

All require admin authentication.
