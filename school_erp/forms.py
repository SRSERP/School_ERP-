from django import forms
from django.db.models import Q
from .models import (
    Student, Teacher, Attendance, FeeInvoice, FeePayment,
    FeeCategory, Exam, ExamResult, Notice, ClassLevel, Section, Subject, SchoolProfile, AcademicSession,
    Timetable, FeeHead, FeeRefund, StudentConcession, TransportRoute, HostelFacility, FeeReceipt,
    Role, RolePermission, UserProfile, AuditLog, Branch, BackupConfiguration, SecurityConfiguration
)
from .student_utils import find_duplicate_student


class StudentForm(forms.ModelForm):
    def __init__(self, *args, school=None, **kwargs):
        self.school = school
        super().__init__(*args, **kwargs)
        if school:
            self.fields['class_level'].queryset = ClassLevel.objects.filter(school=school).order_by('order', 'name')
            self.fields['section'].queryset = Section.objects.filter(class_level__school=school).select_related('class_level')
        else:
            self.fields['class_level'].queryset = ClassLevel.objects.none()
            self.fields['section'].queryset = Section.objects.none()

        # Enforce non-editable (read-only) admission number
        self.fields['admission_number'].widget.attrs['readonly'] = True
        self.fields['admission_number'].widget.attrs['style'] = 'background-color:#f1f5f9; cursor:not-allowed; font-weight:700; color:#334155;'

    class Meta:
        model = Student
        fields = [
            'admission_number', 'roll_number', 'first_name', 'last_name',
            'gender', 'dob', 'blood_group', 'class_level', 'section',
            'admission_date', 'parent_name', 'parent_relation', 'parent_phone',
            'parent_email', 'parent_occupation', 'address', 'emergency_contact',
            'student_aadhaar', 'parent_aadhaar', 'student_photo', 'parent_photo',
            'is_active'
        ]
        widgets = {
            'admission_number': forms.TextInput(attrs={
                'class': 'form-input',
                'readonly': 'readonly',
                'style': 'background-color:#f1f5f9; cursor:not-allowed; font-weight:700; color:#334155;',
                'placeholder': 'Auto-Generated Admission No'
            }),
            'roll_number': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 1'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'dob': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'class_level': forms.Select(attrs={'class': 'form-select', 'id': 'id_class_level'}),
            'section': forms.Select(attrs={'class': 'form-select', 'id': 'id_section'}),
            'admission_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Father/Mother/Guardian'}),
            'parent_relation': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Father/Mother/Guardian'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 9876543210'}),
            'parent_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'parent@example.com'}),
            'parent_occupation': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Profession / Business'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Full Residential Address'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Alternative Contact No'}),
            'student_aadhaar': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '12-digit Student Aadhaar (Optional)', 'maxlength': '14'}),
            'parent_aadhaar': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '12-digit Parent Aadhaar (Optional)', 'maxlength': '14'}),
            'student_photo': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
            'parent_photo': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        first_name = (cleaned_data.get('first_name') or '').strip()
        last_name = (cleaned_data.get('last_name') or '').strip()
        parent_name = (cleaned_data.get('parent_name') or '').strip()
        dob = cleaned_data.get('dob')

        if first_name and parent_name and dob:
            exclude_id = self.instance.pk if (self.instance and self.instance.pk) else None
            duplicate = find_duplicate_student(
                first_name=first_name,
                last_name=last_name,
                father_name=parent_name,
                dob=dob,
                exclude_id=exclude_id,
                school=self.school
            )
            if duplicate:
                dob_str = dob.strftime('%d/%m/%Y') if hasattr(dob, 'strftime') else str(dob)
                student_full = f"{first_name} {last_name}".strip()
                existing_class = duplicate.class_level.name if duplicate.class_level else 'N/A'
                err_msg = (
                    f"Duplicate entry rejected! Student '{student_full}' (Father: '{duplicate.parent_name}', "
                    f"DOB: {dob_str}) is already enrolled in school records "
                    f"[Admission No: {duplicate.admission_number}, Class: {existing_class}]. "
                    f"A student with the same Name, Father's Name, and Date of Birth cannot be registered again."
                )
                self.add_error(None, err_msg)
                self.add_error('first_name', "A student with this Name, Father's Name, and DOB is already registered.")
                self.add_error('parent_name', "Father's name matches an existing student record.")
                self.add_error('dob', f"Date of Birth {dob_str} matches an existing student record.")

        return cleaned_data


class TeacherForm(forms.ModelForm):
    subjects_taught = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2-multi', 'style': 'width:100%;'}),
        help_text="Select one or more subjects taught by this teacher"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['subjects_taught'].initial = self.instance.subjects_taught.all()

    def save(self, commit=True):
        teacher = super().save(commit=commit)
        if commit:
            teacher.subjects_taught.set(self.cleaned_data.get('subjects_taught', []))
        return teacher

    class Meta:
        model = Teacher
        fields = [
            'employee_id', 'first_name', 'last_name', 'gender', 'dob',
            'email', 'phone', 'designation', 'department', 'qualification',
            'joining_date', 'salary', 'address', 'subjects_taught', 'is_active'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. EMP-2026-01'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'dob': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'teacher@srsschool.edu.in'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 9876543210'}),
            'designation': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. PGT Mathematics'}),
            'department': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Science / Mathematics'}),
            'qualification': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. M.Sc, B.Ed'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'salary': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Monthly Salary'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Address'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }



class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ['receipt_number', 'amount_paid', 'payment_date', 'payment_method', 'transaction_reference', 'notes']
        widgets = {
            'receipt_number': forms.TextInput(attrs={'class': 'form-input', 'readonly': 'readonly'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'transaction_reference': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. UPI Ref / Cheque No / Cash Ref'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Remarks (Optional)'}),
        }


class FeeInvoiceForm(forms.ModelForm):
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['student'].queryset = Student.objects.filter(school=school, is_active=True).select_related('class_level', 'section')
            self.fields['fee_category'].queryset = FeeCategory.objects.filter(school=school)
        else:
            self.fields['student'].queryset = Student.objects.filter(is_active=True).select_related('class_level', 'section')
        self.fields['student'].label_from_instance = lambda obj: f"{obj.admission_number} | {obj.full_name} ({obj.class_level.name if obj.class_level else 'N/A'} - Sec {obj.section.name if obj.section else 'N/A'})"

    class Meta:
        model = FeeInvoice
        fields = ['invoice_number', 'student', 'fee_category', 'amount', 'discount', 'fine', 'due_date']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. INV-2026-0099'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'fee_category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Fee Amount (₹)'}),
            'discount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00'}),
            'fine': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'target_audience', 'is_urgent', 'expiry_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Notice Headline'}),
            'content': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Full announcement details...'}),
            'target_audience': forms.Select(attrs={'class': 'form-select'}),
            'is_urgent': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class SchoolSettingsForm(forms.ModelForm):
    class Meta:
        model = SchoolProfile
        fields = [
            'name', 'short_name', 'tagline', 'affiliation_number',
            'board', 'school_code', 'address', 'phone', 'email',
            'website', 'principal_name', 'currency_symbol',
            'logo', 'principal_signature',
            'upi_id', 'upi_payee_name', 'upi_qr_code', 'enable_qr_collection'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Official School Name', 'required': 'required'}),
            'short_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. SRS School'}),
            'tagline': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'School Motto / Tagline'}),
            'affiliation_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. CBSE-AFF/2026/8892'}),
            'board': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. CBSE / ICSE / State Board'}),
            'school_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. SRS-01'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Full Postal Address for Print Slips'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact Phone / Landline'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'contact@school.edu.in'}),
            'website': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://school.edu.in'}),
            'principal_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Principal / Director Name'}),
            'currency_symbol': forms.TextInput(attrs={'class': 'form-input', 'style': 'max-width:90px;'}),
            'logo': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*', 'id': 'schoolLogoInput'}),
            'principal_signature': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*', 'id': 'principalSigInput'}),
            'upi_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. srsschool@upi / 9876543210@paytm'}),
            'upi_payee_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Account / Institution Name for UPI'}),
            'upi_qr_code': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*', 'id': 'upiQrInput'}),
            'enable_qr_collection': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class FeeHeadForm(forms.ModelForm):
    class Meta:
        model = FeeHead
        fields = ['name', 'code', 'fee_type', 'default_amount', 'is_recurring', 'is_optional', 'is_active', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Tuition Fee, Transport Fee, Hostel Fee', 'required': 'required'}),
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. TUITION, TRANS, HOSTEL'}),
            'fee_type': forms.Select(attrs={'class': 'form-select'}),
            'default_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0.00'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_optional': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Fee Head description or remarks'}),
        }


class FeeRefundForm(forms.ModelForm):
    class Meta:
        model = FeeRefund
        fields = ['student', 'receipt', 'amount', 'refund_date', 'refund_mode', 'reference_number', 'reason']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select', 'id': 'refundStudentSelect'}),
            'receipt': forms.Select(attrs={'class': 'form-select', 'id': 'refundReceiptSelect'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0.00', 'required': 'required'}),
            'refund_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date', 'required': 'required'}),
            'refund_mode': forms.Select(attrs={'class': 'form-select'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Bank Ref / Cheque No / UTR'}),
            'reason': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Justification for refund (Withdrawal, TC, Excess payment, etc.)', 'required': 'required'}),
        }


class StudentConcessionForm(forms.ModelForm):
    class Meta:
        model = StudentConcession
        fields = ['student', 'academic_session', 'concession_type', 'fee_head', 'discount_type', 'discount_value', 'reason', 'is_active']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select', 'id': 'concessionStudentSelect'}),
            'academic_session': forms.Select(attrs={'class': 'form-select'}),
            'concession_type': forms.Select(attrs={'class': 'form-select'}),
            'fee_head': forms.Select(attrs={'class': 'form-select'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '10'}),
            'reason': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Eligibility justification'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class TransportRouteForm(forms.ModelForm):
    class Meta:
        model = TransportRoute
        fields = ['route_name', 'vehicle_number', 'driver_name', 'driver_phone', 'monthly_fare', 'pickup_points', 'is_active']
        widgets = {
            'route_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Route 1 - City Center to Campus', 'required': 'required'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. DL 1PB 4589'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Driver / Attendant Name'}),
            'driver_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Driver Contact Number'}),
            'monthly_fare': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '1200.00'}),
            'pickup_points': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Comma-separated stop points'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class HostelFacilityForm(forms.ModelForm):
    class Meta:
        model = HostelFacility
        fields = ['hostel_name', 'room_type', 'monthly_fee', 'warden_name', 'warden_phone', 'capacity', 'is_active']
        widgets = {
            'hostel_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Vivekananda Boys Hostel', 'required': 'required'}),
            'room_type': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Double AC / 3-Bed Sharing'}),
            'monthly_fee': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '6000.00'}),
            'warden_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Warden Name'}),
            'warden_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Warden Contact Phone'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '50'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class ExamForm(forms.ModelForm):
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['academic_session'].queryset = AcademicSession.objects.filter(school=school).order_by('-start_date')

    class Meta:
        model = Exam
        fields = ['name', 'academic_session', 'start_date', 'end_date', 'is_active', 'is_published']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Mid-Term / Annual Examination 2026', 'required': 'required'}),
            'academic_session': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date', 'required': 'required'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date', 'required': 'required'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class TimetableForm(forms.ModelForm):
    def __init__(self, *args, school=None, class_level=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['class_level'].queryset = ClassLevel.objects.filter(school=school).order_by('order', 'name')
            self.fields['teacher'].queryset = Teacher.objects.filter(school=school, is_active=True).order_by('first_name', 'last_name')
        else:
            self.fields['teacher'].queryset = Teacher.objects.filter(is_active=True).order_by('first_name', 'last_name')

        if class_level:
            self.fields['section'].queryset = Section.objects.filter(class_level=class_level).order_by('name')
            self.fields['subject'].queryset = Subject.objects.filter(Q(class_levels=class_level) | Q(class_levels__isnull=True)).distinct().order_by('name')

    class Meta:
        model = Timetable
        fields = ['class_level', 'section', 'day', 'period_number', 'subject', 'teacher', 'start_time', 'end_time', 'room_number']
        widgets = {
            'class_level': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'day': forms.Select(attrs={'class': 'form-select'}),
            'period_number': forms.NumberInput(attrs={'class': 'form-input', 'min': '1', 'max': '12', 'placeholder': 'e.g. 1'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'room_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Room 101'}),
        }


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Vice Principal, Lab Assistant', 'required': 'required'}),
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. VICE_PRINCIPAL, LAB_ASST', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Brief description of roles and responsibilities'}),
        }


class UserCreateUpdateForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. jdoe_teacher'})
    )
    first_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@school.edu'})
    )
    password = forms.CharField(
        max_length=128, required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Enter password (leave blank to keep existing)'})
    )
    role_obj = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_role_obj'})
    )
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact phone number'})
    )
    assigned_teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_assigned_teacher'}),
        help_text="Link this login account to an existing Teacher record."
    )
    assigned_classes = forms.ModelMultipleChoiceField(
        queryset=ClassLevel.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5, 'id': 'id_assigned_classes'}),
        help_text="Hold Ctrl / Cmd to select multiple classes."
    )
    assigned_sections = forms.ModelMultipleChoiceField(
        queryset=Section.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5, 'id': 'id_assigned_sections'}),
        help_text="Hold Ctrl / Cmd to select multiple sections."
    )
    linked_students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6, 'id': 'id_linked_students'}),
        help_text="Hold Ctrl / Cmd to link children for Parent role."
    )
    session_restriction = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Optional: Lock user's view strictly to this academic session."
    )
    is_active = forms.BooleanField(
        required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    def __init__(self, *args, instance_user=None, school=None, is_superadmin=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance_user = instance_user
        if not is_superadmin:
            self.fields['role_obj'].queryset = Role.objects.exclude(code='SUPER_ADMIN')
        if school:
            self.fields['assigned_classes'].queryset = ClassLevel.objects.filter(school=school).order_by('order', 'name')
            self.fields['assigned_sections'].queryset = Section.objects.filter(class_level__school=school).order_by('name')
            self.fields['assigned_teacher'].queryset = Teacher.objects.filter(school=school, is_active=True).order_by('first_name', 'last_name')
            self.fields['linked_students'].queryset = Student.objects.filter(school=school, is_active=True).order_by('first_name', 'last_name')
            self.fields['session_restriction'].queryset = AcademicSession.objects.filter(school=school).order_by('-start_date')

        if instance_user:
            self.fields['username'].initial = instance_user.username
            self.fields['first_name'].initial = instance_user.first_name
            self.fields['last_name'].initial = instance_user.last_name
            self.fields['email'].initial = instance_user.email
            self.fields['is_active'].initial = instance_user.is_active
            profile = getattr(instance_user, 'profile', None)
            if profile:
                self.fields['role_obj'].initial = profile.role_obj
                self.fields['phone'].initial = profile.phone
                self.fields['assigned_teacher'].initial = profile.assigned_teacher
                self.fields['assigned_classes'].initial = profile.assigned_classes.all()
                self.fields['assigned_sections'].initial = profile.assigned_sections.all()
                self.fields['linked_students'].initial = profile.linked_students.all()
                self.fields['session_restriction'].initial = profile.session_restriction


class AuditApprovalForm(forms.Form):
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Approval or rejection justification remarks...'}),
        required=False
    )


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = [
            'name', 'code', 'branch_head', 'phone', 'email',
            'receipt_prefix', 'student_id_prefix', 'address', 'city', 'state', 'pincode',
            'is_main_branch', 'is_active', 'logo'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Main Campus / City Wing'}),
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. BR-DEL-01'}),
            'branch_head': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Mr. Rajesh Kumar'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. +91 9876543210'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'e.g. branch@school.edu.in'}),
            'receipt_prefix': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. RCP-BR1'}),
            'student_id_prefix': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. STU-BR1'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Branch street address'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'State'}),
            'pincode': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'PIN Code'}),
            'is_main_branch': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'logo': forms.FileInput(attrs={'class': 'form-input'}),
        }


class BackupConfigurationForm(forms.ModelForm):
    class Meta:
        model = BackupConfiguration
        fields = [
            'backup_frequency', 'backup_time', 'storage_location',
            'retention_days', 'include_database', 'include_media_files',
            'is_encryption_enabled', 'encryption_passphrase', 'auto_backup_active'
        ]
        widgets = {
            'backup_frequency': forms.Select(attrs={'class': 'form-select'}),
            'backup_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'storage_location': forms.Select(attrs={'class': 'form-select'}),
            'retention_days': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 365}),
            'include_database': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'include_media_files': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_encryption_enabled': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'encryption_passphrase': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Encryption Passphrase'}),
            'auto_backup_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class SecurityConfigurationForm(forms.ModelForm):
    class Meta:
        model = SecurityConfiguration
        fields = [
            'environment_mode', 'session_expiry_minutes', 'max_login_failures',
            'lockout_duration_minutes', 'password_min_length', 'password_require_uppercase',
            'password_require_digits', 'password_require_special', 'enable_mfa',
            'mfa_security_pin', 'enforce_https', 'enable_suspicious_activity_alerts'
        ]
        widgets = {
            'environment_mode': forms.Select(attrs={'class': 'form-select'}),
            'session_expiry_minutes': forms.NumberInput(attrs={'class': 'form-input', 'min': 5, 'max': 1440}),
            'max_login_failures': forms.NumberInput(attrs={'class': 'form-input', 'min': 3, 'max': 20}),
            'lockout_duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 1440}),
            'password_min_length': forms.NumberInput(attrs={'class': 'form-input', 'min': 6, 'max': 32}),
            'password_require_uppercase': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'password_require_digits': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'password_require_special': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'enable_mfa': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'mfa_security_pin': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Optional 2FA Security PIN'}),
            'enforce_https': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'enable_suspicious_activity_alerts': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }



