import datetime
import django
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SRSProject.settings')
django.setup()

from django.contrib.auth.models import User
from school_erp.models import (
    AcademicSession, Student, StudentSessionEnrollment, 
    FeeInvoice, Exam, UserProfile
)

def run():
    print("Initializing Academic Sessions, Enrollments, and Admin User...")
    
    # 1. Ensure Default 2026-2027 Session exists
    session_2026, _ = AcademicSession.objects.get_or_create(
        name="2026-2027",
        defaults={
            'start_date': datetime.date(2026, 4, 1),
            'end_date': datetime.date(2027, 3, 31),
            'is_current': True
        }
    )
    print(f"Active Session: {session_2026.name}")

    # 2. Backfill Students
    students_updated = 0
    enrollments_created = 0
    for s in Student.objects.all():
        if not s.academic_session:
            s.academic_session = session_2026
            s.save(update_fields=['academic_session'])
            students_updated += 1
        
        # Ensure enrollment record
        enr, created = StudentSessionEnrollment.objects.get_or_create(
            student=s,
            academic_session=s.academic_session,
            defaults={
                'class_level': s.class_level,
                'section': s.section,
                'roll_number': s.roll_number,
                'status': 'Active'
            }
        )
        if created:
            enrollments_created += 1

    print(f"Updated {students_updated} students; created {enrollments_created} enrollments.")

    # 3. Backfill Fee Invoices & Exams
    inv_count = FeeInvoice.objects.filter(academic_session__isnull=True).update(academic_session=session_2026)
    exam_count = Exam.objects.filter(academic_session__isnull=True).update(academic_session=session_2026)
    print(f"Linked {inv_count} fee invoices and {exam_count} exams to session {session_2026.name}.")

    # 4. Ensure Admin User & Profile exists
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@srsschool.edu.in',
            password='admin'
        )
        print("Created default superuser 'admin' with password 'admin'")
    
    profile, _ = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={
            'role': 'Administrator',
            'can_manage_students': True,
            'can_manage_attendance': True,
            'can_manage_fees': True,
            'can_manage_exams': True,
            'can_manage_timetable': True,
            'can_manage_classes': True,
            'can_manage_sessions': True,
            'can_manage_users': True,
        }
    )
    print("Admin profile verified.")

if __name__ == '__main__':
    run()
