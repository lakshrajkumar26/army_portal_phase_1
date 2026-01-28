#!/usr/bin/env python3
"""
Test the actual generate_for_candidate method
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import QuestionPaper
from reference.models import Trade
from django.contrib.auth import get_user_model

User = get_user_model()

def test_actual_method():
    """Test the actual generate_for_candidate method"""
    print("🔍 Testing Actual generate_for_candidate Method...")
    print("=" * 60)
    
    # Get TTC trade and SECONDARY paper
    trade = Trade.objects.get(code='TTC')
    paper = QuestionPaper.objects.get(question_paper='SECONDARY')
    
    # Create test user
    test_user, created = User.objects.get_or_create(
        username='actual_test_user',
        defaults={'email': 'actual@example.com'}
    )
    
    try:
        # Call the actual method with the trade (even for SECONDARY papers)
        print(f"Calling paper.generate_for_candidate(user={test_user.username}, trade={trade.name})")
        session = paper.generate_for_candidate(test_user, trade=trade)
        
        print(f"✅ Session created: {session.id}")
        print(f"Total questions: {session.total_questions}")
        
        # Check the actual questions in the session
        exam_questions = session.examquestion_set.all().order_by('order')
        
        print(f"\n📋 Questions in session:")
        wrong_set_count = 0
        set_counts = {}
        
        for exam_q in exam_questions:
            q = exam_q.question
            qset = q.question_set
            
            if qset not in set_counts:
                set_counts[qset] = 0
            set_counts[qset] += 1
            
            if qset != 'C':
                wrong_set_count += 1
                if wrong_set_count <= 5:  # Show first 5 wrong ones
                    print(f"  ❌ Q{q.id}: Set {qset} (expected C), Part {q.part}")
        
        print(f"\n📊 Question set distribution:")
        for qset, count in sorted(set_counts.items()):
            status = "✅" if qset == 'C' else "❌"
            print(f"  {status} Set {qset}: {count} questions")
        
        if wrong_set_count == 0:
            print(f"\n✅ SUCCESS: All questions are from Set C!")
        else:
            print(f"\n❌ FAILURE: {wrong_set_count} questions are from wrong sets!")
        
        # Clean up
        session.delete()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        if created:
            test_user.delete()

if __name__ == "__main__":
    test_actual_method()