# Generated by Django 4.2.16 on 2024-11-16 16:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0014_user_followers"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="followers",
        ),
    ]
