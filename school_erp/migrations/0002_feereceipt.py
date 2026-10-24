import datetime
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school_erp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeeReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt_number', models.CharField(max_length=40, unique=True)),
                ('payment_date', models.DateField(default=datetime.date.today)),
                ('payment_method', models.CharField(choices=[('Cash', 'Cash'), ('UPI / QR', 'UPI / QR Code'), ('Debit/Credit Card', 'Debit/Credit Card'), ('Net Banking', 'Net Banking'), ('Cheque / DD', 'Cheque / DD')], default='Cash', max_length=30)),
                ('transaction_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('subtotal', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('previous_due_cleared', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('total_billed', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('remaining_balance_due', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unified_receipts', to='school_erp.student')),
            ],
            options={
                'ordering': ['-payment_date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='FeeReceiptItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=100)),
                ('month_name', models.CharField(blank=True, help_text='e.g. September 2026', max_length=50, null=True)),
                ('description', models.CharField(max_length=200)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='school_erp.feereceipt')),
            ],
        ),
    ]
