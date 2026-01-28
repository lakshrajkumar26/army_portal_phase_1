#!/usr/bin/env python
"""
Complete verification of the SECONDARY question filtering fix
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from registration.models import CandidateProfile
from questions.models import QuestionPaper, ExamSession, Question
from reference.models import Trade

User = get_user_model()

def test_complete_fix():
    """Test the complete fix for SECONDARY question filtering"""
    
    print("=== COMPLETE FIX VERIFICATION ===\n")
    
    try:
        candidate = CandidateProfile.objects.get(army_no='12345')
        trade = candidate.trade
        
        print(f"Testing for candidate: {candidate.name} (Trade: {trade.code})")
        
        # 1. Test question counts before generation
        print(f"\n1. QUESTION AVAILABILITY CHECK:")
        
        # Check all SECONDARY questions (should be 108 total)
        all_secondary = Question.objects.filter(
            paper_type="SECONDARY",
            is_common=True,
            question_set='C',
            is_active=True
        ).count()
        print(f"   Total SECONDARY Set C questions: {all_secondary}")
        
        # Check OCC-specific SECONDARY questions (should be 54)
        occ_secondary = Question.objects.filter(
            paper_type="SECONDARY",
            is_common=True,
            question_set='C',
            is_active=True,
            text__icontains='OCC'
        ).count()
        print(f"   OCC-specific SECONDARY Set C questions: {occ_secondary}")
        
        # Check DMV-specific SECONDARY questions (should be 54)
        dmv_secondary = Question.objects.filter(
            paper_type="SECONDARY",
            is_common=True,
            question_set='C',
            is_active=True,
            text__icontains='DMV'
        ).count()
        print(f"   DMV-specific SECONDARY Set C questions: {dmv_secondary}")
        
        # 2. Test actual question generation
        print(f"\n2. QUESTION GENERATION TEST:")
        
        # Get paper
        paper = QuestionPaper.objects.filter(
            question_paper='SECONDARY',
            is_active=True
        ).first()
        
        if not paper:
            print("   ❌ No SECONDARY paper found!")
            return
        
        # Clear any existing sessions
        ExamSession.objects.filter(user=candidate.user, paper=paper).delete()
        
        # Generate session
        session = paper.generate_for_candidate(
            user=candidate.user,
            trade=trade
        )
        
        print(f"   ✅ Session generated with {session.total_questions} questions")
        
        # 3. Verify generated questions are OCC-specific
        print(f"\n3. GENERATED QUESTIONS VERIFICATION:")
        
        questions = session.questions.all()
        occ_count = 0
        dmv_count = 0
        other_count = 0
        
        for eq in questions:
            question_text = eq.question.text.upper()
            if 'OCC' in question_text:
                occ_count += 1
            elif 'DMV' in question_text:
                dmv_count += 1
            else:
                other_count += 1
        
        print(f"   OCC questions: {occ_count}")
        print(f"   DMV questions: {dmv_count}")
        print(f"   Other questions: {other_count}")
        
        # 4. Verify part distribution
        print(f"\n4. PART DISTRIBUTION VERIFICATION:")
        
        part_counts = {}
        for eq in questions:
            part = eq.question.part
            part_counts[part] = part_counts.get(part, 0) + 1
        
        expected_dist = {"A": 20, "C": 5, "D": 15, "E": 4, "F": 10}
        
        for part, expected in expected_dist.items():
            actual = part_counts.get(part, 0)
            status = "✅" if actual == expected else "❌"
            print(f"   Part {part}: {actual}/{expected} {status}")
        
        # 5. Final verification
        print(f"\n5. FINAL VERIFICATION:")
        
        if session.total_questions == 54 and dmv_count == 0 and occ_count == 54:
            print("   ✅ SUCCESS: Fix is working correctly!")
            print("   - Exactly 54 questions generated")
            print("   - All questions are OCC-specific")
            print("   - No DMV questions included")
        else:
            print("   ❌ ISSUE: Fix needs more work")
            print(f"   - Total questions: {session.total_questions} (expected: 54)")
            print(f"   - OCC questions: {occ_count} (expected: 54)")
            print(f"   - DMV questions: {dmv_count} (expected: 0)")
        
    except CandidateProfile.DoesNotExist:
        print("Candidate not found!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_complete_fix()