#!/usr/bin/env python3
"""
Script to restart Django development server and clear any cached model definitions.
This resolves the "Unknown column 'registration_candidateprofile.slot_attempting_at'" error.
"""

import os
import sys
import django
import subprocess
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from registration.models import CandidateProfile

def check_database_column():
    """Check if the slot_attempting_at column exists in the database"""
    print("🔍 Checking database column existence...")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'registration_candidateprofile' 
            AND COLUMN_NAME = 'slot_attempting_at'
        """)
        
        result = cursor.fetchone()
        
        if result:
            print("✅ Database column 'slot_attempting_at' exists")
            return True
        else:
            print("❌ Database column 'slot_attempting_at' is missing")
            return False

def test_django_orm():
    """Test if Django ORM can access the field"""
    print("🔍 Testing Django ORM access...")
    
    try:
        # Try to query using the field
        count = CandidateProfile.objects.filter(slot_attempting_at__isnull=True).count()
        print(f"✅ Django ORM can access slot_attempting_at field: {count} records with null values")
        
        # Try to access the field on a model instance
        candidate = CandidateProfile.objects.first()
        if candidate:
            attempting_at = candidate.slot_attempting_at
            print(f"✅ Can access field on model instance: {attempting_at}")
        
        return True
    except Exception as e:
        print(f"❌ Django ORM error: {str(e)}")
        return False

def clear_django_cache():
    """Clear Django's internal caches"""
    print("🧹 Clearing Django caches...")
    
    try:
        # Clear Django's app registry cache
        from django.apps import apps
        apps.clear_cache()
        print("✅ Cleared Django app registry cache")
        
        # Clear model cache
        from django.db import models
        if hasattr(models, '_cache'):
            models._cache.clear()
            print("✅ Cleared Django model cache")
        
        # Force reload of the model
        from importlib import reload
        import registration.models
        reload(registration.models)
        print("✅ Reloaded registration.models module")
        
        return True
    except Exception as e:
        print(f"⚠️ Cache clearing warning: {str(e)}")
        return False

def check_migration_status():
    """Check if all migrations are applied"""
    print("🔍 Checking migration status...")
    
    try:
        from django.core.management import execute_from_command_line
        import io
        import sys
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        try:
            execute_from_command_line(['manage.py', 'showmigrations', 'registration'])
        finally:
            sys.stdout = old_stdout
        
        output = captured_output.getvalue()
        print("Migration status:")
        print(output)
        
        if "[X] 0005_add_slot_attempting_field" in output:
            print("✅ Migration 0005_add_slot_attempting_field is applied")
            return True
        else:
            print("❌ Migration 0005_add_slot_attempting_field is not applied")
            return False
            
    except Exception as e:
        print(f"⚠️ Could not check migration status: {str(e)}")
        return False

def main():
    print("🚀 Django Server Restart and Cache Clear Script")
    print("=" * 60)
    
    # Step 1: Check database column
    db_ok = check_database_column()
    
    # Step 2: Check migration status
    migration_ok = check_migration_status()
    
    # Step 3: Test Django ORM
    orm_ok = test_django_orm()
    
    # Step 4: Clear caches
    cache_ok = clear_django_cache()
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS SUMMARY")
    print("=" * 60)
    print(f"Database Column Exists: {'✅ YES' if db_ok else '❌ NO'}")
    print(f"Migration Applied: {'✅ YES' if migration_ok else '❌ NO'}")
    print(f"Django ORM Working: {'✅ YES' if orm_ok else '❌ NO'}")
    print(f"Cache Cleared: {'✅ YES' if cache_ok else '⚠️ PARTIAL'}")
    
    if db_ok and migration_ok and orm_ok:
        print("\n🎉 SOLUTION: The database and Django ORM are working correctly!")
        print("🔧 The admin interface error is likely due to a cached Django server process.")
        print("\n📋 NEXT STEPS:")
        print("1. Stop your Django development server (Ctrl+C)")
        print("2. Restart the Django development server:")
        print("   python manage.py runserver")
        print("3. Try accessing the admin interface again")
        print("\n💡 The 'Unknown column' error should be resolved after server restart.")
        
    elif db_ok and migration_ok and not orm_ok:
        print("\n⚠️ ISSUE: Database is correct but Django ORM has issues")
        print("🔧 This suggests a Django cache/import problem")
        print("\n📋 SOLUTIONS:")
        print("1. Restart Django server completely")
        print("2. Clear Python bytecode cache: find . -name '*.pyc' -delete")
        print("3. Restart your IDE/development environment")
        
    elif not db_ok or not migration_ok:
        print("\n❌ ISSUE: Database or migration problems detected")
        print("🔧 Run the migration to fix the database:")
        print("   python manage.py migrate registration")
        
    else:
        print("\n❓ UNKNOWN ISSUE: Mixed results detected")
        print("🔧 Try a complete restart of Django server and development environment")

if __name__ == "__main__":
    main()