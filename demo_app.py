"""
Manuscript Viva Demo - Standalone Application for Sharing
"""
import os
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from manuscript_viva_system import ManuscriptVivaSystem
from database import Database, Setting
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import select

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

os.makedirs('uploads', exist_ok=True)

db = Database()
system = ManuscriptVivaSystem()

# Initialize database with prompts and settings on first run
def init_database():
    """Initialize database with prompts and settings if they don't exist"""
    try:
        from initialize_prompts import initialize_prompts, initialize_settings
        initialize_prompts()
        initialize_settings()
    except Exception as e:
        print(f"Database initialization: {e}")

# Run initialization
try:
    init_database()
except:
    pass  # Database already initialized

# Register admin blueprint
from admin_routes import admin_bp
app.register_blueprint(admin_bp)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Upload manuscript page"""
    # Fetch assignment from database
    assignment = "Write a 10-15 page paper comparing and contrasting political developments of the past ten years to either Ayn Rand's Atlas Shrugged or George Orwell's 1984."  # Default fallback
    with db.Session() as session:
        setting = session.execute(
            select(Setting).where(Setting.key == 'assignment')
        ).scalar_one_or_none()
        if setting:
            assignment = setting.value

    return render_template('demo_upload.html', assignment=assignment)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload manuscript and create exam session"""
    if request.method == 'GET':
        # Fetch assignment from database
        assignment = "Write a 10-15 page paper comparing and contrasting political developments of the past ten years to either Ayn Rand's Atlas Shrugged or George Orwell's 1984."  # Default fallback
        with db.Session() as session:
            setting = session.execute(
                select(Setting).where(Setting.key == 'assignment')
            ).scalar_one_or_none()
            if setting:
                assignment = setting.value
        return render_template('demo_upload.html', assignment=assignment)

    # Handle POST - file upload
    if 'manuscript' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['manuscript']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use PDF, DOCX, or TXT'}), 400

    # Get form data
    student_name = request.form.get('student_name', 'Demo User')

    # Get assignment from database
    assignment = "Write a 10-15 page paper comparing and contrasting political developments of the past ten years to either Ayn Rand's Atlas Shrugged or George Orwell's 1984."  # Default fallback
    with db.Session() as session:
        setting = session.execute(
            select(Setting).where(Setting.key == 'assignment')
        ).scalar_one_or_none()
        if setting:
            assignment = setting.value

    # Save uploaded file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)

    # Create or get student
    student_id = f"DEMO_{timestamp}"
    student = db.add_student(student_id, student_name, f"{student_name.lower().replace(' ', '.')}@demo.edu")

    # Process manuscript and create exam
    try:
        result = system.process_manuscript_submission(
            student_id=student_id,
            manuscript_path=filepath,
            assignment_prompt=assignment
        )

        if result:
            # Generate exam page
            exam_page = system.generate_exam_page(
                agent_id=result['agent_id'],
                session_id=result['session_id'],
                student_name=student_name
            )

            return jsonify({
                'success': True,
                'session_id': result['session_id'],
                'exam_url': f"/exam/{result['session_id']}"
            })
        else:
            return jsonify({'error': 'Failed to create exam session'}), 500

    except Exception as e:
        return jsonify({'error': f'Error processing manuscript: {str(e)}'}), 500


@app.route('/exam/<int:session_id>')
def exam_page(session_id):
    """Display the exam page"""
    exam_file = f"exam_pages/exam_session_{session_id}.html"
    if os.path.exists(exam_file):
        return send_file(exam_file)
    else:
        return "Exam session not found", 404


@app.route('/webhook/elevenlabs', methods=['POST'])
def elevenlabs_webhook():
    """Handle ElevenLabs conversation completion webhook"""
    try:
        from elevenlabs.client import ElevenLabs
        import json

        # Get webhook data
        data = request.get_json()
        print(f"[WEBHOOK] Received: {json.dumps(data, indent=2)}")

        # Extract conversation ID from webhook
        conversation_id = data.get('conversation_id') or data.get('conversationId')
        agent_id = data.get('agent_id') or data.get('agentId')

        if not conversation_id:
            print("[WEBHOOK ERROR] No conversation_id in webhook data")
            return jsonify({'error': 'No conversation_id'}), 400

        print(f"[WEBHOOK] Processing conversation: {conversation_id}, agent: {agent_id}")

        # Find exam session by agent_id (more reliable than finding pending exam)
        exam = None
        if agent_id:
            print(f"[WEBHOOK] Looking for exam with agent_id: {agent_id}")
            exams = db.get_all_exams(limit=50)
            exam = next((e for e in exams if e.get('agent_id') == agent_id), None)
            if exam:
                print(f"[WEBHOOK] Found exam by agent_id: session {exam['id']}")

        # Fallback to most recent pending exam if no agent_id match
        if not exam:
            print("[WEBHOOK] No agent_id match, trying most recent pending exam")
            exams = db.get_all_exams(limit=10)
            exam = next((e for e in exams if e.get('status') == 'pending'), None)

        if not exam:
            print("[WEBHOOK ERROR] No matching exam session found")
            return jsonify({'error': 'No matching exam session'}), 404

        session_id = exam['id']
        print(f"[WEBHOOK] Matched to exam session {session_id}")

        # Fetch transcript from ElevenLabs with comprehensive debugging
        elevenlabs_client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        oral_transcript = ""

        try:
            print(f"[WEBHOOK DEBUG] Fetching conversation details for {conversation_id}")

            # Try the conversations.get() method (matches admin code)
            conversation = elevenlabs_client.conversational_ai.conversations.get(conversation_id=conversation_id)
            print(f"[WEBHOOK DEBUG] Conversation type: {type(conversation)}")
            print(f"[WEBHOOK DEBUG] Conversation value: {conversation}")

            # Extract transcript with extensive debugging
            transcript_lines = []

            # Try different ways to get messages
            messages = None
            if hasattr(conversation, 'messages'):
                messages = conversation.messages
                print(f"[WEBHOOK DEBUG] Got messages from attribute, count: {len(messages) if messages else 0}")
            elif isinstance(conversation, dict) and 'messages' in conversation:
                messages = conversation['messages']
                print(f"[WEBHOOK DEBUG] Got messages from dict, count: {len(messages) if messages else 0}")
            else:
                print(f"[WEBHOOK DEBUG] No messages found, checking conversation structure...")
                if hasattr(conversation, '__dict__'):
                    print(f"[WEBHOOK DEBUG] Conversation attributes: {conversation.__dict__.keys()}")

            if messages:
                for i, message in enumerate(messages):
                    print(f"[WEBHOOK DEBUG] Message {i} type: {type(message)}")

                    role = None
                    content = None

                    if hasattr(message, 'role'):
                        role = message.role
                        content = message.message if hasattr(message, 'message') else ''
                    elif isinstance(message, dict):
                        role = message.get('role')
                        content = message.get('message', '')

                    if role and content:
                        transcript_lines.append(f"{role.upper()}: {content}")
                        print(f"[WEBHOOK DEBUG] Added message: {role} ({len(content)} chars)")
                    else:
                        print(f"[WEBHOOK DEBUG] Could not extract message {i}: role={role}, content_len={len(content) if content else 0}")

            oral_transcript = "\n\n".join(transcript_lines)
            print(f"[WEBHOOK] Successfully extracted transcript: {len(oral_transcript)} chars, {len(transcript_lines)} messages")

            if not oral_transcript:
                print(f"[WEBHOOK WARNING] Transcript is empty!")
                oral_transcript = "[Empty transcript - no messages found]"

        except Exception as e:
            print(f"[WEBHOOK ERROR] Failed to fetch transcript: {type(e).__name__}: {e}")
            import traceback
            print(f"[WEBHOOK DEBUG] Traceback: {traceback.format_exc()}")
            oral_transcript = f"[Transcript fetch failed: {str(e)}]"

        # Update exam session with transcript and conversation_id
        db.update_exam_session(
            session_id,
            oral_transcript=oral_transcript,
            conversation_id=conversation_id,
            status='completed',
            completed_at=datetime.now()
        )
        print(f"[WEBHOOK] Updated exam session {session_id} with transcript ({len(oral_transcript)} chars)")

        # Trigger grading automatically
        try:
            results = system.grade_manuscript_and_oral(session_id)
            if results:
                print(f"[WEBHOOK] Grading completed successfully for session {session_id}")
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'grading_triggered': True
                })
            else:
                print(f"[WEBHOOK ERROR] Grading failed for session {session_id}")
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'grading_triggered': False,
                    'error': 'Grading failed'
                })
        except Exception as grading_error:
            print(f"[WEBHOOK ERROR] Grading exception: {grading_error}")
            return jsonify({
                'success': True,
                'session_id': session_id,
                'grading_triggered': False,
                'error': str(grading_error)
            }), 500

    except Exception as e:
        print(f"[WEBHOOK ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/grade/<int:session_id>', methods=['POST'])
def grade_exam(session_id):
    """Grade the completed exam (manual trigger or backup)"""
    try:
        results = system.grade_manuscript_and_oral(session_id)
        if results:
            return jsonify({
                'success': True,
                'results_url': f"/results/{session_id}"
            })
        else:
            return jsonify({'error': 'Grading failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results/<int:session_id>')
def view_results(session_id):
    """Display grading results"""
    return render_template('demo_results.html', session_id=session_id)


@app.route('/api/results/<int:session_id>')
def api_results(session_id):
    """API endpoint for results data"""
    from sqlalchemy import select
    from database import GradingResult, ExamSession

    with db.Session() as session:
        # Get exam session
        exam = session.execute(
            select(ExamSession).where(ExamSession.id == session_id)
        ).scalar_one_or_none()

        if not exam:
            return jsonify({'error': 'Session not found'}), 404

        # Get grading results
        results = session.execute(
            select(GradingResult).where(GradingResult.session_id == session_id)
        ).scalars().all()

        manuscript_results = [r for r in results if '_manuscript' in r.model_name]
        oral_results = [r for r in results if '_oral' in r.model_name]

        return jsonify({
            'student_name': exam.student_name,
            'exam_type': exam.exam_type,
            'created_at': exam.created_at.isoformat(),
            'manuscript_scores': [
                {
                    'model': r.model_name.replace('_manuscript', ''),
                    'score': r.overall_score,
                    'categories': r.category_scores,
                    'assessment': r.assessment
                } for r in manuscript_results
            ],
            'oral_scores': [
                {
                    'model': r.model_name.replace('_oral', ''),
                    'score': r.overall_score,
                    'categories': r.category_scores,
                    'assessment': r.assessment
                } for r in oral_results
            ]
        })


@app.route('/samples')
def samples():
    """List available sample manuscripts"""
    samples_dir = 'sample_manuscripts'
    samples = []
    if os.path.exists(samples_dir):
        for filename in os.listdir(samples_dir):
            if filename.endswith(('.txt', '.pdf', '.docx')):
                filepath = os.path.join(samples_dir, filename)
                samples.append({
                    'filename': filename,
                    'size': os.path.getsize(filepath),
                    'path': filepath
                })
    return render_template('demo_samples.html', samples=samples)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print("="*70)
    print(" MANUSCRIPT VIVA VOCE DEMO")
    print("="*70)
    print(f"\n Starting demo server on port {port}...")
    print(f" Open in browser: http://localhost:{port}")
    print("\n Press Ctrl+C to stop")
    print("="*70)
    app.run(debug=False, port=port, host='0.0.0.0')
