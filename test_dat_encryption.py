#!/usr/bin/env python
"""
Test script to verify DAT file encryption/decryption with passphrase "bharat"
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from registration.admin import _encrypt_bytes_to_dat
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def test_encryption_decryption():
    print("Testing DAT file encryption/decryption...")
    
    # Check current passphrase setting
    passphrase = getattr(settings, "CONVERTER_PASSPHRASE", None)
    print(f"Current CONVERTER_PASSPHRASE: {passphrase}")
    
    if passphrase != "bharat":
        print(f"❌ ERROR: Expected 'bharat' but got '{passphrase}'")
        return False
    
    # Test data
    test_data = b"This is test data for encryption/decryption"
    print(f"Original data: {test_data}")
    
    try:
        # Encrypt the data
        encrypted_data = _encrypt_bytes_to_dat(test_data, passphrase)
        print(f"✅ Encryption successful, encrypted size: {len(encrypted_data)} bytes")
        
        # Now test decryption (simulate what the converter does)
        # Extract salt (16 bytes), iv (12 bytes), and ciphertext
        salt = encrypted_data[:16]
        iv = encrypted_data[16:28]
        ciphertext = encrypted_data[28:]
        
        print(f"Salt: {salt.hex()}")
        print(f"IV: {iv.hex()}")
        print(f"Ciphertext size: {len(ciphertext)} bytes")
        
        # Derive key using same method as encryption
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(passphrase.encode("utf-8"))
        
        # Decrypt
        aesgcm = AESGCM(key)
        decrypted_data = aesgcm.decrypt(iv, ciphertext, None)
        
        print(f"Decrypted data: {decrypted_data}")
        
        if decrypted_data == test_data:
            print("✅ SUCCESS: Encryption/Decryption test PASSED!")
            print("The DAT files should now decrypt correctly with passphrase 'bharat'")
            return True
        else:
            print("❌ FAILED: Decrypted data doesn't match original")
            return False
            
    except Exception as e:
        print(f"❌ ERROR during encryption/decryption: {str(e)}")
        return False

def test_export_function():
    print("\nTesting export function...")
    
    from registration.models import CandidateProfile
    
    # Get a small queryset for testing
    queryset = CandidateProfile.objects.all()[:1]
    
    if not queryset.exists():
        print("❌ No candidates found for testing export")
        return False
    
    try:
        from registration.admin import _build_export_workbook
        
        # Generate workbook
        xlsx_bytes = _build_export_workbook(queryset)
        print(f"✅ Workbook generated successfully, size: {len(xlsx_bytes)} bytes")
        
        # Test encryption
        passphrase = getattr(settings, "CONVERTER_PASSPHRASE", None)
        encrypted_data = _encrypt_bytes_to_dat(xlsx_bytes, passphrase)
        print(f"✅ Export encryption successful, encrypted size: {len(encrypted_data)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR during export test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔐 DAT File Encryption Test")
    print("=" * 50)
    
    success1 = test_encryption_decryption()
    success2 = test_export_function()
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED!")
        print("The DAT export should now work with passphrase 'bharat'")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)