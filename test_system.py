"""
System-wide test script for AI Exam System
"""
import os
from dotenv import load_dotenv
from database import Database
from grading_council import GradingCouncil

load_dotenv()

def test_database():
    """Test database operations"""
    print("\n" + "="*60)
    print("TEST 1: Database Operations")
    print("="*60)

    db = Database('test_exam_system.db')

    # Test adding student
    print("\n1. Testing student creation...")
    try:
        # Try to get student first, if exists that's ok
        student = db.get_student('TEST001')
        if student:
            print(f"[OK] Student already exists: {student['name']}")
        else:
            student = db.add_student(
                student_id='TEST001',
                name='Test Student',
                email='test@example.com',
                project_title='Test Project'
            )
            print(f"[OK] Created student: {student['name']}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

    # Test creating exam session
    print("\n2. Testing exam session creation...")
    try:
        exam = db.create_exam_session(
            student_id='TEST001',
            student_name='Test Student',
            exam_type='project'
        )
        print(f"[OK] Created exam session ID: {exam['id']}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

    # Test updating exam with transcript
    print("\n3. Testing exam update...")
    try:
        updated = db.update_exam_session(
            exam['id'],
            transcript="Sample transcript",
            status='completed'
        )
        print(f"[OK] Updated exam status: {updated['status']}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

    # Test analytics
    print("\n4. Testing analytics...")
    try:
        analytics = db.get_analytics()
        print(f"[OK] Analytics: {analytics['total_students']} students, {analytics['total_exams']} exams")
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

    print("\n[OK] All database tests passed!")
    return True


def test_grading_council():
    """Test grading council"""
    print("\n" + "="*60)
    print("TEST 2: Grading Council")
    print("="*60)

    # Check API keys
    anthropic_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_KEY')

    print("\n1. Checking API keys...")
    print(f"   Anthropic: {'[OK]' if anthropic_key else '[FAIL]'}")
    print(f"   OpenAI: {'[OK]' if openai_key else '[FAIL]'}")
    print(f"   Google: {'[OK]' if google_key else '[FAIL]'}")

    if not (anthropic_key and openai_key):
        print("\n[FAIL] Missing required API keys")
        return False

    # Test grading council initialization
    print("\n2. Testing grading council initialization...")
    try:
        council = GradingCouncil()
        print(f"[OK] Available models: {', '.join(council.available_models)}")

        if len(council.available_models) < 2:
            print("[FAIL] Need at least 2 models")
            return False

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

    print("\n[OK] Grading council tests passed!")
    return True


def test_flask_routes():
    """Test Flask application"""
    print("\n" + "="*60)
    print("TEST 3: Flask Application")
    print("="*60)

    try:
        from app import app

        print("\n1. Testing Flask app creation...")
        print(f"[OK] Flask app created: {app.name}")

        print("\n2. Testing routes...")
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))

        essential_routes = ['/', '/students', '/exams', '/scenarios', '/analytics']
        for route in essential_routes:
            if route in routes:
                print(f"[OK] Route {route} exists")
            else:
                print(f"[FAIL] Route {route} missing")
                return False

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

    print("\n[OK] Flask application tests passed!")
    return True


def run_all_tests():
    """Run all system tests"""
    print("\n" + "="*60)
    print("AI EXAM SYSTEM - COMPREHENSIVE SYSTEM TEST")
    print("="*60)

    results = {
        'Database': test_database(),
        'Grading Council': test_grading_council(),
        'Flask App': test_flask_routes()
    }

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    all_passed = True
    for test_name, passed in results.items():
        status = "[OK] PASSED" if passed else "[FAIL] FAILED"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("ALL TESTS PASSED! System is ready to use.")
        print("\nNext steps:")
        print("1. Run: python run_server.py")
        print("2. Open: http://localhost:5000/")
        print("3. Start conducting exams!")
    else:
        print("SOME TESTS FAILED. Please fix the issues above.")
    print("="*60 + "\n")

    # Cleanup test database
    if os.path.exists('test_exam_system.db'):
        os.remove('test_exam_system.db')
        print("(Cleaned up test database)")

    return all_passed


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
