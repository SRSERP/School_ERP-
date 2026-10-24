from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school_erp', '0002_feereceipt'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassFeeMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthly_tuition_fee', models.DecimalField(decimal_places=2, default=Decimal('2000.00'), help_text='Monthly Tuition Fee', max_digits=10)),
                ('exam_fee', models.DecimalField(decimal_places=2, default=Decimal('1500.00'), help_text='Per Exam Fee', max_digits=10)),
                ('transport_fee', models.DecimalField(decimal_places=2, default=Decimal('1200.00'), help_text='Monthly Bus/Transport', max_digits=10)),
                ('admission_fee', models.DecimalField(decimal_places=2, default=Decimal('5000.00'), help_text='One-time Admission Fee', max_digits=10)),
                ('book_set_fee', models.DecimalField(decimal_places=2, default=Decimal('2500.00'), help_text='Book Set', max_digits=10)),
                ('dress_uniform_fee', models.DecimalField(decimal_places=2, default=Decimal('1800.00'), help_text='School Uniform / Dress', max_digits=10)),
                ('tie_belt_fee', models.DecimalField(decimal_places=2, default=Decimal('250.00'), help_text='Tie & Belt', max_digits=10)),
                ('diary_fee', models.DecimalField(decimal_places=2, default=Decimal('150.00'), help_text='School Diary', max_digits=10)),
                ('id_card_fee', models.DecimalField(decimal_places=2, default=Decimal('100.00'), help_text='Student ID Card', max_digits=10)),
                ('other_activity_fee', models.DecimalField(decimal_places=2, default=Decimal('500.00'), help_text='Other / Activity Fee', max_digits=10)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('class_level', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fee_master', to='school_erp.classlevel')),
            ],
            options={
                'verbose_name': 'Class Fee Master',
                'verbose_name_plural': 'Class Fee Masters',
                'ordering': ['class_level__order'],
            },
        ),
    ]
