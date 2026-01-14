"""
Complete Manuscript-Based Oral Exam System
Supports PDF/DOCX, dual grading (manuscript + oral), pre-exam analysis
"""
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from anthropic import Anthropic
import PyPDF2
from docx import Document
from database import Database
from grading_council import GradingCouncil

load_dotenv()


class ManuscriptExtractor:
    """Extract text from various document formats"""

    @staticmethod
    def extract_from_pdf(filepath: str) -> str:
        """Extract text from PDF"""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = []
                for page in pdf_reader.pages:
                    text.append(page.extract_text())
                return '\n\n'.join(text)
        except Exception as e:
            raise Exception(f"Error extracting PDF: {e}")

    @staticmethod
    def extract_from_docx(filepath: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = Document(filepath)
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            return '\n\n'.join(text)
        except Exception as e:
            raise Exception(f"Error extracting DOCX: {e}")

    @staticmethod
    def extract_from_txt(filepath: str) -> str:
        """Extract text from TXT"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT: {e}")

    @classmethod
    def extract_text(cls, filepath: str) -> str:
        """Auto-detect format and extract text"""
        ext = os.path.splitext(filepath)[1].lower()

        if ext == '.pdf':
            return cls.extract_from_pdf(filepath)
        elif ext == '.docx':
            return cls.extract_from_docx(filepath)
        elif ext == '.txt':
            return cls.extract_from_txt(filepath)
        else:
            raise ValueError(f"Unsupported file format: {ext}")


class ManuscriptAnalyzer:
    """Pre-exam analysis using Claude"""

    def __init__(self):
        anthropic_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_KEY')
        self.client = Anthropic(api_key=anthropic_key)

    def analyze_manuscript(self, manuscript_text: str, assignment_prompt: str) -> dict:
        """
        Analyze manuscript before oral exam
        Identifies key claims, methodology, and generates exactly 5 specific questions
        """

        analysis_prompt = f"""You are preparing an oral examination for a student's manuscript.

ASSIGNMENT:
{assignment_prompt}

STUDENT'S MANUSCRIPT:
{manuscript_text}

YOUR TASK:
Analyze this manuscript and generate EXACTLY 5 specific questions for the oral examination.

The 5 questions MUST follow this structure:
1. CONTENT - Ask about a specific key point or claim in their manuscript
2. REASONING - Why did they take a particular approach or make a specific choice?
3. EVIDENCE - What evidence supports a specific position they took?
4. ALTERNATIVES - What other approaches did they consider or could have considered?
5. LIMITATIONS - What are the limitations of their work or analysis?

Each question should:
- Reference specific content from the manuscript
- Be clear and concise
- Test genuine understanding (not just recall)
- Be answerable in 1-2 minutes

Format as JSON:
{{
    "key_claims": ["claim 1", "claim 2", ...],
    "methodology": "description of their approach",
    "evidence_quality": "assessment of evidence strength",
    "gaps": ["gap 1", "gap 2", ...],
    "exam_questions": [
        {{"number": 1, "category": "CONTENT", "question": "..."}},
        {{"number": 2, "category": "REASONING", "question": "..."}},
        {{"number": 3, "category": "EVIDENCE", "question": "..."}},
        {{"number": 4, "category": "ALTERNATIVES", "question": "..."}},
        {{"number": 5, "category": "LIMITATIONS", "question": "..."}}
    ],
    "overall_impression": "brief assessment"
}}
"""

        try:
            response = self.client.messages.create(
                model="claude-opus-4-5",
                max_tokens=2000,
                messages=[{"role": "user", "content": analysis_prompt}]
            )

            result = response.content[0].text

            # Extract JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()

            import json
            return json.loads(result)

        except Exception as e:
            print(f"Analysis error: {e}")
            return {
                "key_claims": [],
                "methodology": "Unable to analyze",
                "evidence_quality": "Unable to assess",
                "gaps": [],
                "exam_questions": [],
                "overall_impression": "Analysis failed"
            }


class ManuscriptVivaSystem:
    """Complete system for manuscript-based oral exams"""

    def __init__(self):
        self.db = Database()
        self.elevenlabs = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        self.analyzer = ManuscriptAnalyzer()
        self.council = GradingCouncil()

    def create_examiner_agent(self, manuscript_text: str, assignment_prompt: str, analysis: dict):
        """Create ElevenLabs agent with pre-generated questions"""

        # Extract the 5 pre-generated questions
        exam_questions = analysis.get('exam_questions', [])

        # Format questions for the agent
        questions_text = "\n\n".join([
            f"QUESTION {q['number']} ({q['category']}):\n{q['question']}"
            for q in exam_questions
        ])

        agent_prompt = f"""You are an oral examiner conducting a viva voce examination based on a student's submitted manuscript.

IMPORTANT: When the call connects, YOU MUST SPEAK FIRST. Immediately greet the student with: "Hello! I've read your manuscript carefully and I'm ready to begin your oral examination. Let's start with the first question."

EXAMINATION STRUCTURE (MANDATORY):
- YOU speak first - greet them and ask the first question immediately
- Ask EXACTLY these 5 questions IN ORDER, then END THE EXAM
- Ask one question at a time
- After the student answers question 5, IMMEDIATELY end the exam

YOUR 5 QUESTIONS (ask these EXACTLY in this order):

{questions_text}

EXAMINATION RULES:
- Ask question 1, wait for answer
- Ask question 2, wait for answer
- Ask question 3, wait for answer
- Ask question 4, wait for answer
- Ask question 5, wait for answer
- After they answer question 5, END IMMEDIATELY

ENDING THE EXAM (MANDATORY):
- After question 5 is answered, you MUST end the exam immediately
- Say: "Thank you for your responses. That completes the examination. Please hang up now to submit your exam for grading."
- Then STOP TALKING - do not respond to anything else
- Do NOT ask follow-up questions
- Do NOT ask additional questions

Be professional and focused. Ask exactly these 5 questions in order, no more, no less. You must speak first when the call starts!"""

        try:
            # Get webhook URL from environment
            webhook_url = os.getenv('WEBHOOK_URL')

            # Build conversation config
            conversation_config = {
                "agent": {
                    "prompt": {
                        "prompt": agent_prompt
                    },
                    "first_message": f"Hello! I've read your manuscript carefully and I'm ready to begin your oral examination. Let's start with the first question. {exam_questions[0]['question'] if exam_questions else 'Can you explain your main argument?'}"
                }
            }

            # Add webhook if configured
            if webhook_url:
                conversation_config["webhook"] = {
                    "url": webhook_url,
                    "events": ["conversation.ended"]
                }
                print(f"      Webhook configured: {webhook_url}")

            response = self.elevenlabs.conversational_ai.agents.create(
                name=f"Manuscript Viva Examiner",
                conversation_config=conversation_config
            )

            return response.agent_id

        except Exception as e:
            print(f"Error creating agent: {e}")
            return None

    def process_manuscript_submission(self, student_id: str, manuscript_path: str,
                                     assignment_prompt: str):
        """
        Complete workflow: extract → analyze → create exam session

        Args:
            student_id: Student identifier
            manuscript_path: Path to PDF/DOCX/TXT file
            assignment_prompt: Assignment description
        """

        print("\n" + "="*60)
        print("MANUSCRIPT VIVA SYSTEM - PROCESSING SUBMISSION")
        print("="*60)

        # 1. Extract text
        print(f"\n[1/5] Extracting text from: {manuscript_path}")
        try:
            manuscript_text = ManuscriptExtractor.extract_text(manuscript_path)
            print(f"      Extracted {len(manuscript_text)} characters")
        except Exception as e:
            print(f"      ERROR: {e}")
            return None

        # 2. Get student info
        print(f"\n[2/5] Loading student information...")
        student = self.db.get_student(student_id)
        if not student:
            print(f"      ERROR: Student {student_id} not found")
            return None
        print(f"      Student: {student['name']}")

        # 3. Analyze manuscript with Claude
        print(f"\n[3/5] Analyzing manuscript with Claude...")
        analysis = self.analyzer.analyze_manuscript(manuscript_text, assignment_prompt)
        print(f"      Found {len(analysis.get('key_claims', []))} key claims")
        print(f"      Generated {len(analysis.get('exam_questions', []))} exam questions")

        # 4. Create exam session
        print(f"\n[4/5] Creating exam session in database...")
        exam_session = self.db.create_exam_session(
            student_id=student_id,
            student_name=student['name'],
            exam_type='manuscript_viva'
        )

        # Store manuscript and analysis
        session_data = f"""[MANUSCRIPT]
{manuscript_text}

[PRE-EXAM ANALYSIS]
{analysis.get('overall_impression', '')}

Key Claims: {', '.join(analysis.get('key_claims', []))}

[ORAL EXAMINATION TRANSCRIPT TO FOLLOW]
"""
        # Update exam session with all data
        self.db.update_exam_session(
            exam_session['id'],
            transcript=session_data,  # Legacy combined format
            manuscript_content=manuscript_text,  # Separate manuscript text
            manuscript_file_path=manuscript_path,  # Path to uploaded file
            oral_transcript=None  # Will be filled after oral exam
        )
        print(f"      Session created: ID {exam_session['id']}")

        # 5. Create examiner agent
        print(f"\n[5/5] Creating custom examiner agent...")
        agent_id = self.create_examiner_agent(manuscript_text, assignment_prompt, analysis)
        if not agent_id:
            print("      ERROR: Failed to create agent")
            return None
        print(f"      Agent created: {agent_id}")

        # Store agent_id in exam session
        self.db.update_exam_session(
            exam_session['id'],
            agent_id=agent_id
        )

        print("\n" + "="*60)
        print("SUBMISSION PROCESSED SUCCESSFULLY")
        print("="*60)

        return {
            'session_id': exam_session['id'],
            'agent_id': agent_id,
            'analysis': analysis,
            'manuscript_length': len(manuscript_text)
        }

    def grade_manuscript_and_oral(self, session_id: int):
        """
        Dual grading: manuscript and oral exam separately

        Returns separate scores for:
        - Part A: Manuscript (clarity, coherence, comprehensiveness)
        - Part B: Oral Exam (understanding, reasoning, alternatives)
        """

        print("\n" + "="*60)
        print("DUAL GRADING SYSTEM")
        print("="*60)

        # Get exam session
        exam = self.db.get_exam_session(session_id)
        if not exam:
            print("ERROR: Exam session not found")
            return None

        # Get manuscript and oral transcript from dedicated fields
        manuscript_text = exam.get('manuscript_content') or ""
        oral_text = exam.get('oral_transcript') or ""

        # Load rubrics
        with open('rubric_manuscript.txt', 'r') as f:
            manuscript_rubric = f.read()

        with open('rubric_oral_exam.txt', 'r') as f:
            oral_rubric = f.read()

        # PART A: Grade manuscript
        print("\n[PART A] Grading Manuscript...")
        print("  Evaluating: Clarity, Coherence, Comprehensiveness")

        manuscript_prompt = f"{manuscript_rubric}\n\nMANUSCRIPT TO EVALUATE:\n{manuscript_text}"

        manuscript_results = self.council.conduct_grading(
            transcript=manuscript_prompt,
            rubric="",  # Rubric already in prompt
            deliberation_rounds=1
        )

        # PART B: Grade oral exam
        print("\n[PART B] Grading Oral Examination...")
        print("  Evaluating: Understanding, Reasoning, Alternatives")

        if oral_text.strip():
            oral_prompt = f"{oral_rubric}\n\nORAL EXAM TRANSCRIPT:\n{oral_text}"

            oral_results = self.council.conduct_grading(
                transcript=oral_prompt,
                rubric="",  # Rubric already in prompt
                deliberation_rounds=1
            )
        else:
            print("  WARNING: No oral exam transcript found")
            oral_results = None

        # Save results to database
        print("\n[Saving Results to Database...]")

        # Save manuscript grades
        manuscript_saved = 0
        for model, grade_data in manuscript_results['final_grades'].items():
            if 'error' not in grade_data:
                print(f"  Saving {model}_manuscript: score={grade_data.get('overall_score')}")
                try:
                    self.db.save_grading_result(
                        session_id=session_id,
                        model_name=f"{model}_manuscript",
                        round_number=2,  # After deliberation
                        overall_score=grade_data.get('overall_score'),
                        category_scores=grade_data.get('scores', {}),
                        assessment=grade_data.get('overall_assessment', ''),
                        cost=0.05  # Estimated
                    )
                    manuscript_saved += 1
                    print(f"  ✓ Saved {model}_manuscript")
                except Exception as e:
                    print(f"  ✗ Error saving {model}_manuscript: {e}")
            else:
                print(f"  ✗ Skipping {model}_manuscript (has error): {grade_data.get('error')}")

        # Save oral exam grades
        oral_saved = 0
        if oral_results:
            for model, grade_data in oral_results['final_grades'].items():
                if 'error' not in grade_data:
                    print(f"  Saving {model}_oral: score={grade_data.get('overall_score')}")
                    try:
                        self.db.save_grading_result(
                            session_id=session_id,
                            model_name=f"{model}_oral",
                            round_number=2,
                            overall_score=grade_data.get('overall_score'),
                            category_scores=grade_data.get('scores', {}),
                            assessment=grade_data.get('overall_assessment', ''),
                            cost=0.05
                        )
                        oral_saved += 1
                        print(f"  ✓ Saved {model}_oral")
                    except Exception as e:
                        print(f"  ✗ Error saving {model}_oral: {e}")
                else:
                    print(f"  ✗ Skipping {model}_oral (has error): {grade_data.get('error')}")

        print(f"\n[DATABASE] Saved {manuscript_saved} manuscript grades and {oral_saved} oral grades")

        # Mark session complete
        self.db.update_exam_session(session_id, status='completed')

        print("\n" + "="*60)
        print("GRADING COMPLETE")
        print("="*60)

        return {
            'manuscript_results': manuscript_results,
            'oral_results': oral_results
        }

    def generate_exam_page(self, agent_id: str, session_id: int, student_name: str):
        """Generate HTML page for conducting the oral exam"""

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Manuscript Viva - {student_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f7fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{ margin: 0 0 8px 0; font-size: 28px; }}
        .session-info {{ opacity: 0.95; margin-top: 12px; font-size: 14px; }}
        .card {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }}
        .card h2 {{
            color: #2d3748;
            margin-top: 0;
            font-size: 20px;
        }}
        ol, ul {{
            line-height: 1.8;
            color: #4a5568;
        }}
        .alert {{
            padding: 16px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid;
        }}
        .alert-info {{
            background: #e6f7ff;
            border-color: #1890ff;
            color: #096dd9;
        }}
        .alert-warning {{
            background: #fff7e6;
            border-color: #fa8c16;
            color: #d46b08;
        }}
        .widget-container {{
            background: white;
            padding: 32px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .footer {{
            text-align: center;
            color: #718096;
            margin-top: 32px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎓 Manuscript Viva Voce Examination</h1>
        <div class="session-info">
            <strong>Student:</strong> {student_name} |
            <strong>Session:</strong> #{session_id} |
            <strong>Status:</strong> Ready
        </div>
    </div>

    <div class="alert alert-warning">
        <strong>⚠️ Important:</strong> Ensure your microphone is enabled in your browser settings before starting.
    </div>

    <div class="card">
        <h2>📋 Examination Instructions</h2>
        <ol>
            <li>The AI examiner has read your entire manuscript</li>
            <li>The examiner will ask 5 questions testing your understanding</li>
            <li>You may ask the examiner to repeat questions</li>
            <li>To begin, click the <strong>"Start a call"</strong> button below</li>
            <li>Then click the <strong>telephone icon</strong> to connect</li>
            <li>The examiner will greet you and ask the first question</li>
        </ol>
    </div>

    <div class="widget-container">
        <h3>🎙️ Begin Oral Examination</h3>
        <elevenlabs-convai agent-id="{agent_id}"></elevenlabs-convai>
        <script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async></script>
    </div>

    <div class="card">
        <h2>📊 Grading Components</h2>
        <p><strong>Part A - Manuscript (50%):</strong></p>
        <ul>
            <li>Clarity: How well ideas are expressed</li>
            <li>Coherence: Logical flow and organization</li>
            <li>Comprehensiveness: Depth and completeness</li>
        </ul>
        <p><strong>Part B - Oral Examination (50%):</strong></p>
        <ul>
            <li>Understanding: Grasp of your own work</li>
            <li>Reasoning: Justification for choices made</li>
            <li>Alternatives: Consideration of other approaches</li>
        </ul>
    </div>

    <div class="footer">
        Session ID: {session_id} | Agent ID: {agent_id}<br>
        After completion, your responses will be evaluated by a 3-model grading council
    </div>
</body>
</html>
"""

        os.makedirs('exam_pages', exist_ok=True)
        filename = f"exam_session_{session_id}.html"
        filepath = os.path.join('exam_pages', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        return filepath


def demo_complete_system():
    """Demonstrate the complete manuscript viva system"""

    system = ManuscriptVivaSystem()

    # Use existing sample manuscript
    manuscript_path = 'sample_manuscripts/healthcare_ai_paper.txt'

    assignment = """
Write a 1000-word research paper on AI or machine learning applications.
Include: introduction, methodology, findings, discussion, and conclusion.
Use at least 10 peer-reviewed sources. Provide specific examples and evidence.
"""

    print("\n" + "="*70)
    print(" COMPLETE MANUSCRIPT VIVA SYSTEM - DEMONSTRATION")
    print("="*70)

    # Process submission
    result = system.process_manuscript_submission(
        student_id='S001',
        manuscript_path=manuscript_path,
        assignment_prompt=assignment
    )

    if result:
        # Generate exam page
        html_path = system.generate_exam_page(
            agent_id=result['agent_id'],
            session_id=result['session_id'],
            student_name='Alice Chen'
        )

        print(f"\n[OK] Exam page created: {html_path}")
        print(f"\n" + "="*70)
        print(" NEXT STEPS")
        print("="*70)
        print(f"\n1. CONDUCT ORAL EXAM:")
        print(f"   Open: {html_path}")
        print(f"   Click microphone and answer questions")
        print(f"\n2. AFTER EXAM, RUN GRADING:")
        print(f"   python -c \"from manuscript_viva_system import ManuscriptVivaSystem; ")
        print(f"   system = ManuscriptVivaSystem(); ")
        print(f"   system.grade_manuscript_and_oral({result['session_id']})\"")
        print(f"\n3. VIEW RESULTS:")
        print(f"   python run_server.py")
        print(f"   Navigate to: http://localhost:5000/exams/{result['session_id']}/view")


if __name__ == '__main__':
    demo_complete_system()
