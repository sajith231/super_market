# Generated by Django 5.1.1 on 2024-09-21 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0009_remove_shopadminprofile_validity_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopadminprofile',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to='qr_codes/'),
        ),
    ]
