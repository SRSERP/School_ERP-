from django import forms
from django.db.models import Q
from .models import (
    Student, Teacher, Attendance, FeeInvoice, FeePayment,
    FeeCategory, Exam, ExamResult, Notice, ClassLevel, Section, Subject, SchoolProfile, AcademicSession,
    Timetable
)
from .student_utils import find_duplicate_student


class StudentForm(forms.ModelForm):
    def __init__(self, *args, school=None, **kwargs):
        self.school = school
        super().__init__(*args, **kwargs)
        if school:
            self.fields['class_level'].queryset = ClassLevel.objects.filter(school=school).order_by('order', 'name')
            self.fields['section'].queryset = Section.objects.filter(class_level__school=school).select_related('class_level')

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
            'admission_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. SRS-2026-1001'}),
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
            'logo', 'principal_signature'
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

