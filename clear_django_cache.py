#!/usr/bin/env python3
"""
Clear Django cache and force model reload
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.apps import apps

def clear_django_caches():
    """Clear Django's internal caches"""
    
    print("🧹 Clearing Django caches...")
    
    # Clear the app registry cache
    apps.clear_cache()
    
    # Close database connections to force reconnection
    connection.close()
    
    print("✅ Django caches cleared")

def test_model_access():
    """Test if we can access the model with the new field"""
    
    print("🧪 Testing model access...")
    
    try:
        from registration.models import CandidateProfile
        
        # Try to access the field through Django ORM
        candidate = CandidateProfile.objects.first()
        if candidate:
            # Try to access the new field
            attempting_at = candidate.slot_attempting_at
            print(f"✅ Successfully accessed slot_attempting_at: {attempting_at}")
            
            # Try to query using the field
            count = CandidateProfile.objects.filter(slot_attempting_at__isnull=True).count()
            print(f"✅ Successfully queried slot_attempting_at field: {count} records with null values")
            
        else:
            print("ℹ️  No candidates in database to test with")
            
        return True
        
    except Exception as e:
        print(f"❌ Error accessing model: {str(e)}")
        return False

def force_migration_check():
    """Force Django to check migrations again"""
    
    print("🔄 Forcing migration check...")
    
    try:
        # This will force Django to reload migration state
        execute_from_command_line(['manage.py', 'migrate', '--fake-initial'])
        print("✅ Migration check completed")
        return True
    except Exception as e:
        print(f"❌ Migration check failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Clearing Django caches and testing model access...")
    
    try:
        # Clear caches
        clear_django_caches()
        
        # Test model access
        model_ok = test_model_access()
        
        if model_ok:
            print("\n🎉 Model access is working correctly!")
            print("💡 Try restarting your Django development server:")
            print("   1. Stop the current server (Ctrl+C)")
            print("   2. Run: python manage.py runserver")
            print("   3. Try accessing the admin interface again")
        else:
            print("\n❌ Model access failed. There might be a deeper issue.")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)