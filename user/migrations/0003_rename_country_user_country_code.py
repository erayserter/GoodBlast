# Generated by Django 5.0.1 on 2024-01-29 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_user_coins'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='country',
            new_name='country_code',
        ),
    ]
