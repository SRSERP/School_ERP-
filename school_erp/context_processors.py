import datetime
from django.utils import timezone
from .models import SchoolProfile, AcademicSession, UserProfile


def get_current_school(request):
    """
    Returns the current SchoolProfile for the request:
    - If user is authenticated and linked to a school -> user.profile.school
    - If user is Platform Superadmin and switched to a specific school -> session['saas_active_school_id']
    - Fallback -> first SchoolProfile in database
    """
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        profile_obj = getattr(user, 'profile', None)
        if profile_obj and profile_obj.school:
            return profile_obj.school

        # Superadmin previewing a school
        if user.is_superuser or (profile_obj and profile_obj.is_platform_superadmin):
            saas_school_id = request.session.get('saas_active_school_id')
            if saas_school_id:
                s = SchoolProfile.objects.filter(id=saas_school_id).first()
                if s:
                    return s

    school = SchoolProfile.objects.first()
    if not school:
        school = SchoolProfile.objects.create(
            name="SRS International Public School",
            short_name="SRS School ERP",
            tagline="Empowering Minds, Shaping Futures",
            affiliation_number="CBSE-AFF/2026/SRS8892",
            school_code="SRS-01",
            address="SRS Knowledge Park, Knowledge Boulevard, Sector 62, New Delhi - 110092",
            phone="+91 98765 43210 / 011-23456789",
            email="contact@srsschool.edu.in",
            website="https://srsschool.edu.in",
            principal_name="Dr. Rajeshwar Sharma, Ph.D.",
            currency_symbol="₹",
            academic_year="2026-2027",
            registered_session_name="2026-2027",
            registered_session_start_date=datetime.date(2026, 4, 1),
            subscription_start_date=datetime.date.today(),
            subscription_end_date=datetime.date.today() + datetime.timedelta(days=30),
            is_active=True
        )
    return school


def get_active_session(request, school=None):
    """
    Returns the currently active AcademicSession for the school based on request.session.
    Defaults to the session marked is_current=True, or latest session belonging to this school.
    """
    if not school:
        school = get_current_school(request)

    all_sessions = AcademicSession.objects.filter(school=school).order_by('-start_date')
    has_session = hasattr(request, 'session') and request.session is not None
    if not all_sessions.exists():
        default_session = AcademicSession.objects.create(
            school=school,
            name=school.registered_session_name or "2026-2027",
            start_date=school.registered_session_start_date or datetime.date(2026, 4, 1),
            end_date=datetime.date(2027, 3, 31),
            is_current=True
        )
        if has_session:
            request.session[f'active_session_{school.id}'] = default_session.id
        return default_session

    active_id = (request.session.get(f'active_session_{school.id}') or request.session.get('active_academic_session_id')) if has_session else None
    current_session = None
    if active_id:
        try:
            current_session = all_sessions.filter(id=int(active_id)).first()
        except (ValueError, TypeError):
            current_session = None

    if not current_session:
        current_session = all_sessions.filter(is_current=True).first() or all_sessions.first()
        if has_session and current_session:
            request.session[f'active_session_{school.id}'] = current_session.id

    return current_session


def school_context(request):
    """
    Global context processor providing:
    - school (tenant info, logo, subscription status)
    - academic sessions scoped to current school
    - user permissions and SaaS platform admin flag
    """
    school = get_current_school(request)
    all_sessions = list(AcademicSession.objects.filter(school=school).order_by('-start_date'))
    active_session = get_active_session(request, school=school)

    user = request.user
    perms = {
        'can_manage_students': True,
        'can_manage_attendance': True,
        'can_manage_fees': True,
        'can_manage_exams': True,
        'can_manage_timetable': True,
        'can_manage_classes': True,
        'can_manage_sessions': True,
        'can_manage_users': True,
    }
    user_role = "Administrator"
    is_superadmin = False

    if user.is_authenticated:
        profile_obj = getattr(user, 'profile', None)
        if user.is_superuser or (profile_obj and profile_obj.is_platform_superadmin):
            is_superadmin = True
            user_role = "Platform Super Admin"
        elif profile_obj:
            user_role = profile_obj.get_role_display() if hasattr(profile_obj, 'get_role_display') else profile_obj.role
            perms = {
                'can_manage_students': profile_obj.can_manage_students,
                'can_manage_attendance': profile_obj.can_manage_attendance,
                'can_manage_fees': profile_obj.can_manage_fees,
                'can_manage_exams': profile_obj.can_manage_exams,
                'can_manage_timetable': profile_obj.can_manage_timetable,
                'can_manage_classes': profile_obj.can_manage_classes,
                'can_manage_sessions': profile_obj.can_manage_sessions,
                'can_manage_users': profile_obj.can_manage_users,
            }
        else:
            user_role = "Staff"

    days_left = school.days_remaining if school else 30
    subscription_expiring_soon = (0 <= days_left <= 5) and (not is_superadmin)

    return {
        'school': school,
        'all_academic_sessions': all_sessions,
        'current_academic_session': active_session,
        'active_session': active_session,
        'user_perms': perms,
        'current_user_role': user_role,
        'is_platform_superadmin': is_superadmin,
        'subscription_days_left': days_left,
        'subscription_expiring_soon': subscription_expiring_soon,
        'subscription_is_expired': (days_left < 0) and (not is_superadmin),
    }
