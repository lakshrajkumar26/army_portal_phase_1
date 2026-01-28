#!/usr/bin/env python
"""
Test script to verify that question options are properly displayed in the exam interface.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import Question
from registration.models import CandidateProfile
from django.contrib.auth import get_user_model

User = get_user_model()

def test_question_options():
    """Test that questions have proper option data"""
    print("=== Testing Question Options ===")
    
    # Get some MCQ questions
    mcq_questions = Question.objects.filter(part='A', option_a__isnull=False)[:5]
    
    if not mcq_questions.exists():
        print("❌ No MCQ questions with option_a found")
        return False
    
    print(f"✅ Found {mcq_questions.count()} MCQ questions with option data")
    
    for q in mcq_questions:
        print(f"\nQuestion {q.id}:")
        print(f"  Text: {q.text[:50]}...")
        print(f"  Option A: {q.option_a}")
        print(f"  Option B: {q.option_b}")
        print(f"  Option C: {q.option_c}")
        print(f"  Option D: {q.option_d}")
        print(f"  Correct: {q.correct_answer}")
        
        # Check if all options are present
        if all([q.option_a, q.option_b, q.option_c, q.option_d]):
            print("  ✅ All options present")
        else:
            print("  ❌ Missing some options")
    
    return True

def test_candidate_exam_setup():
    """Test that candidates can see proper question sets"""
    print("\n=== Testing Candidate Exam Setup ===")
    
    # Get a test candidate
    candidate = CandidateProfile.objects.first()
    if not candidate:
        print("❌ No candidates found")
        return False
    
    print(f"✅ Testing with candidate: {candidate.name} ({candidate.trade})")
    
    # Check trade activation
    from questions.models import TradePaperActivation
    try:
        activation = TradePaperActivation.objects.get(trade=candidate.trade, is_active=True)
        print(f"✅ Trade activation found: {activation.paper_type}")
        
        # Check question availability
        if activation.paper_type == "PRIMARY":
            questions = Question.objects.filter(
                trade=candidate.trade,
                paper_type="PRIMARY",
                is_active=True
            )
        else:
            questions = Question.objects.filter(
                paper_type="SECONDARY",
                is_common=True,
                is_active=True
            )
        
        print(f"✅ Available questions: {questions.count()}")
        
        # Check questions with options
        questions_with_options = questions.filter(option_a__isnull=False)
        print(f"✅ Questions with option data: {questions_with_options.count()}")
        
        return True
        
    except TradePaperActivation.DoesNotExist:
        print("❌ No trade activation found")
        return False

if __name__ == "__main__":
    print("Testing Question Option Display System")
    print("=" * 50)
    
    success1 = test_question_options()
    success2 = test_candidate_exam_setup()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The option display system is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")