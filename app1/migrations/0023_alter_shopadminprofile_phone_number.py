# Generated by Django 5.0.6 on 2024-10-02 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0022_alter_shopadminprofile_validity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopadminprofile',
            name='phone_number',
            field=models.BigIntegerField(),
        ),
    ]