# Generated by Django 4.2.16 on 2024-11-11 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0005_test_migrations"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="profile_image",
            field=models.ImageField(null=True, upload_to="profile/"),
        ),
    ]
