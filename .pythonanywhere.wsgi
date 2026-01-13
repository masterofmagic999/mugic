"""
PythonAnywhere WSGI Configuration File

Instructions:
1. Upload this file to PythonAnywhere
2. Update the paths below with your username
3. Set your secret keys in the environment variables
4. Configure this file in the Web tab of PythonAnywhere dashboard
"""

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/mugic'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
# IMPORTANT: Replace these with your actual secret keys
os.environ['SECRET_KEY'] = 'your-secret-key-here-generate-with-python-secrets'
os.environ['JWT_SECRET_KEY'] = 'your-jwt-secret-key-here-generate-with-python-secrets'
os.environ['FLASK_ENV'] = 'production'

# Import flask app
from app import app as application
