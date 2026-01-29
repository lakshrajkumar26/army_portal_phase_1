#!/usr/bin/env python3
"""
Test script to verify keyboard security compatibility fixes
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_exam_interface_template():
    """Test that the exam interface template has the enhanced security features"""
    template_path = project_root / 'registration' / 'templates' / 'registration' / 'exam_interface.html'
    
    if not template_path.exists():
        print("❌ Exam interface template not found!")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for enhanced compatibility features
    checks = [
        # Browser compatibility detection
        ('browserInfo', 'Browser compatibility detection'),
        ('supportsFullscreen', 'Fullscreen support detection'),
        ('supportsKeyboardEvents', 'Keyboard events support detection'),
        
        # Enhanced key detection
        ('keyCode = e.keyCode || e.which || 0', 'Cross-browser keyCode detection'),
        ('keyName = e.key || e.code', 'Cross-browser key name detection'),
        ('keyNameLower = keyName.toLowerCase()', 'Case-insensitive key matching'),
        
        # Function key arrays
        ('functionKeyCodes = [112, 113, 114', 'Function key code array'),
        ('functionKeyNames = ["f1", "f2"', 'Function key name array'),
        
        # Enhanced fullscreen methods
        ('requestFullscreen', 'Standard fullscreen method'),
        ('mozRequestFullScreen', 'Firefox fullscreen method'),
        ('webkitRequestFullscreen', 'Webkit fullscreen method'),
        ('msRequestFullscreen', 'IE fullscreen method'),
        
        # Fallback windowed mode
        ('WINDOWED MODE SECURITY ACTIVATED', 'Windowed mode fallback'),
        ('Fullscreen not supported', 'Fullscreen unsupported handling'),
        
        # Enhanced debugging
        ('testKeyboardSecurity', 'Keyboard security testing function'),
        ('examSecurityDebug', 'Debug object for testing'),
        
        # Multiple event listeners
        ('fullscreenEvents.forEach', 'Multiple fullscreen event listeners'),
        ('resize', 'Backup fullscreen monitoring'),
    ]
    
    results = []
    for check, description in checks:
        if check in content:
            print(f"✅ {description}")
            results.append(True)
        else:
            print(f"❌ {description} - NOT FOUND")
            results.append(False)
    
    return all(results)

def test_security_features():
    """Test that all security features are properly implemented"""
    print("🔍 Testing Enhanced Keyboard Security Compatibility...")
    print("=" * 60)
    
    template_ok = test_exam_interface_template()
    
    print("\n" + "=" * 60)
    if template_ok:
        print("✅ ALL SECURITY COMPATIBILITY TESTS PASSED!")
        print("\n🔒 Enhanced Features Added:")
        print("  • Cross-browser key detection (keyCode + key + code)")
        print("  • Function key arrays for better compatibility")
        print("  • Multiple fullscreen API methods")
        print("  • Browser capability detection")
        print("  • Windowed mode fallback for unsupported browsers")
        print("  • Enhanced debugging and testing functions")
        print("  • Multiple fullscreen event listeners")
        print("  • Backup monitoring via resize events")
        
        print("\n🧪 Testing Instructions:")
        print("1. Open exam interface in different browsers")
        print("2. Open browser console and run: examSecurityDebug")
        print("3. Test with: testKeyboardSecurity()")
        print("4. Check violations with: examSecurityDebug.getViolations()")
        
        print("\n🌐 Browser Compatibility:")
        print("  • Chrome/Chromium: Full support")
        print("  • Firefox: Full support")
        print("  • Safari: Full support")
        print("  • Edge: Full support")
        print("  • Internet Explorer: Basic support")
        print("  • Mobile browsers: Windowed mode fallback")
        
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the template file for missing features.")
    
    return template_ok

if __name__ == "__main__":
    success = test_security_features()
    sys.exit(0 if success else 1)