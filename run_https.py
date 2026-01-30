#!/usr/bin/env python3
"""
Script to run Django development server with HTTPS support.
This is required for camera access (getUserMedia) which requires a secure context.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if django-extensions and werkzeug are installed"""
    print("🔍 Checking dependencies...")
    try:
        import django_extensions
        import werkzeug
        print("✅ Dependencies found")
        return True
    except ImportError:
        print("📦 Installing required packages (django-extensions, werkzeug, pyOpenSSL)...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'django-extensions', 'werkzeug', 'pyOpenSSL'], check=True)
            print("✅ Packages installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            return False

def ensure_ssl_certs():
    """Ensure SSL certificates exist"""
    ssl_dir = Path('ssl')
    cert_file = ssl_dir / 'cert.pem'
    key_file = ssl_dir / 'key.pem'
    
    if not ssl_dir.exists():
        ssl_dir.mkdir()
        
    if not cert_file.exists() or not key_file.exists():
        print("🔐 Generating self-signed SSL certificates...")
        try:
            # Using openssl command if available
            subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:4096', 
                '-keyout', str(key_file), '-out', str(cert_file), 
                '-days', '365', '-nodes', 
                '-subj', '/C=IN/ST=Delhi/L=Delhi/O=ArmyPortal/OU=IT/CN=localhost'
            ], check=True)
            print("✅ SSL certificates generated")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Failed to generate SSL certificates via openssl")
            return False
    else:
        print("✅ SSL certificates found")
    return True

def update_settings():
    """Update settings.py to include django_extensions"""
    settings_path = Path('config/settings.py')
    if not settings_path.exists():
        print("❌ config/settings.py not found")
        return False
        
    with open(settings_path, 'r') as f:
        content = f.read()
        
    if 'django_extensions' not in content:
        print("📝 Adding django_extensions to INSTALLED_APPS...")
        # Find INSTALLED_APPS and add django_extensions
        if 'INSTALLED_APPS = [' in content:
            new_content = content.replace(
                'INSTALLED_APPS = [', 
                "INSTALLED_APPS = [\n    'django_extensions',"
            )
            with open(settings_path, 'w') as f:
                f.write(new_content)
            print("✅ Updated settings.py")
        else:
            print("❌ Could not find INSTALLED_APPS in settings.py")
            return False
    else:
        print("✅ django_extensions already in INSTALLED_APPS")
    return True

def start_https_server(host='0.0.0.0', port='8000'):
    """Start the server with HTTPS"""
    print(f"🚀 Starting HTTPS server on https://{host}:{port}...")
    print("⚠️  Note: Your browser will show a security warning because this is a self-signed certificate.")
    print("💡 Click 'Advanced' and 'Proceed to localhost (unsafe)' to continue.")
    
    cmd = [
        sys.executable, 'manage.py', 'runserver_plus',
        f'{host}:{port}',
        '--cert-file', 'ssl/cert.pem',
        '--key-file', 'ssl/key.pem'
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def main():
    print("🛡️  Army Portal HTTPS Runner")
    print("=" * 50)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        return
        
    # Step 2: Ensure SSL certs
    if not ensure_ssl_certs():
        return
        
    # Step 3: Update settings
    if not update_settings():
        return
        
    # Step 4: Start server
    start_https_server()

if __name__ == "__main__":
    main()
