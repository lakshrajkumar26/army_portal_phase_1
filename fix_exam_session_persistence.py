#!/usr/bin/env python3
"""
Fix for Exam Session Persistence Issue

This script addresses the core problem where candidates get stuck with old question sets
even after slot resets and question set changes.

Root Cause:
- ExamSession records with linked ExamQuestion records persist in database
- System resumes old sessions instead of generating new ones with updated question sets
- Question set changes don't clear existing incomplete sessions

Solution:
1. Clear incomplete exam sessions when slots are reset
2. Clear incomplete exam sessions when question sets change
3. Update slot management methods to handle session cleanup
4. Add admin tools for manual session cleanup
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from questions.models import ExamSession, ActivateSets, QuestionSetActivation
from registration.models import CandidateProfile
from reference.models import Trade

def clear_incomplete_sessions_for_user(user, paper_type=None):
    """Clear incomplete exam sessions for a specific user"""
    query = ExamSession.objects.filter(
        user=user,
        completed_at__isnull=True
    )
    
    if paper_type:
        query = query.filter(paper__question_paper=paper_type)
    
    deleted_count = query.count()
    if deleted_count > 0:
        query.delete()
        print(f"✅ Cleared {deleted_count} incomplete sessions for user {user.username}")
    
    return deleted_count

def clear_incomplete_sessions_for_trade(trade, paper_type=None):
    """Clear incomplete exam sessions for all candidates of a specific trade"""
    candidates = CandidateProfile.objects.filter(trade=trade)
    total_cleared = 0
    
    for candidate in candidates:
        cleared = clear_incomplete_sessions_for_user(candidate.user, paper_type)
        total_cleared += cleared
    
    print(f"✅ Cleared {total_cleared} total incomplete sessions for trade {trade.name}")
    return total_cleared

def clear_all_incomplete_sessions():
    """Clear all incomplete exam sessions in the system"""
    deleted_count = ExamSession.objects.filter(completed_at__isnull=True).count()
    if deleted_count > 0:
        ExamSession.objects.filter(completed_at__isnull=True).delete()
        print(f"✅ Cleared {deleted_count} incomplete sessions system-wide")
    else:
        print("ℹ️ No incomplete sessions found")
    
    return deleted_count

def fix_candidate_session_persistence(army_no):
    """Fix session persistence for a specific candidate by army number"""
    try:
        candidate = CandidateProfile.objects.get(army_no=army_no)
        cleared = clear_incomplete_sessions_for_user(candidate.user)
        
        # Reset slot to ensure fresh assignment
        candidate.reset_exam_slot()
        print(f"✅ Reset exam slot for {candidate.name} ({army_no})")
        
        return True
    except CandidateProfile.DoesNotExist:
        print(f"❌ Candidate with army number {army_no} not found")
        return False

def fix_trade_session_persistence(trade_name):
    """Fix session persistence for all candidates of a specific trade"""
    try:
        trade = Trade.objects.get(name__iexact=trade_name)
        cleared = clear_incomplete_sessions_for_trade(trade)
        
        # Reset slots for all candidates of this trade
        candidates = CandidateProfile.objects.filter(trade=trade, has_exam_slot=True)
        reset_count = 0
        for candidate in candidates:
            candidate.reset_exam_slot()
            reset_count += 1
        
        print(f"✅ Reset exam slots for {reset_count} candidates in {trade.name}")
        return True
    except Trade.DoesNotExist:
        print(f"❌ Trade {trade_name} not found")
        return False

def main():
    print("🔧 Exam Session Persistence Fix Tool")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Fix specific candidate (by army number)")
        print("2. Fix all candidates of a trade")
        print("3. Clear all incomplete sessions (DANGER)")
        print("4. Show incomplete session statistics")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            army_no = input("Enter army number: ").strip()
            if army_no:
                fix_candidate_session_persistence(army_no)
        
        elif choice == "2":
            trade_name = input("Enter trade name: ").strip()
            if trade_name:
                fix_trade_session_persistence(trade_name)
        
        elif choice == "3":
            confirm = input("⚠️ This will clear ALL incomplete sessions. Type 'CONFIRM' to proceed: ").strip()
            if confirm == "CONFIRM":
                clear_all_incomplete_sessions()
            else:
                print("❌ Operation cancelled")
        
        elif choice == "4":
            show_session_statistics()
        
        elif choice == "5":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

def show_session_statistics():
    """Show statistics about incomplete sessions"""
    print("\n📊 Incomplete Session Statistics")
    print("-" * 30)
    
    total_incomplete = ExamSession.objects.filter(completed_at__isnull=True).count()
    print(f"Total incomplete sessions: {total_incomplete}")
    
    if total_incomplete > 0:
        # Group by paper type
        from django.db.models import Count
        by_paper = ExamSession.objects.filter(
            completed_at__isnull=True
        ).values('paper__question_paper').annotate(
            count=Count('id')
        ).order_by('-count')
        
        print("\nBy paper type:")
        for item in by_paper:
            print(f"  {item['paper__question_paper']}: {item['count']} sessions")
        
        # Group by trade
        by_trade = ExamSession.objects.filter(
            completed_at__isnull=True
        ).values('trade__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        print("\nBy trade:")
        for item in by_trade[:10]:  # Top 10
            trade_name = item['trade__name'] or 'No Trade'
            print(f"  {trade_name}: {item['count']} sessions")

if __name__ == "__main__":
    main()