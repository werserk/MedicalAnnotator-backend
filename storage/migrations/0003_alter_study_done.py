# Generated by Django 4.1.2 on 2022-11-02 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0002_alter_study_options_study_patient_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='done',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
