"""
Manuscript-Based Oral Exam System
Student submits manuscript → AI reads it → Conducts personalized oral exam
"""
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from database import Database
from grading_council import GradingCouncil

load_dotenv()


class ManuscriptExamSystem:
    """System for conducting oral exams based on submitted manuscripts"""

    def __init__(self):
        self.db = Database()
        self.elevenlabs = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        self.council = GradingCouncil()

    def create_manuscript_exam_agent(self, manuscript_text: str, assignment_prompt: str):
        """
        Create a custom agent that has read the student's manuscript

        Args:
            manuscript_text: The full text of the student's manuscript
            assignment_prompt: The original assignment instructions
        """

        agent_prompt = f"""You are an oral examiner conducting a viva voce examination based on a student's submitted manuscript.

ASSIGNMENT PROMPT:
{assignment_prompt}

STUDENT'S MANUSCRIPT (you have already read this):
{manuscript_text}

YOUR ROLE:
You are conducting an oral examination to assess the student's understanding of their own work. Your questions should:

1. Test understanding of the content they wrote
2. Probe deeper into arguments and claims made
3. Ask them to explain or defend their positions
4. Challenge assumptions or identify gaps
5. Ask about methodology, sources, or reasoning
6. Request clarification on unclear points

EXAMINATION GUIDELINES:
- Ask ONE question at a time
- Reference specific parts of their manuscript
- Ask follow-up questions based on their answers
- If they ask you to repeat, repeat the question verbatim
- Allow adequate think time
- Conduct 7-10 questions total
- End with "EXAMINATION_COMPLETE" when done

QUESTION TYPES TO USE:
- "In your manuscript, you stated [X]. Can you elaborate on why you took that position?"
- "On page/section [Y], you mentioned [Z]. How did you arrive at that conclusion?"
- "What evidence supports your claim that [X]?"
- "Can you explain the reasoning behind [decision/argument]?"
- "What alternative approaches did you consider?"
- "If I challenged [X], how would you defend it?"

FIRST MESSAGE:
"Hello! I've read your manuscript carefully. Let's begin the oral examination. I'd like to start by asking you about [specific aspect from their manuscript]..."

Be professional, probing, and fair. Your goal is to assess genuine understanding of their own work.
"""

        try:
            response = self.elevenlabs.conversational_ai.agents.create(
                name=f"Manuscript Examiner",
                conversation_config={
                    "agent": {
                        "prompt": {
                            "prompt": agent_prompt
                        },
                        "first_message": f"Hello! I've read your manuscript on '{assignment_prompt[:50]}...' Let's begin the oral examination. "
                    }
                }
            )

            return response.agent_id

        except Exception as e:
            print(f"Error creating agent: {e}")
            return None

    def create_exam_session_with_manuscript(self, student_id: str, manuscript_path: str, assignment_prompt: str):
        """
        Create an exam session with manuscript analysis

        Args:
            student_id: Student identifier
            manuscript_path: Path to manuscript file
            assignment_prompt: The assignment description
        """

        # Read manuscript
        try:
            with open(manuscript_path, 'r', encoding='utf-8') as f:
                manuscript_text = f.read()
        except Exception as e:
            print(f"Error reading manuscript: {e}")
            return None

        # Get student info
        student = self.db.get_student(student_id)
        if not student:
            print(f"Student {student_id} not found")
            return None

        # Create exam session
        exam_session = self.db.create_exam_session(
            student_id=student_id,
            student_name=student['name'],
            exam_type='manuscript_viva'
        )

        # Store manuscript in session
        self.db.update_exam_session(
            exam_session['id'],
            transcript=f"[MANUSCRIPT SUBMITTED]\n\n{manuscript_text}\n\n[ORAL EXAMINATION TO FOLLOW]"
        )

        # Create custom agent for this manuscript
        agent_id = self.create_manuscript_exam_agent(manuscript_text, assignment_prompt)

        if not agent_id:
            print("Failed to create examination agent")
            return None

        print(f"\nExam session created!")
        print(f"Session ID: {exam_session['id']}")
        print(f"Agent ID: {agent_id}")
        print(f"Manuscript loaded: {len(manuscript_text)} characters")

        return {
            'session_id': exam_session['id'],
            'agent_id': agent_id,
            'manuscript_length': len(manuscript_text)
        }

    def generate_widget_html(self, agent_id: str, session_id: int, student_name: str):
        """Generate HTML page for conducting the exam"""

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Oral Examination - {student_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin: 0 0 10px 0;
        }}
        .session-info {{
            color: #7f8c8d;
            margin: 10px 0;
        }}
        .instructions {{
            background: #e8f4f8;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }}
        .widget-container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .status {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .warning {{
            background: #fff3cd;
            border: 1px solid #ffeeba;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Oral Examination - Manuscript Viva</h1>
        <div class="session-info">
            <strong>Student:</strong> {student_name}<br>
            <strong>Session ID:</strong> {session_id}<br>
            <strong>Status:</strong> Ready to begin
        </div>
    </div>

    <div class="instructions">
        <h2>Examination Instructions</h2>
        <ol>
            <li><strong>The AI examiner has already read your manuscript</strong></li>
            <li>Click the voice icon below to begin the oral examination</li>
            <li>The examiner will ask 7-10 questions about your manuscript</li>
            <li>Questions will reference specific parts of your work</li>
            <li>Answer thoughtfully - the examiner wants to understand your thinking</li>
            <li>You can ask the examiner to repeat questions if needed</li>
            <li>The conversation will be automatically transcribed</li>
            <li>After completion, your responses will be evaluated</li>
        </ol>
    </div>

    <div class="warning">
        <strong>Important:</strong> Make sure your microphone is enabled in your browser before starting.
    </div>

    <div class="widget-container">
        <h3>Begin Oral Examination</h3>
        <p>Click the microphone icon to start speaking with the examiner.</p>

        <!-- ElevenLabs Conversational AI Widget -->
        <elevenlabs-convai agent-id="{agent_id}"></elevenlabs-convai>
        <script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async></script>
    </div>

    <div class="status">
        <strong>After the examination:</strong><br>
        Your oral responses will be combined with your manuscript and evaluated by a panel of AI graders.
        You'll receive detailed feedback on both your written work and your oral defense.
    </div>

    <script>
        // Save transcript when exam completes
        // (This would integrate with your backend API)
        console.log('Session ID: {session_id}');
        console.log('Agent ID: {agent_id}');
    </script>
</body>
</html>
"""

        filename = f"exam_session_{session_id}.html"
        filepath = os.path.join('exam_pages', filename)

        os.makedirs('exam_pages', exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"\nExam page created: {filepath}")
        print(f"Open this file in a browser to conduct the examination")

        return filepath


def create_sample_manuscript_exam():
    """Demo: Create an exam session for a sample manuscript"""

    system = ManuscriptExamSystem()

    # Sample manuscript
    sample_manuscript = """
TITLE: The Impact of Machine Learning on Healthcare Diagnostics

ABSTRACT:
This paper examines how machine learning algorithms are revolutionizing healthcare diagnostics,
particularly in radiology and pathology. We analyze the benefits, challenges, and ethical
considerations of deploying AI systems in clinical settings.

INTRODUCTION:
The healthcare industry is experiencing a transformation driven by artificial intelligence and
machine learning. Medical imaging, in particular, has benefited from convolutional neural networks
(CNNs) that can detect patterns invisible to the human eye. Studies show that AI systems can
match or exceed human performance in detecting certain conditions.

METHODOLOGY:
We conducted a literature review of 50 peer-reviewed articles published between 2020-2024.
We focused on studies that compared AI diagnostic performance to human clinicians. We also
interviewed 10 radiologists about their experiences with AI-assisted diagnosis.

FINDINGS:
1. AI systems achieved 94% accuracy in detecting lung cancer from CT scans
2. Radiologists using AI assistance were 23% faster in their diagnoses
3. However, 67% of clinicians expressed concerns about over-reliance on AI
4. False negatives in AI systems can be dangerous when used without human oversight

DISCUSSION:
While AI shows promise, human expertise remains essential. The optimal approach appears to be
AI-assisted diagnosis rather than full automation. Clinicians should use AI as a tool to augment
their capabilities, not replace their judgment.

CONCLUSION:
Machine learning has significant potential in healthcare diagnostics, but successful implementation
requires careful attention to validation, training, and maintaining the human element in medical
decision-making.
"""

    # Assignment prompt
    assignment = """
Write a 1000-word research paper on a topic related to AI or machine learning applications.
Your paper should include: introduction, methodology, findings, discussion, and conclusion.
Use at least 10 peer-reviewed sources and provide specific examples.
"""

    # Save sample manuscript
    os.makedirs('sample_manuscripts', exist_ok=True)
    manuscript_path = 'sample_manuscripts/healthcare_ai_paper.txt'
    with open(manuscript_path, 'w', encoding='utf-8') as f:
        f.write(sample_manuscript)

    print("="*60)
    print("MANUSCRIPT-BASED ORAL EXAM - DEMO")
    print("="*60)
    print(f"\nSample manuscript created: {manuscript_path}")
    print(f"Assignment: {assignment[:100]}...")

    # Create exam for a sample student (assuming Alice Chen exists)
    print("\nCreating exam session for Alice Chen...")

    result = system.create_exam_session_with_manuscript(
        student_id='S001',
        manuscript_path=manuscript_path,
        assignment_prompt=assignment
    )

    if result:
        # Generate exam page
        html_path = system.generate_widget_html(
            agent_id=result['agent_id'],
            session_id=result['session_id'],
            student_name='Alice Chen'
        )

        print("\n" + "="*60)
        print("EXAM SESSION READY")
        print("="*60)
        print(f"\nTo conduct the oral examination:")
        print(f"1. Open: {html_path}")
        print(f"2. Click the microphone icon")
        print(f"3. The AI will ask questions about the manuscript")
        print(f"4. Speak your answers naturally")
        print(f"\nThe examiner will ask questions like:")
        print("- 'In your methodology, you mentioned interviewing radiologists. How did you select them?'")
        print("- 'You claimed 94% accuracy. What were the limitations of this finding?'")
        print("- 'Can you elaborate on why you concluded AI should augment rather than replace clinicians?'")


if __name__ == '__main__':
    create_sample_manuscript_exam()
