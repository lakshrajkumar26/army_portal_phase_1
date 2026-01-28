#!/usr/bin/env python3
"""
Test the final fix with individual trade activations
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import Question, QuestionSetActivation, QuestionPaper, TradePaperActivation
from reference.models import Trade
from django.contrib.auth import get_user_model

User = get_user_model()

def test_both_trade_types():
    """Test both PRIMARY and SECONDARY trade types"""
    print("🚀 Final Fix Test - Both Trade Types")
    print("=" * 60)
    
    # Test OCC (PRIMARY trade)
    print("🔵 Testing OCC (PRIMARY trade):")
    test_trade_type('OCC')
    
    print("\n" + "=" * 60)
    
    # Test TTC (SECONDARY trade)
    print("🟣 Testing TTC (SECONDARY trade):")
    test_trade_type('TTC')

def test_trade_type(trade_code):
    """Test a specific trade type"""
    try:
        trade = Trade.objects.get(code=trade_code)
        print(f"   Trade: {trade.name} ({trade.code})")
        
        # Get active paper type for this trade
        trade_activation = TradePaperActivation.objects.get(
            trade=trade,
            is_active=True
        )
        paper_type = trade_activation.paper_type
        print(f"   Paper Type: {paper_type}")
        
        # Get active question set
        qs_activation = QuestionSetActivation.objects.get(
            trade=trade,
            paper_type=paper_type,
            is_active=True
        )
        print(f"   Active Question Set: {qs_activation.question_set}")
        
        # Count available questions
        if paper_type == "SECONDARY":
            questions = Question.objects.filter(
                paper_type="SECONDARY",
                is_common=True,
                question_set=qs_activation.question_set,
                is_active=True
            )
        else:
            questions = Question.objects.filter(
                trade=trade,
                paper_type="PRIMARY",
                question_set=qs_activation.question_set,
                is_active=True
            )
        
        print(f"   Available Questions: {questions.count()}")
        
        # Test paper generation
        paper = QuestionPaper.objects.get(question_paper=paper_type)
        
        test_user, created = User.objects.get_or_create(
            username=f'test_{trade_code.lower()}_user',
            defaults={'email': f'test_{trade_code.lower()}@example.com'}
        )
        
        session = paper.generate_for_candidate(test_user, trade=trade)
        print(f"   Generated Session: {session.total_questions} questions")
        
        # Verify question sets
        session_questions = session.examquestion_set.all()
        correct_set_count = 0
        
        for exam_q in session_questions:
            if exam_q.question.question_set == qs_activation.question_set:
                correct_set_count += 1
        
        print(f"   Correct Set Questions: {correct_set_count}/{session.total_questions}")
        
        if correct_set_count == session.total_questions:
            print(f"   ✅ SUCCESS: All questions from Set {qs_activation.question_set}")
        else:
            print(f"   ❌ FAILURE: {session.total_questions - correct_set_count} wrong set questions")
        
        # Clean up
        session.delete()
        if created:
            test_user.delete()
        
        return correct_set_count == session.total_questions
        
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_both_trade_types()