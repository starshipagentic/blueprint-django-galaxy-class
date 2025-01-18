# SHIP MANUAL
> Framework for Building Test-Driven Django Web Applications with BDD

## Core Architecture

### 1. Project Foundation
- Django web framework for backend
- Django ORM for database abstraction and management
  - Leverages Django's built-in ORM for all database operations
  - No raw SQL - maintain database agnostic approach
  - Use Django migrations for schema management
- Behavior-Driven Development (BDD) testing methodology
- Selenium for browser automation
- OAuth2 for authentication
- Modular app-based structure

### 2. Key Components

#### 2.1 Testing Framework
- Behave for BDD testing
  - Feature files written in Gherkin syntax
  - Step definitions with robust error handling
  - Multiple selector strategies for reliability
  - Explicit waits and timeouts
  - Session handling for authentication
- Selenium WebDriver
  - Headless Chrome configuration
  - WebDriverWait patterns
  - Flexible element location strategies
- Pytest-django for unit testing
- Automated environment setup/teardown

#### 2.2 Authentication Strategy
- Hybrid authentication approach:
  - Primary: Google OAuth2 SSO for end-user convenience
  - Secondary: Django's built-in user management for admin/system users
  - All external users map to Django User model
  - Leverage Django's groups and permissions regardless of auth method
  - Single source of truth: Django's auth system remains the backbone

Key Implementation Points:
- OAuth users automatically create corresponding Django users
- Groups/Roles work identically for both auth methods
- Admin interface uses Django auth exclusively
- Tests can use either auth method
- Permissions system remains consistent across auth types

Implementation Details:
- Session-based authentication
- Test authentication simulation
- Secure cookie handling

#### 2.3 Frontend
- Django templates
- Static file management
- Responsive design patterns
- Clean separation of concerns

### 3. Project Structure
```
project_root/
├── venv/                      # Virtual environment
├── project_name/              # Django project container
│   ├── settings.py           # Project settings
│   ├── urls.py               # Main URL routing
│   └── wsgi.py               # WSGI configuration
├── app_name/                 # Main application module
│   ├── admin.py             # Admin interface
│   ├── models.py            # Data models
│   ├── views.py             # View logic
│   ├── urls.py              # App-specific routing (with namespaces)
│   ├── templates/           # HTML templates
│   └── services/            # External API and service layer
│       ├── base.py         # Base service patterns
│       ├── exceptions.py   # Custom service exceptions
│       └── external/       # External API clients
├── features/                # BDD test suite
│   ├── environment.py       # Test environment & WebDriver setup
│   ├── *.feature           # Behavior specifications
│   └── steps/              # Step implementations
│       ├── __init__.py     # Step utilities
│       ├── auth_steps.py   # Authentication steps
│       └── app_steps.py    # Application steps
├── tests/                   # Pytest test suite
│   ├── __init__.py
│   ├── conftest.py         # Pytest-django configuration
│   └── test_*.py           # django-Unit tests
├── manage.py               # Django management
├── behave.ini              # Behave INI
├── requirements.txt        # Dependencies
└── setup.py               # Package configuration
```

### 4. Development Workflow

#### 4.1 Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies (two approaches)
# 1. With activated venv:
pip install -r requirements.txt

# 2. Direct venv pip usage (more reliable):
./venv/bin/pip install -r requirements.txt  # On Windows: .\venv\Scripts\pip install -r requirements.txt

# For individual package installs:
./venv/bin/pip install package_name  # On Windows: .\venv\Scripts\pip install package_name

# Example for typer and rich:
./venv/bin/pip install typer rich  # On Windows: .\venv\Scripts\pip install typer rich
```

#### 4.2 Test-Driven Development Cycle
1. Write feature file (*.feature)
2. Implement step definitions
3. Run tests (`behave`)
4. Implement application code
5. Refactor and repeat

### 5. Best Practices

#### 5.1 Testing
- Write features before implementation
- Maintain isolated test environments
- Use explicit waits in Selenium
- Implement robust element selectors
- Simulate authentication in tests

#### 5.2 Code Organization
- Separate concerns (models, views, templates)
- Maintain clear URL structure
- Use Django's built-in security features
- Follow Django's app convention
- Keep features atomic and focused

#### 5.3 Authentication
- Use secure session handling
- Implement proper OAuth flows
- Maintain test authentication shortcuts
- Handle authentication failures gracefully

### 6. Dependencies and Setup

#### 6.1 Core Dependencies
```
django>=4.2.0         # Web framework
python-dotenv         # Environment management
social-auth-app-django # OAuth handling SSO (like google)
django-allauth        # Authentication
```

#### 6.2 Testing Dependencies
```
selenium>=4.0.0       # Browser automation
behave>=1.2.6        # BDD testing
behave-django>=1.4.0  # Django + Behave integration
pytest-django>=4.5.0  # Django test integration
webdriver-manager     # WebDriver management
urllib3              # HTTP client
coverage             # Code coverage
```

#### 6.3 Initial Setup Commands
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install django python-dotenv social-auth-app-django django-allauth
pip install selenium behave behave-django pytest pytest-django webdriver-manager coverage

# Create Django project
django-admin startproject project_name
cd project_name

# Create main app
python manage.py startapp main_app

# Create testing directory structure
mkdir -p features/steps
touch features/__init__.py
touch features/environment.py
touch features/steps/__init__.py

# Initialize database
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 7. Configuration Guide

#### 7.1 Django Settings
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for allauth
    
    # Third party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'behave_django',
    
    # Local apps
    'main_app',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# OAuth2 Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': 'your-client-id',
            'secret': 'your-secret',
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Django Auth Settings
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Testing Settings
BEHAVE_DJANGO_TESTSERVER = True
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

#### 7.2 Testing Configuration

##### 7.2.1 Testing Configuration

###### Test Environment Setup
```python
# features/environment.py
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class TestServer(StaticLiveServerTestCase):
    @classmethod
    def setup_class(cls):
        super().setUpClass()
        return cls

def before_all(context):
    # Set up Django test environment with static file serving
    context.server = TestServer.setup_class()
    context.server_url = context.server.live_server_url
    
    # Configure headless Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    context.browser = webdriver.Chrome(options=chrome_options)
    context.wait = WebDriverWait(context.browser, timeout=10)

def after_all(context):
    context.browser.quit()
    if hasattr(context, 'server'):
        context.server.tearDownClass()

def before_scenario(context, scenario):
    # Reset database state
    from django.core.management import call_command
    call_command('flush', verbosity=0, interactive=False)
```

###### Step Pattern Example
```python
# features/steps/app_steps.py
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

@given('I am logged in')
def step_impl(context):
    # Setup session authentication
    from django.contrib.sessions.backends.db import SessionStore
    session = SessionStore()
    session['user_id'] = user.id
    session.save()
    
    # Add session cookie to browser
    context.browser.add_cookie({
        'name': 'sessionid',
        'value': session.session_key,
        'path': '/'
    })
```

##### 7.2.2 Testing with pytest-django

###### Setup and Configuration
```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = project_name.settings
python_files = tests.py test_*.py *_tests.py
```

```python
# conftest.py
pytest_plugins = [
    "pytest_django",
]
```

###### Running Tests
```bash
# Verify pytest-django installation
pytest --trace-config

# Run all tests
pytest                     # Run all tests
pytest app_name/tests/     # Run tests in specific directory
pytest -v                  # Verbose output
pytest -k "test_name"     # Run tests matching pattern

# Run Django tests
python manage.py test

# Run specific Django test
python manage.py test app_name.tests.TestClassName

# Run BDD tests
python manage.py behave

# Run with coverage
coverage run -m pytest
coverage report
coverage html
```

The configuration ensures pytest uses the Django test framework and database management.

##### 7.2.3 Django Groups and Permissions

##### 7.2.4 Test Fixtures

###### Django Fixtures
```python
# fixtures/test_data.json
[
    {
        "model": "app.model",
        "pk": 1,
        "fields": {
            "field1": "value1",
            "field2": "value2"
        }
    }
]

# Create fixtures from existing data
python manage.py dumpdata app.model --indent 2 > fixtures/test_data.json

# Load fixtures in tests
from django.test import TestCase

class MyTest(TestCase):
    fixtures = ['test_data.json']
```

###### BDD Fixtures
```python
# features/environment.py
def before_scenario(context, scenario):
    # Load specific fixtures for BDD tests
    call_command('loaddata', 'test_data.json', verbosity=0)

# features/steps/common_steps.py
@given('there are initial blog posts')
def step_impl(context):
    # Use table syntax in feature files
    for row in context.table:
        Post.objects.create(
            title=row['title'],
            content=row['content']
        )
```

Example feature file usage:
```gherkin
Given there are initial blog posts:
  | title          | content       |
  | First Post     | Hello World   |
  | Second Post    | More content  |
```
```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# Create groups
admin_group = Group.objects.create(name='Administrators')
editor_group = Group.objects.create(name='Editors')
viewer_group = Group.objects.create(name='Viewers')

# Get content type
content_type = ContentType.objects.get_for_model(YourModel)

# Create permissions
view_permission = Permission.objects.create(
    codename='can_view_items',
    name='Can View Items',
    content_type=content_type,
)

edit_permission = Permission.objects.create(
    codename='can_edit_items',
    name='Can Edit Items',
    content_type=content_type,
)

# Assign permissions to groups
viewer_group.permissions.add(view_permission)
editor_group.permissions.add(view_permission, edit_permission)
admin_group.permissions.add(view_permission, edit_permission)
```

### 8. Common Patterns

#### 8.1 View Implementation
- Class-based views for common patterns
- Function views for specific logic
- Proper HTTP method handling
- Authentication decorators
- Form handling

#### 8.2 Testing Patterns
- Page object pattern for UI testing
- Step composition for common actions
- Explicit wait conditions
- Robust element selection
- Error handling and debugging

#### 8.3 URL Pattern Strategy
Always use namespaced URLs:
```python
# project/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls', namespace='app')),
]

# app/urls.py
app_name = 'app'
urlpatterns = [
    path('', views.home, name='home'),
    path('<int:pk>/', views.detail, name='detail'),
]

# In templates/views:
{% url 'app:home' %}
{% url 'app:detail' item.pk %}
```

#### 8.4 External Services Pattern

Structure external API calls and business logic in a `services` directory:
```python
# project_root/app_name/services/
├── __init__.py
├── base.py          # Base service patterns
├── exceptions.py    # Custom service exceptions
└── external/        # External API clients
    ├── __init__.py
    ├── google.py
    └── payment.py
```

Example Implementation:
```python
# services/base.py
from typing import Any
import requests
from .exceptions import ServiceException

class BaseService:
    def __init__(self):
        self.session = requests.Session()
    
    def handle_response(self, response: requests.Response) -> Any:
        try:
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise ServiceException(f"Service error: {str(e)}")

# services/external/google.py
from ..base import BaseService
from django.conf import settings

class GoogleAPIService(BaseService):
    BASE_URL = 'https://www.googleapis.com/oauth2/v1'
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.GOOGLE_API_KEY
    
    def get_user_info(self, token):
        response = self.session.get(
            f"{self.BASE_URL}/userinfo",
            headers={"Authorization": f"Bearer {token}"}
        )
        return self.handle_response(response)

# views.py
from .services.external.google import GoogleAPIService

def user_info_view(request):
    service = GoogleAPIService()
    try:
        user_info = service.get_user_info(request.user.social_auth.token)
        return JsonResponse(user_info)
    except ServiceException as e:
        return JsonResponse({'error': str(e)}, status=400)
```

Best Practices:
- Keep service logic separate from views
- Use dependency injection for testing
- Handle errors consistently
- Cache responses when appropriate
- Use environment variables for credentials
- Implement retry logic for unreliable APIs
- Log service interactions appropriately

Factory Pattern for Services:
```python
# services/factory.py
from enum import Enum
from typing import Type
from .base import BaseService
from .external.openai import OpenAIService
from .external.anthropic import AnthropicService
from .external.google import GoogleAIService

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"

class LLMServiceFactory:
    _services = {
        LLMProvider.OPENAI: OpenAIService,
        LLMProvider.ANTHROPIC: AnthropicService,
        LLMProvider.GOOGLE: GoogleAIService,
    }

    @classmethod
    def get_service(cls, provider: LLMProvider, **kwargs) -> BaseService:
        service_class = cls._services.get(provider)
        if not service_class:
            raise ValueError(f"Unknown provider: {provider}")
        return service_class(**kwargs)

# Usage in views:
def generate_content(request):
    provider = LLMProvider(request.POST.get('provider', 'openai'))
    service = LLMServiceFactory.get_service(
        provider,
        temperature=0.7,
        max_tokens=100
    )
    try:
        response = service.generate(prompt="Hello, world!")
        return JsonResponse({'content': response})
    except ServiceException as e:
        return JsonResponse({'error': str(e)}, status=400)
```

Best Practices for Service Factories:
- Use enums for provider types
- Maintain consistent interface across implementations
- Allow runtime configuration
- Handle provider-specific parameters
- Implement fallback strategies
- Cache factory instances when appropriate
- Use dependency injection for testing

### 9. Deployment Considerations
- Environment variables
- Static file serving
- Database configuration
- OAuth credentials
- Security settings

### 10. Maintenance
- Regular dependency updates
- Test suite maintenance
- Documentation updates
- Security patches
- Performance monitoring

## Quick Start
1. Clone this structure
2. Rename project components
3. Configure virtual environment
4. Install dependencies
5. Initialize Django project
6. Setup test environment
7. Begin TDD cycle

Remember: This is a template for building testable, maintainable web applications. Adapt the structure and practices to your specific needs while maintaining the core testing and architectural principles.
