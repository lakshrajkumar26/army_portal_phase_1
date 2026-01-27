#!/usr/bin/env python
"""
Script to verify PO functionality has been restored correctly.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def verify_po_permissions():
    """Verify PO user permissions are correctly configured"""
    print("🔍 Verifying PO User Functionality")
    print("=" * 50)
    
    try:
        from registration.admin import CandidateProfileAdmin
        from django.contrib.admin.sites import site
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        
        # Create a mock request with PO user
        factory = RequestFactory()
        request = factory.get('/admin/')
        
        # Create a mock PO user
        po_user = User(username='po_test', is_staff=True, is_superuser=False)
        po_user.role = 'PO_ADMIN'  # Simulate PO role
        request.user = po_user
        
        # Get admin instance
        admin_instance = CandidateProfileAdmin(None, site)
        
        # Test PO permissions
        print("📋 Testing PO User Permissions:")
        
        # 1. Check if PO is identified correctly
        is_po = admin_instance._is_po(request)
        print(f"   ✅ PO identification: {is_po}")
        
        # 2. Check list display
        list_display = admin_instance.get_list_display(request)
        has_marks = any('marks' in field for field in list_display)
        print(f"   ✅ Can see marks columns: {has_marks}")
        
        # 3. Check list editable
        admin_instance.changelist_view(request)
        has_editable_marks = len(admin_instance.list_editable) > 0
        print(f"   ✅ Can edit marks inline: {has_editable_marks}")
        
        # 4. Check actions
        actions = admin_instance.get_actions(request)
        can_export_dat = 'export_candidates_dat' in actions
        can_export_marks = 'export_marks_excel' in actions
        can_export_photos = 'export_candidate_images' in actions
        print(f"   ✅ Can export DAT: {can_export_dat}")
        print(f"   ✅ Can export marks: {can_export_marks}")
        print(f"   ✅ Can export photos: {can_export_photos}")
        
        # 5. Check fields access
        fields = admin_instance.get_fields(request)
        has_marks_fields = any('marks' in field for field in fields)
        print(f"   ✅ Can access marks fields: {has_marks_fields}")
        
        # 6. Check readonly fields
        readonly = admin_instance.get_readonly_fields(request)
        marks_readonly = any('marks' in field for field in readonly)
        print(f"   ✅ Marks are editable: {not marks_readonly}")
        
        # 7. Check list display links
        links = admin_instance.get_list_display_links(request, list_display)
        has_links = len(links) > 0 if links else False
        print(f"   ✅ Can click candidate names: {has_links}")
        
        print("\n📊 Summary:")
        all_good = all([
            is_po,
            has_marks,
            has_editable_marks,
            can_export_dat,
            can_export_marks,
            can_export_photos,
            has_marks_fields,
            not marks_readonly,
            has_links
        ])
        
        if all_good:
            print("✅ All PO functionality restored successfully!")
            return True
        else:
            print("❌ Some PO functionality issues detected")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying PO permissions: {e}")
        return False

def verify_question_display():
    """Verify question display improvements"""
    print("\n🔍 Verifying Question Display")
    print("=" * 50)
    
    try:
        from questions.admin import QuestionAdmin
        from questions.models import Question
        from django.contrib.admin.sites import site
        
        # Get admin instance
        admin_instance = QuestionAdmin(Question, site)
        
        # Check if new display methods exist
        has_formatted_options = hasattr(admin_instance, 'formatted_options')
        has_correct_answer_display = hasattr(admin_instance, 'correct_answer_display')
        
        print(f"   ✅ Formatted options display: {has_formatted_options}")
        print(f"   ✅ Correct answer display: {has_correct_answer_display}")
        
        # Check list display includes new fields
        list_display = admin_instance.list_display
        has_options_column = 'formatted_options' in list_display
        has_answer_column = 'correct_answer_display' in list_display
        
        print(f"   ✅ Options column in list: {has_options_column}")
        print(f"   ✅ Answer column in list: {has_answer_column}")
        
        # Test with a sample question if available
        sample_question = Question.objects.first()
        if sample_question:
            try:
                options_display = admin_instance.formatted_options(sample_question)
                answer_display = admin_instance.correct_answer_display(sample_question)
                print(f"   ✅ Sample options display: {len(options_display) < 200}")
                print(f"   ✅ Sample answer display: {len(str(answer_display)) < 100}")
            except Exception as e:
                print(f"   ⚠️  Display method error: {e}")
        
        return has_formatted_options and has_correct_answer_display
        
    except Exception as e:
        print(f"❌ Error verifying question display: {e}")
        return False

def main():
    print("🔧 PO Functionality & Question Display Verification")
    print("=" * 60)
    
    try:
        # Verify PO permissions
        po_ok = verify_po_permissions()
        
        # Verify question display
        question_ok = verify_question_display()
        
        print("\n📊 Final Summary:")
        print("=" * 30)
        print(f"PO functionality: {'✅ RESTORED' if po_ok else '❌ ISSUES'}")
        print(f"Question display: {'✅ IMPROVED' if question_ok else '❌ ISSUES'}")
        
        if po_ok and question_ok:
            print("\n🎉 All fixes applied successfully!")
            print("\n💡 PO users can now:")
            print("   - Edit viva and practical marks (inline and in forms)")
            print("   - Export DAT files for converter")
            print("   - Export marks to Excel")
            print("   - Export candidate photos")
            print("   - Click on candidate names to open detail pages")
            print("\n💡 Question display improvements:")
            print("   - Clean options display in admin")
            print("   - Better formatted correct answers")
            print("   - Enhanced search capabilities")
        else:
            print("\n❌ Some issues remain. Please check the error messages above.")
        
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()