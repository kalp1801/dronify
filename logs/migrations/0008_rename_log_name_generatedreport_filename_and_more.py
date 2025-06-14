# Generated by Django 5.1.6 on 2025-05-07 06:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0007_generatedreport'),
    ]

    operations = [
        migrations.RenameField(
            model_name='generatedreport',
            old_name='log_name',
            new_name='filename',
        ),
        migrations.RemoveField(
            model_name='generatedreport',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='generatedreport',
            name='file_path',
        ),
        migrations.RemoveField(
            model_name='generatedreport',
            name='log_type',
        ),
        migrations.AddField(
            model_name='generatedreport',
            name='generated_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='generatedreport',
            name='report_type',
            field=models.CharField(choices=[('parsed', 'Parsed Drone Log'), ('telemetry', 'Telemetry'), ('exif', 'EXIF')], max_length=20),
        ),
    ]
