#!/usr/bin/env python3
"""
Logging Management Script for Django Exam Portal
Helps manage and reduce excessive debug logging
"""

import os
import sys
from pathlib import Path

def update_log_level(level='INFO'):
    """Update the LOG_LEVEL in .env file"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Update LOG_LEVEL
    lines = content.split('\n')
    updated = False
    
    for i, line in enumerate(lines):
        if line.startswith('LOG_LEVEL='):
            old_level = line.split('=')[1]
            lines[i] = f'LOG_LEVEL={level}'
            print(f"✅ Updated LOG_LEVEL from {old_level} to {level}")
            updated = True
            break
    
    if not updated:
        # Add LOG_LEVEL if not found
        lines.append(f'LOG_LEVEL={level}')
        print(f"✅ Added LOG_LEVEL={level}")
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.write('\n'.join(lines))
    
    return True

def show_current_settings():
    """Show current logging settings"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return
    
    with open(env_file, 'r') as f:
        content = f.read()
    
    print("🔍 Current Logging Settings:")
    print("=" * 40)
    
    for line in content.split('\n'):
        if line.startswith('LOG_LEVEL='):
            print(f"LOG_LEVEL: {line.split('=')[1]}")
        elif line.startswith('DEBUG='):
            print(f"DEBUG: {line.split('=')[1]}")
        elif line.startswith('LOG_FILE_PATH='):
            print(f"LOG_FILE_PATH: {line.split('=')[1]}")

def clear_log_file():
    """Clear the log file"""
    log_file = Path('logs/exam_portal.log')
    
    if log_file.exists():
        try:
            log_file.unlink()
            print("✅ Log file cleared")
        except Exception as e:
            print(f"❌ Failed to clear log file: {e}")
    else:
        print("ℹ️ Log file doesn't exist")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🔧 Django Exam Portal - Logging Management")
        print("=" * 50)
        print("Usage:")
        print("  python manage_logging.py show          - Show current settings")
        print("  python manage_logging.py set <level>   - Set log level (DEBUG/INFO/WARNING/ERROR)")
        print("  python manage_logging.py clear         - Clear log file")
        print("  python manage_logging.py quiet         - Set to quiet mode (WARNING level)")
        print("  python manage_logging.py verbose       - Set to verbose mode (DEBUG level)")
        print()
        show_current_settings()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'show':
        show_current_settings()
    
    elif command == 'set':
        if len(sys.argv) < 3:
            print("❌ Please specify log level: DEBUG, INFO, WARNING, or ERROR")
            return
        
        level = sys.argv[2].upper()
        if level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            print("❌ Invalid log level. Use: DEBUG, INFO, WARNING, or ERROR")
            return
        
        if update_log_level(level):
            print("✅ Log level updated successfully")
            print("🔄 Restart Django server to apply changes")
    
    elif command == 'clear':
        clear_log_file()
    
    elif command == 'quiet':
        if update_log_level('WARNING'):
            print("✅ Set to quiet mode (WARNING level)")
            print("🔄 Restart Django server to apply changes")
    
    elif command == 'verbose':
        if update_log_level('DEBUG'):
            print("✅ Set to verbose mode (DEBUG level)")
            print("⚠️ This will show all debug logs including file monitoring")
            print("🔄 Restart Django server to apply changes")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()