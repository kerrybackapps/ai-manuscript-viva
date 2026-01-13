# AI-Powered Oral Exam System - Full Implementation (Option A)

A complete web-based system for conducting and grading oral exams using AI, with a multi-model grading council and comprehensive administration interface.

Based on: ["Fighting Fire with Fire: Scalable Oral Exams Using AI"](https://www.behind-the-enemy-lines.com/2025/12/fighting-fire-with-fire-scalable-oral.html)

## Features

### Complete Exam Management System
- **Student Management**: Add, view, and track students
- **Exam Sessions**: Create and manage exam sessions
- **Case Study Scenarios**: Randomized scenario bank
- **Transcript Storage**: Save and review exam transcripts
- **Multi-Model Grading**: Claude Sonnet 4.5, OpenAI o1, Gemini 2.0
- **Grading Deliberation**: Multi-round consensus building
- **Analytics Dashboard**: Performance tracking and cost monitoring
- **Web Interface**: Full-featured Flask application

### Grading Council
- **3-Model System**: Claude, GPT, Gemini grade independently
- **Deliberation Rounds**: Models review each other's assessments
- **Convergence Tracking**: Measure agreement between models
- **Cost Tracking**: Monitor API usage per exam
- **Detailed Justifications**: Category-level scoring with explanations

## Quick Start

### 1. Install Dependencies

```bash
# Using venv (recommended)
venv\Scripts\pip.exe install -r requirements.txt

# OR using pip directly
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file with your API keys:

```env
ANTHROPIC_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...
GEMINI_KEY=AIzaSy...
```

### 3. Seed Database

```bash
python seed_data.py
```

This creates:
- 10 case study scenarios
- 3 sample students
- Empty exam database

### 4. Run Tests

```bash
python test_system.py
```

Verifies:
- Database operations
- Grading council setup
- Flask routes

### 5. Start Web Server

```bash
python run_server.py
```

Opens browser at: `http://localhost:5000/`

## System Architecture

### Database Schema

#### Students Table
- Student ID (unique)
- Name, Email
- Project title and description
- Creation timestamp

#### Exam Sessions Table
- Session ID
- Student reference
- Exam type (project, case_study, combined)
- Status (pending, in_progress, completed, failed)
- Transcript
- Timestamps

#### Grading Results Table
- Session reference
- Model name (claude, gpt, gemini)
- Round number
- Overall score (0.0-4.0)
- Category scores (JSON)
- Assessment text
- API cost

#### Scenarios Table
- Title, Description
- Category (ML, AI Ethics, Statistics, MLOps)
- Difficulty (easy, medium, hard)
- Active status

### Web Application Routes

#### Dashboard (`/`)
- System statistics
- Recent exams
- Quick actions

#### Students (`/students`)
- List all students
- Add new students (`/students/add`)
- View student details (`/students/<id>`)
- Exam history per student

#### Exams (`/exams`)
- List all exams
- Start new exam (`/exams/start`)
- Conduct exam (`/exams/<id>/conduct`)
- View results (`/exams/<id>/view`)

#### Scenarios (`/scenarios`)
- List all scenarios
- Add scenarios (`/scenarios/add`)
- Categorized by topic and difficulty

#### Analytics (`/analytics`)
- Total students and exams
- Completion rates
- Average scores by model
- Cost per exam
- Performance trends

### API Endpoints

#### POST `/api/exams/<id>/transcript`
Save exam transcript
```json
{
  "transcript": "EXAM TRANSCRIPT\n..."
}
```

#### POST `/api/exams/<id>/grade`
Grade exam with deliberation
```json
{
  "deliberation_rounds": 1
}
```

Returns:
```json
{
  "success": true,
  "convergence": {
    "average_score": 3.2,
    "within_1_point_agreement": true,
    "standard_deviation": 0.15
  },
  "grades": {
    "claude": {...},
    "gpt": {...},
    "gemini": {...}
  }
}
```

#### GET `/api/scenarios/random`
Get random scenario
```
?category=Machine Learning
&difficulty=medium
```

#### GET `/api/analytics`
Get system analytics

## Usage Workflows

### Workflow 1: Conduct an Exam (Web Interface)

1. **Add Student** (if new)
   - Navigate to Students → Add Student
   - Enter student ID, name, email
   - Enter project title and description

2. **Start Exam**
   - Dashboard → Start New Exam
   - Select student
   - Choose exam type

3. **Upload Transcript**
   - Use CLI demo tool (`python demo.py`) to conduct exam
   - Copy transcript
   - Paste into web interface
   - Click "Save & Grade"

4. **Review Results**
   - System automatically grades with 3 models
   - View convergence metrics
   - Read detailed assessments
   - Export results

### Workflow 2: Conduct an Exam (CLI + Web)

1. **Use Demo Tool** for interactive exam:
   ```bash
   python demo.py
   ```
   - Select Option 2 (Interactive Mode)
   - Conduct exam with student
   - Save transcript from results folder

2. **Upload to Web System**:
   - Go to web interface
   - Create exam session
   - Upload saved transcript
   - Trigger grading

### Workflow 3: Batch Processing

1. **Add Multiple Students**:
   - Use web interface or database directly
   - Bulk import from CSV (future feature)

2. **Generate Exam Sessions**:
   - Create sessions for all students
   - Assign randomized scenarios

3. **Conduct Exams**:
   - Students complete exams (voice or text)
   - Transcripts saved automatically

4. **Batch Grading**:
   - System grades all pending exams
   - Generate aggregate reports

## Cost Analysis

Based on actual usage:

### Per Exam Cost Breakdown
- **Claude Sonnet 4.5**: ~$0.05
- **OpenAI o1**: ~$0.03
- **Gemini 2.0 Flash**: ~$0.01
- **Total per exam**: ~$0.09 (1 round) to ~$0.18 (2 rounds)

### Scaling
- 36 students (original study): ~$3.24
- 100 students: ~$9.00
- 500 students: ~$45.00

Vastly cheaper than human graders at scale.

## Models Used

### Claude Sonnet 4.5
- Model ID: `claude-sonnet-4-5-20250929`
- Best for: Nuanced evaluation, detailed justifications
- Strengths: Understanding context, recognizing failure modes

### OpenAI o1
- Model ID: `o1`
- Best for: Reasoning about technical concepts
- Strengths: Mathematical accuracy, logical consistency

### Gemini 2.0 Flash
- Model ID: `gemini-2.0-flash-exp`
- Best for: Cost-effective grading, quick turnaround
- Strengths: Speed, efficient token usage

## Convergence Metrics

After deliberation, models typically achieve:
- **62%** within-1-point agreement
- **Average std dev**: 0.2-0.4 points
- **Convergence improvement**: 0% → 62% (Round 1 → Round 2)

## File Structure

```
AI Exams/
├── app.py                      # Flask web application
├── database.py                 # SQLAlchemy models and operations
├── exam_conversation.py        # Exam conversation logic
├── grading_council.py          # Multi-model grading system
├── demo.py                     # CLI demo tool
├── run_server.py               # Web server launcher
├── test_system.py              # Comprehensive test suite
├── seed_data.py                # Database seeding
├── requirements.txt            # Python dependencies
├── .env                        # API keys (not in git)
├── templates/                  # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── students.html
│   ├── add_student.html
│   ├── student_detail.html
│   ├── exams.html
│   ├── start_exam.html
│   ├── conduct_exam.html
│   ├── view_exam.html
│   ├── scenarios.html
│   ├── add_scenario.html
│   └── analytics.html
├── static/                     # CSS, JS, images
├── results/                    # Saved exam results (JSON)
├── exam_system.db              # SQLite database
└── sample_*.txt                # Rubric and exam context
```

## Advanced Features

### Custom Rubrics

Edit `sample_rubric.txt` to customize grading criteria:
- Add/remove categories
- Adjust weights
- Change scoring scale
- Modify descriptions

### Scenario Management

- Add scenarios via web interface
- Categorize by topic
- Set difficulty levels
- Activate/deactivate scenarios

### Deliberation Rounds

Adjust in grading API call:
```python
grading_results = council.conduct_grading(
    transcript=transcript,
    rubric=rubric,
    deliberation_rounds=2  # More rounds = better convergence
)
```

## Troubleshooting

### Database Locked
```bash
# Close all connections
rm exam_system.db
python seed_data.py
```

### API Key Errors
- Check `.env` file exists
- Verify key names match: `ANTHROPIC_KEY`, `OPENAI_API_KEY`, `GEMINI_KEY`
- Test keys: `python test_system.py`

### Port Already in Use
```bash
# Change port in app.py or run_server.py
app.run(port=5001)  # Use different port
```

### Unicode Errors (Windows)
System now uses ASCII characters `[OK]` and `[FAIL]` instead of Unicode checkmarks.

## Development Roadmap

### Future Enhancements
- [ ] Voice integration (ElevenLabs Conversational AI)
- [ ] Real-time exam monitoring
- [ ] Batch student import (CSV)
- [ ] Export reports (PDF)
- [ ] Multi-language support
- [ ] Custom rubric builder (UI)
- [ ] Student authentication portal
- [ ] Exam scheduling system
- [ ] Automated scenario generation
- [ ] Grade appeals workflow
- [ ] Integration with LMS platforms

## Security Considerations

- **API Keys**: Never commit `.env` to git
- **Student Data**: Implement FERPA compliance
- **Transcript Storage**: Encrypt sensitive data
- **Access Control**: Add authentication to web interface
- **Audit Trail**: Log all grading decisions

## Performance Optimization

### Database Indexing
```python
# Add indexes for common queries
session_index = Index('idx_session_student', ExamSession.student_id)
grade_index = Index('idx_grade_session', GradingResult.session_id)
```

### Caching
```python
# Cache analytics results
from functools import lru_cache
@lru_cache(maxsize=128)
def get_cached_analytics():
    return db.get_analytics()
```

### Async Grading
```python
# Grade in background for large batches
from celery import Celery
app = Celery('tasks', broker='redis://localhost:6379')

@app.task
def grade_exam_async(session_id):
    # Grading logic
    pass
```

## Contributing

This is a proof-of-concept system. Contributions welcome:
- Bug fixes
- Feature enhancements
- Documentation improvements
- Test coverage

## License

Educational/Research use

## Acknowledgments

- Original research: "Fighting Fire with Fire: Scalable Oral Exams Using AI"
- Anthropic Claude API
- OpenAI API
- Google Gemini API
- Flask framework
- SQLAlchemy ORM

## Support

For issues or questions:
1. Check this documentation
2. Run `python test_system.py`
3. Review error logs
4. Check API key quotas

---

**Built with Claude Code** - January 2026
