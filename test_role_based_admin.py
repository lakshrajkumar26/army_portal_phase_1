#!/usr/bin/env python3
"""
Test script to verify role-based admin interface functionality.
Tests PO_ADMIN vs CENTER_ADMIN permissions and display differences.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from registration.models import CandidateProfile
from registration.admin import CandidateProfileAdmin
from django.test import RequestFactory
from django.contrib.admin.sites import AdminSite

User = get_user_model()

def create_mock_request(user):
    """Create a mock request with the given user"""
    factory = RequestFactory()
    request = factory.get('/admin/registration/candidateprofile/')
    request.user = user
    return request

def test_role_permissions():
    """Test role-based permissions and display logic"""
    print("🧪 Testing Role-Based Admin Interface")
    print("=" * 60)
    
    # Get users by role
    po_admin = User.objects.filter(role='PO_ADMIN').first()
    center_admin = User.objects.filter(role='CENTER_ADMIN').first()
    superuser = User.objects.filter(is_superuser=True).first()
    
    if not po_admin:
        print("❌ No PO_ADMIN user found")
        return False
    
    if not center_admin:
        print("❌ No CENTER_ADMIN user found")
        return False
    
    print(f"📋 Testing with:")
    print(f"   PO_ADMIN: {po_admin.username} (role: {po_admin.role})")
    print(f"   CENTER_ADMIN: {center_admin.username} (role: {center_admin.role})")
    if superuser:
        print(f"   SUPERUSER: {superuser.username} (is_superuser: {superuser.is_superuser})")
    
    # Create admin instance
    admin_site = AdminSite()
    admin = CandidateProfileAdmin(CandidateProfile, admin_site)
    
    # Test 1: Role detection methods
    print("\n1️⃣ Testing Role Detection Methods")
    print("-" * 40)
    
    po_request = create_mock_request(po_admin)
    center_request = create_mock_request(center_admin)
    
    print(f"   PO_ADMIN detection:")
    print(f"     _is_po_admin(po_request): {admin._is_po_admin(po_request)}")
    print(f"     _is_center_admin(po_request): {admin._is_center_admin(center_request)}")
    
    print(f"   CENTER_ADMIN detection:")
    print(f"     _is_po_admin(center_request): {admin._is_po_admin(center_request)}")
    print(f"     _is_center_admin(center_request): {admin._is_center_admin(center_request)}")
    
    # Test 2: List display differences
    print("\n2️⃣ Testing List Display Differences")
    print("-" * 40)
    
    po_display = admin.get_list_display(po_request)
    center_display = admin.get_list_display(center_request)
    
    print(f"   PO_ADMIN list_display: {po_display}")
    print(f"   CENTER_ADMIN list_display: {center_display}")
    
    # Verify PO_ADMIN has marks fields
    marks_fields = ["primary_practical_marks", "primary_viva_marks", "secondary_practical_marks", "secondary_viva_marks"]
    po_has_marks = all(field in po_display for field in marks_fields)
    center_has_marks = any(field in center_display for field in marks_fields)
    
    print(f"   PO_ADMIN has marks fields: {po_has_marks}")
    print(f"   CENTER_ADMIN has marks fields: {center_has_marks}")
    
    # Verify CENTER_ADMIN has trade/question display
    center_has_trade = "trade_questions_display" in center_display
    po_has_trade = "trade_questions_display" in po_display
    
    print(f"   PO_ADMIN has trade display: {po_has_trade}")
    print(f"   CENTER_ADMIN has trade display: {center_has_trade}")
    
    # Verify PO_ADMIN does NOT have slot status
    po_has_slot_status = any("slot_status" in field for field in po_display)
    center_has_slot_status = any("slot_status" in field for field in center_display)
    
    print(f"   PO_ADMIN has slot status: {po_has_slot_status}")
    print(f"   CENTER_ADMIN has slot status: {center_has_slot_status}")
    
    # Test 3: Actions differences
    print("\n3️⃣ Testing Actions Differences")
    print("-" * 40)
    
    po_actions = admin.get_actions(po_request)
    center_actions = admin.get_actions(center_request)
    
    print(f"   PO_ADMIN actions: {list(po_actions.keys())}")
    print(f"   CENTER_ADMIN actions: {list(center_actions.keys())}")
    
    # Verify PO_ADMIN has export actions
    export_actions = ["export_candidates_dat", "export_candidate_images", "export_marks_excel", "export_evaluation_results_dat"]
    po_has_exports = any(action in po_actions for action in export_actions)
    center_has_exports = any(action in center_actions for action in export_actions)
    
    print(f"   PO_ADMIN has export actions: {po_has_exports}")
    print(f"   CENTER_ADMIN has export actions: {center_has_exports}")
    
    # Verify CENTER_ADMIN has slot management actions
    slot_actions = ["assign_exam_slots", "reset_exam_slots", "reassign_exam_slots"]
    po_has_slots = any(action in po_actions for action in slot_actions)
    center_has_slots = any(action in center_actions for action in slot_actions)
    
    print(f"   PO_ADMIN has slot actions: {po_has_slots}")
    print(f"   CENTER_ADMIN has slot actions: {center_has_slots}")
    
    # Test 4: Field access differences
    print("\n4️⃣ Testing Field Access Differences")
    print("-" * 40)
    
    po_fields = admin.get_fields(po_request)
    center_fields = admin.get_fields(center_request)
    
    print(f"   PO_ADMIN fields count: {len(po_fields)}")
    print(f"   CENTER_ADMIN fields count: {len(center_fields)}")
    
    po_readonly = admin.get_readonly_fields(po_request)
    center_readonly = admin.get_readonly_fields(center_request)
    
    # Check if marks are readonly for CENTER_ADMIN
    center_marks_readonly = all(field in center_readonly for field in marks_fields)
    po_marks_readonly = any(field in po_readonly for field in marks_fields)
    
    print(f"   PO_ADMIN marks readonly: {po_marks_readonly}")
    print(f"   CENTER_ADMIN marks readonly: {center_marks_readonly}")
    
    # Test 5: Permissions
    print("\n5️⃣ Testing Permissions")
    print("-" * 40)
    
    po_can_add = admin.has_add_permission(po_request)
    po_can_delete = admin.has_delete_permission(po_request)
    
    center_can_add = admin.has_add_permission(center_request)
    center_can_delete = admin.has_delete_permission(center_request)
    
    print(f"   PO_ADMIN can add: {po_can_add}")
    print(f"   PO_ADMIN can delete: {po_can_delete}")
    print(f"   CENTER_ADMIN can add: {center_can_add}")
    print(f"   CENTER_ADMIN can delete: {center_can_delete}")
    
    # Verify results
    print("\n" + "=" * 60)
    print("📊 VERIFICATION RESULTS")
    print("=" * 60)
    
    success = True
    
    # Check PO_ADMIN requirements
    if not po_has_marks:
        print("❌ PO_ADMIN should have marks fields in display")
        success = False
    else:
        print("✅ PO_ADMIN has marks fields in display")
    
    if po_has_trade:
        print("❌ PO_ADMIN should NOT have trade/question display")
        success = False
    else:
        print("✅ PO_ADMIN does not have trade/question display")
    
    if po_has_slot_status:
        print("❌ PO_ADMIN should NOT have slot status display")
        success = False
    else:
        print("✅ PO_ADMIN does not have slot status display")
    
    if not po_has_exports:
        print("❌ PO_ADMIN should have export actions")
        success = False
    else:
        print("✅ PO_ADMIN has export actions")
    
    if po_has_slots:
        print("❌ PO_ADMIN should NOT have slot management actions")
        success = False
    else:
        print("✅ PO_ADMIN does not have slot management actions")
    
    # Check CENTER_ADMIN requirements
    if center_has_marks:
        print("❌ CENTER_ADMIN should NOT have marks fields in display")
        success = False
    else:
        print("✅ CENTER_ADMIN does not have marks fields in display")
    
    if not center_has_trade:
        print("❌ CENTER_ADMIN should have trade/question display")
        success = False
    else:
        print("✅ CENTER_ADMIN has trade/question display")
    
    if center_has_exports:
        print("❌ CENTER_ADMIN should NOT have export actions")
        success = False
    else:
        print("✅ CENTER_ADMIN does not have export actions")
    
    if not center_has_slot_status:
        print("❌ CENTER_ADMIN should have slot status display")
        success = False
    else:
        print("✅ CENTER_ADMIN has slot status display")
    
    if not center_has_slots:
        print("❌ CENTER_ADMIN should have slot management actions")
        success = False
    else:
        print("✅ CENTER_ADMIN has slot management actions")
    
    # Check readonly fields
    if not center_marks_readonly:
        print("❌ CENTER_ADMIN marks should be readonly")
        success = False
    else:
        print("✅ CENTER_ADMIN marks are readonly")
    
    if po_marks_readonly:
        print("❌ PO_ADMIN marks should be editable")
        success = False
    else:
        print("✅ PO_ADMIN marks are editable")
    
    # Check permissions
    if po_can_add or po_can_delete:
        print("❌ PO_ADMIN should not be able to add/delete candidates")
        success = False
    else:
        print("✅ PO_ADMIN cannot add/delete candidates")
    
    return success

if __name__ == "__main__":
    try:
        print("🚀 Starting Role-Based Admin Interface Tests")
        print("=" * 70)
        
        success = test_role_permissions()
        
        if success:
            print("\n" + "=" * 70)
            print("🎉 ALL TESTS PASSED! Role-based admin interface is working correctly.")
            print("✅ PO_ADMIN: Can edit marks, export data, no slot management")
            print("✅ CENTER_ADMIN: Can manage slots, no marks editing, no exports")
            print("✅ Proper field access and permissions enforced")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)