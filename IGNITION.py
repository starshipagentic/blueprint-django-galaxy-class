import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

def install_required_packages():
    required = ['typer', 'rich']
    for package in required:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing required package: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install required packages before imports
install_required_packages()

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich import print as rprint
                                                                                                        
app = typer.Typer()                                                                                      
console = Console()                                                                                      

# KEEP THESE IMPORTANT COMMENTS - DO NOT REMOVE
# - Use 'config' as the project configuration directory
# - Dynamically name the main app based on user input
# - Update paths, imports, and references accordingly
# - Maintain proper Django project structure and namespacing
# The changes ensure:
# 1. Configuration files are in a clearly named 'config' directory
# 2. Main app uses a meaningful name provided by the user
# 3. All references are updated to reflect the new structure
# 4. Consistent with Django best practices for project layout

ASCII_ART = """                                                                                          
🚀 DJANGO SHIP IGNITION 🚀                                                                               
=========================                                                                                
Initiating Launch Sequence...                                                                                        
"""     

EXPLOSION_ART = """
         .* *
       *    *  *
          *  .  *   *
       *  *  |  *  
    *   *  )|(  *
        * |||||
         |||||
          |||
           |
    🚀 BLAST OFF! 🚀
"""                                                                                   
                                                                                                        
def create_virtual_environment():                                                                        
    """Create and activate virtual environment."""                                                       
    with console.status("[bold green]Creating virtual environment...") as status:                        
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)                               
        console.print("[green]✓[/green] Virtual environment created")                                    
                                                                                                        
def install_dependencies():                                                                              
    """Install required packages."""                                                                     
    requirements = [                                                                                     
        "django>=4.2.0",                                                                                 
        "python-dotenv",                                                                                 
        "social-auth-app-django",                                                                        
        "django-allauth",                                                                                
        "selenium>=4.0.0",                                                                               
        "behave>=1.2.6",                                                                                 
        "behave-django>=1.4.0",                                                                          
        "pytest-django>=4.5.0",                                                                          
        "webdriver-manager",                                                                             
        "coverage",                                                                                      
        "typer",                                                                                         
        "rich",
        "pytest",
        "pytest-django"
    ]                                                                                                    
                                                                                                        
    with Progress(                                                                                       
        SpinnerColumn(),                                                                                 
        TextColumn("[progress.description]{task.description}"),                                          
        transient=True,                                                                                  
    ) as progress:                                                                                       
        task = progress.add_task("[cyan]Installing dependencies...", total=None)                         
                                                                                                        
        # Try both approaches for maximum reliability
        venv_pip = "./venv/bin/pip" if os.name != "nt" else r".\venv\Scripts\pip"
        
        # Install Django first to ensure django-admin is available
        try:
            subprocess.run([venv_pip, "install", "django>=4.2.0"], check=True)
        except subprocess.CalledProcessError as e:
            console.print("[red]Failed to install Django. Aborting.[/red]")
            raise typer.Exit(1)

        # Then install remaining packages
        try:
            for package in requirements[1:]:  # Skip Django since we already installed it
                try:
                    subprocess.run([venv_pip, "install", package], check=True)
                except subprocess.CalledProcessError as e:
                    console.print(f"[red]Failed to install {package}: {str(e)}[/red]")
                    raise
        finally:
            # Write requirements to file for reference
            with open("requirements.txt", "w") as f:
                f.write("\n".join(requirements))
                                                                                                        
        progress.update(task, completed=True)                                                            
                                                                                                        
def setup_django_project(project_name: str):                                                             
    """Initialize Django project structure."""                                                           
    venv_django = "./venv/bin/django-admin" if os.name != "nt" else r".\venv\Scripts\django-admin"
    venv_python = "./venv/bin/python" if os.name != "nt" else r".\venv\Scripts\python"
                                                                                                        
    with console.status("[bold green]Creating Django project...") as status:                             
        try:
            # Create project as 'config'                                                                                 
            subprocess.run([venv_django, "startproject", "config", "."], check=True)                          
        except subprocess.CalledProcessError:
            console.print("[red]Failed to create Django project. Make sure Django is installed correctly.[/red]")
            raise typer.Exit(1)
                                                                                                        
        # Create main app using project_name                                                                                
        subprocess.run([venv_python, "manage.py", "startapp", project_name], check=True)

        # Create tests directory structure
        os.makedirs("tests", exist_ok=True)
        test_files = {
            "tests/__init__.py": "",
            "tests/conftest.py": '''pytest_plugins = [
    "pytest_django",
]
''',
            "tests/test_views.py": '''import pytest
from django.test import Client

@pytest.mark.django_db
def test_home_page():
    client = Client()
    response = client.get('/')
    assert response.status_code == 200
'''
        }
        
        for file_path, content in test_files.items():
            with open(file_path, "w") as f:
                f.write(content)

        # Create pytest.ini
        pytest_ini_content = '''[pytest]
DJANGO_SETTINGS_MODULE = {}.settings
python_files = tests.py test_*.py *_tests.py
addopts = --ds={}.settings
testpaths = tests
'''.format(project_name, project_name)
        
        with open("pytest.ini", "w") as f:
            f.write(pytest_ini_content)

        # Create setup.py
        setup_py_content = '''from setuptools import setup, find_packages

setup(
    name="{}",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'django>=4.2.0',
        'python-dotenv',
        'social-auth-app-django',
        'django-allauth',
        'selenium>=4.0.0',
        'behave>=1.2.6',
        'behave-django>=1.4.0',
        'pytest-django>=4.5.0',
        'webdriver-manager',
        'coverage',
    ],
)
'''.format(project_name)
        
        with open("setup.py", "w") as f:
            f.write(setup_py_content)
        
        # Create services directory structure in project app
        services_dirs = [
            f"{project_name}/services",
            f"{project_name}/services/external",
        ]
        for dir_path in services_dirs:
            os.makedirs(dir_path, exist_ok=True)
            
        # Create service files
        service_files = {
            f"{project_name}/services/__init__.py": "",
            f"{project_name}/services/base.py": '''from typing import Any
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
''',
            f"{project_name}/services/exceptions.py": '''class ServiceException(Exception):
    """Base exception for service errors"""
    pass
''',
            f"{project_name}/services/external/__init__.py": "",
        }
        
        for file_path, content in service_files.items():
            with open(file_path, "w") as f:
                f.write(content)

        # Create main_app/urls.py with proper namespacing
        app_urls_content = '''from django.urls import path
from . import views

app_name = '{project_name}'

urlpatterns = [
    # Add your URL patterns here
]
'''.format(project_name=project_name)

        with open(f"{project_name}/urls.py", "w") as f:
            f.write(app_urls_content)

        # Update project's urls.py and settings.py
        project_urls_content = '''"""
URL configuration for {project_name} project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('{project_name}.urls', namespace='{project_name}')),
]
'''.format(project_name=project_name)

        project_settings_content = '''"""
Django settings for {project_name} project.
"""
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-CHANGE-THIS-IN-PRODUCTION'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
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
    '{project_name}',  # Local app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Required for django-allauth
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

AUTH_PASSWORD_VALIDATORS = [
    {{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}},
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# OAuth2 Settings
SOCIALACCOUNT_PROVIDERS = {{
    'google': {{
        'APP': {{
            'client_id': 'your-client-id',
            'secret': 'your-secret',
            'key': ''
        }},
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {{
            'access_type': 'online',
        }}
    }}
}}

SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Testing Settings
BEHAVE_DJANGO_TESTSERVER = True
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
'''.format(project_name=project_name)

        with open(f"{project_name}/urls.py", "w") as f:
            f.write(project_urls_content)
            
        with open("config/settings.py", "w") as f:
            f.write(project_settings_content)

        # Create directory structure                                                                     
        os.makedirs("features/steps", exist_ok=True)                                                     
        Path("features/__init__.py").touch()                                                             
        
        # Create environment.py with proper test setup
        environment_py_content = '''from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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
    chrome_options.add_argument('--headless')  # Run in headless mode
    service = Service(ChromeDriverManager().install())
    context.browser = webdriver.Chrome(service=service, options=chrome_options)
    context.browser.implicitly_wait(10)

def after_all(context):
    context.browser.quit()
    if hasattr(context, 'server'):
        context.server.tearDownClass()

def before_scenario(context, scenario):
    # Reset database state
    from django.core.management import call_command
    call_command('flush', verbosity=0, interactive=False)
'''
        with open("features/environment.py", "w") as f:
            f.write(environment_py_content)

        # Create homepage.feature
        homepage_feature_content = '''Feature: Homepage
  Scenario: Visit the homepage
    When I visit the homepage
    Then I should see the page load successfully
'''
        with open("features/homepage.feature", "w") as f:
            f.write(homepage_feature_content)

        # Create step definitions file
        steps_content = '''from behave import when, then
from selenium.webdriver.common.by import By

@when('I visit the homepage')
def step_impl(context):
    context.browser.get(context.server_url)

@then('I should see the page load successfully')
def step_impl(context):
    assert context.browser.current_url == context.server_url + "/"
'''
        with open("features/steps/homepage_steps.py", "w") as f:
            f.write(steps_content)
            
        Path("features/steps/__init__.py").touch()                                                       
                                                                                                        
        # Create templates and static directories
        os.makedirs(f"{project_name}/templates/{project_name}", exist_ok=True)
        os.makedirs(f"{project_name}/static/{project_name}/css", exist_ok=True)
        os.makedirs(f"{project_name}/static/{project_name}/js", exist_ok=True)
        os.makedirs(f"{project_name}/static/{project_name}/images", exist_ok=True)

        # Create base template
        base_template = '''{% load static %}
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'main_app/css/style.css' %}">
</head>
<body>
    {% block content %}
    {% endblock %}
    <script src="{% static 'main_app/js/main.js' %}"></script>
</body>
</html>
'''
        with open(f"{project_name}/templates/{project_name}/base.html", "w") as f:
            f.write(base_template)

        # Create initial static files
        with open(f"{project_name}/static/{project_name}/css/style.css", "w") as f:
            f.write("/* Add your styles here */\n")
        
        with open(f"{project_name}/static/{project_name}/js/main.js", "w") as f:
            f.write("// Add your JavaScript here\n")

        # Create .gitignore
        gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test coverage
htmlcov/
.tox/
.coverage
.coverage.*
.cache
coverage.xml
*.cover
'''
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)

        # Initialize git                                                                                 
        subprocess.run(["git", "init"], check=True)                                                      

        # Run migrations
        venv_python = "./venv/bin/python" if os.name != "nt" else r".\venv\Scripts\python"
        console.print("\n[cyan]Running migrations...[/cyan]")
        try:
            subprocess.run([venv_python, "manage.py", "migrate"], check=True)
            console.print("[green]✓[/green] Database migrations applied")
        except subprocess.CalledProcessError:
            console.print("[red]Failed to apply migrations[/red]")
            raise typer.Exit(1)

        # Exit any status display before superuser creation
        console.print("[green]✓[/green] Django project created")

        # Create superuser non-interactively without prompting
        console.print("\n[cyan]Creating superuser...[/cyan]")
        env = os.environ.copy()
        env["DJANGO_SUPERUSER_USERNAME"] = "admin"
        env["DJANGO_SUPERUSER_PASSWORD"] = "admin123"
        env["DJANGO_SUPERUSER_EMAIL"] = "admin@example.com"

        try:
            subprocess.run([venv_python, "manage.py", "createsuperuser", "--noinput"], 
                         check=True,
                         env=env)
            console.print("[green]✓[/green] Superuser 'admin' created")
        except subprocess.CalledProcessError:
            console.print("[red]Failed to create superuser[/red]")
            raise typer.Exit(1)
        
        # Create behave.ini in project root
        behave_ini_content = '''[behave]
paths = features
steps = features/steps
'''
        with open("behave.ini", "w") as f:
            f.write(behave_ini_content)

@app.command()                                                                                           
def launch(project_name: str = typer.Argument(None, help="Name of your Django project")):                 
    """                                                                                                  
    Launch a new Django project with the Ship Manual architecture.                                       
    """
    console.print(Panel(ASCII_ART, style="bold blue"))

    if project_name is None:
        project_name = typer.prompt(
            "\n" + typer.style("What would you like to name your Django project?", fg=typer.colors.CYAN, bold=True),
            default="myproject",
            prompt_suffix=" ",
        )
        
        # Collect mission information
        goal = typer.prompt(
            "\n" + typer.style("What is the goal of your app?", fg=typer.colors.CYAN, bold=True),
            prompt_suffix=" "
        )
        
        # Create MISSION.md
        mission_content = f"""# Mission Statement for {project_name}

## GOAL
{goal}

## PROBLEM
[Describe the specific problem or pain point your app addresses]

## SOLUTION
[Explain how your app solves the problem]

## IMPLEMENTATION PLAN
[Detail the technical approach and key features]

## BENEFITS
[List the key benefits and value proposition for users]
"""
        with open("MISSION.md", "w") as f:
            f.write(mission_content)
        
        console.print(f"\n[bold]Project name:[/bold] {project_name}")
        console.print("[bold]Description:[/bold] Creates a new Django project with BDD testing framework\n")

        # Launch sequence countdown
        for count in range(3, 0, -1):
            console.print(f"[bold red]{count}...[/bold red]", end="\r")
            time.sleep(1)
        console.print("\n")
        console.print(Panel(EXPLOSION_ART, style="bold yellow"))
        time.sleep(1)
                                                                                                        
    # Execute steps sequentially without nested progress bars
    try:
        console.print("\n[cyan]Creating virtual environment...[/cyan]")
        create_virtual_environment()
        
        console.print("\n[cyan]Installing dependencies...[/cyan]")
        install_dependencies()
        
        console.print("\n[cyan]Setting up Django project...[/cyan]")
        setup_django_project(project_name)  # Let this create the directory first
        
        # Move requirements.txt after project creation
        shutil.copy2("requirements.txt", os.path.join(project_name, "requirements.txt"))
        
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
                                                                                                        
    # Show virtual environment status
    venv_python = "./venv/bin/python" if os.name != "nt" else r".\venv\Scripts\python"
    try:
        version_info = subprocess.check_output([venv_python, "-V"], text=True).strip()
        console.print(f"\n[bold green]🚀 Launch successful![/bold green]")
        console.print(f"\n[yellow]Virtual environment is ready with {version_info}[/yellow]")
        console.print("\n[bold cyan]To activate virtual environment:[/bold cyan]")
        if os.name != "nt":
            console.print("    source venv/bin/activate")
        else:
            console.print("    .\\venv\\Scripts\\activate")
        console.print("\n[bold cyan]After activation, you can:[/bold cyan]")
        console.print("1. RUN: python manage.py runserver")
        console.print("2. TEST: python manage.py behave")
        console.print("\n[bold cyan]Super user credentials:[/bold cyan]")
        console.print("Username: admin")
        console.print("Password: admin123")
    except subprocess.CalledProcessError:
        console.print("[red]Warning: Could not verify virtual environment[/red]")
                                                                                                        
if __name__ == "__main__":                                                                               
    app()
