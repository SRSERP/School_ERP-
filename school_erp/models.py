import datetime
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class SchoolProfile(models.Model):
    name = models.CharField(max_length=150, default="SRS International Public School")
    short_name = models.CharField(max_length=50, blank=True, default="SRS School ERP")
    tagline = models.CharField(max_length=200, blank=True, default="Empowering Minds, Shaping Futures")
    affiliation_number = models.CharField(max_length=100, blank=True, default="CBSE-AFF/2026/SRS8892")
    board = models.CharField(max_length=50, blank=True, default="CBSE")
    school_code = models.CharField(max_length=50, default="SRS-DEL-042")
    address = models.TextField(blank=True, default="SRS Knowledge Park, Knowledge Boulevard, Sector 62, New Delhi - 110092")
    phone = models.CharField(max_length=30, blank=True, default="+91 98765 43210 / 011-23456789")
    email = models.EmailField(blank=True, default="contact@srsschool.edu.in")
    website = models.URLField(blank=True, default="https://srsschool.edu.in")
    principal_name = models.CharField(max_length=100, blank=True, default="Dr. Rajeshwar Sharma, Ph.D.")
    currency_symbol = models.CharField(max_length=10, blank=True, default="₹")
    academic_year = models.CharField(max_length=20, blank=True, default="2026-2027")

    # Branding & Customization
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True, help_text="Official School Logo for Receipts & Reports")
    principal_signature = models.ImageField(upload_to='school_signatures/', blank=True, null=True, help_text="Principal Signature / Official Stamp")

    # College / School UPI QR Code for Fee Payments
    upi_id = models.CharField(max_length=100, blank=True, default="srsschool@upi", help_text="College / School UPI ID for QR Payments")
    upi_payee_name = models.CharField(max_length=150, blank=True, default="SRS International Public School", help_text="Payee Name displayed in UPI apps")
    upi_qr_code = models.ImageField(upload_to='school_qr/', blank=True, null=True, help_text="Bank Merchant UPI QR Code Image")
    enable_qr_collection = models.BooleanField(default=True, help_text="Show QR Code on Fee Counter & Slips")

    # Session Registration Lock (Cannot create or switch to earlier sessions)
    registered_session_name = models.CharField(max_length=50, default="2026-2027", help_text="Initial registration session. School cannot create past sessions.")
    registered_session_start_date = models.DateField(default=datetime.date(2026, 4, 1), help_text="Anchor start date of registration session")

    # SaaS Subscription Management (₹499/month)
    subscription_plan_name = models.CharField(max_length=100, default="Standard SaaS Plan (₹499/mo)")
    subscription_monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('499.00'))
    subscription_start_date = models.DateField(default=datetime.date.today)
    subscription_end_date = models.DateField(default=datetime.date(2026, 10, 28))
    is_active = models.BooleanField(default=True, help_text="Set false by Super Admin to deactivate school access")
    notes = models.TextField(blank=True, null=True, help_text="Admin remarks / payment references")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.school_code})"

    @property
    def days_remaining(self):
        """Days remaining until subscription ends. Negative means expired."""
        if not self.subscription_end_date:
            return 0
        today = timezone.now().date()
        return (self.subscription_end_date - today).days

    @property
    def is_subscription_valid(self):
        """Active if is_active is True and subscription has not expired."""
        return self.is_active and self.days_remaining >= 0

    @property
    def subscription_status(self):
        if not self.is_active:
            return 'Deactivated'
        days = self.days_remaining
        if days < 0:
            return 'Expired'
        elif days <= 5:
            return 'Expiring Soon'
        else:
            return 'Active'

    @property
    def status_badge_class(self):
        status = self.subscription_status
        if status == 'Active':
            return 'badge-active'
        elif status == 'Expiring Soon':
            return 'badge-partial'
        elif status == 'Expired':
            return 'badge-unpaid'
        else:
            return 'badge-inactive'

    class Meta:
        verbose_name = "School Profile"
        verbose_name_plural = "School Profiles"


class Branch(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=150, help_text="e.g. Main Campus, North Wing, City Branch")
    code = models.CharField(max_length=30, unique=True, help_text="Unique branch identifier e.g. BR-DEL-01")
    address = models.TextField(blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=100, blank=True, default="")
    pincode = models.CharField(max_length=20, blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    branch_head = models.CharField(max_length=100, blank=True, default="", help_text="Name of Branch Incharge / Head")
    receipt_prefix = models.CharField(max_length=20, blank=True, default="RCP-BR1", help_text="Custom receipt numbering prefix for this branch")
    student_id_prefix = models.CharField(max_length=20, blank=True, default="STU-BR1", help_text="Custom student admission number prefix")
    logo = models.ImageField(upload_to='branch_logos/', blank=True, null=True, help_text="Branch-specific logo if different from main school")
    is_main_branch = models.BooleanField(default=False, help_text="Mark as main / primary branch")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name_plural = "Branches"
        ordering = ['-is_main_branch', 'name']


class AcademicSession(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='academic_sessions')
    name = models.CharField(max_length=50, help_text="e.g. 2026-2027")
    start_date = models.DateField(default=datetime.date.today)
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def total_students(self):
        return self.students.filter(is_active=True).count()

    class Meta:
        ordering = ['-start_date']


class ClassLevel(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='classes')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='class_levels')
    name = models.CharField(max_length=50, help_text="e.g. Class 10")
    code = models.CharField(max_length=20, help_text="e.g. C10")
    order = models.PositiveIntegerField(default=1, help_text="Order for sorting")

    def __str__(self):
        return self.name

    @property
    def total_students(self):
        return self.student_set.filter(is_active=True).count()

    class Meta:
        ordering = ['order', 'name']


class Teacher(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='teachers')
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    employee_id = models.CharField(max_length=30)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Female')
    dob = models.DateField(null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    designation = models.CharField(max_length=100, default="Senior Faculty")
    department = models.CharField(max_length=100, default="Academics")
    qualification = models.CharField(max_length=150, default="M.Sc., B.Ed.")
    joining_date = models.DateField(default=datetime.date.today)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=45000.00)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.designation})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['first_name', 'last_name']


class Section(models.Model):
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=10, help_text="e.g. A, B, C")
    capacity = models.PositiveIntegerField(default=40)
    room_number = models.CharField(max_length=20, default="Room 101")
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='class_teacher_sections')

    def __str__(self):
        return f"{self.class_level.name} - Section {self.name}"

    @property
    def student_count(self):
        return self.students.filter(is_active=True).count()

    class Meta:
        unique_together = ('class_level', 'name')
        ordering = ['class_level__order', 'name']


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    class_levels = models.ManyToManyField(ClassLevel, related_name='subjects', blank=True)
    teachers = models.ManyToManyField(Teacher, related_name='subjects_taught', blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['name']


class Student(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='students')
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    admission_number = models.CharField(max_length=30, unique=True)
    roll_number = models.PositiveIntegerField(default=1)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    dob = models.DateField(help_text="Date of Birth", default=datetime.date(2012, 1, 1))
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, default='B+')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='student_set')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='students')
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    admission_date = models.DateField(default=datetime.date.today)
    
    # Guardian / Parent Info
    parent_name = models.CharField(max_length=100)
    parent_relation = models.CharField(max_length=30, default="Father")
    parent_phone = models.CharField(max_length=20)
    parent_email = models.EmailField(blank=True, null=True)
    parent_occupation = models.CharField(max_length=100, default="Business / Professional")
    
    # Contact & Address
    address = models.TextField(default="New Delhi, India")
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    
    # Identity & Aadhaar (Optional)
    student_aadhaar = models.CharField(max_length=20, blank=True, null=True, help_text="12-digit Student Aadhaar Number (Optional)")
    parent_aadhaar = models.CharField(max_length=20, blank=True, null=True, help_text="12-digit Parent/Guardian Aadhaar Number (Optional)")
    
    # Photographs (Optional)
    student_photo = models.ImageField(upload_to='students/photos/', blank=True, null=True, help_text="Student Passport Photograph")
    parent_photo = models.ImageField(upload_to='parents/photos/', blank=True, null=True, help_text="Parent / Guardian Photograph")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_number})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def attendance_stats(self):
        total = self.attendance_records.count()
        if total == 0:
            return {'total': 0, 'present': 0, 'percentage': 100.0}
        present = self.attendance_records.filter(status='Present').count()
        late = self.attendance_records.filter(status='Late').count()
        # Half credit for late
        effective_present = present + (late * 0.5)
        pct = round((effective_present / total) * 100, 1)
        return {'total': total, 'present': present, 'late': late, 'percentage': pct}

    @property
    def fee_due_amount(self):
        unpaid = self.invoices.filter(status__in=['Unpaid', 'Partially Paid', 'Overdue'])
        total_due = sum((inv.remaining_due for inv in unpaid), Decimal('0.00'))
        return total_due

    class Meta:
        ordering = ['class_level__order', 'section__name', 'roll_number', 'first_name']


class StudentSessionEnrollment(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active Enrolled'),
        ('Promoted', 'Promoted to Next Session'),
        ('Retained', 'Retained in Same Class'),
        ('Passed_Out', 'Passed Out / Graduated'),
        ('Left', 'Left School / TC Issued'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='session_enrollments')
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='enrollments')
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    roll_number = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, default='Active', choices=STATUS_CHOICES)
    promoted_from_session = models.ForeignKey(AcademicSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='promotions_out')
    promoted_at = models.DateTimeField(auto_now_add=True)
    remarks = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'academic_session')
        ordering = ['-academic_session__start_date', 'class_level__order', 'roll_number']

    def __str__(self):
        return f"{self.student.full_name} - {self.academic_session.name} ({self.class_level.name})"


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=50, unique=True) # e.g. SUPER_ADMIN, SCHOOL_ADMIN, PRINCIPAL, TEACHER, ACCOUNTANT, HR, PARENT, STUDENT
    description = models.TextField(blank=True, null=True)
    is_system_role = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def user_count(self):
        return self.user_profiles.count()


class RolePermission(models.Model):
    MODULE_CHOICES = [
        ('STUDENTS', 'Students & SIS'),
        ('FEES', 'Fees & Accounts'),
        ('ATTENDANCE', 'Attendance'),
        ('EXAMS', 'Examinations & Marks'),
        ('TIMETABLE', 'Timetable & Routines'),
        ('SESSIONS', 'Academic Sessions & Promotion'),
        ('STAFF_HR', 'Teachers & Staff / HR'),
        ('USERS_ROLES', 'User Management & Roles'),
        ('AUDIT_LOGS', 'Audit Trail & Logs'),
        ('SETTINGS', 'School Profile & Settings'),
    ]

    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    module_code = models.CharField(max_length=50, choices=MODULE_CHOICES)
    module_name = models.CharField(max_length=100)
    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'module_code')
        ordering = ['role', 'module_code']

    def __str__(self):
        return f"{self.role.name} - {self.module_name}"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Super Admin', 'Super Admin'),
        ('School Admin', 'School Admin'),
        ('Principal', 'Principal'),
        ('Teacher', 'Teacher'),
        ('Accountant', 'Accountant'),
        ('HR', 'HR'),
        ('Parent', 'Parent'),
        ('Student', 'Student'),
        ('Administrator', 'Full Administrator'),
        ('Academic_Incharge', 'Academic / Exam Incharge'),
        ('Receptionist', 'Front Office / Admission Desk'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='staff_users')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_profiles')
    role_obj = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profiles')
    is_platform_superadmin = models.BooleanField(default=False, help_text="Platform SaaS Owner / Super Admin")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='School Admin')
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Scoped Access Restrictions
    assigned_teacher = models.OneToOneField(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profile')
    linked_students = models.ManyToManyField(Student, blank=True, related_name='parent_user_profiles')
    assigned_classes = models.ManyToManyField(ClassLevel, blank=True, related_name='assigned_staff_profiles')
    assigned_sections = models.ManyToManyField(Section, blank=True, related_name='assigned_staff_profiles')
    session_restriction = models.ForeignKey(AcademicSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='restricted_users')

    # Specific Menu-level Permissions (Fallback & backwards-compat)
    can_manage_students = models.BooleanField(default=True, help_text="Students SIS, Admissions & Promotion")
    can_manage_attendance = models.BooleanField(default=True, help_text="Daily Attendance & Register Reports")
    can_manage_fees = models.BooleanField(default=True, help_text="Fee Counter, Invoices & Defaulters")
    can_manage_exams = models.BooleanField(default=True, help_text="Exams, Marks Entry & Report Cards")
    can_manage_timetable = models.BooleanField(default=True, help_text="Routine & Classes Schedule")
    can_manage_classes = models.BooleanField(default=True, help_text="Class & Section Master")
    can_manage_sessions = models.BooleanField(default=True, help_text="Academic Session Creation & Move")
    can_manage_users = models.BooleanField(default=False, help_text="User Registration & Role Permissions")

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Record Created'),
        ('UPDATE', 'Record Updated'),
        ('DELETE', 'Record Deleted'),
        ('APPROVE', 'Operation Approved'),
        ('REJECT', 'Operation Rejected'),
        ('PUBLISH', 'Results Published'),
        ('EXPORT', 'Data Exported'),
        ('LOGIN', 'User Logged In'),
        ('LOGOUT', 'User Logged Out'),
        ('PERMISSION_CHANGE', 'Permissions Changed'),
    ]

    MODULE_CHOICES = [
        ('FEES', 'Fees & Accounts'),
        ('EXAMS', 'Examinations & Marks'),
        ('STUDENTS', 'Students & SIS'),
        ('USERS', 'User Management & Roles'),
        ('ATTENDANCE', 'Attendance'),
        ('STAFF_HR', 'Staff & HR'),
        ('SESSIONS', 'Sessions & Promotion'),
        ('SETTINGS', 'School Settings'),
    ]

    STATUS_CHOICES = [
        ('SUCCESS', 'Success / Executed'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='audit_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    user_role = models.CharField(max_length=50, blank=True, default='')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    module = models.CharField(max_length=30, choices=MODULE_CHOICES)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True, null=True)
    object_repr = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    changes_json = models.JSONField(blank=True, null=True)

    # Sensitive operations & approval workflow
    requires_approval = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='SUCCESS')
    reason = models.TextField(blank=True, null=True, help_text="Mandatory reason for sensitive action")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_audits')
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_remarks = models.TextField(blank=True, null=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {user_str} - {self.action} on {self.object_type} ({self.status})"

    @classmethod
    def log(cls, school, user, module, action, target="", details=""):
        return cls.objects.create(
            school=school,
            user=user,
            module=module if module in dict(cls.MODULE_CHOICES) else 'SETTINGS',
            action=action if action in dict(cls.ACTION_CHOICES) else 'CREATE',
            object_type=module,
            object_repr=str(target)[:250],
            description=details or '',
            status='SUCCESS'
        )



class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Excused', 'Excused'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=datetime.date.today)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Present')
    remarks = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.date}: {self.status}"

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date', 'student__roll_number']


class Timetable(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]

    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='timetables')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='timetables')
    day = models.CharField(max_length=15, choices=DAYS_OF_WEEK)
    period_number = models.PositiveIntegerField(default=1)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=20, default="Room 101")

    def __str__(self):
        return f"{self.class_level.name}-{self.section.name} | {self.day} P{self.period_number}: {self.subject.name}"

    class Meta:
        ordering = ['day', 'period_number']


class FeeCategory(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='fee_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    default_amount = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00)

    def __str__(self):
        return f"{self.name} (₹{self.default_amount})"

    class Meta:
        verbose_name_plural = "Fee Categories"


class ClassFeeMaster(models.Model):
    class_level = models.OneToOneField(ClassLevel, on_delete=models.CASCADE, related_name='fee_master')
    monthly_tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2000.00'), help_text="Monthly Tuition Fee")
    exam_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1500.00'), help_text="Per Exam Fee")
    transport_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1200.00'), help_text="Monthly Bus/Transport")
    admission_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5000.00'), help_text="One-time Admission Fee")
    book_set_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2500.00'), help_text="Book Set")
    dress_uniform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1800.00'), help_text="School Uniform / Dress")
    tie_belt_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('250.00'), help_text="Tie & Belt")
    diary_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('150.00'), help_text="School Diary")
    id_card_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('100.00'), help_text="Student ID Card")
    other_activity_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('500.00'), help_text="Other / Activity Fee")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.class_level.name} - Tuition: ₹{self.monthly_tuition_fee}"

    @property
    def total_annual_estimate(self):
        return (self.monthly_tuition_fee * 12) + (self.exam_fee * 2) + self.book_set_fee + self.dress_uniform_fee + self.tie_belt_fee + self.diary_fee + self.id_card_fee

    class Meta:
        verbose_name = "Class Fee Master"
        verbose_name_plural = "Class Fee Masters"
        ordering = ['class_level__order']


class FeeInvoice(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Partially Paid', 'Partially Paid'),
        ('Unpaid', 'Unpaid'),
        ('Overdue', 'Overdue'),
    ]

    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='invoices')
    invoice_number = models.CharField(max_length=40, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='invoices')
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_payable(self):
        return (self.amount - self.discount) + self.fine

    @property
    def total_paid(self):
        paid = self.payments.aggregate(total=models.Sum('amount_paid'))['total']
        return paid or Decimal('0.00')

    @property
    def remaining_due(self):
        due = self.total_payable - self.total_paid
        return max(Decimal('0.00'), due)

    def update_status(self):
        paid = self.total_paid
        payable = self.total_payable
        if paid >= payable and payable > Decimal('0.00'):
            self.status = 'Paid'
        elif paid > Decimal('0.00') and paid < payable:
            self.status = 'Partially Paid'
        elif timezone.now().date() > self.due_date and paid == Decimal('0.00'):
            self.status = 'Overdue'
        else:
            self.status = 'Unpaid'
        self.save()

    def __str__(self):
        return f"{self.invoice_number} - {self.student.full_name} ({self.fee_category.name})"

    class Meta:
        ordering = ['-created_at']


class FeePayment(models.Model):
    PAYMENT_MODES = [
        ('Cash', 'Cash'),
        ('UPI / QR', 'UPI / QR Code'),
        ('Debit/Credit Card', 'Debit/Credit Card'),
        ('Net Banking', 'Net Banking'),
        ('Cheque / DD', 'Cheque / DD'),
    ]

    receipt_number = models.CharField(max_length=40, unique=True)
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=datetime.date.today)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_MODES, default='Cash')
    transaction_reference = models.CharField(max_length=100, blank=True, null=True, help_text="UPI Txn ID, Cheque No, etc.")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.receipt_number} - ₹{self.amount_paid} ({self.invoice.student.full_name})"

    class Meta:
        ordering = ['-payment_date', '-created_at']


class FeeReceipt(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
    ]

    PAYMENT_MODES = [
        ('Cash', 'Cash'),
        ('UPI / QR', 'UPI / QR Code'),
        ('Debit/Credit Card', 'Debit/Credit Card'),
        ('Net Banking', 'Net Banking'),
        ('Cheque / DD', 'Cheque / DD'),
    ]

    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='receipts')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='receipts')
    receipt_number = models.CharField(max_length=40, unique=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='unified_receipts')
    payment_date = models.DateField(default=datetime.date.today)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_MODES, default='Cash')
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    previous_due_cleared = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_billed = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # Concession, Fine & Cashier Info
    concession_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    concession_type = models.CharField(max_length=100, blank=True, null=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    fine_waived = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collected_fee_receipts')

    # Cancellation & Audit Trail
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    cancellation_reason = models.TextField(blank=True, null=True)
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_fee_receipts')
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # Reconciliation
    is_reconciled = models.BooleanField(default=False)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    reconciled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reconciled_fee_receipts')
    reconciliation_notes = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status_tag = f" [{self.status}]" if self.status != 'Active' else ""
        return f"{self.receipt_number}{status_tag} - {self.student.full_name} (₹{self.amount_paid})"

    class Meta:
        ordering = ['-payment_date', '-created_at']


class FeeReceiptItem(models.Model):
    receipt = models.ForeignKey(FeeReceipt, on_delete=models.CASCADE, related_name='items')
    category_name = models.CharField(max_length=100)
    month_name = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. September 2026")
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.category_name} - ₹{self.amount} ({self.receipt.receipt_number})"


# ==============================================================================
# ADVANCED ENTERPRISE FEE MANAGEMENT MODELS
# ==============================================================================

class FeeHead(models.Model):
    FEE_TYPES = [
        ('Academic', 'Academic (Tuition / Regular)'),
        ('Transport', 'Transport / Bus Route'),
        ('Hostel', 'Hostel / Boarding / Mess'),
        ('Exam', 'Examination Fee'),
        ('Optional', 'Optional / Activity (Lab/Music/Sports)'),
        ('OneTime', 'One-time Admission / Registration'),
        ('Fine', 'Late Fine / Penalty'),
        ('CautionDeposit', 'Refundable Caution Deposit'),
        ('Other', 'Other Miscellaneous Charges'),
    ]

    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='fee_heads')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, blank=True)
    fee_type = models.CharField(max_length=30, choices=FEE_TYPES, default='Academic')
    description = models.TextField(blank=True, null=True)
    default_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_recurring = models.BooleanField(default=True, help_text="True for monthly/quarterly recurring, False for one-time")
    is_optional = models.BooleanField(default=False, help_text="Optional fee opted by specific students")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_fee_type_display()}) - ₹{self.default_amount}"

    class Meta:
        ordering = ['name']


class FeeStructure(models.Model):
    FREQUENCY_CHOICES = [
        ('Monthly', 'Monthly (12 Instalments)'),
        ('Quarterly', 'Quarterly (4 Instalments)'),
        ('Half_Yearly', 'Half-Yearly (2 Instalments)'),
        ('Annually', 'Annual Lump Sum (1 Instalment)'),
        ('Custom', 'Custom Schedules'),
    ]

    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='fee_structures')
    name = models.CharField(max_length=150)
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='fee_structures')
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='fee_structures')
    frequency = models.CharField(max_length=30, choices=FREQUENCY_CHOICES, default='Monthly')
    total_annual_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.class_level.name} ({self.academic_session.name})"

    class Meta:
        ordering = ['class_level__order', 'name']


class FeeStructureItem(models.Model):
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='items')
    fee_head = models.ForeignKey(FeeHead, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    frequency_note = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. Monthly, Per Term, Once")

    def __str__(self):
        return f"{self.fee_structure.name} - {self.fee_head.name}: ₹{self.amount}"


class FeeInstalmentSchedule(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, null=True, blank=True, related_name='instalment_schedules')
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    instalment_number = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=100, help_text="e.g. Instalment 1 (April 2026), Quarter 1")
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    grace_period_days = models.PositiveIntegerField(default=10, help_text="Days after due date before fine applies")
    late_fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50.00'))

    def __str__(self):
        return f"{self.class_level.name} - {self.title} (Due: {self.due_date})"

    class Meta:
        ordering = ['class_level__order', 'due_date', 'instalment_number']


class TransportRoute(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True)
    route_name = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=30, blank=True, help_text="Bus / Van registration number")
    driver_name = models.CharField(max_length=100, blank=True)
    driver_phone = models.CharField(max_length=20, blank=True)
    monthly_fare = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1200.00'))
    pickup_points = models.TextField(blank=True, help_text="Pickup stops separated by commas")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.route_name} (₹{self.monthly_fare}/mo)"


class HostelFacility(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True)
    hostel_name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=50, default="Double Sharing", help_text="e.g. Single AC, Double Non-AC, Dormitory")
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('6000.00'))
    warden_name = models.CharField(max_length=100, blank=True)
    warden_phone = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(default=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.hostel_name} - {self.room_type} (₹{self.monthly_fee}/mo)"


class StudentFacilityAllocation(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='facility_allocation')
    transport_route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True, blank=True)
    hostel_facility = models.ForeignKey(HostelFacility, on_delete=models.SET_NULL, null=True, blank=True)
    optional_heads = models.ManyToManyField(FeeHead, blank=True, limit_choices_to={'is_optional': True})
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Facilities: {self.student.full_name}"


class StudentConcession(models.Model):
    CONCESSION_TYPES = [
        ('Sibling Discount', 'Sibling Discount (Second Child)'),
        ('Merit Scholarship', 'Merit Scholarship / Academic Excellence'),
        ('Staff Ward', 'Staff Ward / Teacher Child'),
        ('EWS / Need Based', 'EWS / Financial Need Concession'),
        ('Sports Quota', 'Sports / Co-curricular Quota'),
        ('Management Discretion', 'Management Discretion / Special Waiver'),
    ]

    DISCOUNT_TYPES = [
        ('Percentage', 'Percentage (%)'),
        ('Fixed', 'Fixed Amount (₹)'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='concessions')
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    concession_type = models.CharField(max_length=50, choices=CONCESSION_TYPES, default='Sibling Discount')
    fee_head = models.ForeignKey(FeeHead, on_delete=models.SET_NULL, null=True, blank=True, help_text="Leave blank to apply to total tuition fee")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='Percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    reason = models.TextField(blank=True, help_text="Eligibility justification or reference")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        val_str = f"{self.discount_value}%" if self.discount_type == 'Percentage' else f"₹{self.discount_value}"
        return f"{self.student.full_name} - {self.get_concession_type_display()} ({val_str})"


class FeeRefund(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Processed', 'Disbursed / Paid'),
        ('Rejected', 'Rejected'),
    ]

    PAYMENT_MODES = [
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer / NEFT / IMPS'),
        ('Cheque / DD', 'Cheque / DD'),
        ('UPI', 'UPI'),
    ]

    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True)
    refund_number = models.CharField(max_length=40, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_refunds')
    receipt = models.ForeignKey(FeeReceipt, on_delete=models.SET_NULL, null=True, blank=True, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_date = models.DateField(default=datetime.date.today)
    refund_mode = models.CharField(max_length=30, choices=PAYMENT_MODES, default='Bank Transfer')
    reference_number = models.CharField(max_length=100, blank=True, help_text="Cheque No, UTR, Bank Ref")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reason = models.TextField(help_text="Reason for refund request (e.g. TC/Withdrawal, Excess Payment)")
    
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_fee_refunds')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_fee_refunds')
    approved_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.refund_number} - {self.student.full_name} (₹{self.amount}) [{self.status}]"

    class Meta:
        ordering = ['-created_at']


class StudentFeeLedger(models.Model):
    ENTRY_TYPES = [
        ('Fee_Charge', 'Fee Charge / Invoice'),
        ('Late_Fine', 'Late Fine Applied'),
        ('Fee_Payment', 'Fee Payment Received'),
        ('Concession', 'Concession / Discount Applied'),
        ('Refund', 'Fee Refund Disbursed'),
        ('Cancellation', 'Receipt Cancelled (Reversal)'),
    ]

    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='ledger_entries')
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    entry_date = models.DateField(default=datetime.date.today)
    entry_type = models.CharField(max_length=30, choices=ENTRY_TYPES)
    voucher_no = models.CharField(max_length=50, blank=True, help_text="Receipt No, Invoice No, or Refund No")
    fee_head = models.ForeignKey(FeeHead, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Fee Due / Charged")
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Amount Paid / Discounted")
    running_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    receipt = models.ForeignKey(FeeReceipt, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} | {self.entry_date} | {self.entry_type} | D:₹{self.debit} C:₹{self.credit}"

    class Meta:
        ordering = ['entry_date', 'id']


class FeeReminderLog(models.Model):
    CHANNEL_CHOICES = [
        ('WhatsApp', 'WhatsApp Message'),
        ('SMS', 'SMS Text'),
        ('Print_Slip', 'Printed Notice Slip'),
    ]

    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_reminders')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='WhatsApp')
    recipient_phone = models.CharField(max_length=30)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2)
    message_text = models.TextField()
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder -> {self.student.full_name} (₹{self.due_amount}) via {self.channel}"

    class Meta:
        ordering = ['-sent_at']


class Exam(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='exams')
    name = models.CharField(max_length=100, help_text="e.g. Mid-Term Examination 2026")
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-start_date']


class ExamResult(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+ (90-100%)'),
        ('A', 'A (80-89%)'),
        ('B', 'B (70-79%)'),
        ('C', 'C (60-69%)'),
        ('D', 'D (50-59%)'),
        ('F', 'F (Fail < 50%)'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES, blank=True)
    remarks = models.CharField(max_length=150, blank=True, null=True, default="Good performance")

    def calculate_grade(self):
        if self.max_marks > 0:
            pct = (float(self.marks_obtained) / float(self.max_marks)) * 100
            if pct >= 90:
                return 'A+'
            elif pct >= 80:
                return 'A'
            elif pct >= 70:
                return 'B'
            elif pct >= 60:
                return 'C'
            elif pct >= 50:
                return 'D'
            else:
                return 'F'
        return 'F'

    def save(self, *args, **kwargs):
        if not self.grade:
            self.grade = self.calculate_grade()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.full_name} | {self.subject.name}: {self.marks_obtained}/{self.max_marks} ({self.grade})"

    class Meta:
        unique_together = ('exam', 'student', 'subject')
        ordering = ['student', 'subject']


class Notice(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='notices')
    AUDIENCE_CHOICES = [
        ('All', 'Everyone (All School)'),
        ('Students', 'Students & Parents'),
        ('Teachers', 'Teachers & Staff Only'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    target_audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='All')
    is_urgent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{'[URGENT] ' if self.is_urgent else ''}{self.title}"

    class Meta:
        ordering = ['-is_urgent', '-created_at']


class BackupConfiguration(models.Model):
    FREQUENCY_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Manual', 'Manual Only'),
    ]
    STORAGE_CHOICES = [
        ('Local', 'Local Secure Storage'),
        ('Offsite', 'Offsite Cloud / External Storage'),
    ]
    school = models.OneToOneField(SchoolProfile, on_delete=models.CASCADE, related_name='backup_config')
    backup_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='Daily')
    backup_time = models.TimeField(default=datetime.time(2, 0), help_text="Scheduled backup time (e.g. 02:00 AM)")
    include_database = models.BooleanField(default=True)
    include_media_files = models.BooleanField(default=True, help_text="Include uploaded student photos, documents, and logos")
    is_encryption_enabled = models.BooleanField(default=True, help_text="Encrypt backup archives using AES/Passphrase")
    encryption_passphrase = models.CharField(max_length=128, blank=True, default="SRS-ERP-Secure-Key-2026", help_text="Secret passphrase used for backup integrity")
    retention_days = models.PositiveIntegerField(default=30, help_text="Retain backups for N days before auto-pruning")
    storage_location = models.CharField(max_length=20, choices=STORAGE_CHOICES, default='Local')
    auto_backup_active = models.BooleanField(default=True)
    last_backup_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Backup Config - {self.school.name}"


class BackupLog(models.Model):
    BACKUP_TYPE_CHOICES = [
        ('Full', 'Full (Database + Media)'),
        ('Database_Only', 'Database Only'),
        ('Media_Only', 'Media Only'),
    ]
    STATUS_CHOICES = [
        ('Success', 'Success'),
        ('Failed', 'Failed'),
        ('In_Progress', 'In Progress'),
    ]
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name='backup_logs')
    backup_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size_mb = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    checksum_sha256 = models.CharField(max_length=64, blank=True, default="", help_text="SHA-256 integrity checksum")
    backup_type = models.CharField(max_length=30, choices=BACKUP_TYPE_CHOICES, default='Full')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Success')
    is_encrypted = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False, help_text="Verified through isolated restore test")
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.backup_name} ({self.status}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']


class SecurityConfiguration(models.Model):
    ENVIRONMENT_CHOICES = [
        ('Development', 'Development'),
        ('Staging', 'Staging / Test'),
        ('Production', 'Production'),
    ]
    school = models.OneToOneField(SchoolProfile, on_delete=models.CASCADE, related_name='security_config')
    environment_mode = models.CharField(max_length=20, choices=ENVIRONMENT_CHOICES, default='Production')
    session_expiry_minutes = models.PositiveIntegerField(default=60, help_text="Idle session timeout in minutes")
    max_login_failures = models.PositiveIntegerField(default=5, help_text="Max consecutive failed logins before temporary IP lockout")
    lockout_duration_minutes = models.PositiveIntegerField(default=15, help_text="Lockout duration in minutes")
    password_min_length = models.PositiveIntegerField(default=8)
    password_require_uppercase = models.BooleanField(default=True)
    password_require_digits = models.BooleanField(default=True)
    password_require_special = models.BooleanField(default=True)
    enable_mfa = models.BooleanField(default=False, help_text="Require 2-Factor Authentication / Security PIN on login")
    mfa_security_pin = models.CharField(max_length=20, blank=True, default="123456", help_text="Optional Admin Security PIN for 2FA")
    enforce_https = models.BooleanField(default=True, help_text="Enforce HSTS and secure cookies")
    enable_suspicious_activity_alerts = models.BooleanField(default=True, help_text="Monitor and flag anomalous logins and permission violations")
    last_security_audit_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Security Policy ({self.environment_mode}) - {self.school.name}"


class LoginAttemptLog(models.Model):
    STATUS_CHOICES = [
        ('Success', 'Success'),
        ('Failed', 'Failed'),
        ('Locked_Out', 'Locked Out'),
    ]
    school = models.ForeignKey(SchoolProfile, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Failed')
    failure_reason = models.CharField(max_length=200, blank=True, default="")
    is_suspicious = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} [{self.status}] from {self.ip_address} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        ordering = ['-timestamp']


