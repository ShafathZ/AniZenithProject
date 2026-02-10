import os

class Config:
    # General Configurations
    DEBUG = False
    ENV = 'production'

    # Security Configurations
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
    PROPAGATE_EXCEPTIONS=True

class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    PROPAGATE_EXCEPTIONS=False

class TestingConfig(Config):
    ENV = 'testing'
    TESTING = True