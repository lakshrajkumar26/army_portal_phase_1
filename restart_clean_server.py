#!/usr/bin/env python3
"""
Restart Django server with clean logging configuration
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def kill_django_processes():
    """Kill any existing Django processes"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                         capture_output=True, check=False)
        else:  # Unix/Linux/Mac
            subprocess.run(['pkill', '-f', 'manage.py runserver'], 
                         capture_output=True, check=False)
        print("✅ Stopped existing Django processes")
    except Exception as e:
        print(f"⚠️ Could not stop processes: {e}")

def clear_django_cache():
    """Clear Django cache and compiled Python files"""
    try:
        # Clear __pycache__ directories
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in dirs:
                pycache_path = Path(root) / '__pycache__'
                for file in pycache_path.glob('*.pyc'):
                    file.unlink()
                print(f"✅ Cleared cache: {pycache_path}")
        
        print("✅ Django cache cleared")
    except Exception as e:
        print(f"⚠️ Could not clear cache: {e}")

def start_server():
    """Start Django server with clean environment"""
    print("🚀 Starting Django server with clean logging...")
    
    # Set environment variables for clean startup
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'  # Ensure immediate output
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000'
        ], env=env)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def main():
    """Main function"""
    print("🔧 Django Exam Portal - Clean Server Restart")
    print("=" * 50)
    
    # Check if manage.py exists
    if not Path('manage.py').exists():
        print("❌ manage.py not found! Run this script from the project root.")
        return
    
    # Step 1: Kill existing processes
    print("1️⃣ Stopping existing Django processes...")
    kill_django_processes()
    time.sleep(2)
    
    # Step 2: Clear cache
    print("2️⃣ Clearing Django cache...")
    clear_django_cache()
    
    # Step 3: Update logging to INFO level
    print("3️⃣ Setting logging to INFO level...")
    try:
        from manage_logging import update_log_level
        update_log_level('INFO')
    except ImportError:
        print("⚠️ Could not import manage_logging, manually set LOG_LEVEL=INFO in .env")
    
    # Step 4: Start server
    print("4️⃣ Starting clean server...")
    time.sleep(1)
    start_server()

if __name__ == "__main__":
    main()