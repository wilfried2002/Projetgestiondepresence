# Generated by Django 5.1.6 on 2025-07-29 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0002_employee_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='salaire_journalier',
            field=models.IntegerField(blank=True, choices=[(4500, '4500 FCFA'), (5000, '5000 FCFA')], null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='employee/photos/'),
        ),
    ]
