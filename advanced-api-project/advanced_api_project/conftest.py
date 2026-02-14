"""
Pytest Configuration for advanced-api-project

This file configures pytest to work optimally with Django and DRF.
It provides fixtures and configuration for running tests with pytest.

Installation:
    pip install pytest pytest-django pytest-cov

Running tests with pytest:
    pytest                           # Run all tests
    pytest -v                        # Verbose output
    pytest --cov=api                 # With coverage
    pytest -k test_create            # Run specific test
    pytest api/test_views.py         # Run specific file
"""

import os
import sys
import django
from django.conf import settings
from pathlib import Path

# Add project to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configure Django settings for pytest
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advanced_api_project.settings_test')

# Setup Django
def pytest_configure():
    """Configure pytest with Django settings."""
    if not settings.configured:
        django.setup()


# ============================================================================
# PYTEST PLUGINS & OPTIONS
# ============================================================================

pytest_plugins = [
    'pytest_django',
]

# Configure pytest-django
def pytest_configure_django():
    """Configure Django test database."""
    return {
        'DJANGO_FIND_PROJECT': True,
        'DJANGO_DEBUG_MODE': True,
    }


# ============================================================================
# TEST DISCOVERY & COLLECTION
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to mark tests with appropriate markers.
    """
    for item in items:
        # Mark tests by file
        if 'test_views' in str(item.fspath):
            item.add_marker('views')
        if 'test_models' in str(item.fspath):
            item.add_marker('models')
        if 'test_serializers' in str(item.fspath):
            item.add_marker('serializers')
        if 'test_filters' in str(item.fspath):
            item.add_marker('filters')


# ============================================================================
# PYTEST FIXTURES FOR API TESTING
# ============================================================================

import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.fixture
def api_client():
    """
    Fixture providing an API client for testing.
    
    Usage:
        def test_api_endpoint(api_client):
            response = api_client.get('/api/books/')
    """
    return APIClient()


@pytest.fixture
def authenticated_client(db):
    """
    Fixture providing an authenticated API client.
    
    Usage:
        def test_authenticated_endpoint(authenticated_client):
            response = authenticated_client.post('/api/books/create/', {...})
    """
    client = APIClient()
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def test_user(db):
    """
    Fixture providing a test user.
    
    Usage:
        def test_user_creation(test_user):
            assert test_user.username == 'testuser'
    """
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def test_admin_user(db):
    """
    Fixture providing a test admin user.
    
    Usage:
        def test_admin_operations(test_admin_user):
            assert test_admin_user.is_staff == True
    """
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


# ============================================================================
# PYTEST MARKERS
# ============================================================================
# Define custom markers for organizing tests

def pytest_configure_markers(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "test_views: marks tests as API view tests"
    )
    config.addinivalue_line(
        "markers", "test_models: marks tests as model tests"
    )
    config.addinivalue_line(
        "markers", "test_serializers: marks tests as serializer tests"
    )
    config.addinivalue_line(
        "markers", "test_filters: marks tests as filter tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


# ============================================================================
# PYTEST CONFIGURATION OPTIONS
# ============================================================================

# pytest.ini configuration is specified below as comments
# or create pytest.ini file with following content:

"""
[pytest]
DJANGO_FIND_PROJECT = true
DJANGO_DEBUG_MODE = true
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --tb=short
    --disable-warnings
    -ra
testpaths = api
"""

# ============================================================================
# PYTEST SETTINGS FOR DJANGO
# ============================================================================

# Pytest will look for these settings:
# DJANGO_SETTINGS_MODULE - Already set above
# DJANGO_FIND_PROJECT - True by default
# DJANGO_DEBUG_MODE - Set above

# Database transaction handling
# Use 'django_db' marker for tests that need database access

print("\n" + "="*80)
print("PYTEST CONFIGURATION LOADED")
print("="*80)
print("✓ Django settings: advanced_api_project.settings_test")
print("✓ Database mode: Transactional isolation")
print("✓ Fixtures available: api_client, authenticated_client, test_user")
print("✓ Markers available: @pytest.mark.views, @pytest.mark.models")
print("✓ Run with: pytest [options]")
print("="*80 + "\n")
