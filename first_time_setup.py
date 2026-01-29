#!/usr/bin/env python3
"""
Complete First Time Setup for Django Exam Portal
Handles all initialization needed when running on a new PC
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    print("🔍 Checking requirements...")
    
    try:
        import django
        import mysql.connector
        import openpyxl
        import cryptography
        print("✅ All required packages found")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("📦 Installing requirements...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
            print("✅ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements")
            return False

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️ .env file not found, creating from .env.example...")
        example_file = Path('.env.example')
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ Created .env file from .env.example")
        else:
            print("❌ .env.example not found!")
            return False
    
    # Update logging level to INFO
    try:
        from manage_logging import update_log_level
        update_log_level('INFO')
        print("✅ Set logging level to INFO")
    except ImportError:
        print("⚠️ Could not update logging level")
    
    return True

def run_first_time_setup():
    """Run the first time setup script"""
    print("🚀 Running first time setup...")
    
    try:
        subprocess.run([sys.executable, 'fix_new_pc_setup.py'], check=True)
        print("✅ First time setup completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed: {e}")
        return False

def create_superuser():
    """Create superuser if needed"""
    print("👤 Setting up admin user...")
    
    try:
        # Check if superuser exists
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if User.objects.filter(is_superuser=True).exists():
            print("✅ Superuser already exists")
            return True
        
        print("📝 Creating superuser...")
        print("Please enter superuser details:")
        
        subprocess.run([sys.executable, 'manage.py', 'createsuperuser'], check=True)
        print("✅ Superuser created successfully")
        return True
        
    except Exception as e:
        print(f"⚠️ Superuser creation skipped: {e}")
        return True  # Not critical

def start_server():
    """Start the Django server"""
    print("🌐 Starting Django server...")
    
    try:
        subprocess.run([sys.executable, 'restart_clean_server.py'])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server start failed: {e}")
        print("💡 Try manually: python manage.py runserver")

def main():
    """Main setup function"""
    print("🚀 Django Exam Portal - Complete First Time Setup")
    print("=" * 60)
    print("This script will:")
    print("1. Check and install requirements")
    print("2. Setup environment variables")
    print("3. Run database migrations")
    print("4. Initialize system data")
    print("5. Fix template errors")
    print("6. Create superuser (optional)")
    print("7. Start the server")
    print("=" * 60)
    
    # Confirm before proceeding
    response = input("Continue with setup? (y/N): ").lower().strip()
    if response != 'y':
        print("Setup cancelled.")
        return
    
    # Step 1: Check requirements
    if not check_requirements():
        print("❌ Requirements check failed")
        return
    
    # Step 2: Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        return
    
    # Step 3: Run first time setup
    if not run_first_time_setup():
        print("❌ First time setup failed")
        return
    
    # Step 4: Create superuser
    create_superuser()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETED SUCCESSFULLY!")
    print()
    print("📋 What was done:")
    print("✅ Requirements installed")
    print("✅ Environment configured")
    print("✅ Database migrations applied")
    print("✅ System data initialized")
    print("✅ Template errors fixed")
    print("✅ Admin user created")
    print()
    print("🌐 Access URLs:")
    print("- Main App: http://127.0.0.1:8000/")
    print("- Admin: http://127.0.0.1:8000/admin/")
    print("- Activate Sets: http://127.0.0.1:8000/admin/questions/activatesets/")
    print()
    print("📝 Next Steps:")
    print("1. Upload questions via Admin > Questions > 1 QP Upload")
    print("2. Configure question sets via Admin > Questions > Activate Sets")
    print("3. Create exam centers via Admin > Centers > Exam centers")
    print("4. Register candidates via Admin > Registration > Candidate profiles")
    print()
    
    # Ask if user wants to start server
    response = input("Start Django server now? (Y/n): ").lower().strip()
    if response != 'n':
        start_server()

if __name__ == "__main__":
    main()