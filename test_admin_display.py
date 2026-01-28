#!/usr/bin/env python3
"""
Test the updated admin display for trade questions
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from registration.models import CandidateProfile
from registration.admin import CandidateProfileAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory

User = get_user_model()

def test_admin_display():
    """Test the trade_questions_display method"""
    print("🔍 Testing Admin Display...")
    print("=" * 60)
    
    # Get a few candidates
    candidates = CandidateProfile.objects.select_related('trade')[:5]
    
    if not candidates.exists():
        print("❌ No candidates found!")
        return
    
    # Create admin instance
    admin_site = AdminSite()
    admin_instance = CandidateProfileAdmin(CandidateProfile, admin_site)
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/admin/')
    
    # Create a test user (simulate PO user)
    test_user = User.objects.filter(is_superuser=True).first()
    if not test_user:
        test_user = User.objects.create_superuser('testadmin', 'test@example.com', 'password')
    
    request.user = test_user
    
    print("📊 Testing trade_questions_display for candidates:")
    print("-" * 60)
    
    for candidate in candidates:
        if candidate.trade:
            display_html = admin_instance.trade_questions_display(candidate)
            # Strip HTML tags for clean display
            import re
            clean_text = re.sub('<[^<]+?>', '', display_html)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            print(f"Army No: {candidate.army_no}")
            print(f"Name: {candidate.name}")
            print(f"Trade: {candidate.trade.name} ({candidate.trade.code})")
            print(f"Display: {clean_text}")
            print("-" * 40)
        else:
            print(f"Army No: {candidate.army_no} - No Trade")
            print("-" * 40)

if __name__ == "__main__":
    test_admin_display()