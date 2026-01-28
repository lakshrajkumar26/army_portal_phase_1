#!/usr/bin/env python3
"""
Test script to verify the exam session persistence fix

This script tests the complete workflow:
1. Create candidate with exam slot
2. Generate exam session with Set C
3. Change question set to Set E
4. Reset/reassign slot
5. Verify new session uses Set E questions
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from questions.models import (
    Question, QuestionPaper, ExamSession, ActivateSets, 
    GlobalPaperTypeControl, TradePaperActivation
)
from registration.models import CandidateProfile
from reference.models import Trade

User = get_user_model()

def setup_test_data():
    """Setup test data for the fix verification"""
    print("🔧 Setting up test data...")
    
    # Get or create test trade
    trade, created = Trade.objects.get_or_create(
        name="TTC",
        defaults={'code': 'TTC', 'slug': 'ttc'}
    )
    
    # Create test questions for different sets
    sets_to_create = ['C', 'E']
    for question_set in sets_to_create:
        for part in ['A', 'B', 'C', 'D', 'E', 'F']:
            # Create enough questions for each part
            part_counts = {'A': 15, 'B': 0, 'C': 5, 'D': 10, 'E': 3, 'F': 10}
            count_needed = part_counts.get(part, 5)
            
            existing_count = Question.objects.filter(
                trade=trade,
                paper_type='PRIMARY',
                question_set=question_set,
                part=part,
                is_active=True
            ).count()
            
            for i in range(existing_count, count_needed):
                Question.objects.get_or_create(
                    text=f"Test question {question_set}{part}{i+1} for {trade.name}",
                    trade=trade,
                    paper_type='PRIMARY',
                    question_set=question_set,
                    part=part,
                    marks=1,
                    is_active=True,
                    defaults={
                        'options': {'A': 'Option A', 'B': 'Option B', 'C': 'Option C', 'D': 'Option D'},
                        'correct_answer': ['A']
                    }
                )
    
    # Create test user and candidate
    test_user, created = User.objects.get_or_create(
        username='test_candidate_fix',
        defaults={'email': 'test@example.com'}
    )
    
    candidate, created = CandidateProfile.objects.get_or_create(
        user=test_user,
        defaults={
            'army_no': 'TEST123456',
            'name': 'Test Candidate Fix',
            'rank': 'Test Rank',
            'trade': trade,
            'dob': '01/01/1990',
            'doe': '2020-01-01',
            'father_name': 'Test Father',
            'state': 'Test State',
            'district': 'Test District'
        }
    )
    
    # Setup paper type activation
    GlobalPaperTypeControl.objects.update_or_create(
        paper_type='PRIMARY',
        defaults={'is_active': True}
    )
    
    # Setup trade paper activation
    TradePaperActivation.objects.update_or_create(
        trade=trade,
        paper_type='PRIMARY',
        defaults={'is_active': True}
    )
    
    # Get or create question paper
    paper, created = QuestionPaper.objects.get_or_create(
        question_paper='PRIMARY',
        defaults={'is_active': True}
    )
    
    print(f"✅ Test data setup complete")
    print(f"   Trade: {trade.name}")
    print(f"   Candidate: {candidate.army_no} - {candidate.name}")
    print(f"   Question sets available: C, E")
    
    return trade, candidate, paper

def test_session_persistence_fix():
    """Test the complete session persistence fix workflow"""
    print("\n🧪 Testing Session Persistence Fix")
    print("=" * 50)
    
    # Setup test data
    trade, candidate, paper = setup_test_data()
    
    # Step 1: Set initial question set to C
    print("\n📝 Step 1: Setting question set to C")
    activate_sets, created = ActivateSets.objects.get_or_create(
        trade=trade,
        defaults={'active_primary_set': 'C', 'active_secondary_set': 'C'}
    )
    activate_sets.active_primary_set = 'C'
    activate_sets.save()
    print(f"✅ Question set C activated for {trade.name}")
    
    # Step 2: Assign exam slot and generate first session
    print("\n📝 Step 2: Assigning exam slot and generating session with Set C")
    candidate.assign_exam_slot()
    
    try:
        session_c = paper.generate_for_candidate(candidate.user, trade=trade)
        print(f"✅ Session created with {session_c.total_questions} questions")
        
        # Check which question set was used
        first_question = session_c.examquestion_set.first()
        if first_question:
            question_set_used = first_question.question.question_set
            print(f"   Questions from set: {question_set_used}")
            
            if question_set_used != 'C':
                print(f"❌ Expected Set C, got Set {question_set_used}")
                return False
        
    except Exception as e:
        print(f"❌ Failed to generate session with Set C: {e}")
        return False
    
    # Step 3: Change question set to E
    print("\n📝 Step 3: Changing question set to E")
    activate_sets.active_primary_set = 'E'
    activate_sets.save()  # This should clear incomplete sessions
    print(f"✅ Question set E activated for {trade.name}")
    
    # Verify incomplete sessions were cleared
    incomplete_sessions = ExamSession.objects.filter(
        user=candidate.user,
        completed_at__isnull=True
    ).count()
    print(f"   Incomplete sessions after set change: {incomplete_sessions}")
    
    # Step 4: Reset and reassign slot
    print("\n📝 Step 4: Resetting and reassigning exam slot")
    candidate.reset_exam_slot()  # This should also clear incomplete sessions
    candidate.assign_exam_slot()  # This should also clear incomplete sessions
    print(f"✅ Slot reset and reassigned")
    
    # Step 5: Generate new session and verify it uses Set E
    print("\n📝 Step 5: Generating new session - should use Set E")
    try:
        session_e = paper.generate_for_candidate(candidate.user, trade=trade)
        print(f"✅ New session created with {session_e.total_questions} questions")
        
        # Check which question set was used
        first_question = session_e.examquestion_set.first()
        if first_question:
            question_set_used = first_question.question.question_set
            print(f"   Questions from set: {question_set_used}")
            
            if question_set_used == 'E':
                print("✅ SUCCESS: New session correctly uses Set E!")
                return True
            else:
                print(f"❌ FAILURE: Expected Set E, got Set {question_set_used}")
                return False
        else:
            print("❌ FAILURE: No questions found in new session")
            return False
            
    except Exception as e:
        print(f"❌ Failed to generate session with Set E: {e}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    try:
        # Delete test sessions
        ExamSession.objects.filter(user__username='test_candidate_fix').delete()
        
        # Delete test candidate
        CandidateProfile.objects.filter(army_no='TEST123456').delete()
        
        # Delete test user
        User.objects.filter(username='test_candidate_fix').delete()
        
        print("✅ Test data cleaned up")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

def main():
    print("🔧 Exam Session Persistence Fix Test")
    print("=" * 50)
    
    try:
        success = test_session_persistence_fix()
        
        if success:
            print("\n🎉 TEST PASSED: Session persistence fix is working!")
            print("   Candidates will now get updated question sets after slot changes.")
        else:
            print("\n❌ TEST FAILED: Session persistence issue still exists.")
            print("   Check the fix implementation.")
            
    except Exception as e:
        print(f"\n💥 TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cleanup_test_data()

if __name__ == "__main__":
    main()