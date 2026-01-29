#!/usr/bin/env python
"""
Simple script to check the current CONVERTER_PASSPHRASE setting
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def check_passphrase():
    print("Checking CONVERTER_PASSPHRASE setting...")
    
    passphrase = getattr(settings, "CONVERTER_PASSPHRASE", None)
    print(f"Current CONVERTER_PASSPHRASE: '{passphrase}'")
    
    if passphrase == "bharat":
        print("✅ SUCCESS: Passphrase is correctly set to 'bharat'")
        return True
    else:
        print(f"❌ ERROR: Expected 'bharat' but got '{passphrase}'")
        return False

if __name__ == "__main__":
    success = check_passphrase()
    sys.exit(0 if success else 1)