"""
Flask Web Application for AI Exam System
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from datetime import datetime
import json
import os
from dotenv import load_dotenv

from database import Database
from exam_conversation import ExamConversation
from grading_council import GradingCouncil

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize database
db = Database()


# Home / Dashboard
@app.route('/')
def index():
    """Main dashboard"""
    analytics = db.get_analytics()
    recent_exams = db.get_all_exams(limit=10)
    return render_template('dashboard.html', analytics=analytics, recent_exams=recent_exams)


# Student Management
@app.route('/students')
def students():
    """List all students"""
    all_students = db.get_all_students()
    return render_template('students.html', students=all_students)


@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    """Add a new student"""
    if request.method == 'POST':
        try:
            data = request.form
            student = db.add_student(
                student_id=data['student_id'],
                name=data['name'],
                email=data.get('email'),
                project_title=data.get('project_title'),
                project_description=data.get('project_description')
            )
            return redirect(url_for('students'))
        except Exception as e:
            return render_template('add_student.html', error=str(e))
    return render_template('add_student.html')


@app.route('/students/<student_id>')
def student_detail(student_id):
    """View student details and exam history"""
    student = db.get_student(student_id)
    if not student:
        return "Student not found", 404
    exams = db.get_student_exams(student_id)
    return render_template('student_detail.html', student=student, exams=exams)


# Exam Management
@app.route('/exams')
def exams():
    """List all exams"""
    all_exams = db.get_all_exams(limit=50)
    return render_template('exams.html', exams=all_exams)


@app.route('/exams/start', methods=['GET', 'POST'])
def start_exam():
    """Start a new exam"""
    if request.method == 'POST':
        try:
            data = request.form
            student_id = data['student_id']
            exam_type = data.get('exam_type', 'project')

            # Get student info
            student = db.get_student(student_id)
            if not student:
                return render_template('start_exam.html',
                                     students=db.get_all_students(),
                                     error="Student not found")

            # Create exam session
            exam_session = db.create_exam_session(
                student_id=student_id,
                student_name=student['name'],
                exam_type=exam_type
            )

            # Redirect to conduct exam
            return redirect(url_for('conduct_exam', session_id=exam_session['id']))

        except Exception as e:
            return render_template('start_exam.html',
                                 students=db.get_all_students(),
                                 error=str(e))

    students = db.get_all_students()
    return render_template('start_exam.html', students=students)


@app.route('/exams/<int:session_id>/conduct')
def conduct_exam(session_id):
    """Conduct exam interface (for text-based exams)"""
    exam = db.get_exam_session(session_id)
    if not exam:
        return "Exam session not found", 404

    student = db.get_student(exam['student_id'])
    return render_template('conduct_exam.html', exam=exam, student=student)


@app.route('/exams/<int:session_id>/view')
def view_exam(session_id):
    """View exam details and transcript"""
    exam = db.get_exam_session(session_id)
    if not exam:
        return "Exam session not found", 404

    grades = db.get_session_grades(session_id)

    # Group grades by round
    grades_by_round = {}
    for grade in grades:
        round_num = grade['round_number']
        if round_num not in grades_by_round:
            grades_by_round[round_num] = {}
        grades_by_round[round_num][grade['model_name']] = grade

    # Calculate convergence for final round
    convergence = None
    if grades_by_round:
        final_round = max(grades_by_round.keys())
        final_grades = grades_by_round[final_round]
        scores = [g['overall_score'] for g in final_grades.values() if g['overall_score']]
        if len(scores) >= 2:
            avg_score = sum(scores) / len(scores)
            within_1 = all(abs(scores[i] - scores[j]) <= 1.0
                          for i in range(len(scores))
                          for j in range(i+1, len(scores)))
            convergence = {
                'average': round(avg_score, 2),
                'within_1_point': within_1,
                'range': f"{min(scores)} - {max(scores)}"
            }

    return render_template('view_exam.html', exam=exam, grades=grades,
                         grades_by_round=grades_by_round, convergence=convergence)


# Scenarios Management
@app.route('/scenarios')
def scenarios():
    """List all scenarios"""
    all_scenarios = db.get_all_scenarios()
    return render_template('scenarios.html', scenarios=all_scenarios)


@app.route('/scenarios/add', methods=['GET', 'POST'])
def add_scenario():
    """Add a new scenario"""
    if request.method == 'POST':
        try:
            data = request.form
            scenario = db.add_scenario(
                title=data['title'],
                description=data['description'],
                category=data['category'],
                difficulty=data.get('difficulty', 'medium')
            )
            return redirect(url_for('scenarios'))
        except Exception as e:
            return render_template('add_scenario.html', error=str(e))
    return render_template('add_scenario.html')


# Analytics
@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    analytics_data = db.get_analytics()
    recent_exams = db.get_all_exams(limit=20)
    return render_template('analytics.html', analytics=analytics_data, exams=recent_exams)


# API Endpoints
@app.route('/api/exams/<int:session_id>/grade', methods=['POST'])
def grade_exam_api(session_id):
    """Grade an exam using the grading council"""
    try:
        exam = db.get_exam_session(session_id)
        if not exam:
            return jsonify({'error': 'Exam not found'}), 404

        if not exam['transcript']:
            return jsonify({'error': 'No transcript available'}), 400

        # Load rubric
        rubric_path = 'sample_rubric.txt'
        with open(rubric_path, 'r') as f:
            rubric = f.read()

        # Grade with council
        council = GradingCouncil()
        deliberation_rounds = request.json.get('deliberation_rounds', 1) if request.json else 1

        results = council.conduct_grading(
            transcript=exam['transcript'],
            rubric=rubric,
            deliberation_rounds=deliberation_rounds
        )

        # Save results to database
        for round_num in range(1, deliberation_rounds + 2):
            round_key = f'round_{round_num}'
            if round_key in results:
                for model_name, grade_data in results[round_key].items():
                    if 'error' not in grade_data:
                        db.save_grading_result(
                            session_id=session_id,
                            model_name=model_name,
                            round_number=round_num,
                            overall_score=grade_data.get('overall_score'),
                            category_scores=grade_data.get('scores', {}),
                            assessment=grade_data.get('overall_assessment', ''),
                            cost=estimate_cost(model_name, grade_data)
                        )

        # Update exam status
        db.update_exam_session(session_id, status='completed', completed_at=datetime.utcnow())

        return jsonify({
            'success': True,
            'convergence': results.get('convergence_metrics', {}),
            'grades': results.get('final_grades', {})
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/exams/<int:session_id>/transcript', methods=['POST'])
def save_transcript_api(session_id):
    """Save exam transcript"""
    try:
        data = request.json
        transcript = data.get('transcript')

        if not transcript:
            return jsonify({'error': 'Transcript required'}), 400

        db.update_exam_session(
            session_id,
            transcript=transcript,
            status='grading'
        )

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scenarios/random')
def random_scenario_api():
    """Get a random scenario"""
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')

    scenario = db.get_random_scenario(category=category, difficulty=difficulty)
    if scenario:
        return jsonify(scenario)
    return jsonify({'error': 'No scenarios found'}), 404


@app.route('/api/analytics')
def analytics_api():
    """Get analytics data"""
    return jsonify(db.get_analytics())


def estimate_cost(model_name, grade_data):
    """Estimate API cost for a grading operation"""
    # Rough estimates based on typical token usage
    costs = {
        'claude': 0.05,  # ~2000 tokens at $3/MTok input, $15/MTok output
        'gpt': 0.03,      # o1 pricing
        'gemini': 0.01    # Gemini 2.0 Flash pricing
    }
    return costs.get(model_name, 0.0)


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
