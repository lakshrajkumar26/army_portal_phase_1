#!/usr/bin/env python
"""
Debug script to identify exam slot and question count issues
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from registration.models import CandidateProfile
from questions.models import Question, QuestionSetActivation, TradePaperActivation, HARD_CODED_TRADE_CONFIG, HARD_CODED_COMMON_DISTRIBUTION
from reference.models import Trade

User = get_user_model()

def debug_exam_issues():
    """Debug the exam slot and question count issues"""
    
    print("=== DEBUGGING EXAM ISSUES ===\n")
    
    # Find the test candidate
    try:
        candidate = CandidateProfile.objects.get(army_no='12345')
        print(f"Found candidate: {candidate.name} (Army No: {candidate.army_no})")
        print(f"Trade: {candidate.trade}")
        print(f"Has exam slot: {candidate.has_exam_slot}")
        print(f"Slot assigned at: {candidate.slot_assigned_at}")
        print(f"Submitted at: {candidate.slot_consumed_at}")
        print(f"Slot status: {candidate.slot_status}")
        print()
        
        # Check trade activation
        if candidate.trade:
            activations = TradePaperActivation.objects.filter(trade=candidate.trade)
            print(f"Trade activations for {candidate.trade}:")
            for activation in activations:
                print(f"  - {activation.paper_type}: {'ACTIVE' if activation.is_active else 'INACTIVE'}")
            
            active_activation = activations.filter(is_active=True).first()
            if active_activation:
                print(f"\nActive paper type: {active_activation.paper_type}")
                
                # Check question set activation
                try:
                    qs_activation = QuestionSetActivation.objects.get(
                        trade=candidate.trade,
                        paper_type=active_activation.paper_type,
                        is_active=True
                    )
                    print(f"Active question set: {qs_activation.question_set}")
                    
                    # Check available questions (using same logic as generate_for_candidate)
                    if active_activation.paper_type == "SECONDARY":
                        questions = Question.objects.filter(
                            paper_type="SECONDARY",
                            is_common=True,
                            question_set=qs_activation.question_set,
                            is_active=True,
                            text__icontains=candidate.trade.code.upper()  # Filter by trade code
                        )
                    else:
                        questions = Question.objects.filter(
                            trade=candidate.trade,
                            paper_type="PRIMARY",
                            question_set=qs_activation.question_set,
                            is_active=True
                        )
                    
                    print(f"Available questions in set {qs_activation.question_set}: {questions.count()}")
                    
                    # Check part distribution
                    part_counts = {}
                    for part in ['A', 'B', 'C', 'D', 'E', 'F']:
                        count = questions.filter(part=part).count()
                        if count > 0:
                            part_counts[part] = count
                    
                    print("Questions by part:")
                    for part, count in part_counts.items():
                        print(f"  Part {part}: {count} questions")
                    
                    # Check expected distribution
                    if active_activation.paper_type == "SECONDARY":
                        expected_dist = HARD_CODED_COMMON_DISTRIBUTION
                    else:
                        trade_code = candidate.trade.code.upper()
                        if trade_code in HARD_CODED_TRADE_CONFIG:
                            expected_dist = HARD_CODED_TRADE_CONFIG[trade_code]["part_distribution"]
                            expected_total = HARD_CODED_TRADE_CONFIG[trade_code]["total_questions"]
                            print(f"\nExpected total questions: {expected_total}")
                        else:
                            expected_dist = HARD_CODED_COMMON_DISTRIBUTION
                    
                    print("\nExpected distribution:")
                    total_expected = 0
                    for part, expected_count in expected_dist.items():
                        if expected_count > 0:
                            available_count = part_counts.get(part, 0)
                            status = "✅" if available_count >= expected_count else "❌"
                            print(f"  Part {part}: {expected_count} required, {available_count} available {status}")
                            total_expected += expected_count
                    
                    print(f"\nTotal expected: {total_expected}")
                    print(f"Total available: {sum(part_counts.values())}")
                    
                except QuestionSetActivation.DoesNotExist:
                    print("No active question set found!")
            else:
                print("No active paper type found!")
        
        # Check all question sets available for this trade
        print(f"\n=== ALL QUESTION SETS FOR {candidate.trade} ===")
        if candidate.trade:
            all_sets = Question.objects.filter(
                trade=candidate.trade,
                is_active=True
            ).values_list('question_set', flat=True).distinct().order_by('question_set')
            
            print(f"Available question sets: {list(all_sets)}")
            
            for question_set in all_sets:
                count = Question.objects.filter(
                    trade=candidate.trade,
                    question_set=question_set,
                    is_active=True
                ).count()
                print(f"  Set {question_set}: {count} questions")
        
    except CandidateProfile.DoesNotExist:
        print("Candidate with army_no='12345' not found")
    
    print("\n=== CHECKING ALL CANDIDATES WITH SLOT ISSUES ===")
    
    # Check all candidates with consumed slots
    consumed_candidates = CandidateProfile.objects.filter(
        slot_consumed_at__isnull=False
    )
    
    print(f"Candidates with consumed slots: {consumed_candidates.count()}")
    for candidate in consumed_candidates:
        print(f"  - {candidate.army_no} ({candidate.name}): consumed at {candidate.slot_consumed_at}")

if __name__ == '__main__':
    debug_exam_issues()