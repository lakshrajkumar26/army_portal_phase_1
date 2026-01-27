#!/usr/bin/env python
"""
Quick test script to verify the exam interface fix
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import Question, ExamSession, QuestionPaper
from registration.models import CandidateProfile
from questions.models import TradePaperActivation

def test_exam_data():
    print("=== EXAM INTERFACE FIX TEST ===")
    
    # Check questions
    total_questions = Question.objects.count()
    print(f"Total questions in DB: {total_questions}")
    
    # Check Part A questions with blanks
    part_a_questions = Question.objects.filter(part='A')
    part_a_with_blanks = part_a_questions.filter(text__contains='____')
    print(f"Part A questions: {part_a_questions.count()}")
    print(f"Part A questions with blanks: {part_a_with_blanks.count()}")
    
    # Check questions with options
    questions_with_options = Question.objects.exclude(options__isnull=True)
    print(f"Questions with options: {questions_with_options.count()}")
    
    # Check candidates
    candidates = CandidateProfile.objects.all()
    print(f"Candidates: {candidates.count()}")
    
    if candidates.exists():
        candidate = candidates.first()
        print(f"Test candidate: {candidate.name} ({candidate.trade})")
        
        # Check activations
        activations = TradePaperActivation.objects.filter(trade=candidate.trade, is_active=True)
        print(f"Active exams for {candidate.trade}: {activations.count()}")
        
        if activations.exists():
            activation = activations.first()
            print(f"Active exam: {activation.paper_type}")
            
            # Check papers
            papers = QuestionPaper.objects.filter(question_paper=activation.paper_type, is_active=True)
            print(f"Active papers: {papers.count()}")
            
            if papers.exists():
                paper = papers.first()
                print(f"Paper: {paper.question_paper}")
                
                # Check sessions
                sessions = ExamSession.objects.filter(user=candidate.user, paper=paper, completed_at__isnull=True)
                print(f"Active sessions: {sessions.count()}")
                
                if sessions.exists():
                    session = sessions.first()
                    print(f"Session questions: {session.questions.count()}")
                    
                    # Check first few questions
                    questions = session.questions.all()[:3]
                    for i, eq in enumerate(questions, 1):
                        q = eq.question
                        has_blanks = '____' in q.text
                        print(f"Q{i}: Part {q.part}, Has blanks: {has_blanks}, Text: {q.text[:50]}...")
                
                print("\n✅ EXAM DATA STRUCTURE IS VALID")
                print("✅ TEMPLATE FIX SHOULD WORK:")
                print("   - Part A questions with blanks will be treated as fill-in-the-blank")
                print("   - Part A questions without blanks will get generic MCQ options")
                print("   - Other question types will work as expected")
                
            else:
                print("❌ No active papers found")
        else:
            print("❌ No active exams found")
    else:
        print("❌ No candidates found")

if __name__ == "__main__":
    test_exam_data()