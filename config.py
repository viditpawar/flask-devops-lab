"""
Application configuration management for different environments.
Supports development, staging, and production configurations.
"""
import os


def _env_bool(name: str, default: bool) -> bool:
    """Read a boolean value from environment variables."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Base configuration with common settings."""

    # Flask settings
    TESTING = False
    DEBUG = False
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # API authentication
    API_KEY_HEADER = 'X-API-Key'
    VALID_API_KEY = os.getenv('VALID_API_KEY', 'default-key')

    # Rate limiting
    RATELIMIT_ENABLED = _env_bool('RATELIMIT_ENABLED', True)
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = '100/hour'

    # Application Insights
    APPINSIGHTS_INSTRUMENTATION_KEY = os.getenv('APPINSIGHTS_INSTRUMENTATION_KEY', '')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = 'json'  # json or text

    # Feature flags
    ENABLE_AUTH = _env_bool('ENABLE_AUTH', False)
    ENABLE_MONITORING = _env_bool('ENABLE_MONITORING', True)


class DevelopmentConfig(Config):
    """Development environment configuration."""
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    ENABLE_AUTH = False  # Disabled in development
    APPINSIGHTS_INSTRUMENTATION_KEY = ''  # Not used in development


class StagingConfig(Config):
    """Staging environment configuration."""
    FLASK_ENV = 'staging'
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'INFO'
    ENABLE_AUTH = True
    RATELIMIT_DEFAULT = '500/hour'


class ProductionConfig(Config):
    """Production environment configuration."""
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'
    ENABLE_AUTH = True
    RATELIMIT_DEFAULT = '1000/hour'


def get_config(env: str = None) -> Config:
    """
    Get configuration object based on environment.

    Args:
        env: Environment name (development, staging, production).
             If None, uses FLASK_ENV environment variable.

    Returns:
        Configuration object for the specified environment.
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')

    config_map = {
        'dev': DevelopmentConfig,
        'development': DevelopmentConfig,
        'stage': StagingConfig,
        'staging': StagingConfig,
        'prod': ProductionConfig,
        'production': ProductionConfig,
    }

    return config_map.get(str(env).lower(), DevelopmentConfig)()
