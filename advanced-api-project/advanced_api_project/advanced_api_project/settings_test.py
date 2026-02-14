"""
Django Test Configuration Settings

This file provides test-specific settings that override the default settings
when running unit tests. It's used to ensure tests run with optimal performance
and in an isolated environment.

Usage:
    python manage.py test --settings=advanced_api_project.settings_test

Or set environment variable:
    export DJANGO_SETTINGS_MODULE=advanced_api_project.settings_test
    python manage.py test
"""

from .settings import *  # noqa: F401, F403

# ============================================================================
# TEST DATABASE CONFIGURATION
# ============================================================================
# Use in-memory SQLite database for fast test execution
# This prevents any impact on development or production databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # In-memory database (fastest option)
        'TEST': {
            'NAME': ':memory:',
            'MIRROR': None,
            'CHARSET': None,
            'COLLATION': None,
            'CREATE_DB': True,
            'USER': None,
            'PASSWORD': None,
            'HOST': None,
            'PORT': None,
            'DEPENDENCIES': [],
            'SERIALIZE': False,
            'TEMPLATE': None,
        },
        'ATOMIC_REQUESTS': False,
        'AUTOCOMMIT': True,
        'CONN_MAX_AGE': 0,
        'CONN_HEALTH_CHECKS': False,
        'CONN_HEALTH_CHECKS_INTERVAL': 60,
    }
}

# ============================================================================
# TEST LOGGING CONFIGURATION
# ============================================================================
# Minimal logging during tests to reduce noise and improve readability

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '{levelname} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'WARNING',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'WARNING',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# ============================================================================
# TEST PASSWORD HASHING
# ============================================================================
# Use fast password hashing for tests (MD5)
# This speeds up test execution since password hashing is otherwise slow

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# ============================================================================
# TEST CACHE CONFIGURATION
# ============================================================================
# Use dummy cache (no-op) for tests to avoid cache-related issues

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# ============================================================================
# TEST EMAIL BACKEND
# ============================================================================
# Use in-memory email backend for tests to prevent actual email sending

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# ============================================================================
# TEST SECURITY SETTINGS
# ============================================================================
# Relax some security settings for testing environment

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://testserver',
    'http://127.0.0.1',
]

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ============================================================================
# TEST PERFORMANCE OPTIMIZATION
# ============================================================================

# Disable middleware that's not necessary for tests
MIDDLEWARE = [
    m for m in MIDDLEWARE if m not in [
        'django.middleware.security.SecurityMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
]

# Disable some checks that are not relevant for tests
SILENCED_SYSTEM_CHECKS = [
    'security.W004',  # SECURE_HSTS_SECONDS
    'security.W008',  # SECURE_SSL_REDIRECT
    'security.W012',  # SESSION_COOKIE_SECURE
]

# ============================================================================
# TEST API SETTINGS
# ============================================================================
# Configure DRF for testing

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# ============================================================================
# TEST RUNNER CONFIGURATION
# ============================================================================

# Use Django's default test runner with test settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# ============================================================================
# DEBUG AND VERBOSITY
# ============================================================================
# Debug settings for test environment

DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = True

# ============================================================================
# TEST PRINT STATEMENTS
# ============================================================================

print("\n" + "="*80)
print("TEST CONFIGURATION LOADED")
print("="*80)
print("✓ Database: In-memory SQLite (fastest performance)")
print("✓ Logging: WARNING level (minimal noise)")
print("✓ Password Hashing: MD5 (fast for tests)")
print("✓ Cache: Dummy backend (no caching)")
print("✓ Email: In-memory backend (no actual emails)")
print("✓ Security: Relaxed for testing environment")
print("="*80 + "\n")
