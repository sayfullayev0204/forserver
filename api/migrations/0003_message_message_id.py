# Generated by Django 5.1.1 on 2024-09-07 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_channel_alter_message_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="message_id",
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
