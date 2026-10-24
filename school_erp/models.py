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


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Administrator', 'Full Administrator'),
        ('Accountant', 'Fee Accountant'),
        ('Academic_Incharge', 'Academic / Exam Incharge'),
        ('Teacher', 'Teacher / Staff'),
        ('Receptionist', 'Front Office / Admission Desk'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='staff_users')
    is_platform_superadmin = models.BooleanField(default=False, help_text="Platform SaaS Owner / Super Admin")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Administrator')
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Specific Menu-level Permissions
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
    PAYMENT_MODES = [
        ('Cash', 'Cash'),
        ('UPI / QR', 'UPI / QR Code'),
        ('Debit/Credit Card', 'Debit/Credit Card'),
        ('Net Banking', 'Net Banking'),
        ('Cheque / DD', 'Cheque / DD'),
    ]

    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='receipts')
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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.receipt_number} - {self.student.full_name} (₹{self.amount_paid})"

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

