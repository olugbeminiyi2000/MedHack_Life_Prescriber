# Generated by Django 4.2.7 on 2024-06-30 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prescription_ongo', '0010_clinicuser_designation'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinicuser',
            name='medical_institution',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
