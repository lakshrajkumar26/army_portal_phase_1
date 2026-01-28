#!/usr/bin/env python
"""
Debug the SECONDARY question filtering issue - why showing 108 instead of 54
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import Question, QuestionSetActivation, TradePaperActivation
from reference.models import Trade

def debug_secondary_filtering():
    """Debug why SECONDARY questions show 108 instead of 54"""
    
    try:
        occ_trade = Trade.objects.get(code='OCC')
        print(f"Debugging SECONDARY questions for {occ_trade}")
        
        # Check current activation
        activation = TradePaperActivation.objects.filter(
            trade=occ_trade,
            is_active=True
        ).first()
        
        print(f"Current active paper type: {activation.paper_type if activation else 'None'}")
        
        # Check question set activation
        try:
            qs_activation = QuestionSetActivation.objects.get(
                trade=occ_trade,
                paper_type='SECONDARY',
                is_active=True
            )
            active_set = qs_activation.question_set
            print(f"Active SECONDARY question set: {active_set}")
        except QuestionSetActivation.DoesNotExist:
            active_set = 'A'
            print(f"No active SECONDARY set found, using default: {active_set}")
        
        print(f"\n=== SECONDARY QUESTION ANALYSIS ===")
        
        # Current logic (what's happening now)
        print(f"1. Current filtering logic:")
        current_filter = Question.objects.filter(
            paper_type="SECONDARY",
            is_common=True,
            question_set=active_set,
            is_active=True
        )
        print(f"   paper_type=SECONDARY, is_common=True, question_set={active_set}, is_active=True")
        print(f"   Total questions found: {current_filter.count()}")
        
        # Show breakdown by trade mentioned in text
        print(f"\n2. Breakdown by trade mentioned in question text:")
        all_trades = Trade.objects.all()
        for trade in all_trades:
            trade_questions = current_filter.filter(text__icontains=trade.code.upper())
            if trade_questions.count() > 0:
                print(f"   {trade.code}: {trade_questions.count()} questions")
        
        # Show part distribution
        print(f"\n3. Part distribution for Set {active_set}:")
        for part in ['A', 'B', 'C', 'D', 'E', 'F']:
            part_count = current_filter.filter(part=part).count()
            if part_count > 0:
                print(f"   Part {part}: {part_count} questions")
        
        print(f"\n=== PROPOSED FIX ===")
        
        # Proposed fix - filter by trade code in text
        print(f"4. Proposed filtering logic (filter by trade code in text):")
        proposed_filter = Question.objects.filter(
            paper_type="SECONDARY",
            is_common=True,
            question_set=active_set,
            is_active=True,
            text__icontains=occ_trade.code.upper()  # Only OCC questions
        )
        print(f"   paper_type=SECONDARY, is_common=True, question_set={active_set}, is_active=True, text__icontains='OCC'")
        print(f"   Total questions found: {proposed_filter.count()}")
        
        # Show part distribution for proposed fix
        print(f"\n5. Part distribution for OCC-only Set {active_set}:")
        for part in ['A', 'B', 'C', 'D', 'E', 'F']:
            part_count = proposed_filter.filter(part=part).count()
            if part_count > 0:
                print(f"   Part {part}: {part_count} questions")
        
        # Show sample questions
        print(f"\n6. Sample questions from proposed filter:")
        sample_questions = proposed_filter[:5]
        for i, q in enumerate(sample_questions, 1):
            print(f"   {i}. [{q.part}] {q.text[:80]}...")
        
    except Trade.DoesNotExist:
        print("OCC trade not found!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_secondary_filtering()