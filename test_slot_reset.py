#!/usr/bin/env python
"""
Test slot reset and reassignment functionality
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from registration.models import CandidateProfile
from django.utils import timezone

def test_slot_reset():
    """Test the slot reset and reassignment logic"""
    
    try:
        candidate = CandidateProfile.objects.get(army_no='12345')
        
        print("=== BEFORE RESET ===")
        print(f"Has exam slot: {candidate.has_exam_slot}")
        print(f"Slot assigned at: {candidate.slot_assigned_at}")
        print(f"Submitted at: {candidate.slot_consumed_at}")
        print(f"Can start exam: {candidate.can_start_exam}")
        print(f"Slot status: {candidate.slot_status}")
        
        # Reset the slot
        print("\n=== RESETTING SLOT ===")
        candidate.reset_exam_slot()
        candidate.refresh_from_db()
        
        print(f"Has exam slot: {candidate.has_exam_slot}")
        print(f"Slot assigned at: {candidate.slot_assigned_at}")
        print(f"Submitted at: {candidate.slot_consumed_at}")
        print(f"Can start exam: {candidate.can_start_exam}")
        print(f"Slot status: {candidate.slot_status}")
        
        # Assign new slot
        print("\n=== ASSIGNING NEW SLOT ===")
        candidate.assign_exam_slot()
        candidate.refresh_from_db()
        
        print(f"Has exam slot: {candidate.has_exam_slot}")
        print(f"Slot assigned at: {candidate.slot_assigned_at}")
        print(f"Submitted at: {candidate.slot_consumed_at}")
        print(f"Can start exam: {candidate.can_start_exam}")
        print(f"Slot status: {candidate.slot_status}")
        
    except CandidateProfile.DoesNotExist:
        print("Candidate not found!")

if __name__ == '__main__':
    test_slot_reset()