"""
Database models and setup for the AI Exam System
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()

class Student(Base):
    """Student model"""
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    student_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    project_title = Column(String(200))
    project_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'project_title': self.project_title,
            'project_description': self.project_description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ExamSession(Base):
    """Exam session model"""
    __tablename__ = 'exam_sessions'

    id = Column(Integer, primary_key=True)
    student_id = Column(String(50), nullable=False)
    student_name = Column(String(100), nullable=False)
    exam_type = Column(String(50))  # 'project', 'case_study', etc.
    status = Column(String(20), default='pending')  # pending, in_progress, completed, failed
    transcript = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'exam_type': self.exam_type,
            'status': self.status,
            'transcript': self.transcript,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class GradingResult(Base):
    """Grading result model"""
    __tablename__ = 'grading_results'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, nullable=False)
    model_name = Column(String(50), nullable=False)  # claude, gpt, gemini
    round_number = Column(Integer, default=1)
    overall_score = Column(Float)
    category_scores = Column(JSON)  # Store detailed scores
    assessment = Column(Text)
    cost = Column(Float, default=0.0)  # API cost
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'model_name': self.model_name,
            'round_number': self.round_number,
            'overall_score': self.overall_score,
            'category_scores': self.category_scores,
            'assessment': self.assessment,
            'cost': self.cost,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Scenario(Base):
    """Case study scenario model"""
    __tablename__ = 'scenarios'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50))  # ML, AI, Statistics, etc.
    difficulty = Column(String(20))  # easy, medium, hard
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'active': self.active
        }


class Prompt(Base):
    """Prompt template model - stores editable prompts and rubrics"""
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., 'manuscript_analysis'
    display_name = Column(String(200), nullable=False)  # e.g., 'Manuscript Analysis Prompt'
    description = Column(Text)
    content = Column(Text, nullable=False)
    category = Column(String(50))  # 'prompt', 'rubric'
    version = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(100), default='admin')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'content': self.content,
            'category': self.category,
            'version': self.version,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }


class Database:
    """Database manager"""

    def __init__(self, db_path='exam_system.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def get_session(self):
        return self.Session()

    def close(self):
        self.Session.remove()

    # Student operations
    def add_student(self, student_id, name, email=None, project_title=None, project_description=None):
        session = self.get_session()
        try:
            student = Student(
                student_id=student_id,
                name=name,
                email=email,
                project_title=project_title,
                project_description=project_description
            )
            session.add(student)
            session.commit()
            return student.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_student(self, student_id):
        session = self.get_session()
        try:
            student = session.query(Student).filter_by(student_id=student_id).first()
            return student.to_dict() if student else None
        finally:
            session.close()

    def get_all_students(self):
        session = self.get_session()
        try:
            students = session.query(Student).all()
            return [s.to_dict() for s in students]
        finally:
            session.close()

    # Exam session operations
    def create_exam_session(self, student_id, student_name, exam_type='project'):
        session = self.get_session()
        try:
            exam = ExamSession(
                student_id=student_id,
                student_name=student_name,
                exam_type=exam_type,
                status='pending'
            )
            session.add(exam)
            session.commit()
            return exam.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_exam_session(self, session_id, **kwargs):
        session = self.get_session()
        try:
            exam = session.query(ExamSession).filter_by(id=session_id).first()
            if exam:
                for key, value in kwargs.items():
                    setattr(exam, key, value)
                session.commit()
                return exam.to_dict()
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_exam_session(self, session_id):
        session = self.get_session()
        try:
            exam = session.query(ExamSession).filter_by(id=session_id).first()
            return exam.to_dict() if exam else None
        finally:
            session.close()

    def get_student_exams(self, student_id):
        session = self.get_session()
        try:
            exams = session.query(ExamSession).filter_by(student_id=student_id).all()
            return [e.to_dict() for e in exams]
        finally:
            session.close()

    def get_all_exams(self, limit=100):
        session = self.get_session()
        try:
            exams = session.query(ExamSession).order_by(ExamSession.started_at.desc()).limit(limit).all()
            return [e.to_dict() for e in exams]
        finally:
            session.close()

    # Grading operations
    def save_grading_result(self, session_id, model_name, round_number, overall_score,
                           category_scores, assessment, cost=0.0):
        session = self.get_session()
        try:
            result = GradingResult(
                session_id=session_id,
                model_name=model_name,
                round_number=round_number,
                overall_score=overall_score,
                category_scores=category_scores,
                assessment=assessment,
                cost=cost
            )
            session.add(result)
            session.commit()
            return result.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_session_grades(self, session_id):
        session = self.get_session()
        try:
            grades = session.query(GradingResult).filter_by(session_id=session_id).all()
            return [g.to_dict() for g in grades]
        finally:
            session.close()

    # Scenario operations
    def add_scenario(self, title, description, category, difficulty='medium'):
        session = self.get_session()
        try:
            scenario = Scenario(
                title=title,
                description=description,
                category=category,
                difficulty=difficulty
            )
            session.add(scenario)
            session.commit()
            return scenario.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_random_scenario(self, category=None, difficulty=None):
        import random
        session = self.get_session()
        try:
            query = session.query(Scenario).filter_by(active=True)
            if category:
                query = query.filter_by(category=category)
            if difficulty:
                query = query.filter_by(difficulty=difficulty)
            scenarios = query.all()
            if scenarios:
                return random.choice(scenarios).to_dict()
            return None
        finally:
            session.close()

    def get_all_scenarios(self):
        session = self.get_session()
        try:
            scenarios = session.query(Scenario).filter_by(active=True).all()
            return [s.to_dict() for s in scenarios]
        finally:
            session.close()

    # Analytics
    def get_analytics(self):
        session = self.get_session()
        try:
            total_students = session.query(Student).count()
            total_exams = session.query(ExamSession).count()
            completed_exams = session.query(ExamSession).filter_by(status='completed').count()
            total_cost = session.query(GradingResult).with_entities(
                session.query(GradingResult.cost).label('total')
            ).scalar() or 0.0

            # Average scores by model
            avg_scores = {}
            for model in ['claude', 'gpt', 'gemini']:
                avg = session.query(GradingResult).filter_by(model_name=model).with_entities(
                    session.query(GradingResult.overall_score).label('avg')
                ).scalar()
                if avg:
                    avg_scores[model] = round(avg, 2)

            return {
                'total_students': total_students,
                'total_exams': total_exams,
                'completed_exams': completed_exams,
                'total_cost': round(total_cost, 2),
                'avg_scores_by_model': avg_scores
            }
        finally:
            session.close()
