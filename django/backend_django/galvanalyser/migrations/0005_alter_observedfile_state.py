# Generated by Django 4.1.4 on 2023-01-12 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galvanalyser', '0004_alter_observedfile_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observedfile',
            name='state',
            field=models.TextField(choices=[('RETRY IMPORT', 'Retry Import'), ('IMPORT FAILED', 'Import Failed'), ('UNSTABLE', 'Unstable'), ('GROWING', 'Growing'), ('STABLE', 'Stable'), ('IMPORTING', 'Importing'), ('IMPORTED', 'Imported')], default='UNSTABLE'),
        ),
    ]
