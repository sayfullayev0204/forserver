# Generated by Django 5.0 on 2024-10-29 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0004_message_url"),
    ]

    operations = [
        migrations.RenameField(
            model_name="telegramuser",
            old_name="last_name",
            new_name="phone",
        ),
    ]
