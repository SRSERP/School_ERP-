from django.contrib import admin
from .models import (
    SchoolProfile, AcademicSession, ClassLevel, Section, Subject,
    Teacher, Student, Attendance, Timetable, FeeCategory,
    FeeInvoice, FeePayment, Exam, ExamResult, Notice
)

admin.site.site_header = "SRS School ERP Administration"
admin.site.site_title = "SRS School ERP Portal"
admin.site.index_title = "School Management Dashboard"


@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'affiliation_number', 'school_code', 'phone', 'email')


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)


@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'order', 'total_students')
    ordering = ('order',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('class_level', 'name', 'room_number', 'class_teacher', 'capacity')
    list_filter = ('class_level',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    filter_horizontal = ('class_levels', 'teachers')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'designation', 'department', 'phone', 'is_active')
    search_fields = ('first_name', 'last_name', 'employee_id', 'phone', 'email')
    list_filter = ('department', 'designation', 'is_active')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'roll_number', 'first_name', 'last_name', 'class_level', 'section', 'parent_phone', 'is_active')
    search_fields = ('first_name', 'last_name', 'admission_number', 'parent_name', 'parent_phone')
    list_filter = ('class_level', 'section', 'is_active', 'gender')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'remarks')
    list_filter = ('status', 'date', 'student__class_level')
    search_fields = ('student__first_name', 'student__last_name', 'student__admission_number')


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('class_level', 'section', 'day', 'period_number', 'subject', 'teacher', 'start_time', 'end_time')
    list_filter = ('day', 'class_level', 'section')


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_amount', 'description')


@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'student', 'fee_category', 'amount', 'due_date', 'status')
    list_filter = ('status', 'fee_category', 'due_date')
    search_fields = ('invoice_number', 'student__first_name', 'student__last_name')


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'invoice', 'amount_paid', 'payment_date', 'payment_method')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('receipt_number', 'invoice__student__first_name', 'transaction_reference')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_session', 'start_date', 'end_date', 'is_active')


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'subject', 'marks_obtained', 'max_marks', 'grade')
    list_filter = ('exam', 'subject', 'grade')
    search_fields = ('student__first_name', 'student__last_name')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_audience', 'is_urgent', 'created_at', 'expiry_date')
    list_filter = ('is_urgent', 'target_audience')
    search_fields = ('title', 'content')
