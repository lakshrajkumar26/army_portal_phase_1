"""
Security Configuration Management for Django Exam Portal

This module provides secure configuration management using environment variables
and validation for production deployments.
"""

import os
import secrets
from typing import Dict, List, Optional, Any
from django.core.exceptions import ImproperlyConfigured


class SecurityConfig:
    """Centralized security configuration management"""
    
    @staticmethod
    def load_secret_key() -> str:
        """
        Load SECRET_KEY from environment variables with fallback generation.
        
        Returns:
            str: Cryptographically secure secret key
            
        Raises:
            ImproperlyConfigured: If no secret key is provided in production
        """
        secret_key = os.environ.get('SECRET_KEY')
        
        if not secret_key:
            if os.environ.get('DJANGO_ENV') == 'production':
                raise ImproperlyConfigured(
                    "SECRET_KEY environment variable is required in production"
                )
            # Generate a secure key for development
            secret_key = secrets.token_urlsafe(50)
            
        return secret_key
    
    @staticmethod
    def get_allowed_hosts() -> List[str]:
        """
        Get ALLOWED_HOSTS from environment variables.
        
        Returns:
            List[str]: List of allowed hostnames
        """
        allowed_hosts = os.environ.get('ALLOWED_HOSTS', '')
        if not allowed_hosts:
            if os.environ.get('DJANGO_ENV') == 'production':
                raise ImproperlyConfigured(
                    "ALLOWED_HOSTS environment variable is required in production"
                )
            return ['localhost', '127.0.0.1']
        
        return [host.strip() for host in allowed_hosts.split(',') if host.strip()]
    
    @staticmethod
    def is_debug_enabled() -> bool:
        """
        Determine if DEBUG mode should be enabled.
        
        Returns:
            bool: True if debug should be enabled, False otherwise
        """
        debug = os.environ.get('DEBUG', 'False').lower()
        django_env = os.environ.get('DJANGO_ENV', 'development').lower()
        
        # Only allow DEBUG=True in development
        if django_env == 'production':
            return False
        
        return debug in ('true', '1', 'yes', 'on')
    
    @staticmethod
    def get_database_config() -> Dict[str, str]:
        """
        Get database configuration from environment variables.
        
        Returns:
            Dict[str, str]: Database configuration dictionary
            
        Raises:
            ImproperlyConfigured: If required database settings are missing
        """
        required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
        config = {}
        
        for var in required_vars:
            value = os.environ.get(var)
            if not value:
                raise ImproperlyConfigured(f"{var} environment variable is required")
            config[var.lower()] = value
        
        config['db_port'] = os.environ.get('DB_PORT', '3306')
        
        return {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config['db_name'],
            'USER': config['db_user'],
            'PASSWORD': config['db_password'],
            'HOST': config['db_host'],
            'PORT': config['db_port'],
        }
    
    @staticmethod
    def validate_security_settings() -> bool:
        """
        Validate all security settings are properly configured.
        
        Returns:
            bool: True if all settings are valid
            
        Raises:
            ImproperlyConfigured: If any security setting is invalid
        """
        try:
            # Validate secret key
            secret_key = SecurityConfig.load_secret_key()
            if len(secret_key) < 32:
                raise ImproperlyConfigured("SECRET_KEY must be at least 32 characters long")
            
            # Validate allowed hosts
            allowed_hosts = SecurityConfig.get_allowed_hosts()
            if not allowed_hosts:
                raise ImproperlyConfigured("ALLOWED_HOSTS cannot be empty")
            
            # Validate database config
            db_config = SecurityConfig.get_database_config()
            if not all(db_config.values()):
                raise ImproperlyConfigured("All database configuration values are required")
            
            return True
            
        except Exception as e:
            raise ImproperlyConfigured(f"Security validation failed: {str(e)}")


class SecureSettingsValidator:
    """Validator for secure Django settings"""
    
    @staticmethod
    def validate_production_settings(settings_dict: Dict[str, Any]) -> List[str]:
        """
        Validate settings for production deployment.
        
        Args:
            settings_dict: Django settings dictionary
            
        Returns:
            List[str]: List of validation errors
        """
        errors = []
        
        # Check DEBUG is False in production
        if settings_dict.get('DEBUG', False):
            errors.append("DEBUG must be False in production")
        
        # Check SECRET_KEY is not the default Django key
        secret_key = settings_dict.get('SECRET_KEY', '')
        if 'django-insecure' in secret_key:
            errors.append("SECRET_KEY must not use the default Django insecure key")
        
        # Check ALLOWED_HOSTS is not wildcard
        allowed_hosts = settings_dict.get('ALLOWED_HOSTS', [])
        if '*' in allowed_hosts:
            errors.append("ALLOWED_HOSTS must not contain wildcard '*' in production")
        
        # Check security middleware is enabled
        middleware = settings_dict.get('MIDDLEWARE', [])
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
        ]
        
        for mw in required_middleware:
            if mw not in middleware:
                errors.append(f"Required security middleware missing: {mw}")
        
        return errors


class EnvironmentLoader:
    """Safe environment variable loading utilities"""
    
    @staticmethod
    def load_env_file(env_file_path: str) -> None:
        """
        Load environment variables from a .env file.
        
        Args:
            env_file_path: Path to the .env file
        """
        if not os.path.exists(env_file_path):
            return
        
        with open(env_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value
    
    @staticmethod
    def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
        """
        Safely get environment variable with validation.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            required: Whether the variable is required
            
        Returns:
            str: Environment variable value
            
        Raises:
            ImproperlyConfigured: If required variable is missing
        """
        value = os.environ.get(key, default)
        
        if required and not value:
            raise ImproperlyConfigured(f"Required environment variable '{key}' is not set")
        
        return value
    
    @staticmethod
    def get_bool_env(key: str, default: bool = False) -> bool:
        """
        Get boolean environment variable.
        
        Args:
            key: Environment variable name
            default: Default boolean value
            
        Returns:
            bool: Boolean value
        """
        value = os.environ.get(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    @staticmethod
    def get_int_env(key: str, default: int = 0) -> int:
        """
        Get integer environment variable.
        
        Args:
            key: Environment variable name
            default: Default integer value
            
        Returns:
            int: Integer value
        """
        value = os.environ.get(key, str(default))
        try:
            return int(value)
        except ValueError:
            return default