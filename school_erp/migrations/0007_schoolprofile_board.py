from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_erp', '0006_alter_schoolprofile_options_academicsession_school_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='schoolprofile',
            name='board',
            field=models.CharField(default='CBSE', max_length=50),
        ),
    ]
