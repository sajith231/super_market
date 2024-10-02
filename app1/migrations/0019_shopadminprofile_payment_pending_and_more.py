# Generated by Django 5.1.1 on 2024-10-01 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0018_alter_shopadminprofile_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopadminprofile',
            name='payment_pending',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='shopadminprofile',
            name='validity',
            field=models.CharField(default='running', max_length=20),
        ),
    ]