"""
Admin Control Panel Routes
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from database import Database, ExamSession, GradingResult, Student
from sqlalchemy import select, desc
import os
from admin_config import ADMIN_PASSWORD, PROMPTS_DIR

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
db = Database()

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
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
                'created_at': exam.created_at,
                'has_grades': len(results) > 0,
                'manuscript_avg': sum(manuscript_scores) / len(manuscript_scores) if manuscript_scores else None,
                'oral_avg': sum(oral_scores) / len(oral_scores) if oral_scores else None,
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
            result_data = {
                'model': r.model_name.replace('_manuscript', '').replace('_oral', ''),
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
            'transcript': exam.transcript,
            'manuscript_results': manuscript_results,
            'oral_results': oral_results,
            'manuscript_avg': sum(r['score'] for r in manuscript_results) / len(manuscript_results) if manuscript_results else None,
            'oral_avg': sum(r['score'] for r in oral_results) / len(oral_results) if oral_results else None
        })


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
