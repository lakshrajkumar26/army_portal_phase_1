#!/usr/bin/env python
"""
Test script to verify export works with passphrase "bharat"
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from registration.models import CandidateProfile
from registration.admin import _build_export_workbook, _encrypt_bytes_to_dat

def test_export():
    print("Testing export with passphrase 'bharat'...")
    
    # Check passphrase
    passphrase = getattr(settings, "CONVERTER_PASSPHRASE", None)
    print(f"Using passphrase: '{passphrase}'")
    
    if passphrase != "bharat":
        print(f"❌ ERROR: Expected 'bharat' but got '{passphrase}'")
        return False
    
    # Get candidates for testing
    queryset = CandidateProfile.objects.all()[:1]
    
    if not queryset.exists():
        print("❌ No candidates found for testing")
        return False
    
    try:
        print("Generating export workbook...")
        xlsx_bytes = _build_export_workbook(queryset)
        print(f"✅ Workbook generated: {len(xlsx_bytes)} bytes")
        
        print("Encrypting to .dat format...")
        dat_bytes = _encrypt_bytes_to_dat(xlsx_bytes, passphrase)
        print(f"✅ DAT file encrypted: {len(dat_bytes)} bytes")
        
        # Save test file
        with open("test_export.dat", "wb") as f:
            f.write(dat_bytes)
        print("✅ Test DAT file saved as 'test_export.dat'")
        
        print("\n🎉 SUCCESS: Export with passphrase 'bharat' works correctly!")
        print("You can now decrypt DAT files using passphrase 'bharat'")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_export()
    sys.exit(0 if success else 1)