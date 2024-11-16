# Generated by Django 4.2.16 on 2024-11-14 05:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0009_alter_follow_follower_alter_follow_table"),
    ]

    operations = [
        migrations.RenameField(
            model_name="follow",
            old_name="user",
            new_name="following",
        ),
        migrations.AlterUniqueTogether(
            name="follow",
            unique_together={("following", "follower")},
        ),
    ]