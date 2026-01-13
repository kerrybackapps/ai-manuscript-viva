"""
Test the dual grading system with a simulated oral exam
"""
from database import Database
from manuscript_viva_system import ManuscriptVivaSystem

# Simulated oral exam conversation
simulated_oral_exam = """

[ORAL EXAMINATION TRANSCRIPT]

Examiner: Hello! I've read your manuscript on healthcare AI diagnostics. Let's begin with your methodology. You mentioned interviewing 10 radiologists. Can you walk me through how you selected these participants?

Student: Yes, I selected radiologists from three different hospitals in the metropolitan area. I wanted diversity in experience levels, so I included radiologists with 5-15 years of experience. I used a convenience sampling method and reached out through professional networks.

Examiner: Interesting. In your findings, you stated that AI systems achieved 94% accuracy in detecting lung cancer. What were the main limitations of this finding?

Student: Well, the 94% accuracy was based on a specific dataset and controlled conditions. The main limitations include: the AI was tested on high-quality CT scans, it may not generalize to different populations or scanner types, and the accuracy varied depending on the stage of cancer. Early-stage cancers were harder to detect.

Examiner: Good points. You concluded that AI should augment rather than replace clinicians. Can you elaborate on the reasoning behind that conclusion?

Student: My reasoning comes from two main concerns. First, the interviews revealed that radiologists catch contextual details that AI might miss - patient history, other conditions, scan quality issues. Second, the literature showed that false negatives in AI can be dangerous. When radiologists use AI as a second opinion rather than relying on it completely, they achieve the best results - faster and more accurate.

Examiner: You mentioned that 67% of clinicians expressed concerns about over-reliance on AI. Did you explore what those specific concerns were?

Student: Yes, the main concerns were: loss of diagnostic skills if too dependent on AI, liability issues when AI makes mistakes, and the black box problem - not understanding why the AI made certain decisions. Some radiologists also worried about workflow disruption and learning curves.

Examiner: What alternative approaches to AI-assisted diagnosis did you consider in your research?

Student: I looked at several alternatives. One was traditional computer-aided detection (CAD) systems, which are rule-based rather than ML-based. Another was having radiologists work in pairs for double-reading. I also considered hybrid approaches where AI does initial screening and flags cases for human review. Each has tradeoffs in cost, speed, and accuracy.

Examiner: If I challenged your claim that AI achieves 94% accuracy, arguing that real-world performance is much lower, how would you defend it?

Student: I would acknowledge that you're right to challenge it. The 94% figure comes from research studies under controlled conditions. Real-world accuracy is indeed lower - probably 80-85% based on deployment studies I reviewed. I should have been clearer in my manuscript that this was a research benchmark, not a field performance metric. The gap between research and practice is actually one of the implementation challenges I discussed.

Examiner: In your conclusion, you mentioned the need for validation and training. Can you be more specific about what validation process you'd recommend?

Student: I'd recommend a multi-phase validation: first, testing on diverse datasets from different hospitals and populations; second, prospective clinical trials where AI is used alongside radiologists; third, ongoing monitoring after deployment with regular audits of false positives and negatives. For training, I'd suggest radiologists need hands-on experience with the AI tools and understanding of their limitations before clinical use.

Examiner: Final question - what's the most significant gap in current research that your manuscript identified?

Student: The biggest gap is the lack of long-term studies on how AI integration affects radiologist skill development and retention. Most studies focus on immediate accuracy gains, but we don't know if radiologists become less skilled over time when relying on AI, or if new radiologists trained with AI from the start will have different capabilities. This has major implications for training programs and clinical practice.

Examiner: Thank you. That completes the oral examination. EXAMINATION_COMPLETE
"""

def test_dual_grading():
    """Test the dual grading system"""

    db = Database()
    system = ManuscriptVivaSystem()

    # Get the exam session
    session_id = 3
    session = db.get_exam_session(session_id)

    if not session:
        print(f"[ERROR] Session {session_id} not found")
        return

    print("="*70)
    print(" TESTING DUAL GRADING SYSTEM")
    print("="*70)

    print(f"\nSession ID: {session_id}")
    print(f"Student: {session['student_name']}")
    print(f"Current transcript length: {len(session['transcript'])} characters")

    # Add simulated oral exam to transcript
    print("\n[1/3] Adding simulated oral exam conversation...")
    updated_transcript = session['transcript'] + simulated_oral_exam
    db.update_exam_session(session_id, transcript=updated_transcript)
    print(f"      Updated transcript length: {len(updated_transcript)} characters")

    # Run dual grading
    print("\n[2/3] Running dual grading system...")
    print("      This will grade:")
    print("      - MANUSCRIPT: clarity, coherence, comprehensiveness")
    print("      - ORAL EXAM: understanding, reasoning, alternatives")
    print()

    results = system.grade_manuscript_and_oral(session_id)

    if results:
        print("\n[3/3] Grading complete!")
        print("\n" + "="*70)
        print(" DUAL GRADING RESULTS")
        print("="*70)

        # Show manuscript results
        if 'manuscript' in results:
            ms = results['manuscript']
            print("\n[A] MANUSCRIPT EVALUATION:")
            print(f"    Model: {ms['model']}")
            print(f"    Overall Score: {ms['overall_score']:.1f}/4.0")
            print(f"    Letter Grade: {ms['letter_grade']}")
            print(f"\n    Category Scores:")
            for cat, score in ms['category_scores'].items():
                print(f"      - {cat}: {score}/4")
            print(f"\n    Summary: {ms['feedback_summary'][:200]}...")

        # Show oral exam results
        if 'oral' in results:
            oral = results['oral']
            print("\n[B] ORAL EXAMINATION EVALUATION:")
            print(f"    Model: {oral['model']}")
            print(f"    Overall Score: {oral['overall_score']:.1f}/4.0")
            print(f"    Letter Grade: {oral['letter_grade']}")
            print(f"\n    Category Scores:")
            for cat, score in oral['category_scores'].items():
                print(f"      - {cat}: {score}/4")
            print(f"\n    Summary: {oral['feedback_summary'][:200]}...")

        print("\n" + "="*70)
        print(f" View full results at: http://localhost:5000/exams/{session_id}/view")
        print("="*70)

    else:
        print("\n[ERROR] Grading failed")

if __name__ == '__main__':
    test_dual_grading()
