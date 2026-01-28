#!/usr/bin/env python3
"""
Check what question sets are actually available in the database
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import Question
from reference.models import Trade

def check_available_sets():
    """Check what question sets are available"""
    print("🔍 Checking Available Question Sets...")
    print("=" * 60)
    
    # Get all trades
    trades = Trade.objects.all()
    
    for trade in trades:
        print(f"\n📊 Trade: {trade.name} ({trade.code})")
        
        # Check PRIMARY questions
        primary_sets = Question.objects.filter(
            trade=trade,
            paper_type="PRIMARY",
            is_active=True
        ).values_list('question_set', flat=True).distinct().order_by('question_set')
        
        if primary_sets:
            print(f"   PRIMARY Sets: {list(primary_sets)}")
            for qset in primary_sets:
                count = Question.objects.filter(
                    trade=trade,
                    paper_type="PRIMARY",
                    question_set=qset,
                    is_active=True
                ).count()
                print(f"     Set {qset}: {count} questions")
        else:
            print("   PRIMARY Sets: None")
        
        # Check SECONDARY questions (common questions)
        secondary_sets = Question.objects.filter(
            paper_type="SECONDARY",
            is_common=True,
            is_active=True
        ).values_list('question_set', flat=True).distinct().order_by('question_set')
        
        if secondary_sets:
            print(f"   SECONDARY Sets: {list(secondary_sets)}")
            for qset in secondary_sets:
                count = Question.objects.filter(
                    paper_type="SECONDARY",
                    is_common=True,
                    question_set=qset,
                    is_active=True
                ).count()
                print(f"     Set {qset}: {count} questions")
        else:
            print("   SECONDARY Sets: None")

if __name__ == "__main__":
    check_available_sets()