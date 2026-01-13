"""
PythonAnywhere WSGI Configuration File

Instructions:
1. Upload this file to PythonAnywhere
2. Update the paths below with your username
3. Set your secret keys as shown below
4. Configure this file in the Web tab of PythonAnywhere dashboard

SECURITY WARNING: Never commit actual secret keys to version control!
Generate secure keys with: python -c "import secrets; print(secrets.token_hex(32))"
"""

import sys
import os

# Add your project directory to the sys.path
# IMPORTANT: Replace '<yourusername>' with your actual PythonAnywhere username
project_home = '/home/<yourusername>/mugic'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
# SECURITY: Replace these placeholder values with your actual secret keys!
# Generate secure keys with: python -c "import secrets; print(secrets.token_hex(32))"
os.environ['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'CHANGE-THIS-your-secret-key-here')
os.environ['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'CHANGE-THIS-your-jwt-secret-key-here')
os.environ['FLASK_ENV'] = 'production'

# Import flask app
from app import app as application
