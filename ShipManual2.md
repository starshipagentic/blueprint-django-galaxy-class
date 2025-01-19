# Complete Django Pattern Integration Guide

## 1. Project Structure
```
project_root/
├── venv/                      # Virtual environment
├── project_name/              # Django project container
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py          # Base settings
│   │   ├── development.py   # Dev settings
│   │   └── production.py    # Prod settings
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI configuration
├── app_name/                # Main application module
│   ├── models/             # Domain models
│   │   ├── __init__.py
│   │   ├── base.py        # Base model patterns
│   │   ├── order.py       # Order domain model
│   │   └── product.py     # Product domain model
│   ├── services/          # Service layer
│   │   ├── __init__.py
│   │   ├── base.py       # Base service patterns
│   │   ├── order.py      # Order services
│   │   └── external/     # External API clients
│   │       ├── google.py # Google OAuth
│   │       └── payment.py # Payment processing
│   ├── views/            # Views
│   │   ├── __init__.py
│   │   ├── base.py      # Base view patterns
│   │   └── order.py     # Order views
│   ├── templates/        # Templates
│   └── static/          # Static files
├── features/            # BDD test suite
│   ├── environment.py   # Test environment setup
│   ├── *.feature       # Feature files
│   └── steps/          # Step definitions
├── tests/              # Unit/Integration tests
├── manage.py           # Django management
└── requirements.txt    # Dependencies
```

## 2. Enhanced Model Layer

### 2.1 Base Model
```python
# app_name/models/base.py
from django.db import models
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def validate_and_save(self, *args, **kwargs):
        """Validate and save with logging"""
        try:
            self.full_clean()
            result = self.save(*args, **kwargs)
            logger.info(f"{self.__class__.__name__} saved: {self.pk}")
            return result
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
```

### 2.2 Domain Models
```python
# app_name/models/order.py
from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from .base import BaseModel

class Order(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def process_payment(self, payment_data):
        """Process order payment"""
        if self.status != 'pending':
            raise ValidationError("Only pending orders can be processed")
        
        with transaction.atomic():
            # Payment processing logic
            self.status = 'processing'
            self.save()
            return True

    @property
    def is_completable(self):
        """Check if order can be completed"""
        return (
            self.status == 'processing' and 
            self.orderitem_set.exists()
        )
```

## 3. Service Layer

### 3.1 Base Service
```python
# app_name/services/base.py
import requests
from typing import Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.cache import cache

class BaseService:
    def __init__(self):
        self._errors = []
        self.session = requests.Session()

    def handle_response(self, response: requests.Response) -> Any:
        """Handle external API response"""
        try:
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.add_error(f"API error: {str(e)}")
            raise

    @transaction.atomic
    def safe_execution(self, operation: callable, *args, **kwargs) -> Any:
        """Execute with error handling"""
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            self.add_error(str(e))
            raise

    def cached_execution(self, key: str, operation: callable, 
                        timeout: int = 300) -> Any:
        """Execute with caching"""
        result = cache.get(key)
        if result is None:
            result = operation()
            cache.set(key, result, timeout)
        return result
```

### 3.2 External Services
```python
# app_name/services/external/google.py
from ..base import BaseService
from django.conf import settings

class GoogleAuthService(BaseService):
    BASE_URL = 'https://www.googleapis.com/oauth2/v1'
    
    def get_user_info(self, token):
        """Get Google user info"""
        response = self.session.get(
            f"{self.BASE_URL}/userinfo",
            headers={"Authorization": f"Bearer {token}"}
        )
        return self.handle_response(response)
```

## 4. Testing Infrastructure

### 4.1 BDD Environment
```python
# features/environment.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

def before_all(context):
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    context.browser = webdriver.Chrome(options=chrome_options)
    context.wait = WebDriverWait(context.browser, timeout=10)

    # Setup Django test server
    context.test_server = StaticLiveServerTestCase()
    context.test_server.setUpClass()
    context.server_url = context.test_server.live_server_url

def after_all(context):
    context.browser.quit()
    context.test_server.tearDownClass()
```

### 4.2 Feature Example
```gherkin
# features/order_processing.feature
Feature: Order Processing
  As a customer
  I want to process orders
  So that I can complete my purchases

  Background:
    Given I am logged in
    And I have items in my cart

  Scenario: Process order payment
    When I submit payment for the order
    Then the order status should be "processing"
    And I should see a success message
```

### 4.3 Step Definitions
```python
# features/steps/order_steps.py
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

@when('I submit payment for the order')
def step_impl(context):
    # Wait for payment form
    form = context.wait.until(
        EC.presence_of_element_located((By.ID, "payment-form"))
    )
    # Fill payment details
    form.find_element(By.NAME, "card_number").send_keys("4242424242424242")
    form.find_element(By.NAME, "expiry").send_keys("1225")
    form.find_element(By.NAME, "cvv").send_keys("123")
    # Submit form
    form.submit()

@then('the order status should be "{status}"')
def step_impl(context, status):
    status_element = context.wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "order-status"))
    )
    assert status_element.text == status
```

## 5. Authentication Integration

### 5.1 Settings Configuration
```python
# settings/base.py
INSTALLED_APPS = [
    # ...
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
    }
}
```

### 5.2 OAuth Views Integration
```python
# app_name/views/auth.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
from ..services.external.google import GoogleAuthService

class GoogleLoginCallbackView(RedirectView):
    def get_redirect_url(self):
        service = GoogleAuthService()
        token = self.request.GET.get('token')
        try:
            user_info = service.get_user_info(token)
            # Process user info and login
            return '/'
        except Exception as e:
            return '/login?error=auth_failed'
```

## 6. Views and Templates

### 6.1 Views
```python
# app_name/views/order.py
from django.views import View
from django.http import JsonResponse
from ..services.order import OrderService

class OrderProcessView(LoginRequiredMixin, View):
    def post(self, request, order_id):
        service = OrderService()
        try:
            order = service.process_order(
                order_id=order_id,
                payment_data=request.POST
            )
            return JsonResponse({
                'status': 'success',
                'order_id': order.id
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
```

### 6.2 Templates
```html
<!-- templates/orders/detail.html -->
{% extends "base.html" %}

{% block content %}
<div class="order-detail">
    <h2>Order #{{ order.id }}</h2>
    <div class="order-status">{{ order.status }}</div>
    
    <form id="payment-form" method="POST" 
          action="{% url 'order_process' order.id %}">
        {% csrf_token %}
        <!-- Payment form fields -->
        <button type="submit">Process Payment</button>
    </form>
</div>
{% endblock %}
```

## 7. Development Workflow

### 7.1 Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Run development server
python manage.py runserver
```

### 7.2 Testing Commands
```bash
# Run BDD tests
python manage.py behave

# Run Django tests
python manage.py test

# Run with coverage
coverage run manage.py test
coverage report
```

## 8. Deployment and Production

### 8.1 Production Settings
```python
# settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    }
}
```

### 8.2 Production Checks
```python
# app_name/management/commands/production_checks.py
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Run production deployment checks'

    def handle(self, *args, **options):
        # Check security settings
        if not settings.SESSION_COOKIE_SECURE:
            self.stderr.write('SESSION_COOKIE_SECURE is not enabled')
            
        # Check cache configuration
        if 'redis' not in settings.CACHES['default']['BACKEND']:
            self.stderr.write('Redis cache is not configured')
```

This integration combines:
- Enhanced models with domain logic
- Robust service layer
- Complete testing infrastructure
- OAuth authentication
- Production-ready configuration

The structure maintains Django's simplicity while adding enterprise-level features from SHIPMANUAL.