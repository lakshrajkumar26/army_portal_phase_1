#!/usr/bin/env python3
"""
Script to generate secure environment configuration files for the Django Exam Portal.

Usage:
    python scripts/generate_env.py --environment production
    python scripts/generate_env.py --environment development
"""

import argparse
import secrets
import os
from pathlib import Path


def generate_secret_key():
    """Generate a cryptographically secure secret key"""
    return secrets.token_urlsafe(50)


def generate_password(length=16):
    """Generate a secure password"""
    return secrets.token_urlsafe(length)


def create_env_file(environment, output_path=None):
    """Create environment file for specified environment"""
    
    if not output_path:
        output_path = f'.env.{environment}' if environment != 'development' else '.env'
    
    # Generate secure values
    secret_key = generate_secret_key()
    db_password = generate_password()
    converter_passphrase = generate_password()
    
    # Environment-specific settings
    if environment == 'production':
        debug = 'False'
        allowed_hosts = 'yourdomain.com,www.yourdomain.com'
        ssl_redirect = 'True'
        secure_cookies = 'True'
        log_level = 'WARNING'
        db_name = 'exam_portal_prod'
    elif environment == 'staging':
        debug = 'False'
        allowed_hosts = 'staging.yourdomain.com'
        ssl_redirect = 'True'
        secure_cookies = 'True'
        log_level = 'INFO'
        db_name = 'exam_portal_staging'
    else:  # development
        debug = 'True'
        allowed_hosts = 'localhost,127.0.0.1'
        ssl_redirect = 'False'
        secure_cookies = 'False'
        log_level = 'DEBUG'
        db_name = 'exam_portal'
    
    # Create environment file content
    env_content = f"""# Django Exam Portal Environment Configuration - {environment.upper()}
# Generated automatically - DO NOT COMMIT TO VERSION CONTROL

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================
DJANGO_ENV={environment}

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
SECRET_KEY={secret_key}
DEBUG={debug}
ALLOWED_HOSTS={allowed_hosts}

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DB_NAME={db_name}
DB_USER=exam_portal_user
DB_PASSWORD={db_password}
DB_HOST=localhost
DB_PORT=3306

# =============================================================================
# SECURITY HEADERS AND HTTPS
# =============================================================================
SECURE_SSL_REDIRECT={ssl_redirect}
SECURE_HSTS_SECONDS={'31536000' if environment == 'production' else '0'}
SECURE_HSTS_INCLUDE_SUBDOMAINS={ssl_redirect}
SECURE_HSTS_PRELOAD={ssl_redirect}

SESSION_COOKIE_SECURE={secure_cookies}
CSRF_COOKIE_SECURE={secure_cookies}
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=True

SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY

# =============================================================================
# FILE UPLOAD CONFIGURATION
# =============================================================================
FILE_UPLOAD_MAX_MEMORY_SIZE=104857600
DATA_UPLOAD_MAX_MEMORY_SIZE=104857600
DATA_UPLOAD_MAX_NUMBER_FIELDS=100000

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_LEVEL={log_level}
LOG_FILE_PATH={'logs/exam_portal.log' if environment == 'development' else '/var/log/exam_portal/exam_portal.log'}

# =============================================================================
# EXAM PORTAL SPECIFIC CONFIGURATION
# =============================================================================
CONVERTER_PASSPHRASE={converter_passphrase}
EXAM_UNIFIED_DAT_ENABLED=True

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# =============================================================================
# CACHE CONFIGURATION
# =============================================================================
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300
"""
    
    # Write the file
    with open(output_path, 'w') as f:
        f.write(env_content)
    
    # Set secure file permissions (Unix/Linux only)
    try:
        os.chmod(output_path, 0o600)
    except:
        pass  # Windows doesn't support chmod
    
    return output_path, secret_key, db_password, converter_passphrase


def main():
    parser = argparse.ArgumentParser(description='Generate secure environment configuration files')
    parser.add_argument(
        '--environment',
        choices=['development', 'staging', 'production'],
        default='development',
        help='Environment to generate configuration for'
    )
    parser.add_argument(
        '--output',
        help='Output file path (default: .env or .env.{environment})'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing file if it exists'
    )
    
    args = parser.parse_args()
    
    output_path = args.output
    if not output_path:
        output_path = '.env' if args.environment == 'development' else f'.env.{args.environment}'
    
    # Check if file exists
    if os.path.exists(output_path) and not args.force:
        print(f"Error: {output_path} already exists. Use --force to overwrite.")
        return 1
    
    # Generate the environment file
    try:
        file_path, secret_key, db_password, converter_passphrase = create_env_file(
            args.environment, output_path
        )
        
        print(f"✓ Generated {args.environment} environment file: {file_path}")
        print("\nIMPORTANT SECURITY INFORMATION:")
        print("=" * 50)
        print(f"SECRET_KEY: {secret_key}")
        print(f"DB_PASSWORD: {db_password}")
        print(f"CONVERTER_PASSPHRASE: {converter_passphrase}")
        print("=" * 50)
        print("\nPlease:")
        print("1. Save these credentials securely")
        print("2. Update database host/user as needed")
        print("3. Set your actual domain names in ALLOWED_HOSTS")
        print("4. Configure email settings if needed")
        print("5. DO NOT commit this file to version control")
        
        if args.environment == 'production':
            print("\nPRODUCTION CHECKLIST:")
            print("- Update ALLOWED_HOSTS with your actual domain")
            print("- Configure proper database credentials")
            print("- Set up HTTPS/SSL certificates")
            print("- Configure email settings")
            print("- Set up log file directory with proper permissions")
            print("- Test all security settings before deployment")
        
        return 0
        
    except Exception as e:
        print(f"Error generating environment file: {e}")
        return 1


if __name__ == '__main__':
    exit(main())