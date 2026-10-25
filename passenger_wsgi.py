"""
cPanel WSGI Application Entry Point (Phusion Passenger)
SRS School ERP Multi-Tenant SaaS Platform
"""
import os
import sys

# Automatically set base directory to the folder containing this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Fallback for explicit virtualenv paths if needed
for venv_path in [
    os.path.join(os.path.expanduser('~'), 'virtualenv', os.path.basename(BASE_DIR), '3.11', 'lib', 'python3.11', 'site-packages'),
    '/home/srsinfoconnect/virtualenv/School_ERP/3.11/lib/python3.11/site-packages',
]:
    if os.path.exists(venv_path) and venv_path not in sys.path:
        sys.path.insert(0, venv_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SRSProject.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
