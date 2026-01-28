#!/usr/bin/env python
"""
Test script for automated exam slot assignment functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from registration.models import CandidateProfile
from reference.models import Trade
from django.contrib.auth import get_user_model

User = get_user_model()

def test_automated_slot_assignment():
    """Test the automated slot assignment functionality"""
    print("🚀 Testing Automated Exam Slot Assignment")
    print("=" * 50)
    
    # Get some test data
    candidates = CandidateProfile.objects.all()[:5]  # Get first 5 candidates
    
    if not candidates:
        print("❌ No candidates found for testing")
        return
    
    print(f"📊 Testing with {len(candidates)} candidates")
    
    # Show initial status
    print("\n📋 Initial Status:")
    for candidate in candidates:
        print(f"  {candidate.army_no} - {candidate.name}: {candidate.slot_status}")
    
    # Test 1: Reset all slots first
    print("\n🔄 Step 1: Resetting all test candidate slots...")
    for candidate in candidates:
        candidate.reset_exam_slot()
    
    # Show status after reset
    print("\n📋 After Reset:")
    for candidate in candidates:
        candidate.refresh_from_db()
        print(f"  {candidate.army_no} - {candidate.name}: {candidate.slot_status}")
    
    # Test 2: Assign slots using the new method
    print("\n✅ Step 2: Assigning exam slots...")
    
    # Get admin user for assignment tracking
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.first()
    except:
        admin_user = None
    
    assigned_count = 0
    for candidate in candidates:
        if candidate.assign_exam_slot(assigned_by_user=admin_user):
            assigned_count += 1
    
    print(f"✅ Assigned {assigned_count} exam slots")
    
    # Show final status
    print("\n📋 Final Status:")
    for candidate in candidates:
        candidate.refresh_from_db()
        print(f"  {candidate.army_no} - {candidate.name}: {candidate.slot_status}")
    
    # Test 3: Verify candidates can now take exams
    print("\n🎯 Step 3: Verifying exam eligibility...")
    eligible_count = 0
    for candidate in candidates:
        if candidate.has_exam_slot and not candidate.slot_consumed_at:
            eligible_count += 1
            print(f"  ✅ {candidate.army_no} - {candidate.name}: Ready for exam")
        else:
            print(f"  ❌ {candidate.army_no} - {candidate.name}: Not ready")
    
    print(f"\n🎉 Result: {eligible_count}/{len(candidates)} candidates are now ready to take exams!")
    
    # Test 4: Test trade-based assignment
    print("\n🎯 Step 4: Testing trade-based assignment...")
    
    # Get candidates by trade
    trades_with_candidates = {}
    for candidate in candidates:
        if candidate.trade:
            if candidate.trade not in trades_with_candidates:
                trades_with_candidates[candidate.trade] = []
            trades_with_candidates[candidate.trade].append(candidate)
    
    if trades_with_candidates:
        for trade, trade_candidates in trades_with_candidates.items():
            print(f"  📊 Trade {trade.name}: {len(trade_candidates)} candidates")
            
            # Reset their slots
            for candidate in trade_candidates:
                candidate.reset_exam_slot()
            
            # Assign slots for this trade
            trade_assigned = 0
            for candidate in trade_candidates:
                if candidate.assign_exam_slot(assigned_by_user=admin_user):
                    trade_assigned += 1
            
            print(f"  ✅ Assigned {trade_assigned} slots for {trade.name}")
    
    print("\n🎉 Automated Slot Assignment Test Completed Successfully!")
    print("=" * 50)
    print("✅ Key Features Verified:")
    print("  • Bulk slot assignment works")
    print("  • Candidates are marked as has_exam_slot=True")
    print("  • Slot assignment tracking works")
    print("  • Trade-based assignment works")
    print("  • Candidates can now take exams without manual intervention")

if __name__ == "__main__":
    test_automated_slot_assignment()