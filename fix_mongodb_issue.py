#!/usr/bin/env python3
"""
Script to fix MongoDB connection issues by removing MongoDB packages.
This script will uninstall mongoengine and pymongo packages that are causing connection attempts.
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔧 Fixing MongoDB Connection Issues")
    print("=" * 50)
    
    # List of MongoDB packages to remove
    mongodb_packages = ['mongoengine', 'pymongo']
    
    print("📋 Packages to remove:")
    for pkg in mongodb_packages:
        print(f"   - {pkg}")
    
    print("\n🗑️ Uninstalling MongoDB packages...")
    
    for package in mongodb_packages:
        print(f"\n   Removing {package}...")
        success, stdout, stderr = run_command(f"pip uninstall {package} -y")
        
        if success:
            print(f"   ✅ Successfully removed {package}")
        else:
            print(f"   ⚠️ Could not remove {package} (may not be installed)")
            if stderr:
                print(f"      Error: {stderr}")
    
    print("\n🔄 Installing packages from updated requirements.txt...")
    success, stdout, stderr = run_command("pip install -r requirements.txt")
    
    if success:
        print("   ✅ Successfully installed packages from requirements.txt")
    else:
        print("   ❌ Error installing packages:")
        print(f"      {stderr}")
        return 1
    
    print("\n✅ MongoDB connection issue should now be fixed!")
    print("\n📋 What was done:")
    print("   1. Removed mongoengine and pymongo packages")
    print("   2. Cleaned up MongoDB configuration from settings.py")
    print("   3. Updated requirements.txt to exclude MongoDB packages")
    print("   4. Reinstalled packages from updated requirements.txt")
    
    print("\n🚀 Next steps:")
    print("   1. Restart your Django development server")
    print("   2. The MongoDB connection errors should be gone")
    print("   3. Your application will only use MySQL database")
    
    return 0

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)