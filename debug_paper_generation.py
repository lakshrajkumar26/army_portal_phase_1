#!/usr/bin/env python3
"""
Debug paper generation step by step
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import Question, QuestionSetActivation, QuestionPaper, ExamSession, ExamQuestion
from reference.models import Trade
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def debug_paper_generation():
    """Debug paper generation step by step"""
    print("🔍 Debugging Paper Generation Step by Step...")
    print("=" * 60)
    
    # Get TTC trade and SECONDARY paper
    trade = Trade.objects.get(code='TTC')
    paper = QuestionPaper.objects.get(question_paper='SECONDARY')
    
    print(f"Trade: {trade.name} ({trade.code})")
    print(f"Paper: {paper.question_paper}")
    
    # Get active question set
    try:
        active_set = QuestionSetActivation.objects.get(
            trade=trade,
            paper_type='SECONDARY',
            is_active=True
        )
        print(f"Active set: {active_set.question_set}")
    except QuestionSetActivation.DoesNotExist:
        print("❌ No active set found")
        return
    
    # Create test user
    test_user, created = User.objects.get_or_create(
        username='debug_test_user',
        defaults={'email': 'debug@example.com'}
    )
    
    print(f"\n🧪 Simulating paper generation...")
    
    # Simulate the exact logic from generate_for_candidate
    is_secondary = (paper.question_paper == "SECONDARY")
    print(f"is_secondary: {is_secondary}")
    
    # Get distribution
    from questions.models import HARD_CODED_COMMON_DISTRIBUTION
    dist = HARD_CODED_COMMON_DISTRIBUTION.copy()
    print(f"Distribution: {dist}")
    
    # Get active question set (this is the fixed logic)
    active_question_set = 'A'  # Default fallback
    if trade:
        try:
            active_set = QuestionSetActivation.objects.get(
                trade=trade,
                paper_type=paper.question_paper,
                is_active=True
            )
            active_question_set = active_set.question_set
            print(f"Found active question set: {active_question_set}")
        except QuestionSetActivation.DoesNotExist:
            print("Using default question set: A")
    
    # Test each part
    print(f"\n📋 Testing question selection for each part:")
    
    for part, count in dist.items():
        count = int(count)
        if count <= 0:
            continue
        
        print(f"\nPart {part} (need {count} questions):")
        
        # Build the query exactly as in the method
        qs = Question.objects.filter(is_active=True, part=part)
        
        if is_secondary:
            qs = qs.filter(
                paper_type="SECONDARY", 
                is_common=True,
                question_set=active_question_set
            )
        else:
            qs = qs.filter(
                paper_type="PRIMARY", 
                trade=trade,
                question_set=active_question_set
            )
        
        print(f"  Query: {qs.query}")
        print(f"  Available: {qs.count()} questions")
        
        # Get the actual questions that would be selected
        selected = list(qs.order_by("?")[:count])
        print(f"  Selected: {len(selected)} questions")
        
        if selected:
            print(f"  Sample questions:")
            for i, q in enumerate(selected[:3]):
                print(f"    Q{q.id}: Set {q.question_set}, Text: {q.text[:50]}...")
            if len(selected) > 3:
                print(f"    ... and {len(selected) - 3} more")
    
    # Clean up
    if created:
        test_user.delete()

if __name__ == "__main__":
    debug_paper_generation()