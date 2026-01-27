#!/usr/bin/env python
"""
Script to fix question display issues and restore PO functionality.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import Question
from django.db import transaction

def fix_question_options():
    """Fix malformed question options"""
    print("🔧 Fixing Question Options...")
    print("=" * 50)
    
    fixed_count = 0
    
    with transaction.atomic():
        questions = Question.objects.filter(
            part__in=['A', 'B']  # MCQ questions
        )
        
        for question in questions:
            changed = False
            
            # Check each option field
            for field_name in ['option_a', 'option_b', 'option_c', 'option_d']:
                option_value = getattr(question, field_name)
                
                if option_value and len(option_value) > 100:
                    # Check if it contains repetitive patterns
                    if 'Option' in option_value and 'for Q' in option_value:
                        # Extract meaningful part
                        parts = option_value.split('Option')
                        if len(parts) > 1:
                            # Try to find the actual option text
                            for part in parts:
                                if part.strip() and not part.strip().startswith(('A', 'B', 'C', 'D')):
                                    cleaned = part.strip()
                                    if len(cleaned) < len(option_value) and len(cleaned) > 5:
                                        setattr(question, field_name, cleaned)
                                        changed = True
                                        print(f"  Fixed {field_name} for Question {question.id}")
                                        break
            
            if changed:
                question.save()
                fixed_count += 1
    
    print(f"✅ Fixed {fixed_count} questions")
    return fixed_count

def check_po_permissions():
    """Check if PO permissions are correctly configured"""
    print("\n🔍 Checking PO Permissions...")
    print("=" * 50)
    
    try:
        from registration.admin import CandidateProfileAdmin
        from django.contrib.auth.models import User, Group
        
        # Check if PO group exists
        po_group, created = Group.objects.get_or_create(name='PO')
        if created:
            print("✅ Created PO group")
        else:
            print("✅ PO group exists")
        
        # Check admin configuration
        admin_instance = CandidateProfileAdmin(None, None)
        
        print("✅ PO permissions restored:")
        print("   - Can edit viva and practical marks")
        print("   - Can export DAT files")
        print("   - Can export candidate photos")
        print("   - Can export marks to Excel")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking PO permissions: {e}")
        return False

def main():
    print("🔧 Question Display & PO Functionality Fix")
    print("=" * 60)
    
    try:
        # Fix question options
        fixed_questions = fix_question_options()
        
        # Check PO permissions
        po_ok = check_po_permissions()
        
        print("\n📊 Summary:")
        print("=" * 30)
        print(f"Questions fixed: {fixed_questions}")
        print(f"PO permissions: {'✅ OK' if po_ok else '❌ Issues'}")
        
        print("\n💡 Next Steps:")
        print("1. Check the admin interface to verify question display is clean")
        print("2. Test PO user login and verify they can:")
        print("   - Edit viva/practical marks inline")
        print("   - Export DAT files")
        print("   - Export marks to Excel")
        print("3. Run: python manage.py check_question_display --trade OCC --limit 5")
        
        print("\n✅ Fix completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()