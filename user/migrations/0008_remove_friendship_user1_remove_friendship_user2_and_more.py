# Generated by Django 4.2.16 on 2024-11-13 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0007_alter_user_is_private"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="friendship",
            name="user1",
        ),
        migrations.RemoveField(
            model_name="friendship",
            name="user2",
        ),
        migrations.AlterField(
            model_name="user",
            name="is_private",
            field=models.BooleanField(
                default=False,
                help_text="True if the account is private, False if public",
            ),
        ),
        migrations.DeleteModel(
            name="FriendRequest",
        ),
        migrations.DeleteModel(
            name="Friendship",
        ),
    ]