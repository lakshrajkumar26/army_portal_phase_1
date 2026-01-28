#!/usr/bin/env python3
"""
Test script to verify question set selection is working correctly.
This script will check if candidates are getting questions from the correct activated question set.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import Question, QuestionSetActivation, GlobalPaperTypeControl, QuestionPaper
from reference.models import Trade
from django.contrib.auth import get_user_model

User = get_user_model()

def test_question_set_selection():
    """Test that question set selection works correctly"""
    print("🔍 Testing Question Set Selection Logic...")
    print("=" * 60)
    
    # Get active paper type
    try:
        active_control = GlobalPaperTypeControl.objects.get(is_active=True)
        active_paper_type = active_control.paper_type
        print(f"✅ Active Paper Type: {active_paper_type}")
    except GlobalPaperTypeControl.DoesNotExist:
        print("❌ No active paper type found!")
        return False
    
    # Get a test trade
    test_trade = Trade.objects.first()
    if not test_trade:
        print("❌ No trades found!")
        return False
    
    print(f"🎯 Testing with Trade: {test_trade.name} ({test_trade.code})")
    
    # Check active question set for this trade
    try:
        active_set = QuestionSetActivation.objects.get(
            trade=test_trade,
            paper_type=active_paper_type,
            is_active=True
        )
        print(f"✅ Active Question Set: {active_set.question_set}")
    except QuestionSetActivation.DoesNotExist:
        print(f"❌ No active question set found for {test_trade.name} {active_paper_type}")
        return False
    
    # Check available questions for this trade and set
    if active_paper_type == "SECONDARY":
        questions = Question.objects.filter(
            paper_type="SECONDARY",
            is_common=True,
            question_set=active_set.question_set,
            is_active=True
        )
        print(f"📊 SECONDARY Questions in Set {active_set.question_set}: {questions.count()}")
    else:
        questions = Question.objects.filter(
            trade=test_trade,
            paper_type="PRIMARY",
            question_set=active_set.question_set,
            is_active=True
        )
        print(f"📊 PRIMARY Questions for {test_trade.name} in Set {active_set.question_set}: {questions.count()}")
    
    # Show breakdown by part
    parts = ['A', 'B', 'C', 'D', 'E', 'F']
    print("\n📋 Question Breakdown by Part:")
    for part in parts:
        part_count = questions.filter(part=part).count()
        if part_count > 0:
            print(f"   Part {part}: {part_count} questions")
    
    # Test paper generation
    print(f"\n🧪 Testing Paper Generation...")
    try:
        paper = QuestionPaper.objects.get(question_paper=active_paper_type)
        
        # Create a test user
        test_user, created = User.objects.get_or_create(
            username='test_question_set_user',
            defaults={'email': 'test@example.com'}
        )
        
        # Generate exam session (always pass trade, even for SECONDARY papers)
        session = paper.generate_for_candidate(test_user, trade=test_trade)
        
        print(f"✅ Paper generated successfully!")
        print(f"   Total questions in session: {session.total_questions}")
        
        # Verify all questions are from the correct set
        session_questions = session.examquestion_set.all()
        wrong_set_count = 0
        
        for exam_q in session_questions:
            if exam_q.question.question_set != active_set.question_set:
                wrong_set_count += 1
                print(f"❌ Wrong set question found: Q{exam_q.question.id} is from Set {exam_q.question.question_set}, expected Set {active_set.question_set}")
        
        if wrong_set_count == 0:
            print(f"✅ All {session.total_questions} questions are from the correct Set {active_set.question_set}")
        else:
            print(f"❌ Found {wrong_set_count} questions from wrong sets!")
        
        # Clean up test session
        session.delete()
        if created:
            test_user.delete()
        
        return wrong_set_count == 0
        
    except Exception as e:
        print(f"❌ Error generating paper: {str(e)}")
        return False

def show_question_set_status():
    """Show current question set activation status"""
    print("\n📊 Current Question Set Activation Status:")
    print("=" * 60)
    
    # Show global paper type
    try:
        active_control = GlobalPaperTypeControl.objects.get(is_active=True)
        print(f"🌐 Global Active Paper Type: {active_control.paper_type}")
    except GlobalPaperTypeControl.DoesNotExist:
        print("❌ No global paper type activated!")
        return
    
    # Show activations per trade
    activations = QuestionSetActivation.objects.filter(is_active=True).select_related('trade')
    
    if not activations.exists():
        print("❌ No question set activations found!")
        return
    
    print(f"\n📋 Active Question Sets ({activations.count()} total):")
    for activation in activations.order_by('trade__name', 'paper_type'):
        print(f"   {activation.trade.name} ({activation.trade.code}) - {activation.paper_type}: Set {activation.question_set}")

if __name__ == "__main__":
    print("🚀 Question Set Selection Test")
    print("=" * 60)
    
    # Show current status
    show_question_set_status()
    
    # Test selection logic
    success = test_question_set_selection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Question Set Selection Test PASSED!")
        print("   Candidates will receive questions from the correct activated question set.")
    else:
        print("❌ Question Set Selection Test FAILED!")
        print("   There are issues with question set filtering.")
    
    print("=" * 60)