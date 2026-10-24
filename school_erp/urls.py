from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Students
    path('students/', views.student_list_view, name='student_list'),
    path('students/new/', views.student_create_view, name='student_create'),
    path('students/bulk-upload/', views.student_bulk_upload_view, name='student_bulk_upload'),
    path('students/export-template/', views.export_student_excel_template_view, name='student_excel_template'),
    path('students/<int:pk>/', views.student_detail_view, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_edit_view, name='student_edit'),
    path('students/<int:pk>/id-card/', views.student_id_card_view, name='student_id_card'),
    
    # Teachers
    path('teachers/', views.teacher_list_view, name='teacher_list'),
    path('teachers/new/', views.teacher_create_view, name='teacher_create'),
    path('teachers/<int:pk>/', views.teacher_detail_view, name='teacher_detail'),
    path('teachers/<int:pk>/edit/', views.teacher_edit_view, name='teacher_edit'),
    path('teachers/<int:pk>/delete/', views.teacher_delete_view, name='teacher_delete'),
    path('teacher/portal/', views.teacher_portal_view, name='teacher_portal'),
    
    # Academics
    path('classes/', views.classes_view, name='classes'),
    path('timetable/', views.timetable_view, name='timetable'),
    path('timetable/new/', views.timetable_create_view, name='timetable_create'),
    path('timetable/<int:pk>/edit/', views.timetable_edit_view, name='timetable_edit'),
    path('timetable/<int:pk>/delete/', views.timetable_delete_view, name='timetable_delete'),
    path('timetable/generate-default/', views.timetable_generate_default_view, name='timetable_generate_default'),
    
    # Attendance
    path('attendance/', views.attendance_view, name='attendance'),
    path('attendance/report/', views.attendance_report_view, name='attendance_report'),
    
    # Fees & Accounting
    path('fees/', views.fees_dashboard_view, name='fees_dashboard'),
    path('fees/dashboard/', views.fees_dashboard_view, name='fees_dashboard_alias'),
    path('fees/ledger/', views.fees_list_view, name='fees_list'),
    path('fees/counter/', views.fee_counter_view, name='fee_counter'),
    path('fees/master/', views.class_fee_master_view, name='class_fee_master'),
    path('fees/defaulters/', views.fees_defaulters_view, name='fees_defaulters'),
    path('fees/invoice/new/', views.fee_invoice_create_view, name='fee_invoice_create'),
    path('fees/invoice/<int:invoice_id>/pay/', views.fee_collect_view, name='fee_collect'),
    path('fees/receipt/<int:payment_id>/', views.fee_receipt_view, name='fee_receipt'),
    path('fees/receipt/unified/<int:receipt_id>/', views.unified_receipt_view, name='unified_receipt'),
    path('fees/defaulters/export-excel/', views.export_defaulters_excel_view, name='export_defaulters_excel'),
    
    # Public Slips for Parents (Accessible without login)
    path('slip/receipt/<str:receipt_number>/', views.public_fee_receipt_view, name='public_fee_receipt'),
    path('slip/payment/<str:receipt_number>/', views.public_payment_receipt_view, name='public_payment_receipt'),
    path('slip/report-card/<int:student_id>/<int:exam_id>/', views.public_report_card_view, name='public_report_card'),
    path('slip/id-card/<int:student_id>/', views.public_id_card_view, name='public_id_card'),
    
    # Smart Reports & Executive Analytics
    path('reports/', views.reports_hub_view, name='reports_hub'),
    path('reports/export/fees/', views.export_fees_report_excel, name='export_fees_report_excel'),
    
    # Examinations & Reports
    path('exams/', views.exam_list_view, name='exam_list'),
    path('exams/new/', views.exam_create_view, name='exam_create'),
    path('exams/<int:exam_id>/toggle-publish/', views.exam_toggle_publish_view, name='exam_toggle_publish'),
    path('exams/<int:exam_id>/delete/', views.exam_delete_view, name='exam_delete'),
    path('exams/marks/', views.marks_entry_view, name='marks_entry'),
    path('exams/<int:exam_id>/bulk-cards/<int:class_id>/', views.bulk_report_cards_view, name='bulk_report_cards'),
    path('students/<int:student_id>/report-card/<int:exam_id>/', views.report_card_view, name='report_card'),
    
    # Notices & Circulars
    path('notices/', views.notices_view, name='notices'),
    path('notices/new/', views.notice_create_view, name='notice_create'),
    
    # Academic Sessions Management & Switcher
    path('sessions/', views.academic_sessions_list_view, name='academic_sessions_manage'),
    path('sessions/switch/', views.switch_academic_session_view, name='switch_academic_session'),
    path('sessions/switch/<int:session_id>/', views.switch_academic_session_get_view, name='switch_academic_session_get'),
    
    # Student Promotion / Move to Next Session
    path('students/<int:pk>/promote/', views.student_promote_view, name='student_promote'),
    path('students/bulk-promote/', views.student_bulk_promote_view, name='student_bulk_promote'),
    
    # Staff User Registration & Role/Menu Permissions
    path('users/', views.user_list_view, name='user_list'),
    path('users/new/', views.user_create_view, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit_view, name='user_edit'),
    path('users/<int:pk>/toggle-status/', views.user_toggle_status_view, name='user_toggle_status'),

    # SaaS Platform Super Admin & Tenant Controls
    path('saas-admin/', views.saas_admin_dashboard_view, name='saas_admin_dashboard'),
    path('saas-admin/schools/new/', views.saas_school_create_view, name='saas_school_create'),
    path('saas-admin/schools/<int:school_id>/edit/', views.saas_school_edit_view, name='saas_school_edit'),
    path('saas-admin/schools/<int:school_id>/reset-password/', views.saas_school_reset_password_view, name='saas_school_reset_password'),
    path('saas-admin/schools/<int:school_id>/renew/', views.saas_school_renew_view, name='saas_school_renew'),
    path('saas-admin/schools/<int:school_id>/toggle-status/', views.saas_school_toggle_status_view, name='saas_school_toggle_status'),
    path('saas-admin/switch/<int:school_id>/', views.saas_switch_school_view, name='saas_switch_school'),

    # School Profile & Logo Branding Settings
    path('school/settings/', views.school_settings_view, name='school_settings'),

    # Auth
    path('login/', views.user_login_view, name='user_login'),
    path('logout/', views.user_logout_view, name='user_logout'),
]
