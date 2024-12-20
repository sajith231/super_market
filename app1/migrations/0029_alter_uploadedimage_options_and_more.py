# Generated by Django 5.1.1 on 2024-11-20 04:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0028_alter_uploadedimage_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='uploadedimage',
            options={'ordering': ['display_order', '-uploaded_at']},
        ),
        migrations.RemoveField(
            model_name='uploadedimage',
            name='description',
        ),
        migrations.AddField(
            model_name='uploadedimage',
            name='display_order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='uploadedimage',
            name='image',
            field=models.ImageField(upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='uploadedimage',
            name='shop_admin_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_images', to='app1.shopadminprofile'),
        ),
    ]
