# Generated by Django 3.2.6 on 2023-07-26 02:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_summary_file_slider_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='summary_file',
            name='slider_value',
        ),
    ]
