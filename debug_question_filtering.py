#!/usr/bin/env python3
"""
Debug question filtering to see what's happening
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import Question, QuestionSetActivation
from reference.models import Trade

def debug_question_filtering():
    """Debug the question filtering logic"""
    print("🔍 Debugging Question Filtering...")
    print("=" * 60)
    
    # Get TTC trade
    trade = Trade.objects.get(code='TTC')
    
    # Get active question set
    try:
        active_set = QuestionSetActivation.objects.get(
            trade=trade,
            paper_type='SECONDARY',
            is_active=True
        )
        print(f"✅ Active set for {trade.name}: {active_set.question_set}")
    except QuestionSetActivation.DoesNotExist:
        print(f"❌ No active set found for {trade.name}")
        return
    
    # Test the exact query used in generate_for_candidate
    print(f"\n🧪 Testing query for Part A questions...")
    
    # This is the exact query from the method
    qs = Question.objects.filter(
        is_active=True, 
        part='A',
        paper_type="SECONDARY", 
        is_common=True,
        question_set=active_set.question_set
    )
    
    print(f"Query: {qs.query}")
    print(f"Count: {qs.count()}")
    
    if qs.count() > 0:
        print(f"First 5 questions:")
        for q in qs[:5]:
            print(f"  Q{q.id}: Set {q.question_set}, Part {q.part}, Common: {q.is_common}")
    
    # Check what sets are actually available for SECONDARY questions
    print(f"\n📊 Available SECONDARY question sets:")
    all_secondary = Question.objects.filter(
        paper_type="SECONDARY",
        is_common=True,
        is_active=True
    )
    
    sets = all_secondary.values_list('question_set', flat=True).distinct().order_by('question_set')
    for qset in sets:
        count = all_secondary.filter(question_set=qset).count()
        print(f"  Set {qset}: {count} questions")
    
    # Check if there are any Set C questions at all
    print(f"\n🔍 Checking Set C questions specifically:")
    set_c_questions = Question.objects.filter(
        paper_type="SECONDARY",
        is_common=True,
        question_set='C',
        is_active=True
    )
    print(f"Total Set C SECONDARY questions: {set_c_questions.count()}")
    
    if set_c_questions.count() > 0:
        print("Part breakdown:")
        for part in ['A', 'B', 'C', 'D', 'E', 'F']:
            part_count = set_c_questions.filter(part=part).count()
            if part_count > 0:
                print(f"  Part {part}: {part_count} questions")
    
    # Check a few sample questions to see their actual question_set values
    print(f"\n🔍 Sample questions from database:")
    sample_questions = Question.objects.filter(
        paper_type="SECONDARY",
        is_common=True,
        is_active=True
    )[:10]
    
    for q in sample_questions:
        print(f"  Q{q.id}: Set '{q.question_set}', Part {q.part}, Text: {q.text[:50]}...")

if __name__ == "__main__":
    debug_question_filtering()