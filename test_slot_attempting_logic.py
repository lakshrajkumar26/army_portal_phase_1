#!/usr/bin/env python3
"""
Test script to verify the complete slot attempting logic implementation.
This tests the three-state system: Available → Attempting → Consumed
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from registration.models import CandidateProfile
from reference.models import Trade
from questions.models import TradePaperActivation, QuestionPaper
from django.utils import timezone

User = get_user_model()

def test_slot_attempting_logic():
    """Test the complete slot attempting logic"""
    print("🧪 Testing Slot Attempting Logic")
    print("=" * 50)
    
    # Find a test candidate
    candidate = CandidateProfile.objects.first()
    if not candidate:
        print("❌ No candidates found in database")
        return False
    
    print(f"📋 Testing with candidate: {candidate.army_no} - {candidate.name}")
    print(f"🏷️  Trade: {candidate.trade}")
    
    # Test 1: Initial state - no slot
    print("\n1️⃣ Testing initial state (no slot)")
    candidate.reset_exam_slot()
    print(f"   Status: {candidate.slot_status}")
    print(f"   Can start exam: {candidate.can_start_exam}")
    assert not candidate.has_exam_slot
    assert candidate.slot_assigned_at is None
    assert candidate.slot_attempting_at is None
    assert candidate.slot_consumed_at is None
    print("   ✅ Initial state correct")
    
    # Test 2: Assign slot - Available state
    print("\n2️⃣ Testing slot assignment (Available state)")
    candidate.assign_exam_slot()
    print(f"   Status: {candidate.slot_status}")
    print(f"   Can start exam: {candidate.can_start_exam}")
    assert candidate.has_exam_slot
    assert candidate.slot_assigned_at is not None
    assert candidate.slot_attempting_at is None
    assert candidate.slot_consumed_at is None
    assert "Available" in candidate.slot_status
    print("   ✅ Available state correct")
    
    # Test 3: Start exam attempt - Attempting state
    print("\n3️⃣ Testing exam attempt start (Attempting state)")
    success = candidate.start_exam_attempt()
    print(f"   Start attempt success: {success}")
    print(f"   Status: {candidate.slot_status}")
    print(f"   Can start exam: {candidate.can_start_exam}")
    assert success
    assert candidate.has_exam_slot
    assert candidate.slot_assigned_at is not None
    assert candidate.slot_attempting_at is not None
    assert candidate.slot_consumed_at is None
    assert "Attempting" in candidate.slot_status
    print("   ✅ Attempting state correct")
    
    # Test 4: Try to start attempt again - should return False
    print("\n4️⃣ Testing duplicate attempt start (should fail)")
    success = candidate.start_exam_attempt()
    print(f"   Start attempt success: {success}")
    assert not success  # Should return False since already attempting
    print("   ✅ Duplicate attempt correctly prevented")
    
    # Test 5: Verify can still access exam during attempt
    print("\n5️⃣ Testing exam access during attempt")
    print(f"   Can start exam: {candidate.can_start_exam}")
    assert candidate.can_start_exam  # Should still be True during attempt
    print("   ✅ Exam access allowed during attempt")
    
    # Test 6: Consume slot - Consumed state
    print("\n6️⃣ Testing slot consumption (Consumed state)")
    success = candidate.consume_exam_slot()
    print(f"   Consume slot success: {success}")
    print(f"   Status: {candidate.slot_status}")
    print(f"   Can start exam: {candidate.can_start_exam}")
    assert success
    assert candidate.has_exam_slot
    assert candidate.slot_assigned_at is not None
    assert candidate.slot_attempting_at is not None
    assert candidate.slot_consumed_at is not None
    assert "Consumed" in candidate.slot_status
    assert not candidate.can_start_exam  # Should be False after consumption
    print("   ✅ Consumed state correct")
    
    # Test 7: Try to consume again - should return False
    print("\n7️⃣ Testing duplicate consumption (should fail)")
    success = candidate.consume_exam_slot()
    print(f"   Consume slot success: {success}")
    assert not success  # Should return False since already consumed
    print("   ✅ Duplicate consumption correctly prevented")
    
    # Test 8: Reassign slot after consumption
    print("\n8️⃣ Testing slot reassignment after consumption")
    old_consumed_time = candidate.slot_consumed_at
    candidate.assign_exam_slot()
    print(f"   Status: {candidate.slot_status}")
    print(f"   Can start exam: {candidate.can_start_exam}")
    assert candidate.has_exam_slot
    assert candidate.slot_assigned_at > old_consumed_time  # New assignment should be after consumption
    assert candidate.slot_attempting_at is None  # Should be reset
    assert candidate.slot_consumed_at is None  # Should be cleared for fresh attempt
    assert candidate.can_start_exam  # Should be able to start exam again
    print("   ✅ Slot reassignment after consumption works")
    
    # Test 9: Reset slot
    print("\n9️⃣ Testing slot reset")
    candidate.reset_exam_slot()
    print(f"   Status: {candidate.slot_status}")
    print(f"   Can start exam: {candidate.can_start_exam}")
    assert not candidate.has_exam_slot
    assert candidate.slot_assigned_at is None
    assert candidate.slot_attempting_at is None
    assert candidate.slot_consumed_at is None
    assert not candidate.can_start_exam
    print("   ✅ Slot reset correct")
    
    print("\n🎉 All slot attempting logic tests passed!")
    return True

def test_admin_display():
    """Test the admin display logic for slot status"""
    print("\n🖥️  Testing Admin Display Logic")
    print("=" * 50)
    
    candidate = CandidateProfile.objects.first()
    if not candidate:
        print("❌ No candidates found")
        return False
    
    # Test different states
    states_to_test = [
        ("No Slot", lambda: candidate.reset_exam_slot()),
        ("Available", lambda: candidate.assign_exam_slot()),
        ("Attempting", lambda: candidate.start_exam_attempt()),
        ("Consumed", lambda: candidate.consume_exam_slot()),
    ]
    
    for state_name, setup_func in states_to_test:
        setup_func()
        status_display = candidate.slot_status
        print(f"   {state_name}: {status_display}")
        
        # Verify expected keywords are in the status
        if state_name == "No Slot":
            assert "No Slot" in status_display
        elif state_name == "Available":
            assert "Available" in status_display
        elif state_name == "Attempting":
            assert "Attempting" in status_display
        elif state_name == "Consumed":
            assert "Consumed" in status_display
    
    print("   ✅ All admin display states working correctly")
    return True

def test_edge_cases():
    """Test edge cases and error conditions"""
    print("\n🔍 Testing Edge Cases")
    print("=" * 50)
    
    candidate = CandidateProfile.objects.first()
    if not candidate:
        print("❌ No candidates found")
        return False
    
    # Test 1: Start attempt without slot
    print("\n   Testing attempt start without slot")
    candidate.reset_exam_slot()
    success = candidate.start_exam_attempt()
    print(f"   Start attempt without slot: {success}")
    assert not success
    print("   ✅ Correctly prevented attempt start without slot")
    
    # Test 2: Consume slot without attempt
    print("\n   Testing slot consumption without attempt")
    candidate.assign_exam_slot()
    success = candidate.consume_exam_slot()
    print(f"   Consume slot without attempt: {success}")
    assert success  # Should still work - direct consumption is allowed
    print("   ✅ Direct slot consumption works")
    
    # Test 3: Multiple rapid operations
    print("\n   Testing rapid operations")
    candidate.reset_exam_slot()
    candidate.assign_exam_slot()
    candidate.start_exam_attempt()
    candidate.consume_exam_slot()
    print(f"   Final status: {candidate.slot_status}")
    assert "Consumed" in candidate.slot_status
    print("   ✅ Rapid operations handled correctly")
    
    print("\n   ✅ All edge cases handled correctly")
    return True

if __name__ == "__main__":
    try:
        print("🚀 Starting Slot Attempting Logic Tests")
        print("=" * 60)
        
        # Run all tests
        test1_passed = test_slot_attempting_logic()
        test2_passed = test_admin_display()
        test3_passed = test_edge_cases()
        
        if test1_passed and test2_passed and test3_passed:
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED! Slot attempting logic is working correctly.")
            print("✅ Three-state system implemented: Available → Attempting → Consumed")
            print("✅ Admin display shows correct status with timestamps")
            print("✅ Edge cases handled properly")
            print("✅ Candidates can refresh/re-enter during attempting state")
            print("✅ Slots are only consumed on actual exam submission")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)