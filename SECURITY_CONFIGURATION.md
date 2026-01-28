# Security Configuration Guide

This document explains the security configuration system implemented for the Django Exam Portal.

## Overview

The security configuration system addresses critical vulnerabilities by:
- Moving all sensitive configuration to environment variables
- Implementing secure defaults for production
- Providing validation and error checking
- Supporting multiple deployment environments

## Quick Start

### 1. Generate Environment Configuration

```bash
# For development
python scripts/generate_env.py --environment development

# For production
python scripts/generate_env.py --environment production
```

### 2. Validate Security Configuration

```bash
# Validate current configuration
python manage.py validate_security

# Validate for production
python manage.py validate_security --environment production

# Attempt automatic fixes
python manage.py validate_security --environment production --fix
```

### 3. Set File Permissions (Unix/Linux)

```bash
chmod 600 .env
chmod 600 .env.production
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key (50+ characters) | `generated-secure-key` |
| `DEBUG` | Debug mode (False in production) | `False` |
| `ALLOWED_HOSTS` | Comma-separated hostnames | `yourdomain.com,www.yourdomain.com` |
| `DB_NAME` | Database name | `exam_portal_prod` |
| `DB_USER` | Database username | `exam_portal_user` |
| `DB_PASSWORD` | Database password | `secure-password` |
| `DB_HOST` | Database host | `localhost` |

### Security Variables

| Variable | Description | Production Value |
|----------|-------------|------------------|
| `SECURE_SSL_REDIRECT` | Force HTTPS redirect | `True` |
| `SESSION_COOKIE_SECURE` | Secure session cookies | `True` |
| `CSRF_COOKIE_SECURE` | Secure CSRF cookies | `True` |
| `SECURE_HSTS_SECONDS` | HSTS max age | `31536000` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_PORT` | Database port | `3306` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CONVERTER_PASSPHRASE` | DAT file passphrase | `bharat` |

## Environment Files

### Development (.env)
```bash
DJANGO_ENV=development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SECRET_KEY=development-key
# ... other settings
```

### Production (.env.production)
```bash
DJANGO_ENV=production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=production-secure-key
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
# ... other settings
```

## Security Features

### 1. Environment-Based Configuration
- All sensitive data loaded from environment variables
- No hardcoded secrets in source code
- Environment-specific defaults

### 2. Production Security Validation
- Automatic validation on startup
- Prevents insecure production deployments
- Clear error messages for misconfigurations

### 3. HTTPS and Security Headers
- Automatic HTTPS enforcement in production
- Secure cookie configuration
- Security headers (HSTS, XSS protection, etc.)

### 4. Database Security
- Environment-based database credentials
- Connection validation
- Secure fallbacks for development

## Deployment Checklist

### Development
- [ ] Copy `.env.example` to `.env`
- [ ] Update database credentials
- [ ] Run `python manage.py validate_security`

### Staging
- [ ] Generate staging environment file
- [ ] Configure staging database
- [ ] Test HTTPS configuration
- [ ] Validate security settings

### Production
- [ ] Generate production environment file with secure credentials
- [ ] Set `DJANGO_ENV=production`
- [ ] Configure HTTPS/SSL certificates
- [ ] Set secure `ALLOWED_HOSTS`
- [ ] Configure production database
- [ ] Set up log file directory with proper permissions
- [ ] Run security validation: `python manage.py validate_security --environment production`
- [ ] Test all functionality in production environment

## Security Best Practices

### 1. Secret Management
- Use strong, unique passwords (16+ characters)
- Generate new SECRET_KEY for each environment
- Never commit `.env` files to version control
- Rotate secrets regularly

### 2. File Permissions
```bash
# Set secure permissions for environment files
chmod 600 .env*
chmod 600 config/settings.py
```

### 3. Database Security
- Use dedicated database user with minimal privileges
- Enable database SSL/TLS connections
- Regular database backups with encryption

### 4. HTTPS Configuration
- Use valid SSL certificates
- Enable HSTS headers
- Configure secure cookie settings
- Test SSL configuration with tools like SSL Labs

## Troubleshooting

### Common Issues

#### 1. Missing Environment Variables
```
Error: SECRET_KEY environment variable is required in production
```
**Solution:** Set the required environment variable or run the generate script.

#### 2. Insecure Production Settings
```
SECURITY VALIDATION ERRORS:
- DEBUG must be False in production
```
**Solution:** Set `DEBUG=False` in your environment file.

#### 3. Database Connection Errors
```
Error: DB_NAME environment variable is required
```
**Solution:** Ensure all database environment variables are set.

### Validation Commands

```bash
# Check what environment variables are set
python manage.py validate_security

# Test database connection
python manage.py dbshell

# Check Django configuration
python manage.py check --deploy
```

## Migration from Old Configuration

### 1. Backup Current Settings
```bash
cp config/settings.py config/settings.py.backup
```

### 2. Generate Environment File
```bash
python scripts/generate_env.py --environment development
```

### 3. Update Environment Variables
Edit `.env` file with your current database credentials and settings.

### 4. Test Configuration
```bash
python manage.py validate_security
python manage.py runserver
```

### 5. Deploy to Production
Follow the production deployment checklist above.

## Support

For security-related issues or questions:
1. Check this documentation
2. Run `python manage.py validate_security --fix`
3. Review Django security documentation
4. Contact system administrator

## Security Updates

This security configuration system will be updated as needed to address:
- New security vulnerabilities
- Django security best practices
- Compliance requirements
- Performance optimizations

Always test security updates in a staging environment before production deployment.