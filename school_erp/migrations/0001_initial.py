import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g. 2026-2027', max_length=50, unique=True)),
                ('start_date', models.DateField(default=datetime.date.today)),
                ('end_date', models.DateField()),
                ('is_current', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='ClassLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g. Class 10', max_length=50, unique=True)),
                ('code', models.CharField(help_text='e.g. C10', max_length=20, unique=True)),
                ('order', models.PositiveIntegerField(default=1, help_text='Order for sorting')),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='FeeCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('default_amount', models.DecimalField(decimal_places=2, default=5000.0, max_digits=10)),
            ],
            options={
                'verbose_name_plural': 'Fee Categories',
            },
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('target_audience', models.CharField(choices=[('All', 'Everyone (All School)'), ('Students', 'Students & Parents'), ('Teachers', 'Teachers & Staff Only')], default='All', max_length=20)),
                ('is_urgent', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-is_urgent', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SchoolProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='SRS International Public School', max_length=150)),
                ('short_name', models.CharField(default='SRS School ERP', max_length=50)),
                ('tagline', models.CharField(default='Empowering Minds, Shaping Futures', max_length=200)),
                ('affiliation_number', models.CharField(default='CBSE-AFF/2026/SRS8892', max_length=100)),
                ('school_code', models.CharField(default='SRS-DEL-042', max_length=50)),
                ('address', models.TextField(default='SRS Knowledge Park, Knowledge Boulevard, Sector 62, New Delhi - 110092')),
                ('phone', models.CharField(default='+91 98765 43210 / 011-23456789', max_length=30)),
                ('email', models.EmailField(default='contact@srsschool.edu.in', max_length=254)),
                ('website', models.URLField(default='https://srsschool.edu.in')),
                ('principal_name', models.CharField(default='Dr. Rajeshwar Sharma, Ph.D.', max_length=100)),
                ('currency_symbol', models.CharField(default='₹', max_length=10)),
                ('academic_year', models.CharField(default='2026-2027', max_length=20)),
            ],
            options={
                'verbose_name': 'School Profile',
                'verbose_name_plural': 'School Profile',
            },
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g. Mid-Term Examination 2026', max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('is_published', models.BooleanField(default=False)),
                ('academic_session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='school_erp.academicsession')),
            ],
            options={
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(max_length=30, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Female', max_length=10)),
                ('dob', models.DateField(blank=True, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=20)),
                ('designation', models.CharField(default='Senior Faculty', max_length=100)),
                ('department', models.CharField(default='Academics', max_length=100)),
                ('qualification', models.CharField(default='M.Sc., B.Ed.', max_length=150)),
                ('joining_date', models.DateField(default=datetime.date.today)),
                ('salary', models.DecimalField(decimal_places=2, default=45000.0, max_digits=10)),
                ('address', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['first_name', 'last_name'],
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('class_levels', models.ManyToManyField(blank=True, related_name='subjects', to='school_erp.classlevel')),
                ('teachers', models.ManyToManyField(blank=True, related_name='subjects_taught', to='school_erp.teacher')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g. A, B, C', max_length=10)),
                ('capacity', models.PositiveIntegerField(default=40)),
                ('room_number', models.CharField(default='Room 101', max_length=20)),
                ('class_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='school_erp.classlevel')),
                ('class_teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='class_teacher_sections', to='school_erp.teacher')),
            ],
            options={
                'ordering': ['class_level__order', 'name'],
                'unique_together': {('class_level', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admission_number', models.CharField(max_length=30, unique=True)),
                ('roll_number', models.PositiveIntegerField(default=1)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Male', max_length=10)),
                ('dob', models.DateField(default=datetime.date(2012, 1, 1), help_text='Date of Birth')),
                ('blood_group', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], default='B+', max_length=5)),
                ('admission_date', models.DateField(default=datetime.date.today)),
                ('parent_name', models.CharField(max_length=100)),
                ('parent_relation', models.CharField(default='Father', max_length=30)),
                ('parent_phone', models.CharField(max_length=20)),
                ('parent_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('parent_occupation', models.CharField(default='Business / Professional', max_length=100)),
                ('address', models.TextField(default='New Delhi, India')),
                ('emergency_contact', models.CharField(blank=True, max_length=20, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('class_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_set', to='school_erp.classlevel')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='school_erp.section')),
            ],
            options={
                'ordering': ['class_level__order', 'section__name', 'roll_number', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='FeeInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(max_length=40, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('fine', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('due_date', models.DateField()),
                ('status', models.CharField(choices=[('Paid', 'Paid'), ('Partially Paid', 'Partially Paid'), ('Unpaid', 'Unpaid'), ('Overdue', 'Overdue')], default='Unpaid', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('academic_session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='school_erp.academicsession')),
                ('fee_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='school_erp.feecategory')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='school_erp.student')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='FeePayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt_number', models.CharField(max_length=40, unique=True)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateField(default=datetime.date.today)),
                ('payment_method', models.CharField(choices=[('Cash', 'Cash'), ('UPI / QR', 'UPI / QR Code'), ('Debit/Credit Card', 'Debit/Credit Card'), ('Net Banking', 'Net Banking'), ('Cheque / DD', 'Cheque / DD')], default='Cash', max_length=30)),
                ('transaction_reference', models.CharField(blank=True, help_text='UPI Txn ID, Cheque No, etc.', max_length=100, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='school_erp.feeinvoice')),
            ],
            options={
                'ordering': ['-payment_date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Timetable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')], max_length=15)),
                ('period_number', models.PositiveIntegerField(default=1)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('room_number', models.CharField(default='Room 101', max_length=20)),
                ('class_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timetables', to='school_erp.classlevel')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timetables', to='school_erp.section')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='school_erp.subject')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='school_erp.teacher')),
            ],
            options={
                'ordering': ['day', 'period_number'],
            },
        ),
        migrations.CreateModel(
            name='ExamResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marks_obtained', models.DecimalField(decimal_places=2, max_digits=5)),
                ('max_marks', models.DecimalField(decimal_places=2, default=100.0, max_digits=5)),
                ('grade', models.CharField(blank=True, choices=[('A+', 'A+ (90-100%)'), ('A', 'A (80-89%)'), ('B', 'B (70-79%)'), ('C', 'C (60-69%)'), ('D', 'D (50-59%)'), ('F', 'F (Fail < 50%)')], max_length=5)),
                ('remarks', models.CharField(blank=True, default='Good performance', max_length=150, null=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='school_erp.exam')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_results', to='school_erp.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='school_erp.subject')),
            ],
            options={
                'ordering': ['student', 'subject'],
                'unique_together': {('exam', 'student', 'subject')},
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('status', models.CharField(choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Late', 'Late'), ('Excused', 'Excused')], default='Present', max_length=15)),
                ('remarks', models.CharField(blank=True, max_length=150, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='school_erp.student')),
            ],
            options={
                'ordering': ['-date', 'student__roll_number'],
                'unique_together': {('student', 'date')},
            },
        ),
    ]
