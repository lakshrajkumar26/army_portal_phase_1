"""
Django management command to validate security configuration.

Usage:
    python manage.py validate_security
    python manage.py validate_security --environment production
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from config.security_config import SecurityConfig, SecureSettingsValidator
import os


class Command(BaseCommand):
    help = 'Validate security configuration for the exam portal'

    def add_arguments(self, parser):
        parser.add_argument(
            '--environment',
            type=str,
            default='development',
            choices=['development', 'staging', 'production'],
            help='Environment to validate (default: development)'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix common security issues'
        )

    def handle(self, *args, **options):
        environment = options['environment']
        fix_issues = options['fix']
        
        self.stdout.write(
            self.style.SUCCESS(f'Validating security configuration for {environment} environment...')
        )
        
        # Validate basic security configuration
        try:
            SecurityConfig.validate_security_settings()
            self.stdout.write(self.style.SUCCESS('✓ Basic security configuration is valid'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Basic security validation failed: {e}'))
            if not fix_issues:
                raise CommandError('Security validation failed. Use --fix to attempt automatic fixes.')
        
        # Validate production-specific settings
        if environment == 'production':
            validation_errors = SecureSettingsValidator.validate_production_settings(
                settings.__dict__
            )
            
            if validation_errors:
                self.stdout.write(self.style.ERROR('Production security validation errors:'))
                for error in validation_errors:
                    self.stdout.write(self.style.ERROR(f'  ✗ {error}'))
                
                if fix_issues:
                    self._attempt_fixes(validation_errors)
                else:
                    raise CommandError(
                        'Production security validation failed. '
                        'Please fix these issues or use --fix to attempt automatic fixes.'
                    )
            else:
                self.stdout.write(self.style.SUCCESS('✓ Production security validation passed'))
        
        # Check environment variables
        self._check_environment_variables(environment)
        
        # Check file permissions
        self._check_file_permissions()
        
        self.stdout.write(
            self.style.SUCCESS(f'Security validation completed for {environment} environment')
        )

    def _check_environment_variables(self, environment):
        """Check that required environment variables are set"""
        self.stdout.write('Checking environment variables...')
        
        required_vars = ['SECRET_KEY', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
        
        if environment == 'production':
            required_vars.extend(['ALLOWED_HOSTS'])
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.stdout.write(
                self.style.WARNING(f'Missing environment variables: {", ".join(missing_vars)}')
            )
        else:
            self.stdout.write(self.style.SUCCESS('✓ All required environment variables are set'))

    def _check_file_permissions(self):
        """Check file permissions for sensitive files"""
        self.stdout.write('Checking file permissions...')
        
        sensitive_files = ['.env', '.env.production', 'config/settings.py']
        
        for file_path in sensitive_files:
            if os.path.exists(file_path):
                file_stat = os.stat(file_path)
                permissions = oct(file_stat.st_mode)[-3:]
                
                if permissions != '600':
                    self.stdout.write(
                        self.style.WARNING(f'{file_path} has permissions {permissions}, should be 600')
                    )
                else:
                    self.stdout.write(self.style.SUCCESS(f'✓ {file_path} has secure permissions'))

    def _attempt_fixes(self, validation_errors):
        """Attempt to fix common security issues"""
        self.stdout.write(self.style.WARNING('Attempting to fix security issues...'))
        
        fixes_applied = []
        
        for error in validation_errors:
            if 'DEBUG must be False' in error:
                self.stdout.write('Setting DEBUG=False in environment...')
                os.environ['DEBUG'] = 'False'
                fixes_applied.append('Set DEBUG=False')
            
            elif 'SECRET_KEY must not use the default' in error:
                import secrets
                new_key = secrets.token_urlsafe(50)
                self.stdout.write('Generated new SECRET_KEY (please save to environment variables)')
                self.stdout.write(f'SECRET_KEY={new_key}')
                fixes_applied.append('Generated new SECRET_KEY')
            
            elif 'ALLOWED_HOSTS must not contain wildcard' in error:
                self.stdout.write('Please set ALLOWED_HOSTS environment variable with your domain names')
                fixes_applied.append('Identified ALLOWED_HOSTS issue')
        
        if fixes_applied:
            self.stdout.write(self.style.SUCCESS(f'Applied fixes: {", ".join(fixes_applied)}'))
        else:
            self.stdout.write(self.style.WARNING('No automatic fixes available for these issues'))