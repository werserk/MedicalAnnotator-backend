# Generated by Django 4.1.2 on 2022-10-28 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='upload_type',
            field=models.CharField(choices=[('DIR', 'Directory'), ('FILE', 'File')], default='FILE', max_length=4),
        ),
    ]
