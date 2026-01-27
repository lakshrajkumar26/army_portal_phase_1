#!/usr/bin/env python
"""
Quick script to fix exam configuration issues.
Run this to resolve "Exam paper configuration missing" errors.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

def main():
    print("🔧 Fixing Exam Configuration Issues...")
    print("=" * 50)
    
    try:
        # First, run a dry run to see what needs to be fixed
        print("📋 Checking current configuration...")
        call_command('fix_question_paper_config', '--dry-run')
        
        print("\n" + "=" * 50)
        response = input("Apply these fixes? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            print("\n🔧 Applying fixes...")
            call_command('fix_question_paper_config')
            print("\n✅ Configuration fixes applied successfully!")
            print("\n💡 Next steps:")
            print("   1. Test candidate login to verify the fix")
            print("   2. Check admin interface for proper paper type activation")
        else:
            print("\n❌ No changes made.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()