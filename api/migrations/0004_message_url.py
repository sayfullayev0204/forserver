# Generated by Django 5.1.1 on 2024-09-07 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_message_message_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='url',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]