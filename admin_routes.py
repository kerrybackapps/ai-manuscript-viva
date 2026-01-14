"""
Admin Control Panel Routes
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from database import Database, ExamSession, GradingResult, Student, Setting
from sqlalchemy import select, desc
import os
from datetime import datetime, timedelta
from admin_config import ADMIN_PASSWORD, PROMPTS_DIR

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
db = Database()

# Model name mapping for display
MODEL_DISPLAY_NAMES = {
    'claude': 'Claude Opus 4.5',
    'gpt': 'OpenAI GPT-5.2',
    'gemini': 'Gemini 3.0'
}

def get_model_display_name(model_key):
    """Convert model key to full display name"""
    return MODEL_DISPLAY_NAMES.get(model_key, model_key.upper())

def utc_to_cst(utc_dt):
    """Convert UTC datetime to CST (UTC-6)"""
    if utc_dt is None:
        return None
    # CST is UTC-6
    return utc_dt - timedelta(hours=6)

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            # Check if this is an AJAX/fetch request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
               request.headers.get('Content-Type') == 'application/json' or \
               request.path.startswith('/admin/exam/') and request.method == 'POST':
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            return redirect(url_for('admin.admin_home'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/', methods=['GET', 'POST'])
def admin_home():
    """Admin login page - redirects to dashboard if already logged in"""
    # If already logged in, redirect to dashboard
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))

    # Otherwise show login form
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session.permanent = True
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid password')
    return render_template('admin_login.html')


@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_home'))


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard - show all exam sessions"""
    with db.Session() as s:
        # Get all exam sessions with student info
        sessions = s.execute(
            select(ExamSession).order_by(desc(ExamSession.created_at))
        ).scalars().all()

        # Get grading results for each session
        sessions_data = []
        for exam in sessions:
            results = s.execute(
                select(GradingResult).where(GradingResult.session_id == exam.id)
            ).scalars().all()

            # Calculate average scores
            manuscript_scores = [r.overall_score for r in results if '_manuscript' in r.model_name]
            oral_scores = [r.overall_score for r in results if '_oral' in r.model_name]

            sessions_data.append({
                'id': exam.id,
                'student_name': exam.student_name,
                'exam_type': exam.exam_type,
                'created_at': utc_to_cst(exam.created_at),
                'has_grades': len(results) > 0,
                'manuscript_avg': sum(manuscript_scores) / len(manuscript_scores) if manuscript_scores else 0,
                'oral_avg': sum(oral_scores) / len(oral_scores) if oral_scores else 0,
                'grader_count': len(results)
            })

    return render_template('admin_dashboard.html', sessions=sessions_data)


@admin_bp.route('/exam/<int:session_id>')
@admin_required
def exam_detail(session_id):
    """Detailed view of exam session with all grading"""
    return render_template('admin_exam_detail.html', session_id=session_id)


@admin_bp.route('/api/exam/<int:session_id>')
@admin_required
def api_exam_detail(session_id):
    """API endpoint for exam detail data"""
    with db.Session() as s:
        # Get exam session
        exam = s.execute(
            select(ExamSession).where(ExamSession.id == session_id)
        ).scalar_one_or_none()

        if not exam:
            return jsonify({'error': 'Exam not found'}), 404

        # Get grading results
        results = s.execute(
            select(GradingResult).where(GradingResult.session_id == session_id)
        ).scalars().all()

        # Separate manuscript and oral results
        manuscript_results = []
        oral_results = []

        for r in results:
            model_key = r.model_name.replace('_manuscript', '').replace('_oral', '')
            result_data = {
                'model': model_key,
                'model_display_name': get_model_display_name(model_key),
                'score': r.overall_score,
                'categories': r.category_scores,
                'assessment': r.assessment,
                'cost': r.cost,
                'round': r.round_number
            }

            if '_manuscript' in r.model_name:
                manuscript_results.append(result_data)
            elif '_oral' in r.model_name:
                oral_results.append(result_data)

        return jsonify({
            'id': exam.id,
            'student_name': exam.student_name,
            'student_id': exam.student_id,
            'exam_type': exam.exam_type,
            'created_at': exam.created_at.isoformat(),
            'transcript': exam.transcript,  # Legacy combined transcript
            'manuscript_content': exam.manuscript_content,
            'manuscript_file_path': exam.manuscript_file_path,
            'oral_transcript': exam.oral_transcript,
            'manuscript_results': manuscript_results,
            'oral_results': oral_results,
            'manuscript_avg': sum(r['score'] for r in manuscript_results) / len(manuscript_results) if manuscript_results else None,
            'oral_avg': sum(r['score'] for r in oral_results) / len(oral_results) if oral_results else None
        })


@admin_bp.route('/exam/<int:session_id>/delete', methods=['POST'])
@admin_required
def delete_exam(session_id):
    """Delete an exam session and all associated data"""
    try:
        db.delete_exam_session(session_id)
        return jsonify({'success': True, 'message': 'Exam deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/exam/<int:session_id>/grade', methods=['POST'])
@admin_required
def grade_exam_admin(session_id):
    """Manually trigger grading for an exam session"""
    try:
        from demo_app import system
        from elevenlabs.client import ElevenLabs
        import os

        # Get model_set from request JSON
        data = request.get_json() or {}
        model_set = data.get('model_set', '2')  # Default to full models

        # Get exam session
        exam = db.get_exam_session(session_id)
        if not exam:
            return jsonify({'success': False, 'error': 'Exam session not found'}), 404

        # Fetch transcript from ElevenLabs if not already present
        if not exam.get('oral_transcript') and exam.get('agent_id'):
            print(f"[ADMIN GRADING] Fetching transcript for agent {exam['agent_id']}")

            try:
                elevenlabs_client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))

                # DEBUG: Try to get conversations
                print("[DEBUG] Attempting to list conversations...")
                try:
                    conversations_response = elevenlabs_client.conversational_ai.conversations.list(agent_id=exam['agent_id'])
                    print(f"[DEBUG] Response type: {type(conversations_response)}")

                    # Try to get the first item to see structure
                    conversations = list(conversations_response) if conversations_response else []
                    print(f"[DEBUG] Number of conversations: {len(conversations)}")

                    if conversations:
                        first_item = conversations[0]
                        print(f"[DEBUG] First item type: {type(first_item)}")

                        # Handle tuple structure: ('conversations', [actual conversation list])
                        actual_conversations = []
                        if isinstance(first_item, tuple) and len(first_item) == 2:
                            print(f"[DEBUG] Item is tuple with {len(first_item)} elements")
                            print(f"[DEBUG] Tuple[0]: {first_item[0]}")
                            print(f"[DEBUG] Tuple[1] type: {type(first_item[1])}")
                            if isinstance(first_item[1], list):
                                actual_conversations = first_item[1]
                                print(f"[DEBUG] Extracted {len(actual_conversations)} conversations from tuple")
                        else:
                            actual_conversations = [first_item]
                            print(f"[DEBUG] Using first_item directly")

                        # Now get conversation_id from the actual conversation object
                        conversation_id = None
                        if actual_conversations:
                            first_conv = actual_conversations[0]
                            print(f"[DEBUG] First conversation type: {type(first_conv)}")

                            # Extract conversation_id
                            if hasattr(first_conv, 'conversation_id'):
                                conversation_id = first_conv.conversation_id
                                print(f"[DEBUG] Got conversation_id from attribute: {conversation_id}")
                            elif isinstance(first_conv, dict):
                                conversation_id = first_conv.get('conversation_id')
                                print(f"[DEBUG] Got conversation_id from dict: {conversation_id}")

                        if conversation_id:
                            print(f"[ADMIN GRADING] Successfully extracted conversation_id: {conversation_id}")

                            # Get conversation details
                            print(f"[DEBUG] Fetching conversation details...")
                            conversation = elevenlabs_client.conversational_ai.conversations.get(conversation_id=conversation_id)
                            print(f"[DEBUG] Conversation details type: {type(conversation)}")

                            # Extract transcript - API uses 'transcript' field not 'messages'
                            transcript_lines = []

                            # Get transcript from conversation (list of transcript entries)
                            transcript_entries = None
                            if hasattr(conversation, 'transcript'):
                                transcript_entries = conversation.transcript
                                print(f"[DEBUG] Got transcript from attribute, count: {len(transcript_entries) if transcript_entries else 0}")
                            elif isinstance(conversation, dict) and 'transcript' in conversation:
                                transcript_entries = conversation['transcript']
                                print(f"[DEBUG] Got transcript from dict, count: {len(transcript_entries) if transcript_entries else 0}")
                            else:
                                print(f"[DEBUG] No transcript field found, checking conversation structure...")
                                if hasattr(conversation, '__dict__'):
                                    print(f"[DEBUG] Conversation attributes: {list(conversation.__dict__.keys())}")

                            if transcript_entries:
                                for i, entry in enumerate(transcript_entries):
                                    print(f"[DEBUG] Transcript entry {i} type: {type(entry)}")

                                    role = None
                                    content = None

                                    # According to ElevenLabs API docs, each entry has 'role' and 'message'
                                    if hasattr(entry, 'role'):
                                        role = entry.role
                                        content = entry.message if hasattr(entry, 'message') else None
                                    elif isinstance(entry, dict):
                                        role = entry.get('role')
                                        content = entry.get('message')

                                    if role and content:
                                        transcript_lines.append(f"{role.upper()}: {content}")
                                        print(f"[DEBUG] Added entry: {role} ({len(content)} chars)")
                                    else:
                                        print(f"[DEBUG] Skipped entry {i}: role={role}, content={'<empty>' if not content else '<present>'}")

                            oral_transcript = "\n\n".join(transcript_lines)
                            print(f"[ADMIN GRADING] Successfully extracted transcript: {len(oral_transcript)} chars, {len(transcript_lines)} messages")

                            if len(oral_transcript) > 0:
                                # Update exam session with transcript
                                db.update_exam_session(
                                    session_id,
                                    oral_transcript=oral_transcript,
                                    conversation_id=conversation_id,
                                    status='completed'
                                )
                                print(f"[ADMIN GRADING] Transcript saved to database")
                            else:
                                print(f"[ADMIN GRADING WARNING] Transcript is empty")
                        else:
                            print(f"[ADMIN GRADING ERROR] Could not extract conversation_id from response")
                    else:
                        print("[ADMIN GRADING] No conversations found for this agent")

                except Exception as inner_e:
                    print(f"[DEBUG ERROR] Exception during conversation fetch: {type(inner_e).__name__}: {inner_e}")
                    import traceback
                    print(f"[DEBUG] Traceback: {traceback.format_exc()}")

            except Exception as e:
                print(f"[ADMIN GRADING ERROR] Failed to fetch transcript: {e}")
                import traceback
                print(f"[DEBUG] Outer traceback: {traceback.format_exc()}")
                # Continue with grading even if transcript fetch fails

        # Proceed with grading with selected model set
        results = system.grade_manuscript_and_oral(session_id, model_set=model_set)
        if results:
            return jsonify({'success': True, 'message': 'Grading completed successfully'})
        else:
            return jsonify({'success': False, 'error': 'Grading failed'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/prompts')
@admin_required
def prompts():
    """List all editable prompts"""
    from database import Prompt
    from sqlalchemy import select

    with db.Session() as s:
        all_prompts = s.execute(select(Prompt).order_by(Prompt.category, Prompt.name)).scalars().all()
        prompts_list = [p.to_dict() for p in all_prompts]

    return render_template('admin_prompts.html', prompts=prompts_list)


@admin_bp.route('/prompts/<prompt_name>', methods=['GET', 'POST'])
@admin_required
def edit_prompt(prompt_name):
    """Edit a specific prompt"""
    from database import Prompt
    from sqlalchemy import select

    with db.Session() as s:
        prompt = s.execute(
            select(Prompt).where(Prompt.name == prompt_name)
        ).scalar_one_or_none()

        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404

        if request.method == 'POST':
            content = request.form.get('content', '')
            prompt.content = content
            prompt.version += 1
            prompt.updated_by = 'admin'  # Could track actual admin user if auth implemented
            s.commit()
            return jsonify({'success': True, 'message': 'Prompt updated successfully'})

        # GET request - return editor page
        prompt_data = prompt.to_dict()

    return render_template('admin_prompt_editor.html',
                         prompt_name=prompt_name,
                         display_name=prompt_data['display_name'],
                         content=prompt_data['content'],
                         version=prompt_data['version'])


@admin_bp.route('/api/prompts/<prompt_name>')
@admin_required
def api_get_prompt(prompt_name):
    """API endpoint to get prompt content"""
    from database import Prompt
    from sqlalchemy import select

    with db.Session() as s:
        prompt = s.execute(
            select(Prompt).where(Prompt.name == prompt_name)
        ).scalar_one_or_none()

        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404

        return jsonify(prompt.to_dict())


@admin_bp.route('/api/prompts/<prompt_name>', methods=['POST'])
@admin_required
def api_update_prompt(prompt_name):
    """API endpoint to update prompt content"""
    from database import Prompt
    from sqlalchemy import select

    with db.Session() as s:
        prompt = s.execute(
            select(Prompt).where(Prompt.name == prompt_name)
        ).scalar_one_or_none()

        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404

        content = request.json.get('content', '')
        prompt.content = content
        prompt.version += 1
        prompt.updated_by = 'admin'
        s.commit()

        return jsonify({'success': True, 'message': 'Prompt updated successfully', 'version': prompt.version})


@admin_bp.route('/settings')
@admin_required
def settings():
    """View and edit app settings"""
    with db.Session() as s:
        all_settings = s.execute(select(Setting).order_by(Setting.key)).scalars().all()
        settings_list = [setting.to_dict() for setting in all_settings]

    return render_template('admin_settings.html', settings=settings_list)


@admin_bp.route('/settings/<setting_key>', methods=['GET', 'POST'])
@admin_required
def edit_setting(setting_key):
    """Edit a specific setting"""
    with db.Session() as s:
        setting = s.execute(
            select(Setting).where(Setting.key == setting_key)
        ).scalar_one_or_none()

        if not setting:
            return jsonify({'error': 'Setting not found'}), 404

        if request.method == 'POST':
            value = request.form.get('value', '')
            setting.value = value
            setting.updated_by = 'admin'
            s.commit()
            return jsonify({'success': True, 'message': 'Setting updated successfully'})

        # GET request - return editor page
        setting_data = setting.to_dict()

    return render_template('admin_setting_editor.html',
                         setting_key=setting_key,
                         display_name=setting_key.replace('_', ' ').title(),
                         value=setting_data['value'],
                         description=setting_data.get('description', ''))


@admin_bp.route('/test-transcript', methods=['GET'])
@admin_required
def test_transcript():
    """Test endpoint for ElevenLabs transcript retrieval"""
    from elevenlabs.client import ElevenLabs

    try:
        elevenlabs_client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        agent_id = os.getenv('ELEVENLABS_AGENT_ID')

        # List recent conversations
        conversations_response = elevenlabs_client.conversational_ai.conversations.list(agent_id=agent_id)

        # Extract conversations from tuple if needed
        if isinstance(conversations_response, tuple):
            conversations = list(conversations_response[1]) if len(conversations_response) > 1 else []
        else:
            conversations = list(conversations_response) if conversations_response else []

        results = []
        for conv in conversations[:3]:  # Test first 3 conversations
            conv_id = conv.conversation_id if hasattr(conv, 'conversation_id') else conv.get('conversation_id')

            # Fetch full conversation
            conversation = elevenlabs_client.conversational_ai.conversations.get(conversation_id=conv_id)

            # Extract transcript
            transcript_lines = []
            transcript_entries = None

            if hasattr(conversation, 'transcript'):
                transcript_entries = conversation.transcript
            elif isinstance(conversation, dict) and 'transcript' in conversation:
                transcript_entries = conversation['transcript']

            if transcript_entries:
                for entry in transcript_entries:
                    role = None
                    content = None

                    if hasattr(entry, 'role'):
                        role = entry.role
                        content = entry.message if hasattr(entry, 'message') else None
                    elif isinstance(entry, dict):
                        role = entry.get('role')
                        content = entry.get('message')

                    if role and content:
                        transcript_lines.append(f"{role.upper()}: {content[:100]}...")  # First 100 chars

            results.append({
                'conversation_id': conv_id,
                'transcript_count': len(transcript_lines),
                'sample': transcript_lines[:2] if transcript_lines else ['No transcript entries']
            })

        return jsonify({
            'success': True,
            'agent_id': agent_id,
            'conversations_found': len(conversations),
            'tested': results
        })

    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
