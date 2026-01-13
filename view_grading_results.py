"""
View grading results from the database
"""
from database import Database, GradingResult
from sqlalchemy import select
import json

db = Database()
session_id = 3

# Query grading results
with db.Session() as session:
    results = session.execute(
        select(GradingResult).where(GradingResult.session_id == session_id)
    ).scalars().all()

    print("="*70)
    print(f" GRADING RESULTS FOR SESSION {session_id}")
    print("="*70)
    print(f"\nFound {len(results)} grading results:\n")

    # Separate manuscript and oral results
    manuscript_results = [r for r in results if '_manuscript' in r.model_name]
    oral_results = [r for r in results if '_oral' in r.model_name]

    if manuscript_results:
        print("\n" + "="*70)
        print("[A] MANUSCRIPT GRADING RESULTS")
        print("="*70)
        for r in manuscript_results:
            print(f"\nModel: {r.model_name.replace('_manuscript', '')}")
            print(f"Overall Score: {r.overall_score:.2f}/4.0")
            print(f"Categories: {r.category_scores}")
            print(f"Assessment excerpt: {r.assessment[:150] if r.assessment else 'N/A'}...")

    if oral_results:
        print("\n" + "="*70)
        print("[B] ORAL EXAMINATION GRADING RESULTS")
        print("="*70)
        for r in oral_results:
            print(f"\nModel: {r.model_name.replace('_oral', '')}")
            print(f"Overall Score: {r.overall_score:.2f}/4.0")
            print(f"Categories: {r.category_scores}")
            print(f"Assessment excerpt: {r.assessment[:150] if r.assessment else 'N/A'}...")

    print("\n" + "="*70)
