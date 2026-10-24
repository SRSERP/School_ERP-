"""
cPanel WSGI Application Entry Point (Phusion Passenger)
SRS School ERP Multi-Tenant SaaS Platform
"""
import os
import sys

BASE_DIR = '/home/srsinfoconnect/School_ERP'
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

venv_site_packages = '/home/srsinfoconnect/virtualenv/School_ERP/3.11/lib/python3.11/site-packages'
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SRSProject.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
