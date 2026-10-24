#!/usr/bin/env python
"""Django's command-line utility for administrative tasks - SRS School ERP."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SRSProject.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Auto-migrate and auto-seed on 'runserver' if database is empty
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        try:
            import django
            django.setup()
            from django.core.management import call_command
            print("==================================================")
            print("  Starting SRS School ERP...")
            print("  Checking database migrations...")
            call_command('migrate', interactive=False)
            
            from school_erp.models import Student
            if Student.objects.count() == 0:
                print("  Populating initial school data (classes, students, fees, exams)...")
                from school_erp.seed_data import seed_all
                seed_all()
            print("  SRS School ERP is ready! Open http://127.0.0.1:8000 in your browser.")
            print("==================================================")
        except Exception as e:
            print(f"Notice: Auto-check info: {e}")

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
